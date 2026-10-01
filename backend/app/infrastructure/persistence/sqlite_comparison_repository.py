"""
Repositorio SQLite para Comparaciones, Correspondencias y Evidencias.
Implementa el puerto IComparisonRepository.
"""

from datetime import datetime
import json
from typing import List, Optional
from app.domain.comparison import (
    Comparison,
    ContentMatch,
    EvidenceRegion,
    MatchClassification,
    MatchEvidence,
    ScoreBreakdown,
    UnmatchedItem,
)
from app.domain.ports import IComparisonRepository
from app.infrastructure.persistence.database import DatabaseManager


class SqliteComparisonRepository(IComparisonRepository):
    """Implementación de persistencia de comparaciones y correspondencias sobre SQLite."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def save(self, comparison: Comparison) -> None:
        """Guarda la comparación, sus correspondencias y contenidos huérfanos transaccionalmente."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Insertar comparación
            cursor.execute(
                """
                INSERT INTO comparisons (
                    id, objective_syllabus_id, compared_syllabus_id,
                    global_score, objective_coverage, compared_coverage,
                    model_version, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    global_score = excluded.global_score,
                    objective_coverage = excluded.objective_coverage,
                    compared_coverage = excluded.compared_coverage;
                """,
                (
                    comparison.id,
                    comparison.objective_syllabus_id,
                    comparison.compared_syllabus_id,
                    comparison.global_score,
                    comparison.objective_coverage,
                    comparison.compared_coverage,
                    comparison.model_version,
                    comparison.created_at.isoformat(),
                ),
            )

            # Insertar matches
            cursor.execute("DELETE FROM content_matches WHERE comparison_id = ?;", (comparison.id,))
            for m in comparison.matches:
                regions_data = {
                    "objective": [
                        {
                            "id": r.id,
                            "match_id": r.match_id,
                            "syllabus_id": r.syllabus_id,
                            "content_id": r.content_id,
                            "page_number": r.page_number,
                            "page_width": r.page_width,
                            "page_height": r.page_height,
                            "x0": r.x0,
                            "y0": r.y0,
                            "x1": r.x1,
                            "y1": r.y1,
                            "text": r.text,
                            "evidence_type": r.evidence_type,
                        }
                        for r in (getattr(m.evidence, "objective_regions", None) or [])
                    ],
                    "compared": [
                        {
                            "id": r.id,
                            "match_id": r.match_id,
                            "syllabus_id": r.syllabus_id,
                            "content_id": r.content_id,
                            "page_number": r.page_number,
                            "page_width": r.page_width,
                            "page_height": r.page_height,
                            "x0": r.x0,
                            "y0": r.y0,
                            "x1": r.x1,
                            "y1": r.y1,
                            "text": r.text,
                            "evidence_type": r.evidence_type,
                        }
                        for r in (getattr(m.evidence, "compared_regions", None) or [])
                    ],
                }

                cursor.execute(
                    """
                    INSERT INTO content_matches (
                        id, comparison_id, objective_item_id, compared_item_id,
                        objective_title, compared_title, objective_section, compared_section,
                        objective_page, compared_page, semantic_sim, lexical_sim,
                        keyword_overlap, structural_sim, composite_score,
                        classification, evidence_type, shared_keywords_json,
                        objective_snippet, compared_snippet, evidence_regions_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        m.id,
                        comparison.id,
                        m.objective_item_id,
                        m.compared_item_id,
                        m.objective_title,
                        m.compared_title,
                        m.objective_section,
                        m.compared_section,
                        m.objective_page,
                        m.compared_page,
                        m.score_breakdown.semantic_similarity,
                        m.score_breakdown.lexical_similarity,
                        m.score_breakdown.keyword_overlap,
                        m.score_breakdown.structural_similarity,
                        m.score_breakdown.composite_score,
                        m.classification.value,
                        m.evidence.evidence_type,
                        json.dumps(m.evidence.shared_keywords, ensure_ascii=False),
                        m.evidence.objective_snippet,
                        m.evidence.compared_snippet,
                        json.dumps(regions_data, ensure_ascii=False),
                    ),
                )

            # Insertar contenidos sin correspondencia
            cursor.execute("DELETE FROM unmatched_items WHERE comparison_id = ?;", (comparison.id,))
            for u in comparison.unmatched_objective:
                cursor.execute(
                    """
                    INSERT INTO unmatched_items (
                        comparison_id, syllabus_role, item_id, syllabus_id,
                        section_name, title, text_snippet, page,
                        best_candidate_id, best_candidate_title, best_score
                    ) VALUES (?, 'OBJECTIVE', ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        comparison.id,
                        u.item_id,
                        u.syllabus_id,
                        u.section_name,
                        u.title,
                        u.text_snippet,
                        u.page,
                        u.best_candidate_id,
                        u.best_candidate_title,
                        u.best_score,
                    ),
                )

            for u in comparison.unmatched_compared:
                cursor.execute(
                    """
                    INSERT INTO unmatched_items (
                        comparison_id, syllabus_role, item_id, syllabus_id,
                        section_name, title, text_snippet, page,
                        best_candidate_id, best_candidate_title, best_score
                    ) VALUES (?, 'COMPARED', ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        comparison.id,
                        u.item_id,
                        u.syllabus_id,
                        u.section_name,
                        u.title,
                        u.text_snippet,
                        u.page,
                        u.best_candidate_id,
                        u.best_candidate_title,
                        u.best_score,
                    ),
                )

            conn.commit()

    def get_by_id(self, comparison_id: str) -> Optional[Comparison]:
        """Recupera la comparación completa por ID junto con todos sus matches y evidencias."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM comparisons WHERE id = ?;", (comparison_id,))
            comp_row = cursor.fetchone()
            if not comp_row:
                return None

            # Recuperar matches
            cursor.execute("SELECT * FROM content_matches WHERE comparison_id = ? ORDER BY composite_score DESC;", (comparison_id,))
            match_rows = cursor.fetchall()
            matches = []
            for m in match_rows:
                obj_regions: List[EvidenceRegion] = []
                cmp_regions: List[EvidenceRegion] = []
                raw_regions = m["evidence_regions_json"] if "evidence_regions_json" in m.keys() else None
                if raw_regions:
                    try:
                        r_data = json.loads(raw_regions)
                        if isinstance(r_data, dict):
                            for r in r_data.get("objective", []):
                                obj_regions.append(EvidenceRegion(**r))
                            for r in r_data.get("compared", []):
                                cmp_regions.append(EvidenceRegion(**r))
                    except Exception:
                        pass

                matches.append(
                    ContentMatch(
                        id=m["id"],
                        comparison_id=m["comparison_id"],
                        objective_item_id=m["objective_item_id"],
                        compared_item_id=m["compared_item_id"],
                        objective_title=m["objective_title"],
                        compared_title=m["compared_title"],
                        objective_section=m["objective_section"],
                        compared_section=m["compared_section"],
                        objective_page=m["objective_page"],
                        compared_page=m["compared_page"],
                        score_breakdown=ScoreBreakdown(
                            semantic_similarity=m["semantic_sim"],
                            lexical_similarity=m["lexical_sim"],
                            keyword_overlap=m["keyword_overlap"],
                            structural_similarity=m["structural_sim"],
                            composite_score=m["composite_score"],
                            weights={"semantic": 0.40, "lexical": 0.30, "keyword": 0.15, "structural": 0.15},
                        ),
                        classification=MatchClassification(m["classification"]),
                        evidence=MatchEvidence(
                            evidence_type=m["evidence_type"],
                            shared_keywords=json.loads(m["shared_keywords_json"]),
                            semantic_score=m["semantic_sim"],
                            lexical_score=m["lexical_sim"],
                            objective_snippet=m["objective_snippet"],
                            compared_snippet=m["compared_snippet"],
                            objective_page=m["objective_page"],
                            compared_page=m["compared_page"],
                            objective_regions=obj_regions,
                            compared_regions=cmp_regions,
                        ),
                    )
                )

            # Recuperar unmatched
            cursor.execute("SELECT * FROM unmatched_items WHERE comparison_id = ?;", (comparison_id,))
            unmatched_rows = cursor.fetchall()

            unmatched_obj = [
                UnmatchedItem(
                    item_id=u["item_id"],
                    syllabus_id=u["syllabus_id"],
                    section_name=u["section_name"],
                    title=u["title"],
                    text_snippet=u["text_snippet"],
                    page=u["page"],
                    best_candidate_id=u["best_candidate_id"],
                    best_candidate_title=u["best_candidate_title"],
                    best_score=u["best_score"],
                )
                for u in unmatched_rows
                if u["syllabus_role"] == "OBJECTIVE"
            ]

            unmatched_cmp = [
                UnmatchedItem(
                    item_id=u["item_id"],
                    syllabus_id=u["syllabus_id"],
                    section_name=u["section_name"],
                    title=u["title"],
                    text_snippet=u["text_snippet"],
                    page=u["page"],
                    best_candidate_id=u["best_candidate_id"],
                    best_candidate_title=u["best_candidate_title"],
                    best_score=u["best_score"],
                )
                for u in unmatched_rows
                if u["syllabus_role"] == "COMPARED"
            ]

            return Comparison(
                id=comp_row["id"],
                objective_syllabus_id=comp_row["objective_syllabus_id"],
                compared_syllabus_id=comp_row["compared_syllabus_id"],
                global_score=comp_row["global_score"],
                objective_coverage=comp_row["objective_coverage"],
                compared_coverage=comp_row["compared_coverage"],
                model_version=comp_row["model_version"],
                created_at=datetime.fromisoformat(comp_row["created_at"]),
                matches=matches,
                unmatched_objective=unmatched_obj,
                unmatched_compared=unmatched_cmp,
            )

    def list_all(self) -> List[Comparison]:
        """Retorna el listado de comparaciones registradas en el historial."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM comparisons ORDER BY created_at DESC;")
            rows = cursor.fetchall()
            return [
                Comparison(
                    id=r["id"],
                    objective_syllabus_id=r["objective_syllabus_id"],
                    compared_syllabus_id=r["compared_syllabus_id"],
                    global_score=r["global_score"],
                    objective_coverage=r["objective_coverage"],
                    compared_coverage=r["compared_coverage"],
                    model_version=r["model_version"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
                for r in rows
            ]
