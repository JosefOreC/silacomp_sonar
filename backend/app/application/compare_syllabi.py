"""
Caso de uso para la comparación integral y pre-evaluación explicable entre dos sílabos.
Implementa el motor híbrido, scoring ponderado, clasificación y análisis bidireccional.
"""

from datetime import datetime
from dataclasses import replace
import re
from typing import Dict, List, Optional, Set, Tuple
import uuid
import numpy as np
from scipy.optimize import linear_sum_assignment

from app.domain.comparison import (
    Comparison,
    ContentMatch,
    MatchClassification,
    MatchEvidence,
    ScoreBreakdown,
    UnmatchedItem,
)
from app.domain.content import ContentItem
from app.domain.ports import IComparisonRepository, IModelInferenceService
from app.domain.scoring import (
    BASELINE_VERSION, DEFAULT_WEIGHTS, DEFAULT_THRESHOLDS,
    adaptive_pair_score, classify_score, has_content_affinity as content_affinity,
)
from app.infrastructure.nlp.normalizer import TextNormalizer
from app.infrastructure.nlp.vector_service import NlpVectorService
from app.infrastructure.pdf.spatial_locator import SpatialLocatorService


class CompareSyllabiUseCase:
    """Orquesta la comparación exhaustiva entre los contenidos de dos sílabos."""

    def __init__(
        self,
        vector_service: NlpVectorService,
        comparison_repository: Optional[IComparisonRepository] = None,
        spatial_locator: Optional[SpatialLocatorService] = None,
        model_version: str = BASELINE_VERSION,
        inference_service: Optional[IModelInferenceService] = None,
    ) -> None:
        self.vector_service = vector_service
        self.repository = comparison_repository
        self.spatial_locator = spatial_locator or SpatialLocatorService()
        self.model_version = model_version
        self.inference_service = inference_service

    def _compute_pair_score(
        self,
        sem_sim: float,
        lex_sim: float,
        key_sim: float,
        est_sim: float,
        base_weights: Dict[str, float],
    ) -> Tuple[float, ScoreBreakdown]:
        """
        Calcula el score compuesto con ajuste adaptativo de pesos:
        - Si la afinidad conceptual es sólida (sem_sim >= 0.75 o lex_sim >= 0.70),
          la equivalencia temática es concluyente: la penalización estructural se neutraliza (0.0)
          y se transfiere a semántica (0.50), léxica (0.35) y palabras clave (0.15).
        - Si la afinidad conceptual es moderada (sem_sim >= 0.60 o lex_sim >= 0.45),
          se atenúa la penalización estructural a 0.05.
        - Si hay contención léxica directa alta (lex_sim >= 0.85) o afinidad semántica concluyente (sem_sim >= 0.85),
          se garantiza un piso representativo de convalidación académica (>= 0.80).
        """
        score, breakdown = adaptive_pair_score(sem_sim, lex_sim, key_sim, est_sim, base_weights)
        if self.inference_service is not None:
            prediction = self.inference_service.predict_pair({
                "semantic_sim": sem_sim, "lexical_sim": lex_sim, "asymmetric_containment": lex_sim,
                "keyword_overlap": key_sim, "structural_sim": est_sim,
            })
            if prediction is not None:
                score = max(0.0, min(1.0, round(float(prediction[1]), 4)))
                breakdown = replace(breakdown, composite_score=score)
        return score, breakdown

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

        best_score_per_obj: Dict[str, Tuple[float, Optional[ContentItem]]] = {
            item.id: (0.0, None) for item in objective_items
        }
        best_score_per_cmp: Dict[str, Tuple[float, Optional[ContentItem]]] = {
            item.id: (0.0, None) for item in compared_items
        }

        if n_obj == 0 or n_cmp == 0:
            return Comparison(
                id=comparison_id,
                objective_syllabus_id=objective_syllabus_id,
                compared_syllabus_id=compared_syllabus_id,
                global_score=0.0,
                objective_coverage=0.0,
                compared_coverage=0.0,
                model_version=self.model_version,
                created_at=datetime.now(),
                matches=[],
                unmatched_objective=[
                    UnmatchedItem(
                        item_id=it.id,
                        syllabus_id=objective_syllabus_id,
                        section_name=it.section_name,
                        title=it.title,
                        text_snippet=it.text[:200],
                        page=it.page_start,
                    )
                    for it in objective_items
                ],
                unmatched_compared=[
                    UnmatchedItem(
                        item_id=it.id,
                        syllabus_id=compared_syllabus_id,
                        section_name=it.section_name,
                        title=it.title,
                        text_snippet=it.text[:200],
                        page=it.page_start,
                    )
                    for it in compared_items
                ],
            )

        # Extracción y limpieza de tópicos nucleares y frases de contenido
        def _get_item_phrases(item: ContentItem) -> Tuple[str, List[str]]:
            core = item.title.split(" - ")[-1].strip() if " - " in item.title else item.title.strip()
            phrases = [core] if core else []
            if item.text:
                raw_sentences = re.split(r'[\n;]+|(?<=[a-záéíóú0-9])\.\s+', item.text)
                for s in raw_sentences:
                    sc = s.strip(" .:\t\n\r-")
                    if " - " in sc:
                        sc = sc.split(" - ")[-1].strip()
                    if len(sc) >= 4 and not sc.lower().startswith(('en esta unidad', 'descargado', 'downloaded', 'lomoarcpsd', 'scan to open')):
                        if sc.lower() not in [p.lower() for p in phrases]:
                            phrases.append(sc)
            return core, phrases

        obj_phrases_list = [_get_item_phrases(it)[1] for it in objective_items]
        cmp_phrases_list = [_get_item_phrases(it)[1] for it in compared_items]

        # Precomputación vectorial y textual por lote para alto rendimiento
        obj_texts = [f"{it.title}. {it.text}".strip() for it in objective_items]
        cmp_texts = [f"{it.title}. {it.text}".strip() for it in compared_items]

        norm_obj_texts = [TextNormalizer.normalize_for_indexing(t) for t in obj_texts]
        norm_cmp_texts = [TextNormalizer.normalize_for_indexing(t) for t in cmp_texts]

        core_obj_texts = [it.title.split(" - ")[-1].strip() if " - " in it.title else it.title.strip() for it in objective_items]
        core_cmp_texts = [it.title.split(" - ")[-1].strip() if " - " in it.title else it.title.strip() for it in compared_items]

        sem_matrix: Optional[np.ndarray] = None
        sem_core_matrix: Optional[np.ndarray] = None
        if hasattr(self.vector_service, "encode_texts") and n_obj > 0 and n_cmp > 0:
            try:
                emb_obj = self.vector_service.encode_texts(obj_texts)
                emb_cmp = self.vector_service.encode_texts(cmp_texts)
                if emb_obj is not None and emb_cmp is not None and len(emb_obj) > 0 and len(emb_cmp) > 0:
                    sem_matrix = np.dot(emb_obj, emb_cmp.T)

                emb_core_obj = self.vector_service.encode_texts(core_obj_texts)
                emb_core_cmp = self.vector_service.encode_texts(core_cmp_texts)
                if emb_core_obj is not None and emb_core_cmp is not None and len(emb_core_obj) > 0 and len(emb_core_cmp) > 0:
                    sem_core_matrix = np.dot(emb_core_obj, emb_core_cmp.T)
            except Exception:
                sem_matrix = None
                sem_core_matrix = None

        # 1. Matriz exhaustiva de afinidad y candidatos con pesos adaptativos
        affinity_matrix = np.zeros((n_obj, n_cmp), dtype=float)
        pair_evaluations: Dict[Tuple[int, int], Tuple[float, ScoreBreakdown, MatchEvidence]] = {}
        candidates_by_obj: Dict[str, List[Tuple[float, ContentItem, ScoreBreakdown, MatchEvidence]]] = {
            it.id: [] for it in objective_items
        }

        for i, obj_item in enumerate(objective_items):
            text_obj = obj_texts[i]
            norm_obj = norm_obj_texts[i]
            core_obj = core_obj_texts[i]

            for j, cmp_item in enumerate(compared_items):
                text_cmp = cmp_texts[j]
                norm_cmp = norm_cmp_texts[j]
                core_cmp = core_cmp_texts[j]

                # Atajo de correspondencia exacta 100% idéntica
                if norm_obj and norm_obj == norm_cmp:
                    sem_sim = 1.0
                    lex_sim = 1.0
                    key_sim = 1.0
                    est_sim = 1.0
                    composite = 1.0
                    breakdown = ScoreBreakdown(
                        semantic_similarity=1.0,
                        lexical_similarity=1.0,
                        keyword_overlap=1.0,
                        structural_similarity=1.0,
                        composite_score=1.0,
                        weights=w,
                    )
                else:
                    # 1. Similitud semántica multi-escala (núcleo precomputado vs texto extendido)
                    if sem_core_matrix is not None:
                        sem_core = max(0.0, min(1.0, round(float(sem_core_matrix[i, j]), 4)))
                    else:
                        sem_core = self.vector_service.compute_semantic_similarity(core_obj, core_cmp)

                    if sem_matrix is not None:
                        sem_full = max(0.0, min(1.0, round(float(sem_matrix[i, j]), 4)))
                    else:
                        sem_full = self.vector_service.compute_semantic_similarity(text_obj, text_cmp)

                    # Similitud asimétrica por sub-frases (detección de sub-tópicos y contención de conceptos)
                    sem_phrase_max = 0.0
                    lex_phrase_max = 0.0
                    key_phrase_max = 0.0

                    for cp in cmp_phrases_list[j]:
                        lp = self.vector_service.compute_lexical_similarity(core_obj, cp)
                        if lp > lex_phrase_max:
                            lex_phrase_max = lp
                        kp = self.vector_service.compute_keyword_overlap(core_obj, cp)
                        if kp > key_phrase_max:
                            key_phrase_max = kp
                        if lp >= 0.70 or kp >= 0.65:
                            sp = self.vector_service.compute_semantic_similarity(core_obj, cp)
                            if sp > sem_phrase_max:
                                sem_phrase_max = sp

                    for op in obj_phrases_list[i]:
                        lp = self.vector_service.compute_lexical_similarity(op, core_cmp)
                        if lp > lex_phrase_max:
                            lex_phrase_max = lp
                        kp = self.vector_service.compute_keyword_overlap(op, core_cmp)
                        if kp > key_phrase_max:
                            key_phrase_max = kp
                        if lp >= 0.70 or kp >= 0.65:
                            sp = self.vector_service.compute_semantic_similarity(op, core_cmp)
                            if sp > sem_phrase_max:
                                sem_phrase_max = sp

                    sem_sim = max(sem_core, sem_full, sem_phrase_max)

                    # 2. Similitud léxica multi-escala (TF-IDF + contención asimétrica de conceptos)
                    lex_core = self.vector_service.compute_lexical_similarity(core_obj, core_cmp)
                    lex_full = self.vector_service.compute_lexical_similarity(text_obj, text_cmp)
                    lex_sim = max(lex_core, lex_full, lex_phrase_max)

                    # 3. Solapamiento de palabras clave multi-escala
                    key_core = self.vector_service.compute_keyword_overlap(core_obj, core_cmp)
                    key_full = self.vector_service.compute_keyword_overlap(text_obj, text_cmp)
                    key_sim = max(key_core, key_full, key_phrase_max)

                    est_sim = self.vector_service.compute_structural_similarity(
                        order_a=obj_item.order,
                        total_items_a=n_obj,
                        order_b=cmp_item.order,
                        total_items_b=n_cmp,
                        unit_a=obj_item.unit_number,
                        unit_b=cmp_item.unit_number,
                    )

                    composite, breakdown = self._compute_pair_score(sem_sim, lex_sim, key_sim, est_sim, w)

                # Actualizar mejores scores globales para cálculo de cobertura
                if composite > best_score_per_obj[obj_item.id][0]:
                    best_score_per_obj[obj_item.id] = (composite, cmp_item)
                if composite > best_score_per_cmp[cmp_item.id][0]:
                    best_score_per_cmp[cmp_item.id] = (composite, obj_item)

                shared_kw = self.vector_service.extract_shared_keywords(text_obj, text_cmp)
                ev_type = (
                    "HYBRID"
                    if (sem_sim > 0.6 and lex_sim > 0.4)
                    else ("SEMANTIC" if sem_sim >= lex_sim else "LEXICAL")
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

                affinity_matrix[i, j] = composite
                pair_evaluations[(i, j)] = (composite, breakdown, evidence)
                candidates_by_obj[obj_item.id].append((composite, cmp_item, breakdown, evidence))

            # Ordenar candidatos por score descendente
            candidates_by_obj[obj_item.id].sort(key=lambda x: x[0], reverse=True)

        # 2. Asignación orientada a la convalidación del Sílabo Objetivo
        # Priorizamos el mejor candidato que demuestre cobertura pedagógica del tema.
        # Si la asignación bipartita sugiere un candidato alternativo libre con afinidad sólida
        # (score a menos de 0.04 del mejor y score >= th['partial']), se diversifica.
        cost_matrix = 1.0 - affinity_matrix
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        bipartite_matches = dict(zip(row_ind, col_ind))

        cmp_usage_count: Dict[str, int] = {}
        seen_pairs: Set[Tuple[str, str]] = set()
        primary_match_by_obj: Dict[str, Tuple[float, ContentItem, ScoreBreakdown, MatchEvidence]] = {}

        # Para cada ítem del objetivo, determinar su correspondencia más sólida:
        for i, obj_item in enumerate(objective_items):
            cands = candidates_by_obj.get(obj_item.id, [])
            if not cands:
                continue

            best_cand = cands[0]  # Mejor candidato absoluto por afinidad
            best_score = best_cand[0]

            chosen_cand = best_cand

            # Diversificación controlada solo si la alternativa bipartita no degrada la convalidación
            if i in bipartite_matches:
                j_bip = bipartite_matches[i]
                bip_score = affinity_matrix[i, j_bip]
                bip_eval = pair_evaluations[(i, j_bip)]
                if bip_score >= (best_score - 0.04) and bip_score >= th["partial"]:
                    chosen_cand = (bip_score, compared_items[j_bip], bip_eval[1], bip_eval[2])

            chosen_score, chosen_cmp, chosen_bd, chosen_ev = chosen_cand
            has_content_affinity = (
                content_affinity(chosen_bd.semantic_similarity, chosen_bd.lexical_similarity, chosen_bd.keyword_overlap)
            )

            if chosen_score >= th["uncertain"] and has_content_affinity:
                primary_match_by_obj[obj_item.id] = chosen_cand
                cmp_usage_count[chosen_cmp.id] = cmp_usage_count.get(chosen_cmp.id, 0) + 1
                seen_pairs.add((obj_item.id, chosen_cmp.id))

        # 4. Creación formal de matches primarios y evaluación de correspondencias 1:N
        for obj_item in objective_items:
            primary = primary_match_by_obj.get(obj_item.id)
            if not primary:
                continue

            score, cmp_item, breakdown, evidence = primary
            usage = cmp_usage_count.get(cmp_item.id, 0)
            pair_key = (obj_item.id, cmp_item.id)
            cands = candidates_by_obj.get(obj_item.id, [])
            has_content_affinity = (
                content_affinity(breakdown.semantic_similarity, breakdown.lexical_similarity, breakdown.keyword_overlap)
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

            actual_obj_page = obj_regions[0].page_number if obj_regions else obj_item.page_start
            actual_cmp_page = cmp_regions[0].page_number if cmp_regions else cmp_item.page_start

            enriched_evidence = MatchEvidence(
                evidence_type=evidence.evidence_type,
                shared_keywords=evidence.shared_keywords,
                semantic_score=evidence.semantic_score,
                lexical_score=evidence.lexical_score,
                objective_snippet=evidence.objective_snippet,
                compared_snippet=evidence.compared_snippet,
                objective_page=actual_obj_page,
                compared_page=actual_cmp_page,
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
                    objective_page=actual_obj_page,
                    compared_page=actual_cmp_page,
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
                    content_affinity(sec_breakdown.semantic_similarity, sec_breakdown.lexical_similarity, sec_breakdown.keyword_overlap)
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

                sec_actual_obj_page = sec_obj_regions[0].page_number if sec_obj_regions else obj_item.page_start
                sec_actual_cmp_page = sec_cmp_regions[0].page_number if sec_cmp_regions else sec_cmp.page_start

                sec_enriched_evidence = MatchEvidence(
                    evidence_type=sec_evidence.evidence_type,
                    shared_keywords=sec_evidence.shared_keywords,
                    semantic_score=sec_evidence.semantic_score,
                    lexical_score=sec_evidence.lexical_score,
                    objective_snippet=sec_evidence.objective_snippet,
                    compared_snippet=sec_evidence.compared_snippet,
                    objective_page=sec_actual_obj_page,
                    compared_page=sec_actual_cmp_page,
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
                        objective_page=sec_actual_obj_page,
                        compared_page=sec_actual_cmp_page,
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
        # Si existen contenidos clasificados en unidades temáticas (unit_number > 0),
        # la cobertura formativa se computa sobre estos temas analíticos curriculares.
        curr_obj_items = [it for it in objective_items if it.unit_number and it.unit_number > 0]
        curr_cmp_items = [it for it in compared_items if it.unit_number and it.unit_number > 0]

        eff_obj_items = curr_obj_items if curr_obj_items else objective_items
        eff_cmp_items = curr_cmp_items if curr_cmp_items else compared_items

        eff_covered_obj = len(covered_objective_ids.intersection({it.id for it in eff_obj_items}))
        eff_covered_cmp = len(covered_compared_ids.intersection({it.id for it in eff_cmp_items}))

        obj_cov = round((eff_covered_obj / max(1, len(eff_obj_items))) * 100.0, 1)
        cmp_cov = round((eff_covered_cmp / max(1, len(eff_cmp_items))) * 100.0, 1)

        # 5. Porcentaje Global de Correspondencia Estimada
        # Ponderación basada en promedio de mejores scores de cobertura del temario analítico del objetivo
        sum_best_obj = sum(best_score_per_obj[it.id][0] for it in eff_obj_items)
        global_score = round(sum_best_obj / max(1, len(eff_obj_items)), 4)

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
        return classify_score(score, thresholds, has_content_affinity)
