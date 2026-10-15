"""Regresiones de filtración entre fuentes académicas y datos sintéticos."""

from dataclasses import replace

import numpy as np
import pytest

from app.application.dataset_service import DatasetService
from app.infrastructure.ml.academic_split import academic_groups, split_examples
from app.infrastructure.ml.supervised_trainer import SklearnSupervisedTrainer


@pytest.fixture
def reviewed_examples():
    examples = DatasetService(None).generate_bootstrap_synthetic_dataset(120)
    return [replace(
        ex, id=f"REAL-{i}", model_version="reviewed-model",
        source_university_obj=f"University {i % 8}", source_course_obj="CS-101",
        source_university_cmp=f"Partner {i % 8}", source_course_cmp="CS-201",
        source_syllabus_obj=f"OBJ-SYL-{i % 8}", source_syllabus_cmp=f"CMP-SYL-{i % 8}",
    ) for i, ex in enumerate(examples)]


def test_group_split_is_disjoint_deterministic_and_human_only(reviewed_examples):
    service = DatasetService(None)
    examples = reviewed_examples + service.generate_bootstrap_synthetic_dataset(30)
    _, y, _ = service.extract_feature_matrix(examples)
    train, test, groups, metadata = split_examples(examples, y, 0.25, 42)
    train_again, test_again, _, _ = split_examples(examples, y, 0.25, 42)
    assert set(groups[train[:len(train) - 30]]).isdisjoint(groups[test])
    assert set(test) <= set(range(120))
    assert set(range(120, 150)) <= set(train)
    assert set(y[train]) == set(y[test]) == {0, 1, 2}
    assert metadata["synthetic_test_count"] == 0
    np.testing.assert_array_equal(train, train_again)
    np.testing.assert_array_equal(test, test_again)


def test_shared_sources_are_connected_across_roles_and_accent_variants(reviewed_examples):
    a, b, c = reviewed_examples[:3]
    a = replace(a, source_university_obj=" UNIVERSIDAD Perú ", source_course_obj=" Álgebra I ")
    b = replace(b, source_university_cmp="universidad peru", source_course_cmp="algebra i")
    c = replace(c, source_syllabus_obj=b.source_syllabus_obj)
    groups = academic_groups([a, b, c])
    assert len(set(groups)) == 1


def test_missing_provenance_cannot_be_randomly_split(reviewed_examples):
    examples = [replace(ex, source_course_obj=None) for ex in reviewed_examples]
    _, y, _ = DatasetService(None).extract_feature_matrix(examples)
    with pytest.raises(ValueError, match="grupos académicos independientes"):
        split_examples(examples, y, 0.25, 42)


def test_synthetic_metrics_are_not_eligible_for_auto_activation():
    examples = DatasetService(None).generate_bootstrap_synthetic_dataset(60)
    _, y, _ = DatasetService(None).extract_feature_matrix(examples)
    _, _, _, metadata = split_examples(examples, y, 0.25, 42)
    assert metadata["evaluation_scope"] == "synthetic"
    assert metadata["eligible_for_auto_activation"] is False


def test_training_and_calibration_use_academic_groups(reviewed_examples, tmp_path):
    trainer = SklearnSupervisedTrainer(str(tmp_path))
    _, metrics = trainer.train_and_evaluate(reviewed_examples)
    split = metrics["split"]
    assert split["evaluation_scope"] == "human_reviews"
    assert set(split["train_groups"]).isdisjoint(split["test_groups"])
    assert metrics["calibration_method"] == "academic_groups"
    assert metrics["accuracy"] >= 0.75


def test_group_split_rejects_classes_confined_to_one_academic_group(reviewed_examples):
    examples = [replace(ex, source_university_obj=f"University {ex.ground_truth_label}",
                        source_course_obj="CS-101", source_university_cmp=f"Partner {ex.ground_truth_label}",
                        source_course_cmp="CS-201", source_syllabus_obj=None, source_syllabus_cmp=None)
                for ex in reviewed_examples]
    _, y, _ = DatasetService(None).extract_feature_matrix(examples)
    with pytest.raises(ValueError, match="conservando las clases"):
        split_examples(examples, y, 0.25, 42)


def test_grouped_calibration_with_bootstrap_preserves_real_evaluation(reviewed_examples, tmp_path):
    bootstrap = DatasetService(None).generate_bootstrap_synthetic_dataset(30)
    _, metrics = SklearnSupervisedTrainer(str(tmp_path)).train_and_evaluate(reviewed_examples + bootstrap)
    assert metrics["split"]["synthetic_train_count"] == 30
    assert metrics["split"]["synthetic_test_count"] == 0
    assert metrics["calibration_method"] == "academic_groups"
