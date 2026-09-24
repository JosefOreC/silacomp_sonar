"""
Prueba de integración End-to-End (E2E) para la Fase 1 del sistema ConvComp.
Valida el ciclo de vida completo: Carga -> Extracción -> Segmentación -> Comparación NLP -> Reportes -> Revisión Humana -> Dataset.
"""

from fastapi.testclient import TestClient
import pytest
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_complete_e2e_system_flow(client: TestClient, sample_digital_pdf: str) -> None:
    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["phase"] == 1

    # 2. Cargar Sílabo Objetivo
    with open(sample_digital_pdf, "rb") as f:
        res_obj = client.post(
            "/api/syllabi/upload",
            files={"file": ("silabo_objetivo.pdf", f, "application/pdf")},
            data={
                "university": "Universidad Nacional de Ingeniería",
                "course_name": "Base de Datos I",
                "course_code": "INF-201",
            },
        )
    assert res_obj.status_code == 201
    obj_data = res_obj.json()
    obj_id = obj_data["id"]
    assert obj_data["total_pages"] == 2
    assert obj_data["total_characters"] > 150

    # 3. Cargar Sílabo Comparado
    with open(sample_digital_pdf, "rb") as f:
        res_cmp = client.post(
            "/api/syllabi/upload",
            files={"file": ("silabo_comparado.pdf", f, "application/pdf")},
            data={
                "university": "Pontificia Universidad Católica del Perú",
                "course_name": "Sistemas de Bases de Datos",
                "course_code": "CC-302",
            },
        )
    assert res_cmp.status_code == 201
    cmp_data = res_cmp.json()
    cmp_id = cmp_data["id"]

    # 4. Listar Sílabos Cargados
    res_list = client.get("/api/syllabi")
    assert res_list.status_code == 200
    all_syllabi = res_list.json()
    assert any(s["id"] == obj_id for s in all_syllabi)
    assert any(s["id"] == cmp_id for s in all_syllabi)

    # 5. Ejecutar Comparación Algorítmica Reproducible
    res_comp = client.post(
        "/api/comparisons",
        json={
            "objective_syllabus_id": obj_id,
            "compared_syllabus_id": cmp_id,
            "weights": {"semantic": 0.40, "lexical": 0.30, "keyword": 0.15, "structural": 0.15},
            "thresholds": {"match": 0.85, "partial": 0.70, "uncertain": 0.50},
        },
    )
    assert res_comp.status_code == 201
    comp = res_comp.json()
    comp_id = comp["id"]
    assert 0.0 <= comp["global_score"] <= 1.0
    assert 0.0 <= comp["objective_coverage"] <= 100.0
    assert 0.0 <= comp["compared_coverage"] <= 100.0
    assert len(comp["matches"]) > 0

    first_match = comp["matches"][0]
    assert first_match["objective_page"] >= 1
    assert first_match["compared_page"] >= 1
    assert first_match["score_breakdown"]["composite_score"] > 0
    assert first_match["evidence"]["evidence_type"] in ["LEXICAL", "SEMANTIC", "HYBRID"]

    # 6. Descarga y Verificación de Informes (PDF y HTML)
    res_pdf = client.get(f"/api/comparisons/{comp_id}/report/pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert len(res_pdf.content) > 1000

    res_html = client.get(f"/api/comparisons/{comp_id}/report/html")
    assert res_html.status_code == 200
    assert "text/html" in res_html.headers["content-type"]
    assert "Informe de Comparaci" in res_html.text
    # Verificación de cumplimiento: Disclaimer formal obligatorio
    assert "pre-evaluaci" in res_html.text

    # 7. Auditoría y Revisión Humana (Preservación de Inmutabilidad)
    original_classification = first_match["classification"]
    res_rev = client.post(
        "/api/reviews",
        json={
            "comparison_id": comp_id,
            "match_id": first_match["id"],
            "prediction_before": original_classification,
            "human_decision": "MATCH",
            "correction_type": "CONFIRMED",
            "justification": "Validación formal: Los temas de normalización y álgebra relacional coinciden.",
            "reviewer_id": "COMISION_ACADEMICA_E2E",
        },
    )
    assert res_rev.status_code == 201

    # Verificación de inmutabilidad: el match original en la BD no debe ser sobrescrito
    res_comp_after = client.get(f"/api/comparisons/{comp_id}")
    assert res_comp_after.status_code == 200
    match_after = [m for m in res_comp_after.json()["matches"] if m["id"] == first_match["id"]][0]
    assert match_after["classification"] == original_classification, "La predicción algorítmica original debe ser inmutable."

    # 8. Exportación y Estadísticas del Dataset de Calibración
    res_stats = client.get("/api/dataset/statistics")
    assert res_stats.status_code == 200
    stats = res_stats.json()
    assert stats["total_examples"] >= 1

    res_export = client.get("/api/dataset/export")
    assert res_export.status_code == 200
    export_data = res_export.json()
    assert len(export_data) >= 1
    assert "human_decision" in export_data[0]
    assert "prediction_before" in export_data[0]