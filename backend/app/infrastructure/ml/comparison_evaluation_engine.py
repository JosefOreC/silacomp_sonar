"""Captura y replay de llamadas NLP para ejecutar el comparador completo sin efectos laterales."""

import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import platform
from typing import Any, Callable, Dict, Optional, Tuple

import numpy as np

from app.application.compare_syllabi import CompareSyllabiUseCase
from app.domain.comparison import Comparison, MatchClassification
from app.domain.content import ContentItem
from app.domain.model_version import ModelVersion
from app.domain.ports import IComparisonEvaluationEngine, IModelInferenceService
from app.domain.scientific_evaluation import EvaluationValidationError, evaluation_digest
from app.domain.scoring import BASELINE_VERSION
from app.infrastructure.ml.model_inference_service import ModelInferenceService
from app.infrastructure.nlp.vector_service import NlpVectorService
from app.settings import data_dir


def canonical_hash(value: Any) -> str:
    return evaluation_digest(value)


class RecordedVectors:
    METHODS = {"encode_texts", "compute_semantic_similarity", "compute_lexical_similarity",
               "compute_keyword_overlap", "compute_structural_similarity", "extract_shared_keywords"}

    def __init__(self, trace: Dict[str, Any], delegate: Optional[NlpVectorService] = None) -> None:
        self.trace = trace
        self.delegate = delegate

    def __getattr__(self, name: str) -> Callable[..., Any]:
        if name not in self.METHODS:
            raise AttributeError(name)

        def call(*args: Any, **kwargs: Any) -> Any:
            key = canonical_hash([name, args, kwargs])
            if key not in self.trace:
                if self.delegate is None:
                    raise EvaluationValidationError(f"El replay requiere una llamada NLP no registrada: {name}.")
                value = getattr(self.delegate, name)(*args, **kwargs)
                if isinstance(value, np.ndarray):
                    recorded = {"kind": "array", "dtype": str(value.dtype), "value": value.tolist()}
                else:
                    recorded = {"kind": "value", "value": value}
                # Verificar finitud y representación JSON antes de congelar.
                json.dumps(recorded, allow_nan=False)
                self.trace[key] = recorded
            result = self.trace[key]
            return np.array(result["value"], dtype=result["dtype"]) if result["kind"] == "array" else result["value"]

        return call


class StrictInference(IModelInferenceService):
    def __init__(self, delegate: ModelInferenceService) -> None:
        self.delegate = delegate

    def predict_pair(self, features: Dict[str, float]) -> Tuple[MatchClassification, float, Dict[str, float]]:
        prediction = self.delegate.predict_pair(features)
        if prediction is None:
            raise EvaluationValidationError("Falló la inferencia del modelo; no se aplicó fallback al baseline.")
        return prediction


class ComparisonEvaluationEngine(IComparisonEvaluationEngine):
    def __init__(self, vectors: NlpVectorService) -> None:
        self.vectors = vectors

    def fingerprint(self) -> Dict[str, Any]:
        app_dir = Path(__file__).resolve().parents[2]
        files = ["application/compare_syllabi.py", "domain/scoring.py", "domain/content.py", "domain/evaluation_metrics.py",
                 "domain/academic_sources.py", "application/scientific_evaluation_service.py",
                 "infrastructure/nlp/normalizer.py", "infrastructure/nlp/vector_service.py",
                 "infrastructure/ml/model_inference_service.py", "infrastructure/ml/comparison_evaluation_engine.py"]
        return {"code": {file: hashlib.sha256((app_dir / file).read_bytes()).hexdigest() for file in files},
                "python": platform.python_version(),
                "packages": {package: version(package) for package in ("numpy", "scipy", "scikit-learn", "sentence-transformers", "joblib")}}

    @staticmethod
    def _run(case: Dict[str, Any], vectors: RecordedVectors, model: Optional[ModelVersion],
             inference: Optional[IModelInferenceService] = None) -> Comparison:
        return CompareSyllabiUseCase(
            vector_service=vectors, comparison_repository=None, model_version=model.version_id if model else BASELINE_VERSION,
            inference_service=inference,
        ).execute(
            objective_syllabus_id=case["objective_syllabus"]["id"], compared_syllabus_id=case["compared_syllabus"]["id"],
            objective_items=[ContentItem(**item) for item in case["objective_items"]],
            compared_items=[ContentItem(**item) for item in case["compared_items"]],
            weights=case["weights"], thresholds=case["thresholds"],
        )

    def capture(self, case: Dict[str, Any]) -> Dict[str, Any]:
        trace = {}
        vectors = RecordedVectors(trace, self.vectors)
        self._run(case, vectors, None)
        # La asignación de otra versión puede elegir otro candidato primario/secundario.
        for primary in case["compared_items"]:
            for secondary in case["compared_items"]:
                if primary["id"] != secondary["id"]:
                    vectors.compute_lexical_similarity(primary["text"], secondary["text"])
        return trace

    def evaluate(self, case: Dict[str, Any], model: Optional[ModelVersion]) -> Tuple[Comparison, Dict[str, Any]]:
        inference = None
        artifact = None
        digest = None
        if model is not None:
            artifact = Path(model.artifact_path) if model.artifact_path else data_dir() / "models" / f"{model.version_id}.joblib"
            if not artifact.is_file():
                raise EvaluationValidationError("El artefacto del modelo no está disponible.")
            content = artifact.read_bytes()
            digest = hashlib.sha256(content).hexdigest()
            delegate = ModelInferenceService()
            if not delegate.load_artifact_bytes(content, model.version_id):
                raise EvaluationValidationError("No se pudo cargar el artefacto del modelo.")
            inference = StrictInference(delegate)
        manifest = {"version_id": model.version_id if model else BASELINE_VERSION, "artifact_sha256": digest,
                    "algorithm": model.algorithm_name if model else "Hybrid-Bipartite-Adaptive",
                    "training_source_hash": canonical_hash(model.metrics.get("data_source_tokens")) if model else None,
                    "parameters": model.parameters if model else {}, "thresholds": case["thresholds"], "weights": case["weights"]}
        result = self._run(case, RecordedVectors(case["nlp_trace"]), model, inference)
        if artifact is not None and hashlib.sha256(artifact.read_bytes()).hexdigest() != digest:
            raise EvaluationValidationError("El artefacto cambió durante la evaluación.")
        manifest["manifest_hash"] = canonical_hash(manifest)
        return result, manifest
