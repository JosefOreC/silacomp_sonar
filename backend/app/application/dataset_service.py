"""
Servicio de gestión y preparación del Dataset Científico para Aprendizaje Supervisado (Fase 2.0).
Extrae características multivariadas, realiza división estratificada y exporta en formatos JSON/CSV.
"""

import csv
import io
import json
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from app.domain.comparison import MatchClassification
from app.domain.ports import IDatasetRepository, IReviewRepository
from app.domain.review import DatasetExample


FEATURE_NAMES = [
    "semantic_sim",
    "lexical_sim",
    "asymmetric_containment",
    "structural_sim",
    "keyword_overlap",
]

LABEL_TO_INT = {
    MatchClassification.MATCH.value: 2,
    MatchClassification.PARTIAL_MATCH.value: 1,
    MatchClassification.UNCERTAIN.value: 1,  # Tratado como parcial/dudoso
    MatchClassification.NO_MATCH.value: 0,
}

INT_TO_LABEL = {
    2: MatchClassification.MATCH.value,
    1: MatchClassification.PARTIAL_MATCH.value,
    0: MatchClassification.NO_MATCH.value,
}


class DatasetService:
    """Servicio de ingeniería de características y preparación de datos de entrenamiento y evaluación."""

    def __init__(
        self,
        dataset_repo: IDatasetRepository,
        review_repo: Optional[IReviewRepository] = None,
    ) -> None:
        self.dataset_repo = dataset_repo
        self.review_repo = review_repo

    def get_all_examples(self, limit: int = 10000) -> List[DatasetExample]:
        """Obtiene todas las observaciones del dataset persistido."""
        return self.dataset_repo.list_examples(limit=limit)

    def extract_feature_matrix(
        self,
        examples: List[DatasetExample],
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Extrae la matriz de características X (N x 5) y el vector de etiquetas y (N,)
        para entrenamiento con scikit-learn.
        
        Returns:
            Tuple: (X, y, feature_names)
        """
        X_rows: List[List[float]] = []
        y_vals: List[int] = []

        for ex in examples:
            feat = ex.features or {}
            row = [
                float(feat.get("semantic_sim", 0.0)),
                float(feat.get("lexical_sim", 0.0)),
                float(feat.get("asymmetric_containment", feat.get("lexical_sim", 0.0))),
                float(feat.get("structural_sim", 0.0)),
                float(feat.get("keyword_overlap", 0.0)),
            ]
            X_rows.append(row)

            # Mapear etiqueta ground truth a entero ordinal
            label = ex.ground_truth_label or ex.prediction_label or MatchClassification.NO_MATCH.value
            y_val = LABEL_TO_INT.get(label, 0)
            y_vals.append(y_val)

        # Conservar decimales persistidos: float32 puede desplazar 0.70 por debajo del umbral adaptativo.
        return np.array(X_rows, dtype=np.float64), np.array(y_vals, dtype=np.int64), FEATURE_NAMES

    def export_to_csv(self, examples: List[DatasetExample]) -> str:
        """Exporta las observaciones en formato CSV plano compatible con herramientas de análisis de datos."""
        output = io.StringIO()
        writer = csv.writer(output)

        headers = [
            "id",
            "review_id",
            "objective_item_id",
            "compared_item_id",
            "prediction_label",
            "ground_truth_label",
            "model_version",
            "source_university_obj",
            "source_university_cmp",
            "source_course_obj",
            "source_course_cmp",
            "source_syllabus_obj",
            "source_syllabus_cmp",
            "semantic_sim",
            "lexical_sim",
            "asymmetric_containment",
            "structural_sim",
            "keyword_overlap",
            "created_at",
        ]
        writer.writerow(headers)

        for ex in examples:
            feat = ex.features or {}
            writer.writerow([
                ex.id,
                ex.review_id,
                ex.objective_item_id,
                ex.compared_item_id,
                ex.prediction_label,
                ex.ground_truth_label,
                ex.model_version,
                ex.source_university_obj,
                ex.source_university_cmp,
                ex.source_course_obj,
                ex.source_course_cmp,
                ex.source_syllabus_obj,
                ex.source_syllabus_cmp,
                feat.get("semantic_sim", 0.0),
                feat.get("lexical_sim", 0.0),
                feat.get("asymmetric_containment", feat.get("lexical_sim", 0.0)),
                feat.get("structural_sim", 0.0),
                feat.get("keyword_overlap", 0.0),
                ex.created_at.isoformat() if ex.created_at else "",
            ])

        return output.getvalue()

    def generate_bootstrap_synthetic_dataset(self, n_samples: int = 120) -> List[DatasetExample]:
        """
        Genera una muestra controlada de calibración pedagógica (distribución balanceada de MATCH, PARTIAL y NO_MATCH)
        para asegurar convergencia de modelos cuando el historial de revisiones docentes es inicial (< 30 ejemplos).
        """
        rng = np.random.default_rng(42)
        examples: List[DatasetExample] = []

        # 1. Ejemplos de MATCH sólido (conceptos equivalentes o idénticos)
        n_match = n_samples // 3
        for i in range(n_match):
            sem = rng.uniform(0.78, 0.98)
            lex = rng.uniform(0.65, 0.95)
            asym = rng.uniform(0.70, 0.98)
            struct = rng.uniform(0.50, 1.0)
            key = rng.uniform(0.60, 0.95)

            ex = DatasetExample(
                id=f"BOOT-MATCH-{i:03d}",
                review_id=f"REV-BOOT-M-{i:03d}",
                objective_item_id=f"OBJ-M-{i}",
                compared_item_id=f"CMP-M-{i}",
                objective_text=f"Tema curricular universitario convalidable {i}",
                compared_text=f"Tema curricular universitario homologable {i}",
                features={
                    "semantic_sim": round(float(sem), 4),
                    "lexical_sim": round(float(lex), 4),
                    "asymmetric_containment": round(float(asym), 4),
                    "structural_sim": round(float(struct), 4),
                    "keyword_overlap": round(float(key), 4),
                },
                prediction_label=MatchClassification.MATCH.value,
                ground_truth_label=MatchClassification.MATCH.value,
                model_version="bootstrap-calibration-001",
            )
            examples.append(ex)

        # 2. Ejemplos de PARTIAL_MATCH (coincidencias temáticas parciales o unidades cruzadas)
        n_partial = n_samples // 3
        for i in range(n_partial):
            sem = rng.uniform(0.55, 0.77)
            lex = rng.uniform(0.35, 0.65)
            asym = rng.uniform(0.40, 0.75)
            struct = rng.uniform(0.20, 0.80)
            key = rng.uniform(0.30, 0.60)

            ex = DatasetExample(
                id=f"BOOT-PARTIAL-{i:03d}",
                review_id=f"REV-BOOT-P-{i:03d}",
                objective_item_id=f"OBJ-P-{i}",
                compared_item_id=f"CMP-P-{i}",
                objective_text=f"Tema de alcance parcial complementario {i}",
                compared_text=f"Tema de contenido similar pero menor profundidad {i}",
                features={
                    "semantic_sim": round(float(sem), 4),
                    "lexical_sim": round(float(lex), 4),
                    "asymmetric_containment": round(float(asym), 4),
                    "structural_sim": round(float(struct), 4),
                    "keyword_overlap": round(float(key), 4),
                },
                prediction_label=MatchClassification.PARTIAL_MATCH.value,
                ground_truth_label=MatchClassification.PARTIAL_MATCH.value,
                model_version="bootstrap-calibration-001",
            )
            examples.append(ex)

        # 3. Ejemplos de NO_MATCH (temas dispares sin correlación académica)
        n_nomatch = n_samples - n_match - n_partial
        for i in range(n_nomatch):
            sem = rng.uniform(0.05, 0.44)
            lex = rng.uniform(0.0, 0.28)
            asym = rng.uniform(0.0, 0.30)
            struct = rng.uniform(0.0, 0.50)
            key = rng.uniform(0.0, 0.20)

            ex = DatasetExample(
                id=f"BOOT-NOMATCH-{i:03d}",
                review_id=f"REV-BOOT-N-{i:03d}",
                objective_item_id=f"OBJ-N-{i}",
                compared_item_id=f"CMP-N-{i}",
                objective_text=f"Tema especializado no cubierto en el plan {i}",
                compared_text=f"Materia completamente distinta {i}",
                features={
                    "semantic_sim": round(float(sem), 4),
                    "lexical_sim": round(float(lex), 4),
                    "asymmetric_containment": round(float(asym), 4),
                    "structural_sim": round(float(struct), 4),
                    "keyword_overlap": round(float(key), 4),
                },
                prediction_label=MatchClassification.NO_MATCH.value,
                ground_truth_label=MatchClassification.NO_MATCH.value,
                model_version="bootstrap-calibration-001",
            )
            examples.append(ex)

        return examples
