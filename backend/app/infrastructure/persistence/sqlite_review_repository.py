"""
Repositorio SQLite para Revisiones Humanas inmutables y Dataset Staging.
Implementa los puertos IReviewRepository e IDatasetRepository.
"""

from datetime import datetime
import json
import sqlite3
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
                ;
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
            obj_id = review.manual_objective_item_id or "UNKNOWN"
            cmp_id = review.manual_compared_item_id or "UNKNOWN"

            if review.match_id:
                cursor.execute(
                    """
                    SELECT objective_item_id, compared_item_id, objective_snippet, compared_snippet,
                           semantic_sim, lexical_sim, keyword_overlap, structural_sim
                    FROM content_matches WHERE id = ?;
                    """,
                    (review.match_id,),
                )
                match_row = cursor.fetchone()
                if match_row:
                    obj_id = match_row["objective_item_id"]
                    cmp_id = match_row["compared_item_id"]
                    obj_text = match_row["objective_snippet"]
                    cmp_text = match_row["compared_snippet"]
                    features = {
                        "semantic_sim": match_row["semantic_sim"],
                        "lexical_sim": match_row["lexical_sim"],
                        "keyword_overlap": match_row["keyword_overlap"],
                        "structural_sim": match_row["structural_sim"],
                    }

            if not review.match_id:
                for item_id, is_objective in ((obj_id, True), (cmp_id, False)):
                    cursor.execute("SELECT text FROM content_items WHERE id = ?", (item_id,))
                    item = cursor.fetchone()
                    if item and is_objective:
                        obj_text = item["text"]
                    elif item:
                        cmp_text = item["text"]

            cursor.execute(
                """SELECT obj.university AS obj_uni, cmp.university AS cmp_uni,
                          COALESCE(NULLIF(obj.course_code, ''), NULLIF(obj.course_name, '')) AS obj_course,
                          COALESCE(NULLIF(cmp.course_code, ''), NULLIF(cmp.course_name, '')) AS cmp_course,
                          c.objective_syllabus_id AS obj_syllabus, c.compared_syllabus_id AS cmp_syllabus
                   FROM comparisons c
                   JOIN syllabi obj ON obj.id = c.objective_syllabus_id
                   JOIN syllabi cmp ON cmp.id = c.compared_syllabus_id
                   WHERE c.id = ?""", (review.comparison_id,),
            )
            provenance = cursor.fetchone()

            # Insertar en dataset_examples si no existe ya para esta review
            dataset_id = f"DATA-{uuid.uuid4().hex[:10].upper()}"
            cursor.execute(
                """
                INSERT INTO dataset_examples (
                    id, review_id, objective_item_id, compared_item_id,
                    objective_text, compared_text, features_json,
                    prediction_label, ground_truth_label, model_version,
                    source_university_obj, source_university_cmp, created_at,
                    source_course_obj, source_course_cmp, source_syllabus_obj, source_syllabus_cmp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO NOTHING;
                """,
                (
                    dataset_id,
                    review.id,
                    obj_id,
                    cmp_id,
                    obj_text,
                    cmp_text,
                    json.dumps(features),
                    prediction_label,
                    review.human_decision.value,
                    review.model_version,
                    provenance["obj_uni"] if provenance else None,
                    provenance["cmp_uni"] if provenance else None,
                    datetime.now().isoformat(),
                    provenance["obj_course"] if provenance else None,
                    provenance["cmp_course"] if provenance else None,
                    provenance["obj_syllabus"] if provenance else None,
                    provenance["cmp_syllabus"] if provenance else None,
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
    def list_all(self, limit: int = 500, offset: int = 0) -> List[Review]:
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM reviews ORDER BY created_at, id LIMIT ? OFFSET ?", (limit, offset),
            ).fetchall()
            return [self._map_review(row) for row in rows]

    @staticmethod
    def _map_review(row: sqlite3.Row) -> Review:
        return Review(
            id=row["id"], comparison_id=row["comparison_id"], match_id=row["match_id"],
            prediction_before=MatchClassification(row["prediction_before"]) if row["prediction_before"] else None,
            human_decision=MatchClassification(row["human_decision"]),
            correction_type=CorrectionType(row["correction_type"]), justification=row["justification"],
            reviewer_id=row["reviewer_id"], model_version=row["model_version"],
            created_at=datetime.fromisoformat(row["created_at"]),
            manual_objective_item_id=row["manual_obj_id"], manual_compared_item_id=row["manual_cmp_id"],
        )

    def save_example(self, example: DatasetExample) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO dataset_examples (
                    id, review_id, objective_item_id, compared_item_id,
                    objective_text, compared_text, features_json,
                    prediction_label, ground_truth_label, model_version,
                    source_university_obj, source_university_cmp, created_at,
                    source_course_obj, source_course_cmp, source_syllabus_obj, source_syllabus_cmp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ;
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
                    example.source_course_obj,
                    example.source_course_cmp,
                    example.source_syllabus_obj,
                    example.source_syllabus_cmp,
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
            # Recuperar también procedencia histórica sin reescribir predicciones ni datos originales.
            cursor.execute(
                """SELECT d.*, m.objective_item_id AS match_obj_id, m.compared_item_id AS match_cmp_id,
                          obj.sha256_hash AS obj_hash, cmp.sha256_hash AS cmp_hash,
                          COALESCE(m.objective_page, obj_item.page_start) AS obj_page,
                          COALESCE(m.compared_page, cmp_item.page_start) AS cmp_page,
                          obj.university AS obj_uni, cmp.university AS cmp_uni,
                          COALESCE(NULLIF(obj.course_code, ''), NULLIF(obj.course_name, '')) AS obj_course,
                          COALESCE(NULLIF(cmp.course_code, ''), NULLIF(cmp.course_name, '')) AS cmp_course,
                          c.objective_syllabus_id AS obj_syllabus, c.compared_syllabus_id AS cmp_syllabus
                   FROM dataset_examples d
                   LEFT JOIN reviews r ON r.id = d.review_id
                   LEFT JOIN content_matches m ON m.id = r.match_id
                   LEFT JOIN content_items obj_item ON obj_item.id = COALESCE(m.objective_item_id, d.objective_item_id)
                   LEFT JOIN content_items cmp_item ON cmp_item.id = COALESCE(m.compared_item_id, d.compared_item_id)
                   LEFT JOIN comparisons c ON c.id = r.comparison_id
                   LEFT JOIN syllabi obj ON obj.id = c.objective_syllabus_id
                   LEFT JOIN syllabi cmp ON cmp.id = c.compared_syllabus_id
                   ORDER BY d.created_at DESC, d.id LIMIT ? OFFSET ?""", (limit, offset),
            )
            rows = cursor.fetchall()
            return [
                DatasetExample(
                    id=r["id"],
                    review_id=r["review_id"],
                    objective_item_id=r["match_obj_id"] or r["objective_item_id"],
                    compared_item_id=r["match_cmp_id"] or r["compared_item_id"],
                    objective_text=r["objective_text"],
                    compared_text=r["compared_text"],
                    features=json.loads(r["features_json"]),
                    prediction_label=r["prediction_label"],
                    ground_truth_label=r["ground_truth_label"],
                    model_version=r["model_version"],
                    source_university_obj=r["source_university_obj"] or r["obj_uni"],
                    source_university_cmp=r["source_university_cmp"] or r["cmp_uni"],
                    source_course_obj=r["source_course_obj"] or r["obj_course"],
                    source_course_cmp=r["source_course_cmp"] or r["cmp_course"],
                    source_syllabus_obj=r["source_syllabus_obj"] or r["obj_syllabus"],
                    source_syllabus_cmp=r["source_syllabus_cmp"] or r["cmp_syllabus"],
                    source_page_obj=r["obj_page"],
                    source_page_cmp=r["cmp_page"],
                    source_syllabus_hash_obj=r["obj_hash"],
                    source_syllabus_hash_cmp=r["cmp_hash"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
                for r in rows
            ]
