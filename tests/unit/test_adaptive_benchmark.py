"""Casos de regresión del benchmark adaptativo y sus límites de interpretación."""

import numpy as np
import pytest

from app.application.compare_syllabi import CompareSyllabiUseCase, DEFAULT_WEIGHTS
from app.application.dataset_service import DatasetService
from app.domain.comparison import MatchClassification
from app.domain.review import DatasetExample
from app.domain.scoring import DEFAULT_THRESHOLDS, adaptive_pair_score, classify_score
from app.infrastructure.ml.supervised_trainer import SklearnSupervisedTrainer
from app.infrastructure.nlp.vector_service import NlpVectorService


@pytest.mark.parametrize("semantic,lexical,keyword,structural,score,classification", [
    (0.90, 0.10, 0.0, 0.0, 0.80, MatchClassification.MATCH),
    (0.10, 0.90, 0.0, 0.0, 0.80, MatchClassification.MATCH),
    (0.60, 0.45, 0.80, 0.80, 0.595, MatchClassification.PARTIAL_MATCH),
    (0.55, 0.40, 0.80, 0.80, 0.5675, MatchClassification.UNCERTAIN),
    (0.10, 0.10, 0.0, 0.0, 0.075, MatchClassification.NO_MATCH),
])
def test_shared_scoring_preserves_adaptive_weights_and_thresholds(
    semantic, lexical, keyword, structural, score, classification,
) -> None:
    actual, breakdown = adaptive_pair_score(semantic, lexical, keyword, structural, DEFAULT_WEIGHTS)
    assert actual == pytest.approx(score)
    assert classify_score(actual, DEFAULT_THRESHOLDS) == classification
    # El comparador debe conservar puntuaciones y desglose al reutilizar las reglas del dominio.
    use_case = CompareSyllabiUseCase(NlpVectorService())
    assert use_case._compute_pair_score(semantic, lexical, keyword, structural, DEFAULT_WEIGHTS) == (actual, breakdown)


def test_benchmark_uses_adaptive_floors_and_does_not_count_containment_twice() -> None:
    # Orden: semántica, léxica, contención, estructura, palabras clave.
    X = np.array([
        [0.90, 0.10, 0.0, 0.0, 0.0],  # Piso de equivalencia semántica.
        [0.10, 0.10, 0.95, 0.0, 0.0],  # Contención aislada no es un segundo voto léxico.
        [0.60, 0.45, 0.0, 0.80, 0.80],
        [0.55, 0.40, 0.0, 0.80, 0.80],  # UNCERTAIN se integra en la clase parcial.
    ])
    np.testing.assert_array_equal(
        SklearnSupervisedTrainer._compute_heuristic_baseline_predictions(X), [2, 0, 1, 1],
    )


def test_custom_weights_and_affinity_guard_are_preserved() -> None:
    weights = {"semantic": 0.0, "lexical": 0.0, "keyword": 0.0, "structural": 1.0}
    score, breakdown = adaptive_pair_score(0.0, 0.0, 0.0, 1.0, weights)
    assert score == 1.0
    assert weights == breakdown.weights
    assert classify_score(score, DEFAULT_THRESHOLDS, content_affinity=False) == MatchClassification.UNCERTAIN


def test_feature_matrix_preserves_adaptive_boundary_for_benchmark() -> None:
    example = DatasetExample(
        id="BOUNDARY", review_id="REV-BOUNDARY", objective_item_id="OBJ", compared_item_id="CMP",
        objective_text="A", compared_text="B", ground_truth_label="MATCH",
        features={"semantic_sim": 0.74, "lexical_sim": 0.70, "keyword_overlap": 0.95, "structural_sim": 0.0},
    )
    X, _, _ = DatasetService(None).extract_feature_matrix([example])
    assert SklearnSupervisedTrainer._compute_heuristic_baseline_predictions(X).tolist() == [2]
