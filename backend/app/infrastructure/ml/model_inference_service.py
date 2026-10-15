"""
Servicio de Inferencia para Modelos Supervisados de Clasificación y Calibración Probabilística (Fase 2.0).
Carga el modelo activo en memoria y calcula probabilidades calibradas para cada correspondencia temática.
"""

import os
import io
from typing import Any, Dict, Optional, Tuple
import joblib
import numpy as np

from app.domain.comparison import MatchClassification
from app.domain.model_version import ModelVersion
from app.domain.ports import IModelInferenceService
from app.settings import data_dir


class ModelInferenceService(IModelInferenceService):
    """Ejecuta inferencia con modelos entrenados y calcula probabilidades para el caso de uso de comparación."""

    def __init__(self, models_dir: Optional[str] = None) -> None:
        self.models_dir = models_dir or str(data_dir() / "models")
        self._cached_version_id: Optional[str] = None
        self._cached_model_artifact: Optional[Dict[str, Any]] = None

    def load_model(self, version: ModelVersion) -> bool:
        """Carga el artefacto serializado del modelo en memoria si no está ya cacheado."""
        if self._cached_version_id == version.version_id and self._cached_model_artifact is not None:
            return True

        self._cached_version_id = None
        self._cached_model_artifact = None
        artifact_path = version.artifact_path or os.path.join(self.models_dir, f"{version.version_id}.joblib")
        if not os.path.exists(artifact_path):
            return False

        try:
            with open(artifact_path, "rb") as artifact:
                content = artifact.read()
            return self.load_artifact_bytes(content, version.version_id)
        except Exception:
            self._cached_model_artifact = None
            self._cached_version_id = None
            return False

    def load_artifact_bytes(self, content: bytes, version_id: str) -> bool:
        """Carga exactamente los bytes cuya huella se registra en el experimento."""
        self._cached_model_artifact = None
        self._cached_version_id = None
        try:
            artifact = joblib.load(io.BytesIO(content))
            if not isinstance(artifact, dict) or "model" not in artifact:
                return False
            self._cached_model_artifact = artifact
            self._cached_version_id = version_id
            return True
        except Exception:
            return False

    def predict_pair(
        self,
        features: Dict[str, float],
    ) -> Optional[Tuple[MatchClassification, float, Dict[str, float]]]:
        """
        Calcula la clasificación y las probabilidades estimadas para un par temático.

        Returns:
            Tuple con (Clasificación, Score Calibrado [0, 1], Diccionario de probabilidades por clase).
            Retorna None si no hay modelo cargado.
        """
        if self._cached_model_artifact is None:
            return None

        model = self._cached_model_artifact["model"]
        x_vec = np.array([
            [
                float(features.get("semantic_sim", 0.0)),
                float(features.get("lexical_sim", 0.0)),
                float(features.get("asymmetric_containment", features.get("lexical_sim", 0.0))),
                float(features.get("structural_sim", 0.0)),
                float(features.get("keyword_overlap", 0.0)),
            ]
        ], dtype=np.float32)

        try:
            pred_class_idx = int(model.predict(x_vec)[0])
            prob_dict: Dict[str, float] = {}

            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(x_vec)[0]
                classes = list(getattr(model, "classes_", [0, 1, 2]))
                for cls_idx, p in zip(classes, probs):
                    if cls_idx == 2:
                        prob_dict["MATCH"] = round(float(p), 4)
                    elif cls_idx == 1:
                        prob_dict["PARTIAL_MATCH"] = round(float(p), 4)
                    else:
                        prob_dict["NO_MATCH"] = round(float(p), 4)

            # Mapear índice predicho a MatchClassification
            if pred_class_idx == 2:
                classification = MatchClassification.MATCH
                calibrated_score = prob_dict.get("MATCH", 0.85)
            elif pred_class_idx == 1:
                classification = MatchClassification.PARTIAL_MATCH
                calibrated_score = 0.50 + 0.30 * prob_dict.get("PARTIAL_MATCH", 0.60)
            else:
                classification = MatchClassification.NO_MATCH
                calibrated_score = 0.30 * (1.0 - prob_dict.get("NO_MATCH", 0.80))

            return classification, round(float(calibrated_score), 4), prob_dict

        except Exception:
            return None
