"""Métricas completas y exclusión transitiva del conjunto reservado."""

from dataclasses import replace
from datetime import datetime
from unittest.mock import Mock

import pytest

from app.application.reserved_evaluation_policy import ReservedEvaluationPolicy
from app.application.compare_syllabi import CompareSyllabiUseCase
from app.domain.academic_sources import academic_source_tokens
from app.domain.comparison import Comparison, MatchClassification
from app.domain.evaluation_metrics import correspondence_metrics
from app.domain.review import DatasetExample
from app.domain.scoring import DEFAULT_WEIGHTS
from app.infrastructure.nlp.vector_service import NlpVectorService


def example(index: int) -> DatasetExample:
    return DatasetExample(str(index), str(index), f"OBJ-{index}", f"CMP-{index}", f"Objetivo {index}", f"Comparado {index}",
                          source_university_obj=f"Uni-{index}", source_course_obj="CS", source_syllabus_obj=f"SYL-{index}",
                          source_university_cmp=f"Cmp-{index}", source_course_cmp="CS", source_syllabus_cmp=f"CMP-SYL-{index}")


def test_reserved_groups_are_excluded_transitively_and_by_document_hash() -> None:
    held = replace(example(0), source_syllabus_hash_obj="same-document")
    bridge = replace(example(1), source_syllabus_obj=held.source_syllabus_obj)
    linked = replace(example(2), source_syllabus_cmp=bridge.source_syllabus_cmp)
    copy = replace(example(3), source_syllabus_hash_cmp="same-document")
    independent = example(4)
    repo = Mock()
    repo.list_snapshots.return_value = [Mock(payload={"reserved_source_tokens": academic_source_tokens(held)})]
    result = ReservedEvaluationPolicy(repo).filter_examples([linked, independent, bridge, copy])
    assert result == [independent]


def test_active_model_inference_changes_scoring_instead_of_only_version_label() -> None:
    inference = Mock()
    inference.predict_pair.return_value = (MatchClassification.NO_MATCH, .02, {"NO_MATCH": 1.0})
    use_case = CompareSyllabiUseCase(NlpVectorService(), inference_service=inference)
    score, breakdown = use_case._compute_pair_score(.9, .9, .8, .5, DEFAULT_WEIGHTS)
    assert score == .02
    assert breakdown.composite_score == .02
    inference.predict_pair.assert_called_once()


def test_complete_metrics_count_missing_positive_pairs_and_coverage_error() -> None:
    item = lambda identity: {"id": identity, "unit_number": 1}
    case = {"comparison_id": "C", "objective_items": [item("O1"), item("O2")], "compared_items": [item("P1"), item("P2")],
            "labels": [{"objective_item_id": "O1", "compared_item_id": "P1", "label": "MATCH"},
                       {"objective_item_id": "O1", "compared_item_id": "P2", "label": "NO_MATCH"},
                       {"objective_item_id": "O2", "compared_item_id": "P1", "label": "NO_MATCH"},
                       {"objective_item_id": "O2", "compared_item_id": "P2", "label": "MATCH"}]}
    prediction = Comparison("P", "O", "P", .1, 0, 0, "baseline", datetime.now())
    metrics = correspondence_metrics(case, prediction)
    assert metrics["false_negative"] == 2
    assert metrics["recall"] == 0
    assert metrics["f1"] == 0
    assert metrics["expected_objective_coverage"] == 100
    assert metrics["objective_coverage_error"] == 100
