"""
Pruebas unitarias para entidades de dominio de Comparación, Scoring y Evidencias.
"""

from datetime import datetime
import pytest
from app.domain.comparison import (
    Comparison,
    ContentMatch,
    MatchClassification,
    MatchEvidence,
    ScoreBreakdown,
    UnmatchedItem,
)


def test_score_breakdown_validation() -> None:
    weights = {"semantic": 0.4, "lexical": 0.3, "keyword": 0.15, "structural": 0.15}
    valid = ScoreBreakdown(
        semantic_similarity=0.90,
        lexical_similarity=0.85,
        keyword_overlap=0.80,
        structural_similarity=0.75,
        composite_score=0.85,
        weights=weights,
    )
    assert valid.composite_score == 0.85

    with pytest.raises(ValueError, match="Los componentes de score deben estar en el rango"):
        ScoreBreakdown(
            semantic_similarity=1.5,  # Fuera de rango
            lexical_similarity=0.5,
            keyword_overlap=0.5,
            structural_similarity=0.5,
            composite_score=0.5,
            weights=weights,
        )


def test_comparison_summary_and_counts() -> None:
    weights = {"semantic": 0.4, "lexical": 0.3, "keyword": 0.15, "structural": 0.15}
    breakdown = ScoreBreakdown(0.9, 0.9, 0.9, 0.9, 0.9, weights)
    evidence = MatchEvidence("HYBRID", ["sql", "tablas"], 0.9, 0.9, "snip1", "snip2", 1, 2)
    
    match1 = ContentMatch(
        id="m1",
        comparison_id="comp1",
        objective_item_id="obj1",
        compared_item_id="cmp1",
        objective_title="Tema 1",
        compared_title="Tema 1 equiv",
        objective_section="Unidad I",
        compared_section="Unidad I",
        objective_page=1,
        compared_page=2,
        score_breakdown=breakdown,
        classification=MatchClassification.MATCH,
        evidence=evidence,
    )

    comparison = Comparison(
        id="comp1",
        objective_syllabus_id="obj-syl",
        compared_syllabus_id="cmp-syl",
        global_score=0.85,
        objective_coverage=90.0,
        compared_coverage=80.0,
        model_version="baseline-001",
        created_at=datetime.now(),
        matches=[match1],
        unmatched_objective=[],
        unmatched_compared=[],
    )

    assert comparison.total_matches == 1
    counts = comparison.count_by_classification
    assert counts["MATCH"] == 1
    assert counts["NO_MATCH"] == 0
    assert comparison.is_acceptable_pre_evaluation(threshold_percentage=70.0) is True
    assert comparison.is_acceptable_pre_evaluation(threshold_percentage=90.0) is False
