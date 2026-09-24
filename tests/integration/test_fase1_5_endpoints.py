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


def test_complete_fase_1_5_e2e_flow(client: TestClient, sample_digital_pdf: str) -> None:
    """
    TASK-18.2: Prueba automatizada E2E del ciclo de vida integral de Fase 1.5:
    1. Carga de sílabos con PDFs digitales.
    2. Comparación automática con detección espacial de Bounding Boxes.
    3. Descarga de streaming de PDFs para visualizador pericial.
    4. Consulta y validación de evidencias con coordenadas espaciales.
    5. Dictamen docente desde el visor pericial (Revisión humana inmutable).
    6. Generación de informes formal HTML y PDF conteniendo trazabilidad espacial.
    """
    # 1. Cargar sílabos
    with open(sample_digital_pdf, "rb") as f:
        res_obj = client.post(
            "/api/syllabi/upload",
            files={"file": ("silabo_fase15_e2e_obj.pdf", f, "application/pdf")},
            data={"course_name": "Redes de Computadoras I", "university": "Universidad A"},
        )
    assert res_obj.status_code == 201
    obj_id = res_obj.json()["id"]

    with open(sample_digital_pdf, "rb") as f:
        res_cmp = client.post(
            "/api/syllabi/upload",
            files={"file": ("silabo_fase15_e2e_cmp.pdf", f, "application/pdf")},
            data={"course_name": "Redes Avanzadas", "university": "Universidad B"},
        )
    assert res_cmp.status_code == 201
    cmp_id = res_cmp.json()["id"]

    # 2. Ejecutar comparación
    res_comp = client.post(
        "/api/comparisons",
        json={"objective_syllabus_id": obj_id, "compared_syllabus_id": cmp_id},
    )
    assert res_comp.status_code == 201
    comp_data = res_comp.json()
    comp_id = comp_data["id"]
    matches = comp_data["matches"]
    assert len(matches) > 0

    first_match = matches[0]
    match_id = first_match["id"]

    # 3. Validar streaming de PDF para visor doble
    pdf_obj_stream = client.get(f"/api/syllabi/{obj_id}/pdf")
    assert pdf_obj_stream.status_code == 200
    assert len(pdf_obj_stream.content) > 0

    pdf_cmp_stream = client.get(f"/api/syllabi/{cmp_id}/pdf")
    assert pdf_cmp_stream.status_code == 200
    assert len(pdf_cmp_stream.content) > 0

    # 4. Validar trazabilidad espacial
    res_evidence = client.get(f"/api/comparisons/{comp_id}/matches/{match_id}/evidence")
    assert res_evidence.status_code == 200
    ev_data = res_evidence.json()
    assert ev_data["match_id"] == match_id
    assert len(ev_data["objective_regions"]) > 0
    assert ev_data["objective_regions"][0]["page_width"] > 0
    assert ev_data["objective_regions"][0]["page_height"] > 0

    # 5. Dictamen pericial desde el visor (revisión humana)
    res_rev = client.post(
        "/api/reviews",
        json={
            "comparison_id": comp_id,
            "match_id": match_id,
            "prediction_before": first_match["classification"],
            "human_decision": "MATCH",
            "correction_type": "CONFIRMED",
            "justification": "Evidencia espacial verificada en visor pericial: coincide con el temario oficial.",
            "reviewer_id": "PERITO_ACADEMICO_FASE15",
        },
    )
    assert res_rev.status_code == 201

    # 6. Generación de informes formales con trazabilidad espacial
    res_html = client.get(f"/api/comparisons/{comp_id}/report/html")
    assert res_html.status_code == 200
    assert "Trazabilidad Espacial" in res_html.text

    res_pdf = client.get(f"/api/comparisons/{comp_id}/report/pdf")
    assert res_pdf.status_code == 200
    assert "application/pdf" in res_pdf.headers["content-type"]
    assert len(res_pdf.content) > 1000

