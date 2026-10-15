"""Cola, lotes persistidos y medición antes/después sin sobrescribir predicciones."""

from fastapi.testclient import TestClient
import pytest

from app.api.deps import get_comparison_repository, get_review_repository, get_db_manager
from app.main import app
from tests.integration.test_ground_truth_endpoints import seed_comparison, review


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_batch_lifecycle_keeps_selection_and_completion_immutable(client: TestClient) -> None:
    comp = seed_comparison(1)
    original_prediction = get_comparison_repository().get_by_id(comp.id)
    queue = client.get("/api/active-learning/queue?comparison_id=COMP-1&limit=1").json()
    assert queue["total"] == 3
    assert queue["coverage"]["total_pairs"] == 3
    assert queue["coverage"]["reviewed_pairs"] == 0
    created = client.post("/api/active-learning/batches", json={"comparison_id": comp.id, "reviewer_id": "B", "limit": 2})
    assert created.status_code == 201, created.text
    snapshot = created.json()["batch"]
    assert snapshot["reference_thresholds"] == {"match": .75, "partial": .58, "uncertain": .45}
    batch_id = snapshot["id"]
    selected = {case["match_id"] for case in snapshot["cases"]}
    assert len(selected) == 2
    for match in comp.matches:
        if match.id in selected:
            assert review(client, match, "B").status_code == 201
    progress = client.get(f"/api/active-learning/batches/{batch_id}").json()
    assert progress["batch"] == snapshot
    assert progress["coverage_current"]["reviewed_pairs"] == 2
    assert progress["coverage_current"]["consensus_pairs"] == 0
    assert progress["eligible_case_ids"] == []
    assert client.get("/api/active-learning/queue?reviewer_id=b").json()["total"] == 1
    for match in comp.matches:
        if match.id in selected:
            assert review(client, match, "A").status_code == 201
    closed = client.post(f"/api/active-learning/batches/{batch_id}/complete")
    assert closed.status_code == 200
    completion = closed.json()["completion"]
    assert completion["coverage_after"]["consensus_percentage"] == 100
    assert completion["scope_after"]["total_pairs"] == 3
    assert completion["scope_after"]["consensus_pairs"] == 2
    assert client.get("/api/active-learning/queue").json()["total"] == 1
    # Un cambio posterior no reescribe la medición al cerrar el lote.
    changed = next(m for m in comp.matches if m.id in selected)
    review(client, changed, "B", "NO_MATCH")
    reopened = client.post(f"/api/active-learning/batches/{batch_id}/complete").json()
    assert reopened["completion"] == completion
    assert reopened["coverage_current"]["consensus_pairs"] == 1
    assert client.get("/api/active-learning/batches").json()[0] == snapshot
    assert get_comparison_repository().get_by_id(comp.id) == original_prediction


def test_queue_filters_manual_pairs_and_second_reviewer_eligibility(client: TestClient) -> None:
    comp = seed_comparison(2)
    review(client, comp.matches[0], "A")
    review(client, comp.matches[1], "A")
    review(client, comp.matches[1], "B", "NO_MATCH")
    manual = {"comparison_id": comp.id, "reviewer_id": "A", "human_decision": "UNCERTAIN",
              "correction_type": "MANUAL_LINK", "justification": "Cruce manual para segunda revisión",
              "manual_objective_item_id": "OBJ-2-0", "manual_compared_item_id": "CMP-2-1"}
    assert client.post("/api/reviews", json=manual).status_code == 201
    queue = client.get("/api/active-learning/queue?reason=SECOND_REVIEW&reviewer_id=B").json()
    assert queue["total"] == 2
    assert queue["coverage"]["total_pairs"] == 4
    assert any(c["match_id"] is None and c["score"] is None for c in queue["items"])
    assert client.get("/api/active-learning/queue?reason=SECOND_REVIEW&reviewer_id=a").json()["total"] == 0
    disagreement = client.get("/api/active-learning/queue?reason=DISAGREEMENT&reviewer_id=a").json()
    assert disagreement["total"] == 1
    assert disagreement["items"][0]["match_id"] == comp.matches[1].id
    assert get_review_repository().count_examples() == 4


def test_empty_queue_and_invalid_requests(client: TestClient) -> None:
    empty = client.get("/api/active-learning/queue").json()
    assert empty["total"] == 0
    assert empty["coverage"]["reviewed_percentage"] is None
    assert client.post("/api/active-learning/batches", json={"reviewer_id": "A"}).status_code == 409
    assert client.post("/api/active-learning/batches", json={"reviewer_id": "  "}).status_code == 422
    assert client.get("/api/active-learning/queue?limit=0").status_code == 422
    assert client.get("/api/active-learning/queue?offset=-1").status_code == 422
    assert client.get("/api/active-learning/queue?reason=INVALID").status_code == 422
    assert client.get("/api/active-learning/queue?comparison_id=missing").status_code == 404
    assert client.get("/api/active-learning/batches/missing").status_code == 404
    assert client.post("/api/active-learning/batches/missing/complete").status_code == 404


def test_queue_pagination_and_source_loss_preserve_batch_snapshot(client: TestClient) -> None:
    comp = seed_comparison(3)
    all_ids = [case["case_id"] for case in client.get("/api/active-learning/queue").json()["items"]]
    pages = [client.get(f"/api/active-learning/queue?limit=1&offset={i}").json()["items"][0]["case_id"] for i in range(3)]
    assert pages == all_ids
    assert client.get("/api/active-learning/queue?offset=3").json()["items"] == []
    response = client.post("/api/active-learning/batches", json={"reviewer_id": "A", "comparison_id": comp.id})
    snapshot = response.json()["batch"]
    # Solo se elimina el fixture temporal; el lote debe denunciar la pérdida de su fuente.
    with get_db_manager().get_connection() as conn:
        conn.execute("DELETE FROM comparisons WHERE id = ?", (comp.id,))
    assert client.get(f"/api/active-learning/batches/{snapshot['id']}").status_code == 409
    assert client.post(f"/api/active-learning/batches/{snapshot['id']}/complete").status_code == 409
    assert client.get("/api/active-learning/batches").json()[0] == snapshot
