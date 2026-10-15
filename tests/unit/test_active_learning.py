"""Orden, elegibilidad y denominador de la cola de anotación."""

from copy import deepcopy
from datetime import datetime

from app.domain.active_learning import PriorityReason, annotation_coverage, build_annotation_cases, prioritize_cases
from app.domain.comparison import Comparison, ContentMatch, MatchClassification as Label, MatchEvidence, ScoreBreakdown
from tests.unit.test_ground_truth import annotation, pairs_from


def comparison() -> Comparison:
    matches = []
    for i, (score, label) in enumerate([(.99, Label.MATCH), (.9, Label.MATCH), (.5, Label.UNCERTAIN), (.6, Label.PARTIAL_MATCH), (.95, Label.MATCH)]):
        matches.append(ContentMatch(
            id=f"MATCH-{i}", comparison_id="COMP", objective_item_id=f"OBJ-{i}", compared_item_id=f"CMP-{i}",
            objective_title="Objetivo", compared_title="Comparado", objective_section="Unidad", compared_section="Unidad",
            objective_page=1, compared_page=2, score_breakdown=ScoreBreakdown(score, score, .5, .5, score, {}),
            classification=label, evidence=MatchEvidence("HYBRID", [], score, score, "Objetivo", "Comparado", 1, 2),
        ))
    return Comparison("COMP", "OBJ-SYL", "CMP-SYL", .5, 100, 100, "test", datetime.now(), matches)


def test_priority_is_deterministic_explained_and_preserves_predictions() -> None:
    comp = comparison()
    original = deepcopy(comp)
    pairs = pairs_from([annotation(1, "A", Label.MATCH, 0), annotation(2, "B", Label.NO_MATCH, 0),
                        annotation(3, "A", Label.MATCH, 1), annotation(4, "A", Label.MATCH, 4),
                        annotation(5, "B", Label.MATCH, 4)])
    cases = build_annotation_cases([comp], pairs)
    queue = prioritize_cases(cases)
    assert [c.objective_item_id for c in queue] == ["OBJ-0", "OBJ-1", "OBJ-2", "OBJ-3"]
    assert [c.reason for c in queue[:2]] == [PriorityReason.DISAGREEMENT, PriorityReason.SECOND_REVIEW]
    assert queue[2].uncertain_prediction is True
    assert queue[2].near_boundary is True
    assert all(c.status != "CONSENSUS" for c in queue)
    assert prioritize_cases(list(reversed(cases))) == queue
    assert comp == original
    assert len(prioritize_cases(cases, " a ")) == 3  # Puede corregir desacuerdo, no repetir su voto único.
    assert len(prioritize_cases(cases, reason=PriorityReason.UNREVIEWED)) == 2
    coverage = annotation_coverage(cases)
    assert coverage.total_pairs == 5
    assert coverage.reviewed_pairs == 3
    assert coverage.consensus_pairs == 1
    assert coverage.reviewed_percentage == 60
    assert coverage.consensus_percentage == 20


def test_queue_contains_manual_pairs_without_inventing_scores_or_probabilities() -> None:
    pairs = pairs_from([annotation(1, "A", Label.MATCH, 99)])
    cases = build_annotation_cases([comparison()], pairs)
    manual = next(c for c in cases if c.objective_item_id == "OBJ-99")
    assert manual.score is None
    assert manual.boundary_distance is None
    assert manual.reason == PriorityReason.SECOND_REVIEW


def test_empty_coverage_is_undefined_instead_of_artificially_complete() -> None:
    coverage = annotation_coverage([])
    assert coverage.total_pairs == 0
    assert coverage.reviewed_percentage is None
    assert coverage.consensus_percentage is None


def test_duplicate_matches_are_one_pair_with_stable_selection() -> None:
    comp = comparison()
    comp.matches.append(deepcopy(comp.matches[0]))
    comp.matches.reverse()
    assert len(build_annotation_cases([comp], [])) == 5
