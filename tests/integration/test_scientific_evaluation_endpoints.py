"""Snapshots, replay completo, reserva de grupos y promoción sin activación."""

from dataclasses import replace
from datetime import datetime
from pathlib import Path
import sqlite3

from fastapi.testclient import TestClient
import joblib
import pytest
from sklearn.tree import DecisionTreeClassifier

from app.api.deps import get_vector_service, get_model_repository, get_scientific_repository, get_syllabus_repository, get_comparison_repository
from app.domain.academic_sources import academic_source_tokens
from app.domain.model_version import ModelVersion
from app.domain.review import DatasetExample
from app.domain.scoring import BASELINE_VERSION
from app.infrastructure.ml.comparison_evaluation_engine import ComparisonEvaluationEngine
from app.main import app
from app.settings import data_dir
from tests.integration.test_ground_truth_endpoints import seed_comparison, review


class ControlledVectors:
    """Matriz deliberadamente adversa: scores bajos en diagonal, altos fuera de diagonal."""
    def encode_texts(self, texts):
        return None

    @staticmethod
    def _diagonal(a, b):
        return ("alpha" in a.lower()) == ("alpha" in b.lower())

    def compute_semantic_similarity(self, a, b):
        return .4 if self._diagonal(a, b) else .9

    def compute_lexical_similarity(self, a, b):
        return .25 if self._diagonal(a, b) else .9

    def compute_keyword_overlap(self, a, b):
        return .15 if self._diagonal(a, b) else .9

    def compute_structural_similarity(self, **kwargs):
        return 0.0

    def extract_shared_keywords(self, a, b):
        return []


@pytest.fixture
def client():
    app.dependency_overrides[get_vector_service] = lambda: ControlledVectors()
    yield TestClient(app)
    app.dependency_overrides.pop(get_vector_service, None)


def annotate_complete(client, group):
    comparison = seed_comparison(group, size=2)
    repo = get_syllabus_repository()
    for role, syl in (("Origen", comparison.objective_syllabus_id), ("Destino", comparison.compared_syllabus_id)):
        items = repo.get_content_items(syl)
        repo.save_content_items([replace(item, title=f"{role}{marker}", text=f"{role}{marker} contenido cohorte{group}",
                                         normalized_text=f"{role}{marker} contenido cohorte{group}") for item, marker in zip(items, ("alpha", "beta"))])
    for obj in range(2):
        for cmp in range(2):
            for author in ("A", "B"):
                response = client.post("/api/reviews", json={
                    "comparison_id": comparison.id, "reviewer_id": author, "human_decision": "MATCH" if obj == cmp else "NO_MATCH",
                    "correction_type": "MANUAL_LINK", "justification": "Anotación exhaustiva del par para evaluación",
                    "manual_objective_item_id": f"OBJ-{group}-{obj}", "manual_compared_item_id": f"CMP-{group}-{cmp}",
                })
                assert response.status_code == 201, response.text
    return comparison


def register_candidate(version="candidate-1", contaminated=None):
    clf = DecisionTreeClassifier(random_state=42).fit([[.4, .25, .25, 0, .15], [.9, .9, .9, 0, .9]], [2, 0])
    path = data_dir() / "models" / f"{version}.joblib"
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": clf}, path)
    ex = DatasetExample("T", "TR", "TRAIN-O", "TRAIN-C", "Tema de entrenamiento", "Otro tema de entrenamiento",
                        source_university_obj="Training-Uni", source_course_obj="TC", source_syllabus_obj="TRAIN-SYL",
                        source_university_cmp="Training-Partner", source_course_cmp="TP", source_syllabus_cmp="TRAIN-CMP")
    tokens = academic_source_tokens(ex) if contaminated is None else contaminated
    model = ModelVersion(version, "DecisionTreeClassifier", "Fixture controlado", {}, {}, False, datetime.now(),
                         metrics={"data_provenance_schema": 2, "data_source_tokens": tokens}, artifact_path=str(path))
    get_model_repository().save(model)
    return model


def snapshot(client, ids):
    response = client.post("/api/evaluation/snapshots", json={"name": "Conjunto reservado", "comparison_ids": ids})
    assert response.status_code == 201, response.text
    return response.json()


def experiment(client, identity, candidate="candidate-1"):
    return client.post("/api/evaluation/experiments", json={"snapshot_id": identity, "candidate_version": candidate})


def test_full_replay_is_repeatable_promotes_improvement_and_preserves_live_data(client):
    comparisons = [annotate_complete(client, group) for group in (1, 2)]
    original = [get_comparison_repository().get_by_id(c.id) for c in comparisons]
    register_candidate()
    held = snapshot(client, [c.id for c in comparisons])
    assert held["independent_groups"] == 2
    assert held["pair_count"] == 8
    first = experiment(client, held["id"])
    assert first.status_code == 201, first.text
    report = first.json()["report"]
    assert report["evaluations"]["reference"]["aggregate"]["f1"] == 0
    assert report["evaluations"]["candidate"]["aggregate"]["f1"] == 1
    assert report["promotion_recommended"] is True
    assert report["automatic_activation"] is False
    assert client.get("/api/models/active").json()["version_id"] == BASELINE_VERSION
    # Cambiar revisiones vivas no reescribe el gold congelado ni el replay.
    review(client, comparisons[0].matches[0], "A", "NO_MATCH")
    second = experiment(client, held["id"])
    assert second.status_code == 201, second.text
    assert second.json()["report"] == report
    assert client.get(f"/api/evaluation/experiments/{first.json()['id']}").json() == first.json()
    assert [get_comparison_repository().get_by_id(c.id) for c in comparisons] == original
    exported = client.get(f"/api/evaluation/snapshots/{held['id']}/export").json()
    assert len(exported["payload"]["cases"][0]["labels"]) == 4
    assert exported["payload"]["cases"][0]["nlp_trace"]
    repository = get_scientific_repository()
    with pytest.raises(sqlite3.IntegrityError):
        repository.save_snapshot(repository.get_snapshot(held["id"]))
    with pytest.raises(sqlite3.IntegrityError):
        repository.save_experiment(repository.get_experiment(first.json()["id"]))


def test_snapshot_rejects_partial_matrix_and_reservation_blocks_training(client):
    comp = seed_comparison(3, size=2)
    bad = client.post("/api/evaluation/snapshots", json={"name": "Incompleto", "comparison_ids": [comp.id]})
    assert bad.status_code == 409
    assert "matriz completa" in bad.json()["detail"]
    assert client.get("/api/evaluation/snapshots").json() == []
    complete = annotate_complete(client, 4)
    snapshot(client, [complete.id])
    response = client.post("/api/models/train", json={"use_bootstrap": True})
    assert response.status_code == 400
    assert "reservados" in response.json()["detail"]
    # Otros grupos siguen siendo entrenables; la reserva no se limita a IDs de revisión.
    for group in (10, 11, 12):
        comparison = seed_comparison(group, size=6)
        for index, match in enumerate(comparison.matches):
            review(client, match, "C", ["MATCH", "PARTIAL_MATCH", "NO_MATCH"][index % 3])
    trained = client.post("/api/models/train", json={"use_bootstrap": False})
    assert trained.status_code == 201, trained.text
    tokens = trained.json()["metrics"]["data_source_tokens"]
    assert not any(token == ["syllabus", "OBJ-SYL-4"] for token in tokens)


def test_contamination_artifact_loss_and_environment_change_are_explicit(client, monkeypatch):
    comp = annotate_complete(client, 5)
    held = snapshot(client, [comp.id])
    payload = get_scientific_repository().get_snapshot(held["id"]).payload
    register_candidate("contaminated", payload["reserved_source_tokens"])
    assert experiment(client, held["id"], "contaminated").status_code == 409
    model = register_candidate()
    Path(model.artifact_path).unlink()
    assert experiment(client, held["id"]).status_code == 409
    register_candidate()
    monkeypatch.setattr(ComparisonEvaluationEngine, "fingerprint", lambda self: {"changed": True})
    assert experiment(client, held["id"]).status_code == 409
    assert client.get("/api/evaluation/experiments").json() == []


def test_single_group_and_regression_cannot_recommend_promotion(client):
    comp = annotate_complete(client, 6)
    held = snapshot(client, [comp.id])
    register_candidate()
    result = experiment(client, held["id"])
    assert result.status_code == 201, result.text
    assert result.json()["report"]["promotion_recommended"] is False
    assert result.json()["report"]["checks"]["independent_groups"] is False
    reverse = client.post("/api/evaluation/experiments", json={"snapshot_id": held["id"],
                          "reference_version": "candidate-1", "candidate_version": BASELINE_VERSION})
    assert reverse.status_code == 201, reverse.text
    assert reverse.json()["report"]["promotion_recommended"] is False
    assert reverse.json()["report"]["regressions"][0]["f1_delta"] < 0


def test_changed_artifact_cannot_reuse_evaluated_version(client):
    comp = annotate_complete(client, 7)
    held = snapshot(client, [comp.id])
    model = register_candidate()
    first = experiment(client, held["id"])
    assert first.status_code == 201, first.text
    # Un artefacto válido pero distinto tampoco puede reutilizar la identidad.
    replacement = DecisionTreeClassifier(random_state=42).fit(
        [[.4, .25, .25, 0, .15], [.9, .9, .9, 0, .9]], [0, 2])
    joblib.dump({"model": replacement}, model.artifact_path)
    changed = experiment(client, held["id"])
    assert changed.status_code == 409, changed.text
    assert "experimento previo" in changed.json()["detail"]
    assert len(client.get("/api/evaluation/experiments").json()) == 1
    assert client.get(f"/api/evaluation/experiments/{first.json()['id']}").json() == first.json()


def test_missing_artifact_activation_preserves_active_model_and_clears_inference(client):
    from app.infrastructure.ml.model_inference_service import ModelInferenceService

    model = register_candidate()
    inference = ModelInferenceService()
    assert inference.load_model(model)
    assert inference.predict_pair({"semantic_sim": .4, "lexical_sim": .25, "keyword_overlap": .15}) is not None
    missing = replace(model, version_id="missing-version", artifact_path=str(data_dir() / "absent.joblib"))
    assert inference.load_model(missing) is False
    assert inference.predict_pair({}) is None

    get_model_repository().save(missing)
    before = client.get("/api/models/active").json()
    response = client.post(f"/api/models/{missing.version_id}/activate")
    assert response.status_code == 409, response.text
    assert client.get("/api/models/active").json() == before
