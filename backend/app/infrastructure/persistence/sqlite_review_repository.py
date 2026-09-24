"""
Repositorio SQLite para Revisiones Humanas inmutables y Dataset Staging.
Implementa los puertos IReviewRepository e IDatasetRepository.
"""

from datetime import datetime
import json
from typing import List, Optional
import uuid

from app.domain.comparison import MatchClassification
from app.domain.ports import IDatasetRepository, IReviewRepository
from app.domain.review import CorrectionType, DatasetExample, Review
from app.infrastructure.persistence.database import DatabaseManager


class SqliteReviewRepository(IReviewRepository, IDatasetRepository):
    """
    Persistencia de revisiones y staging de dataset.
    REGLA: Garantiza inmutabilidad y coexistencia de la predicción de la IA y el juicio humano.
    """

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def save(self, review: Review) -> None:
        """Guarda la revisión humana y genera una tupla en el dataset de aprendizaje."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO reviews (
                    id, comparison_id, match_id, prediction_before,
                    human_decision, correction_type, justification,
                    reviewer_id, model_version, created_at,
                    manual_obj_id, manual_cmp_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    human_decision = excluded.human_decision,
                    correction_type = excluded.correction_type,
                    justification = excluded.justification;
                """,
                (
                    review.id,
                    review.comparison_id,
                    review.match_id,
                    review.prediction_before.value if review.prediction_before else None,
                    review.human_decision.value,
                    review.correction_type.value,
                    review.justification,
                    review.reviewer_id,
                    review.model_version,
                    review.created_at.isoformat(),
                    review.manual_objective_item_id,
                    review.manual_compared_item_id,
                ),
            )

            # Buscar datos para dataset_example
            obj_text = ""
            cmp_text = ""
            features: dict = {}
            prediction_label = review.prediction_before.value if review.prediction_before else "NONE"

            if review.match_id:
                cursor.execute(
                    """
                    SELECT objective_snippet, compared_snippet, semantic_sim, lexical_sim, keyword_overlap, structural_sim
                    FROM content_matches WHERE id = ?;
                    """,
                    (review.match_id,),
                )
                match_row = cursor.fetchone()
                if match_row:
                    obj_text = match_row["objective_snippet"]
                    cmp_text = match_row["compared_snippet"]
                    features = {
                        "semantic_sim": match_row["semantic_sim"],
                        "lexical_sim": match_row["lexical_sim"],
                        "keyword_overlap": match_row["keyword_overlap"],
                        "structural_sim": match_row["structural_sim"],
                    }

            # Insertar en dataset_examples si no existe ya para esta review
            dataset_id = f"DATA-{uuid.uuid4().hex[:10].upper()}"
            cursor.execute(
                """
                INSERT INTO dataset_examples (
                    id, review_id, objective_item_id, compared_item_id,
                    objective_text, compared_text, features_json,
                    prediction_label, ground_truth_label, model_version,
                    source_university_obj, source_university_cmp, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING;
                """,
                (
                    dataset_id,
                    review.id,
                    review.manual_objective_item_id or (review.match_id or "UNKNOWN"),
                    review.manual_compared_item_id or (review.match_id or "UNKNOWN"),
                    obj_text,
                    cmp_text,
                    json.dumps(features),
                    prediction_label,
                    review.human_decision.value,
                    review.model_version,
                    None,
                    None,
                    datetime.now().isoformat(),
                ),
            )

            conn.commit()

    def get_by_comparison_id(self, comparison_id: str) -> List[Review]:
        """Recupera todas las revisiones humanas registradas para una comparación."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reviews WHERE comparison_id = ? ORDER BY created_at ASC;", (comparison_id,))
            rows = cursor.fetchall()
            return [
                Review(
                    id=r["id"],
                    comparison_id=r["comparison_id"],
                    match_id=r["match_id"],
                    prediction_before=MatchClassification(r["prediction_before"]) if r["prediction_before"] else None,
                    human_decision=MatchClassification(r["human_decision"]),
                    correction_type=CorrectionType(r["correction_type"]),
                    justification=r["justification"],
                    reviewer_id=r["reviewer_id"],
                    model_version=r["model_version"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                    manual_objective_item_id=r["manual_obj_id"],
                    manual_compared_item_id=r["manual_cmp_id"],
                )
                for r in rows
            ]

    def get_by_id(self, review_id: str) -> Optional[Review]:
        """Recupera una revisión específica por su ID."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reviews WHERE id = ?;", (review_id,))
            r = cursor.fetchone()
            if not r:
                return None
            return Review(
                id=r["id"],
                comparison_id=r["comparison_id"],
                match_id=r["match_id"],
                prediction_before=MatchClassification(r["prediction_before"]) if r["prediction_before"] else None,
                human_decision=MatchClassification(r["human_decision"]),
                correction_type=CorrectionType(r["correction_type"]),
                justification=r["justification"],
                reviewer_id=r["reviewer_id"],
                model_version=r["model_version"],
                created_at=datetime.fromisoformat(r["created_at"]),
                manual_objective_item_id=r["manual_obj_id"],
                manual_compared_item_id=r["manual_cmp_id"],
            )

    # Métodos de IDatasetRepository
    def save_example(self, example: DatasetExample) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO dataset_examples (
                    id, review_id, objective_item_id, compared_item_id,
                    objective_text, compared_text, features_json,
                    prediction_label, ground_truth_label, model_version,
                    source_university_obj, source_university_cmp, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    ground_truth_label = excluded.ground_truth_label;
                """,
                (
                    example.id,
                    example.review_id,
                    example.objective_item_id,
                    example.compared_item_id,
                    example.objective_text,
                    example.compared_text,
                    json.dumps(example.features),
                    example.prediction_label,
                    example.ground_truth_label,
                    example.model_version,
                    example.source_university_obj,
                    example.source_university_cmp,
                    (example.created_at or datetime.now()).isoformat(),
                ),
            )
            conn.commit()

    def count_examples(self) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) AS total FROM dataset_examples;")
            row = cursor.fetchone()
            return row["total"] if row else 0

    def list_examples(self, limit: int = 100, offset: int = 0) -> List[DatasetExample]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM dataset_examples ORDER BY created_at DESC LIMIT ? OFFSET ?;", (limit, offset))
            rows = cursor.fetchall()
            return [
                DatasetExample(
                    id=r["id"],
                    review_id=r["review_id"],
                    objective_item_id=r["objective_item_id"],
                    compared_item_id=r["compared_item_id"],
                    objective_text=r["objective_text"],
                    compared_text=r["compared_text"],
                    features=json.loads(r["features_json"]),
                    prediction_label=r["prediction_label"],
                    ground_truth_label=r["ground_truth_label"],
                    model_version=r["model_version"],
                    source_university_obj=r["source_university_obj"],
                    source_university_cmp=r["source_university_cmp"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
                for r in rows
            ]
