"""Reglas puras de scoring compartidas por comparación y evaluación por pares."""

from typing import Dict, Tuple

from app.domain.comparison import MatchClassification, ScoreBreakdown

BASELINE_VERSION = "bipartite-adaptive-002"
DEFAULT_WEIGHTS = {"semantic": 0.45, "lexical": 0.30, "keyword": 0.15, "structural": 0.10}
DEFAULT_THRESHOLDS = {"match": 0.75, "partial": 0.58, "uncertain": 0.45}


def has_content_affinity(semantic: float, lexical: float, keyword: float) -> bool:
    return semantic >= 0.40 or lexical >= 0.25 or keyword >= 0.15


def adaptive_pair_score(
    semantic: float, lexical: float, keyword: float, structural: float,
    base_weights: Dict[str, float],
) -> Tuple[float, ScoreBreakdown]:
    """Ajusta pesos y pisos de correspondencia conservando el desglose original."""
    weights = dict(base_weights)
    if semantic >= 0.75 or lexical >= 0.70:
        weights.update(structural=0.0, semantic=0.50, lexical=0.35, keyword=0.15)
    elif semantic >= 0.60 or lexical >= 0.45:
        weights.update(structural=0.05, semantic=0.50, lexical=0.30, keyword=0.15)
    composite = (
        weights.get("semantic", 0.45) * semantic
        + weights.get("lexical", 0.30) * lexical
        + weights.get("keyword", 0.15) * keyword
        + weights.get("structural", 0.10) * structural
    )
    if lexical >= 0.85 or semantic >= 0.85:
        composite = max(composite, 0.80)
    elif lexical >= 0.65 or semantic >= 0.65:
        composite = max(composite, 0.60)
    composite = max(0.0, min(1.0, round(composite, 4)))
    return composite, ScoreBreakdown(
        semantic_similarity=semantic, lexical_similarity=lexical,
        keyword_overlap=keyword, structural_similarity=structural,
        composite_score=composite, weights=weights,
    )


def classify_score(
    score: float, thresholds: Dict[str, float], content_affinity: bool = True,
) -> MatchClassification:
    if score >= thresholds["match"] and content_affinity:
        return MatchClassification.MATCH
    if score >= thresholds["partial"] and content_affinity:
        return MatchClassification.PARTIAL_MATCH
    if score >= thresholds["uncertain"]:
        return MatchClassification.UNCERTAIN
    return MatchClassification.NO_MATCH
