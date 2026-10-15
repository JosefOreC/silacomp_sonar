"""
Pruebas de integración de endpoints REST para la API de FastAPI.
"""

from fastapi.testclient import TestClient
import pytest

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["phase"] == 3
    assert data["version"] == client.get("/openapi.json").json()["info"]["version"]


def test_upload_digital_and_scanned_pdf(client: TestClient, sample_digital_pdf: str, blank_scanned_pdf: str) -> None:
    # 1. Cargar PDF digital válido
    with open(sample_digital_pdf, "rb") as f:
        res = client.post(
            "/api/syllabi/upload",
            files={"file": ("silabo_valido.pdf", f, "application/pdf")},
            data={"university": "UNI", "course_name": "Base de Datos I", "course_code": "INF-201"},
        )
    assert res.status_code == 201
    data = res.json()
    assert data["filename"] == "silabo_valido.pdf"
    assert data["total_pages"] == 2
    assert data["university"] == "UNI"
    syl_id = data["id"]

    # Consultar ítems del sílabo
    res_items = client.get(f"/api/syllabi/{syl_id}/items")
    assert res_items.status_code == 200
    items = res_items.json()
    assert len(items) > 0

    # 2. Cargar PDF escaneado (sin texto) -> debe responder 422 con advertencia de OCR
    with open(blank_scanned_pdf, "rb") as f:
        res_scan = client.post(
            "/api/syllabi/upload",
            files={"file": ("escaneado.pdf", f, "application/pdf")},
        )
    assert res_scan.status_code == 422
    assert "OCR" in res_scan.json()["detail"] or "Fase 2" in res_scan.json()["detail"]


def test_full_comparison_and_review_flow(client: TestClient, sample_digital_pdf: str) -> None:
    # Subir Sílabo Objetivo
    with open(sample_digital_pdf, "rb") as f:
        res_obj = client.post(
            "/api/syllabi/upload",
            files={"file": ("obj.pdf", f, "application/pdf")},
            data={"course_name": "Base de Datos I"},
        )
    assert res_obj.status_code == 201
    obj_id = res_obj.json()["id"]

    # Subir Sílabo Comparado
    with open(sample_digital_pdf, "rb") as f:
        res_cmp = client.post(
            "/api/syllabi/upload",
            files={"file": ("cmp.pdf", f, "application/pdf")},
            data={"course_name": "Sistemas de Bases de Datos"},
        )
    assert res_cmp.status_code == 201
    cmp_id = res_cmp.json()["id"]

    # Ejecutar Comparación
    res_comp = client.post(
        "/api/comparisons",
        json={
            "objective_syllabus_id": obj_id,
            "compared_syllabus_id": cmp_id,
        },
    )
    assert res_comp.status_code == 201
    comp_data = res_comp.json()
    comp_id = comp_data["id"]
    assert comp_data["global_score"] > 0.60
    assert len(comp_data["matches"]) > 0

    # Consultar detalle por endpoint
    res_detail = client.get(f"/api/comparisons/{comp_id}")
    assert res_detail.status_code == 200
    assert res_detail.json()["id"] == comp_id

    # Consultar matches
    res_matches = client.get(f"/api/comparisons/{comp_id}/matches")
    assert res_matches.status_code == 200
    matches = res_matches.json()
    assert len(matches) > 0
    first_match = matches[0]

    # Registrar Revisión Humana
    res_rev = client.post(
        "/api/reviews",
        json={
            "comparison_id": comp_id,
            "match_id": first_match["id"],
            "prediction_before": first_match["classification"],
            "human_decision": "MATCH",
            "correction_type": "CONFIRMED",
            "justification": "Contenidos idénticos de álgebra y modelo relacional.",
            "reviewer_id": "DR_LOPEZ",
        },
    )
    assert res_rev.status_code == 201
    rev_data = res_rev.json()
    assert rev_data["human_decision"] == "MATCH"

    # Consultar Estadísticas del Dataset Staging
    res_stats = client.get("/api/dataset/statistics")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert stats["total_examples"] >= 1
