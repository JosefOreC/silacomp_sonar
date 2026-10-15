"""Revisiones inmutables, consulta de consenso y entrenamiento trazable."""

import csv
from dataclasses import replace
from datetime import datetime
import io
import json
import sqlite3

from fastapi.testclient import TestClient
import pytest

from app.api.deps import get_comparison_repository, get_review_repository, get_syllabus_repository
from app.domain.comparison import Comparison, ContentMatch, MatchClassification as Label, MatchEvidence, ScoreBreakdown
from app.domain.content import ContentItem
from app.domain.syllabus import Syllabus
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def seed_comparison(group: int, size: int = 3) -> Comparison:
    repo = get_syllabus_repository()
    for role in ("OBJ", "CMP"):
        syllabus_id = f"{role}-SYL-{group}"
        repo.save(Syllabus(
            id=syllabus_id, filename="test.pdf", file_path="test.pdf", file_size_bytes=1,
            sha256_hash=f"{group}-{role}", total_pages=1, created_at=datetime.now(),
            university=f"University-{group}-{role}", course_code="CS-101",
        ))
        repo.save_content_items([ContentItem(
            id=f"{role}-{group}-{i}", syllabus_id=syllabus_id, section_name="Unidad", title=f"Tema {i}",
            text=f"Contenido {group} {role} {i}", normalized_text=f"contenido {group} {role} {i}",
            page_start=1, page_end=1, order=i,
        ) for i in range(size)])
    matches = []
    for i in range(size):
        score = [.9, .65, .1][i % 3]
        matches.append(ContentMatch(
            id=f"MATCH-{group}-{i}", comparison_id=f"COMP-{group}",
            objective_item_id=f"OBJ-{group}-{i}", compared_item_id=f"CMP-{group}-{i}",
            objective_title="Objetivo", compared_title="Comparado", objective_section="Unidad", compared_section="Unidad",
            objective_page=1, compared_page=1, classification=Label.MATCH,
            score_breakdown=ScoreBreakdown(score, score, score, .5, score, {}),
            evidence=MatchEvidence("HYBRID", [], score, score, f"Objetivo {group}-{i}", f"Comparado {group}-{i}", 1, 1),
        ))
    comp = Comparison(f"COMP-{group}", f"OBJ-SYL-{group}", f"CMP-SYL-{group}", .6, 100, 100, "baseline", datetime.now(), matches)
    get_comparison_repository().save(comp)
    return comp


def review(client: TestClient, match: ContentMatch, author: str, decision: str = "MATCH"):
    return client.post("/api/reviews", json={
        "comparison_id": match.comparison_id, "match_id": match.id, "reviewer_id": author,
        "prediction_before": "NO_MATCH", "human_decision": decision, "correction_type": "CONFIRMED",
        "justification": "Evidencia revisada por el docente",
    })


def test_ground_truth_lifecycle_filters_exports_and_original_prediction(client: TestClient) -> None:
    comp = seed_comparison(1)
    match = comp.matches[0]
    first = review(client, match, " Docente A ")
    assert first.status_code == 201
    assert first.json()["prediction_before"] == "MATCH"
    assert review(client, match, "docente a", "NO_MATCH").status_code == 201
    page = client.get("/api/dataset/ground-truth").json()
    assert page["summary"]["single_review_pairs"] == 1
    assert page["items"][0]["reviewer_count"] == 1
    assert review(client, match, "Docente B").status_code == 201
    assert client.get("/api/dataset/ground-truth?status=DISAGREEMENT").json()["total"] == 1
    assert review(client, match, "docente a").status_code == 201
    page = client.get("/api/dataset/ground-truth?comparison_id=COMP-1&status=CONSENSUS&limit=1").json()
    assert page["summary"]["consensus_pairs"] == 1
    assert page["items"][0]["review_count"] == 4
    assert page["items"][0]["consensus_label"] == "MATCH"
    assert client.get("/api/dataset/ground-truth?offset=1").json()["items"] == []
    agreement = client.get("/api/dataset/agreement?comparison_id=COMP-1").json()[0]
    assert agreement["common_pairs"] == 1
    assert agreement["observed_agreement"] == 1
    assert agreement["cohen_kappa"] is None
    exported = client.get("/api/dataset/ground-truth/export").json()
    assert len(exported) == 1
    assert len(exported[0]["votes"]) == 2
    assert exported[0]["features"]["semantic_sim"] == .9
    assert exported[0]["source_university_obj"] == "University-1-OBJ"
    assert exported[0]["source_page_obj"] == 1
    assert exported[0]["source_page_cmp"] == 1
    assert exported[0]["feature_source_review_id"]
    rows = list(csv.DictReader(io.StringIO(client.get("/api/dataset/ground-truth/export?format=csv").text)))
    assert json.loads(rows[0]["votes"])[0]["review_id"]
    assert client.get("/api/dataset/ground-truth?comparison_id=missing").status_code == 404
    assert client.get("/api/dataset/ground-truth?limit=0").status_code == 422
    assert client.get("/api/dataset/ground-truth?offset=-1").status_code == 422
    assert client.get("/api/dataset/ground-truth/export?format=xml").status_code == 422
    assert get_comparison_repository().get_by_id(comp.id).matches[0].classification == Label.MATCH


def test_review_events_and_dataset_rows_cannot_be_overwritten(client: TestClient) -> None:
    comp = seed_comparison(2)
    response = review(client, comp.matches[0], "A")
    repo = get_review_repository()
    original = repo.get_by_id(response.json()["id"])
    with pytest.raises(sqlite3.IntegrityError):
        repo.save(replace(original, human_decision=Label.NO_MATCH))
    example = repo.list_examples()[0]
    with pytest.raises(sqlite3.IntegrityError):
        repo.save_example(replace(example, ground_truth_label="NO_MATCH"))
    assert repo.get_by_id(original.id).human_decision == Label.MATCH
    assert repo.count_examples() == 1


def test_manual_review_requires_contents_from_correct_syllabi(client: TestClient) -> None:
    seed_comparison(3)
    payload = {"comparison_id": "COMP-3", "human_decision": "MATCH", "correction_type": "MANUAL_LINK",
               "justification": "Vinculación manual revisada", "reviewer_id": "A"}
    assert client.post("/api/reviews", json=payload).status_code == 422
    payload.update(manual_objective_item_id="CMP-3-0", manual_compared_item_id="OBJ-3-0")
    assert client.post("/api/reviews", json=payload).status_code == 422
    payload.update(manual_objective_item_id="OBJ-3-0", manual_compared_item_id="CMP-3-0")
    assert client.post("/api/reviews", json=payload).status_code == 201
    page = client.get("/api/dataset/ground-truth").json()
    assert page["items"][0]["objective_item_id"] == "OBJ-3-0"
    assert page["items"][0]["source_page_obj"] == 1
    payload["reviewer_id"] = "   "
    assert client.post("/api/reviews", json=payload).status_code == 422


def test_consensus_training_rejects_unresolved_reviews_instead_of_bootstrap(client: TestClient) -> None:
    comp = seed_comparison(4)
    review(client, comp.matches[0], "A")
    response = client.post("/api/models/train", json={"ground_truth_policy": "consensus", "use_bootstrap": True})
    assert response.status_code == 400
    assert "No hay pares consensuados" in response.json()["detail"]


def test_consensus_training_uses_one_example_per_pair_and_records_source_reviews(client: TestClient) -> None:
    source_ids = []
    for group in range(4):
        comp = seed_comparison(group, size=6)
        for index, match in enumerate(comp.matches):
            label = ["MATCH", "PARTIAL_MATCH", "NO_MATCH"][index % 3]
            for author in ("A", "B"):
                response = review(client, match, author, label)
                assert response.status_code == 201
                source_ids.append(response.json()["id"])
    response = client.post("/api/models/train", json={"ground_truth_policy": "consensus", "use_bootstrap": False})
    assert response.status_code == 201, response.text
    metrics = response.json()["metrics"]
    assert metrics["ground_truth_policy"] == "consensus"
    assert metrics["train_sample_count"] + metrics["test_sample_count"] == 24
    assert set(metrics["source_review_ids"]) == set(source_ids)
    assert metrics["split"]["evaluation_scope"] == "human_reviews"
    assert get_review_repository().count_examples() == 48
