"""
Caso de uso para la comparación integral y pre-evaluación explicable entre dos sílabos.
Implementa el motor híbrido, scoring ponderado, clasificación y análisis bidireccional.
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid

from app.domain.comparison import (
    Comparison,
    ContentMatch,
    MatchClassification,
    MatchEvidence,
    ScoreBreakdown,
    UnmatchedItem,
)
from app.domain.content import ContentItem
from app.domain.ports import IComparisonRepository
from app.infrastructure.nlp.vector_service import NlpVectorService


DEFAULT_WEIGHTS = {
    "semantic": 0.40,
    "lexical": 0.30,
    "keyword": 0.15,
    "structural": 0.15,
}

DEFAULT_THRESHOLDS = {
    "match": 0.85,
    "partial": 0.70,
    "uncertain": 0.50,
}


class CompareSyllabiUseCase:
    """Orquesta la comparación exhaustiva entre los contenidos de dos sílabos."""

    def __init__(
        self,
        vector_service: NlpVectorService,
        comparison_repository: Optional[IComparisonRepository] = None,
        model_version: str = "baseline-001",
    ) -> None:
        self.vector_service = vector_service
        self.repository = comparison_repository
        self.model_version = model_version

    def execute(
        self,
        objective_syllabus_id: str,
        compared_syllabus_id: str,
        objective_items: List[ContentItem],
        compared_items: List[ContentItem],
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[Dict[str, float]] = None,
    ) -> Comparison:
        """
        Ejecuta la comparación multidimensional:
        1. Evalúa cada par de ítems temáticos (Léxico, Semántico, Overlap, Estructural).
        2. Aplica umbrales y clasifica (MATCH, PARTIAL_MATCH, UNCERTAIN, NO_MATCH).
        3. Identifica correspondencias múltiples (1:1, 1:N).
        4. Detecta brechas de contenido en ambas direcciones.
        5. Calcula métricas globales de cobertura bidireccional.
        """
        w = weights or DEFAULT_WEIGHTS
        th = thresholds or DEFAULT_THRESHOLDS

        comparison_id = f"COMP-{uuid.uuid4().hex[:12].upper()}"
        matches: List[ContentMatch] = []
        covered_objective_ids = set()
        covered_compared_ids = set()

        # Matrices de candidatos y puntuaciones
        n_obj = len(objective_items)
        n_cmp = len(compared_items)

        best_score_per_obj: Dict[str, tuple[float, Optional[ContentItem]]] = {
            item.id: (0.0, None) for item in objective_items
        }
        best_score_per_cmp: Dict[str, tuple[float, Optional[ContentItem]]] = {
            item.id: (0.0, None) for item in compared_items
        }

        # 1. Búsqueda y evaluación de correspondencias (Objetivo -> Comparado)
        for obj_item in objective_items:
            candidates_for_obj: List[tuple[float, ContentItem, ScoreBreakdown, MatchEvidence]] = []
            text_obj = f"{obj_item.title}. {obj_item.text}".strip()

            for cmp_item in compared_items:
                text_cmp = f"{cmp_item.title}. {cmp_item.text}".strip()
                sem_sim = self.vector_service.compute_semantic_similarity(text_obj, text_cmp)
                lex_sim = self.vector_service.compute_lexical_similarity(text_obj, text_cmp)
                key_sim = self.vector_service.compute_keyword_overlap(text_obj, text_cmp)
                est_sim = self.vector_service.compute_structural_similarity(
                    order_a=obj_item.order,
                    total_items_a=n_obj,
                    order_b=cmp_item.order,
                    total_items_b=n_cmp,
                    unit_a=obj_item.unit_number,
                    unit_b=cmp_item.unit_number,
                )

                # Cálculo de score compuesto ponderado
                composite = (
                    w["semantic"] * sem_sim
                    + w["lexical"] * lex_sim
                    + w["keyword"] * key_sim
                    + w["structural"] * est_sim
                )
                composite = max(0.0, min(1.0, round(composite, 4)))

                # Actualizar mejores scores
                if composite > best_score_per_obj[obj_item.id][0]:
                    best_score_per_obj[obj_item.id] = (composite, cmp_item)
                if composite > best_score_per_cmp[cmp_item.id][0]:
                    best_score_per_cmp[cmp_item.id] = (composite, obj_item)

                # Si califica al menos para análisis o revisión (score >= umbral incierto)
                if composite >= th["uncertain"]:
                    shared_kw = self.vector_service.extract_shared_keywords(text_obj, text_cmp)
                    ev_type = "HYBRID" if (sem_sim > 0.6 and lex_sim > 0.4) else ("SEMANTIC" if sem_sim >= lex_sim else "LEXICAL")

                    breakdown = ScoreBreakdown(
                        semantic_similarity=sem_sim,
                        lexical_similarity=lex_sim,
                        keyword_overlap=key_sim,
                        structural_similarity=est_sim,
                        composite_score=composite,
                        weights=w,
                    )

                    evidence = MatchEvidence(
                        evidence_type=ev_type,
                        shared_keywords=shared_kw,
                        semantic_score=sem_sim,
                        lexical_score=lex_sim,
                        objective_snippet=obj_item.text[:220],
                        compared_snippet=cmp_item.text[:220],
                        objective_page=obj_item.page_start,
                        compared_page=cmp_item.page_start,
                    )

                    candidates_for_obj.append((composite, cmp_item, breakdown, evidence))

            # Ordenar candidatos por score descendente
            candidates_for_obj.sort(key=lambda x: x[0], reverse=True)

            # Conservar candidatos significativos (relación 1:1 o 1:N si hay correspondencias parciales altas)
            for idx, (score, cmp_item, breakdown, evidence) in enumerate(candidates_for_obj):
                # El mejor siempre se evalúa; los secundarios solo si son >= partial
                if idx > 0 and score < th["partial"]:
                    break

                classification = self._classify(score, th)

                matches.append(
                    ContentMatch(
                        id=f"MATCH-{uuid.uuid4().hex[:10].upper()}",
                        comparison_id=comparison_id,
                        objective_item_id=obj_item.id,
                        compared_item_id=cmp_item.id,
                        objective_title=obj_item.title,
                        compared_title=cmp_item.title,
                        objective_section=obj_item.section_name,
                        compared_section=cmp_item.section_name,
                        objective_page=obj_item.page_start,
                        compared_page=cmp_item.page_start,
                        score_breakdown=breakdown,
                        classification=classification,
                        evidence=evidence,
                    )
                )

                if classification in (MatchClassification.MATCH, MatchClassification.PARTIAL_MATCH):
                    covered_objective_ids.add(obj_item.id)
                    covered_compared_ids.add(cmp_item.id)

        # 2. Identificar contenidos no correspondidos del Objetivo
        unmatched_objective: List[UnmatchedItem] = []
        for obj_item in objective_items:
            if obj_item.id not in covered_objective_ids:
                best_score, best_cmp = best_score_per_obj.get(obj_item.id, (0.0, None))
                unmatched_objective.append(
                    UnmatchedItem(
                        item_id=obj_item.id,
                        syllabus_id=objective_syllabus_id,
                        section_name=obj_item.section_name,
                        title=obj_item.title,
                        text_snippet=obj_item.text[:200],
                        page=obj_item.page_start,
                        best_candidate_id=best_cmp.id if best_cmp else None,
                        best_candidate_title=best_cmp.title if best_cmp else None,
                        best_score=best_score,
                    )
                )

        # 3. Identificar contenidos no correspondidos del Comparado (Bidireccional)
        unmatched_compared: List[UnmatchedItem] = []
        for cmp_item in compared_items:
            if cmp_item.id not in covered_compared_ids:
                best_score, best_obj = best_score_per_cmp.get(cmp_item.id, (0.0, None))
                unmatched_compared.append(
                    UnmatchedItem(
                        item_id=cmp_item.id,
                        syllabus_id=compared_syllabus_id,
                        section_name=cmp_item.section_name,
                        title=cmp_item.title,
                        text_snippet=cmp_item.text[:200],
                        page=cmp_item.page_start,
                        best_candidate_id=best_obj.id if best_obj else None,
                        best_candidate_title=best_obj.title if best_obj else None,
                        best_score=best_score,
                    )
                )

        # 4. Cálculo de Cobertura Bidireccional
        obj_cov = round((len(covered_objective_ids) / max(1, n_obj)) * 100.0, 1)
        cmp_cov = round((len(covered_compared_ids) / max(1, n_cmp)) * 100.0, 1)

        # 5. Porcentaje Global de Correspondencia Estimada
        # Ponderación basada en promedio de mejores scores de cobertura del objetivo
        sum_best_obj = sum(best_score_per_obj[it.id][0] for it in objective_items)
        global_score = round(sum_best_obj / max(1, n_obj), 4)

        comparison = Comparison(
            id=comparison_id,
            objective_syllabus_id=objective_syllabus_id,
            compared_syllabus_id=compared_syllabus_id,
            global_score=global_score,
            objective_coverage=obj_cov,
            compared_coverage=cmp_cov,
            model_version=self.model_version,
            created_at=datetime.now(),
            matches=matches,
            unmatched_objective=unmatched_objective,
            unmatched_compared=unmatched_compared,
        )

        if self.repository:
            self.repository.save(comparison)

        return comparison

    def _classify(self, score: float, thresholds: Dict[str, float]) -> MatchClassification:
        """Asigna la etiqueta categórica según los umbrales configurados."""
        if score >= thresholds["match"]:
            return MatchClassification.MATCH
        if score >= thresholds["partial"]:
            return MatchClassification.PARTIAL_MATCH
        if score >= thresholds["uncertain"]:
            return MatchClassification.UNCERTAIN
        return MatchClassification.NO_MATCH
