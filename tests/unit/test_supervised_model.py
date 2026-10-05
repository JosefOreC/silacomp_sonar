"""
Pruebas unitarias para el pipeline de Aprendizaje Supervisado y Calibración Probabilística (Fase 2.0).
"""

import os
import tempfile
import pytest

from app.application.dataset_service import DatasetService
from app.domain.comparison import MatchClassification
from app.infrastructure.ml.model_inference_service import ModelInferenceService
from app.infrastructure.ml.supervised_trainer import SklearnSupervisedTrainer


@pytest.fixture
def sample_dataset():
    """Genera un dataset sintético controlado para pruebas unitarias de ML."""
    service = DatasetService(dataset_repo=None)
    return service.generate_bootstrap_synthetic_dataset(n_samples=60)


def test_dataset_service_feature_extraction(sample_dataset):
    service = DatasetService(dataset_repo=None)
    X, y, feature_names = service.extract_feature_matrix(sample_dataset)

    assert X.shape == (60, 5)
    assert len(y) == 60
    assert len(feature_names) == 5
    assert "semantic_sim" in feature_names
    assert "asymmetric_containment" in feature_names


def test_dataset_service_export_csv(sample_dataset):
    service = DatasetService(dataset_repo=None)
    csv_text = service.export_to_csv(sample_dataset)

    assert "semantic_sim" in csv_text
    assert "ground_truth_label" in csv_text
    lines = csv_text.strip().splitlines()
    assert len(lines) == 61  # Header + 60 rows


def test_supervised_trainer_calibrated_logistic(sample_dataset):
    with tempfile.TemporaryDirectory() as tmp_dir:
        trainer = SklearnSupervisedTrainer(models_dir=tmp_dir)
        model_version, metrics = trainer.train_and_evaluate(
            examples=sample_dataset,
            algorithm="calibrated_logistic",
            test_size=0.25,
            random_state=42,
        )

        assert model_version.version_id.startswith("sup-calibrat")
        assert model_version.algorithm_name == "CalibratedLogisticRegression"
        assert metrics["accuracy"] >= 0.75
        assert metrics["f1_macro"] >= 0.70
        assert "confusion_matrix" in metrics
        assert "baseline_comparison" in metrics
        assert os.path.exists(model_version.artifact_path)


def test_supervised_trainer_random_forest(sample_dataset):
    with tempfile.TemporaryDirectory() as tmp_dir:
        trainer = SklearnSupervisedTrainer(models_dir=tmp_dir)
        model_version, metrics = trainer.train_and_evaluate(
            examples=sample_dataset,
            algorithm="random_forest",
            test_size=0.25,
            random_state=42,
        )

        assert model_version.algorithm_name == "RandomForestClassifier"
        assert metrics["accuracy"] >= 0.75
        assert "feature_importances" in metrics
        assert len(metrics["feature_importances"]) == 5


def test_model_inference_service_probability_prediction(sample_dataset):
    with tempfile.TemporaryDirectory() as tmp_dir:
        trainer = SklearnSupervisedTrainer(models_dir=tmp_dir)
        model_version, _ = trainer.train_and_evaluate(
            examples=sample_dataset,
            algorithm="calibrated_logistic",
        )

        inference = ModelInferenceService(models_dir=tmp_dir)
        loaded = inference.load_model(model_version)
        assert loaded is True

        # Prueba con vector de alta afinidad (debe predecir MATCH con alta probabilidad)
        high_features = {
            "semantic_sim": 0.95,
            "lexical_sim": 0.90,
            "asymmetric_containment": 0.92,
            "structural_sim": 0.85,
            "keyword_overlap": 0.80,
        }
        res_match = inference.predict_pair(high_features)
        assert res_match is not None
        cls_match, score_match, probs_match = res_match
        assert cls_match == MatchClassification.MATCH
        assert score_match >= 0.70
        assert probs_match.get("MATCH", 0.0) >= 0.50

        # Prueba con vector dispar (debe predecir NO_MATCH)
        low_features = {
            "semantic_sim": 0.15,
            "lexical_sim": 0.05,
            "asymmetric_containment": 0.08,
            "structural_sim": 0.10,
            "keyword_overlap": 0.0,
        }
        res_nomatch = inference.predict_pair(low_features)
        assert res_nomatch is not None
        cls_nomatch, score_nomatch, probs_nomatch = res_nomatch
        assert cls_nomatch == MatchClassification.NO_MATCH
        assert score_nomatch <= 0.40
