"""
Pruebas de integración para los nuevos endpoints de la Fase 1.5:
- Streaming del PDF original: GET /api/syllabi/{id}/pdf
- Catálogo de evidencias espaciales: GET /api/comparisons/{id}/evidence
- Detalle espacial unitario: GET /api/comparisons/{id}/matches/{match_id}/evidence
"""

from fastapi.testclient import TestClient
import pytest
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_pdf_streaming_and_evidence_endpoints(client: TestClient, sample_digital_pdf: str) -> None:
    # 1. Subir Sílabo Objetivo
    with open(sample_digital_pdf, "rb") as f:
        res_obj = client.post(
            "/api/syllabi/upload",
            files={"file": ("obj_fase15.pdf", f, "application/pdf")},
            data={"course_name": "Base de Datos I"},
        )
    assert res_obj.status_code == 201
    obj_id = res_obj.json()["id"]

    # 2. Subir Sílabo Comparado
    with open(sample_digital_pdf, "rb") as f:
        res_cmp = client.post(
            "/api/syllabi/upload",
            files={"file": ("cmp_fase15.pdf", f, "application/pdf")},
            data={"course_name": "Sistemas de Bases de Datos"},
        )
    assert res_cmp.status_code == 201
    cmp_id = res_cmp.json()["id"]

    # 3. Probar GET /api/syllabi/{id}/pdf (Streaming no destructivo)
    res_pdf_stream = client.get(f"/api/syllabi/{obj_id}/pdf")
    assert res_pdf_stream.status_code == 200
    assert "application/pdf" in res_pdf_stream.headers["content-type"]
    assert len(res_pdf_stream.content) > 0

    # 4. Probar 404 para ID inexistente
    res_not_found = client.get("/api/syllabi/SYL-NONEXISTENT/pdf")
    assert res_not_found.status_code == 404

    # 5. Ejecutar Comparación con cálculo de regiones espaciales
    res_comp = client.post(
        "/api/comparisons",
        json={
            "objective_syllabus_id": obj_id,
            "compared_syllabus_id": cmp_id,
        },
    )
    assert res_comp.status_code == 201
    comp_id = res_comp.json()["id"]
    matches = res_comp.json()["matches"]
    assert len(matches) > 0

    # Verificar que el match tiene regiones de evidencia
    first_match = matches[0]
    assert "evidence" in first_match
    assert "objective_regions" in first_match["evidence"]
    assert len(first_match["evidence"]["objective_regions"]) > 0
    first_reg = first_match["evidence"]["objective_regions"][0]
    assert first_reg["page_width"] > 0
    assert first_reg["page_height"] > 0

    # 6. Consultar catálogo de evidencias espaciales GET /api/comparisons/{id}/evidence
    res_ev_cat = client.get(f"/api/comparisons/{comp_id}/evidence")
    assert res_ev_cat.status_code == 200
    cat_data = res_ev_cat.json()
    assert cat_data["comparison_id"] == comp_id
    assert cat_data["total_matches"] > 0
    assert len(cat_data["evidence_items"]) > 0

    # 7. Consultar detalle de evidencia unitario GET /api/comparisons/{id}/matches/{match_id}/evidence
    match_id = first_match["id"]
    res_single_ev = client.get(f"/api/comparisons/{comp_id}/matches/{match_id}/evidence")
    assert res_single_ev.status_code == 200
    single_data = res_single_ev.json()
    assert single_data["match_id"] == match_id
    assert len(single_data["objective_regions"]) > 0
    assert single_data["objective_regions"][0]["x1"] > single_data["objective_regions"][0]["x0"]
