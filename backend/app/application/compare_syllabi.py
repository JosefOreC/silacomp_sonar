"""
Caso de uso para la comparación integral y pre-evaluación explicable entre dos sílabos.
Implementa el motor híbrido, scoring ponderado, clasificación y análisis bidireccional.
"""

from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
import uuid
import numpy as np

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
from app.infrastructure.nlp.normalizer import TextNormalizer
from app.infrastructure.nlp.vector_service import NlpVectorService
from app.infrastructure.pdf.spatial_locator import SpatialLocatorService


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
        spatial_locator: Optional[SpatialLocatorService] = None,
        model_version: str = "baseline-001",
    ) -> None:
        self.vector_service = vector_service
        self.repository = comparison_repository
        self.spatial_locator = spatial_locator or SpatialLocatorService()
        self.model_version = model_version

    def execute(
        self,
        objective_syllabus_id: str,
        compared_syllabus_id: str,
        objective_items: List[ContentItem],
        compared_items: List[ContentItem],
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[Dict[str, float]] = None,
        objective_pdf_path: Optional[str] = None,
        compared_pdf_path: Optional[str] = None,
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

        # Precomputación vectorial y textual por lote para alto rendimiento
        obj_texts = [f"{it.title}. {it.text}".strip() for it in objective_items]
        cmp_texts = [f"{it.title}. {it.text}".strip() for it in compared_items]

        norm_obj_texts = [TextNormalizer.normalize_for_indexing(t) for t in obj_texts]
        norm_cmp_texts = [TextNormalizer.normalize_for_indexing(t) for t in cmp_texts]

        sem_matrix: Optional[np.ndarray] = None
        if hasattr(self.vector_service, "encode_texts") and n_obj > 0 and n_cmp > 0:
            try:
                emb_obj = self.vector_service.encode_texts(obj_texts)
                emb_cmp = self.vector_service.encode_texts(cmp_texts)
                if emb_obj is not None and emb_cmp is not None and len(emb_obj) > 0 and len(emb_cmp) > 0:
                    sem_matrix = np.dot(emb_obj, emb_cmp.T)
            except Exception:
                sem_matrix = None

        # 1. Búsqueda y evaluación de correspondencias (Objetivo -> Comparado)
        candidates_by_obj: Dict[str, List[tuple[float, ContentItem, ScoreBreakdown, MatchEvidence]]] = {}

        for i, obj_item in enumerate(objective_items):
            candidates_for_obj: List[tuple[float, ContentItem, ScoreBreakdown, MatchEvidence]] = []
            text_obj = obj_texts[i]
            norm_obj = norm_obj_texts[i]

            for j, cmp_item in enumerate(compared_items):
                text_cmp = cmp_texts[j]
                norm_cmp = norm_cmp_texts[j]

                # Atajo de correspondencia exacta 100% idéntica
                if norm_obj and norm_obj == norm_cmp:
                    sem_sim = 1.0
                    lex_sim = 1.0
                    key_sim = 1.0
                    est_sim = 1.0
                    composite = 1.0
                else:
                    if sem_matrix is not None:
                        sem_sim = max(0.0, min(1.0, round(float(sem_matrix[i, j]), 4)))
                    else:
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

                # Actualizar mejores scores globales para cálculo de cobertura
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
            candidates_by_obj[obj_item.id] = candidates_for_obj

        # 2. Selección inteligente de correspondencias sin redundancia ni repetición
        cmp_usage_count: Dict[str, int] = {}
        seen_pairs: Set[Tuple[str, str]] = set()

        for obj_item in objective_items:
            cands = candidates_by_obj.get(obj_item.id, [])
            if not cands:
                continue

            # Prioridad 1: Candidato no utilizado previamente (usage == 0) para evitar redundancias
            # Prioridad 2: Si no hay candidato libre disponible con afinidad, permitir reutilización (usage < 2)
            primary_cand = None
            for cand in cands:
                score, cmp_item, breakdown, evidence = cand
                has_content_affinity = (
                    breakdown.semantic_similarity >= 0.40
                    or breakdown.lexical_similarity >= 0.25
                    or breakdown.keyword_overlap >= 0.15
                )
                if not has_content_affinity:
                    continue
                pair_key = (obj_item.id, cmp_item.id)
                if pair_key in seen_pairs:
                    continue
                if cmp_usage_count.get(cmp_item.id, 0) == 0:
                    primary_cand = cand
                    break

            if primary_cand is None:
                for cand in cands:
                    score, cmp_item, breakdown, evidence = cand
                    has_content_affinity = (
                        breakdown.semantic_similarity >= 0.40
                        or breakdown.lexical_similarity >= 0.25
                        or breakdown.keyword_overlap >= 0.15
                    )
                    if not has_content_affinity:
                        continue
                    pair_key = (obj_item.id, cmp_item.id)
                    if pair_key in seen_pairs:
                        continue
                    if cmp_usage_count.get(cmp_item.id, 0) < 2:
                        primary_cand = cand
                        break

            if primary_cand is None:
                continue

            score, cmp_item, breakdown, evidence = primary_cand
            usage = cmp_usage_count.get(cmp_item.id, 0)
            pair_key = (obj_item.id, cmp_item.id)
            has_content_affinity = (
                breakdown.semantic_similarity >= 0.40
                or breakdown.lexical_similarity >= 0.25
                or breakdown.keyword_overlap >= 0.15
            )

            classification = self._classify(score, th, has_content_affinity)
            match_id = f"MATCH-{uuid.uuid4().hex[:10].upper()}"

            obj_regions = []
            cmp_regions = []
            if self.spatial_locator:
                if objective_pdf_path:
                    obj_regions = self.spatial_locator.locate_regions_for_item(
                        pdf_path=objective_pdf_path,
                        match_id=match_id,
                        syllabus_id=objective_syllabus_id,
                        content_id=obj_item.id,
                        page_number=obj_item.page_start,
                        title=obj_item.title,
                        snippet=obj_item.text,
                        keywords=evidence.shared_keywords,
                        evidence_type=evidence.evidence_type,
                    )
                if compared_pdf_path:
                    cmp_regions = self.spatial_locator.locate_regions_for_item(
                        pdf_path=compared_pdf_path,
                        match_id=match_id,
                        syllabus_id=compared_syllabus_id,
                        content_id=cmp_item.id,
                        page_number=cmp_item.page_start,
                        title=cmp_item.title,
                        snippet=cmp_item.text,
                        keywords=evidence.shared_keywords,
                        evidence_type=evidence.evidence_type,
                    )

            enriched_evidence = MatchEvidence(
                evidence_type=evidence.evidence_type,
                shared_keywords=evidence.shared_keywords,
                semantic_score=evidence.semantic_score,
                lexical_score=evidence.lexical_score,
                objective_snippet=evidence.objective_snippet,
                compared_snippet=evidence.compared_snippet,
                objective_page=evidence.objective_page,
                compared_page=evidence.compared_page,
                objective_regions=obj_regions,
                compared_regions=cmp_regions,
            )

            matches.append(
                ContentMatch(
                    id=match_id,
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
                    evidence=enriched_evidence,
                )
            )

            primary_chosen = (score, cmp_item, breakdown, evidence)
            seen_pairs.add(pair_key)
            cmp_usage_count[cmp_item.id] = usage + 1

            if classification in (MatchClassification.MATCH, MatchClassification.PARTIAL_MATCH):
                covered_objective_ids.add(obj_item.id)
                covered_compared_ids.add(cmp_item.id)

            # Evaluación de correspondencia múltiple genuina (1:N)
            for cand in cands:
                sec_score, sec_cmp, sec_breakdown, sec_evidence = cand
                if sec_cmp.id == primary_chosen[1].id:
                    continue

                # 1. Puntuación alta y muy cercana al mejor candidato
                if sec_score < th["partial"] or sec_score < (primary_chosen[0] - 0.10):
                    break

                # 2. El candidato secundario debe ser libre (no compartido)
                sec_usage = cmp_usage_count.get(sec_cmp.id, 0)
                if sec_usage >= 1:
                    continue

                sec_pair_key = (obj_item.id, sec_cmp.id)
                if sec_pair_key in seen_pairs:
                    continue

                # 3. El contenido comparado debe ser sustancialmente distinto al primario
                prim_cmp = primary_chosen[1]
                text_overlap = self.vector_service.compute_lexical_similarity(prim_cmp.text, sec_cmp.text)
                if text_overlap > 0.70 or prim_cmp.title.strip().lower() == sec_cmp.title.strip().lower():
                    continue

                sec_has_content_affinity = (
                    sec_breakdown.semantic_similarity >= 0.40
                    or sec_breakdown.lexical_similarity >= 0.25
                    or sec_breakdown.keyword_overlap >= 0.15
                )
                sec_classification = self._classify(sec_score, th, sec_has_content_affinity)
                if sec_classification not in (MatchClassification.MATCH, MatchClassification.PARTIAL_MATCH):
                    continue

                sec_match_id = f"MATCH-{uuid.uuid4().hex[:10].upper()}"

                sec_obj_regions = []
                sec_cmp_regions = []
                if self.spatial_locator:
                    if objective_pdf_path:
                        sec_obj_regions = self.spatial_locator.locate_regions_for_item(
                            pdf_path=objective_pdf_path,
                            match_id=sec_match_id,
                            syllabus_id=objective_syllabus_id,
                            content_id=obj_item.id,
                            page_number=obj_item.page_start,
                            title=obj_item.title,
                            snippet=obj_item.text,
                            keywords=sec_evidence.shared_keywords,
                            evidence_type=sec_evidence.evidence_type,
                        )
                    if compared_pdf_path:
                        sec_cmp_regions = self.spatial_locator.locate_regions_for_item(
                            pdf_path=compared_pdf_path,
                            match_id=sec_match_id,
                            syllabus_id=compared_syllabus_id,
                            content_id=sec_cmp.id,
                            page_number=sec_cmp.page_start,
                            title=sec_cmp.title,
                            snippet=sec_cmp.text,
                            keywords=sec_evidence.shared_keywords,
                            evidence_type=sec_evidence.evidence_type,
                        )

                sec_enriched_evidence = MatchEvidence(
                    evidence_type=sec_evidence.evidence_type,
                    shared_keywords=sec_evidence.shared_keywords,
                    semantic_score=sec_evidence.semantic_score,
                    lexical_score=sec_evidence.lexical_score,
                    objective_snippet=sec_evidence.objective_snippet,
                    compared_snippet=sec_evidence.compared_snippet,
                    objective_page=sec_evidence.objective_page,
                    compared_page=sec_evidence.compared_page,
                    objective_regions=sec_obj_regions,
                    compared_regions=sec_cmp_regions,
                )

                matches.append(
                    ContentMatch(
                        id=sec_match_id,
                        comparison_id=comparison_id,
                        objective_item_id=obj_item.id,
                        compared_item_id=sec_cmp.id,
                        objective_title=obj_item.title,
                        compared_title=sec_cmp.title,
                        objective_section=obj_item.section_name,
                        compared_section=sec_cmp.section_name,
                        objective_page=obj_item.page_start,
                        compared_page=sec_cmp.page_start,
                        score_breakdown=sec_breakdown,
                        classification=sec_classification,
                        evidence=sec_enriched_evidence,
                    )
                )

                seen_pairs.add(sec_pair_key)
                cmp_usage_count[sec_cmp.id] = sec_usage + 1
                covered_objective_ids.add(obj_item.id)
                covered_compared_ids.add(sec_cmp.id)

                # Permitir como máximo un candidato secundario (relación 1:2 tope)
                break

        # 3. Identificar contenidos no correspondidos del Objetivo
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

        # 4. Identificar contenidos no correspondidos del Comparado (Bidireccional)
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

    def _classify(
        self,
        score: float,
        thresholds: Dict[str, float],
        has_content_affinity: bool = True,
    ) -> MatchClassification:
        """Asigna la etiqueta categórica según los umbrales configurados y la afinidad de contenido."""
        if score >= thresholds["match"] and has_content_affinity:
            return MatchClassification.MATCH
        if score >= thresholds["partial"] and has_content_affinity:
            return MatchClassification.PARTIAL_MATCH
        if score >= thresholds["uncertain"]:
            return MatchClassification.UNCERTAIN
        return MatchClassification.NO_MATCH

