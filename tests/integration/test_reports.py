"""
Pruebas de generación y descarga de informes formales (HTML y PDF).
"""

from datetime import datetime
import os
from fastapi.testclient import TestClient
import pytest

from app.domain.comparison import Comparison, ContentMatch, MatchClassification, MatchEvidence, ScoreBreakdown
from app.domain.syllabus import Syllabus
from app.infrastructure.reports.html_report_generator import HtmlReportGenerator, DISCLAIMER_TEXT
from app.infrastructure.reports.pdf_report_generator import PdfReportGenerator
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_html_report_generator_direct() -> None:
    now = datetime.now()
    obj_syl = Syllabus(
        id="OBJ-01",
        filename="silabo_obj.pdf",
        file_path="uploads/silabo_obj.pdf",
        file_size_bytes=1024,
        sha256_hash="hash_obj",
        total_pages=3,
        created_at=now,
        course_name="Base de Datos I",
        course_code="INF-201",
        university="Universidad Nacional de Ingeniería",
    )
    cmp_syl = Syllabus(
        id="CMP-01",
        filename="silabo_cmp.pdf",
        file_path="uploads/silabo_cmp.pdf",
        file_size_bytes=2048,
        sha256_hash="hash_cmp",
        total_pages=4,
        created_at=now,
        course_name="Bases de Datos Relacionales",
        course_code="CC-302",
        university="Pontificia Universidad Católica del Perú",
    )

    match = ContentMatch(
        id="MATCH-1",
        comparison_id="COMP-01",
        objective_item_id="ITEM-OBJ-1",
        compared_item_id="ITEM-CMP-1",
        objective_title="Normalización de Bases de Datos",
        compared_title="Formas Normales 1FN, 2FN, 3FN y BCNF",
        objective_section="UNIDAD III",
        compared_section="CAPÍTULO 4",
        objective_page=2,
        compared_page=3,
        score_breakdown=ScoreBreakdown(
            semantic_similarity=0.91,
            lexical_similarity=0.82,
            keyword_overlap=0.88,
            structural_similarity=0.90,
            composite_score=0.88,
            weights={"semantic": 0.4, "lexical": 0.3, "keyword": 0.15, "structural": 0.15},
        ),
        classification=MatchClassification.MATCH,
        evidence=MatchEvidence(
            evidence_type="SEMANTIC_AND_KEYWORD",
            shared_keywords=["normalizacion", "1fn", "2fn", "3fn"],
            semantic_score=0.91,
            lexical_score=0.82,
            objective_snippet="Se estudian las formas normales hasta Boyce-Codd.",
            compared_snippet="Análisis de dependencias funcionales y BCNF.",
            objective_page=2,
            compared_page=3,
        ),
    )

    comparison = Comparison(
        id="COMP-01",
        objective_syllabus_id="OBJ-01",
        compared_syllabus_id="CMP-01",
        global_score=0.88,
        objective_coverage=0.90,
        compared_coverage=0.85,
        model_version="heuristic-v1.0",
        created_at=now,
        matches=[match],
        unmatched_objective=[],
        unmatched_compared=[],
    )

    html = HtmlReportGenerator.generate_html(comparison, obj_syl, cmp_syl)

    assert "Base de Datos I" in html
    assert "Bases de Datos Relacionales" in html
    assert "DISCLAIMER_TEXT" not in html
    assert "pre-evaluaci" in html
    assert "Normalizaci" in html
    assert "@media print" in html


def test_pdf_report_generator_direct(tmp_path: str) -> None:
    now = datetime.now()
    obj_syl = Syllabus(
        id="OBJ-02",
        filename="obj2.pdf",
        file_path="uploads/obj2.pdf",
        file_size_bytes=1000,
        sha256_hash="hash2",
        total_pages=2,
        created_at=now,
        course_name="Algoritmos y Estructuras de Datos",
        university="UNI",
    )
    cmp_syl = Syllabus(
        id="CMP-02",
        filename="cmp2.pdf",
        file_path="uploads/cmp2.pdf",
        file_size_bytes=1200,
        sha256_hash="hash3",
        total_pages=2,
        created_at=now,
        course_name="Estructuras de Datos Avanzadas",
        university="UNMSM",
    )

    comparison = Comparison(
        id="COMP-TEST-PDF",
        objective_syllabus_id="OBJ-02",
        compared_syllabus_id="CMP-02",
        global_score=0.76,
        objective_coverage=0.80,
        compared_coverage=0.75,
        model_version="heuristic-v1.0",
        created_at=now,
        matches=[],
        unmatched_objective=[],
        unmatched_compared=[],
    )

    gen = PdfReportGenerator(output_dir=str(tmp_path))
    report = gen.generate(comparison, obj_syl, cmp_syl)

    assert os.path.exists(report.file_path)
    assert os.path.getsize(report.file_path) > 1000


def test_api_report_endpoints(client: TestClient, sample_digital_pdf: str) -> None:
    with open(sample_digital_pdf, "rb") as f:
        res_obj = client.post(
            "/api/syllabi/upload",
            files={"file": ("obj_rep.pdf", f, "application/pdf")},
            data={"course_name": "Curso A"},
        )
    obj_id = res_obj.json()["id"]

    with open(sample_digital_pdf, "rb") as f:
        res_cmp = client.post(
            "/api/syllabi/upload",
            files={"file": ("cmp_rep.pdf", f, "application/pdf")},
            data={"course_name": "Curso B"},
        )
    cmp_id = res_cmp.json()["id"]

    res_comp = client.post(
        "/api/comparisons",
        json={"objective_syllabus_id": obj_id, "compared_syllabus_id": cmp_id},
    )
    comp_id = res_comp.json()["id"]

    res_html = client.get(f"/api/comparisons/{comp_id}/report/html")
    assert res_html.status_code == 200
    assert "text/html" in res_html.headers["content-type"]
    assert "Informe de Comparaci" in res_html.text

    res_pdf = client.get(f"/api/comparisons/{comp_id}/report/pdf")
    assert res_pdf.status_code == 200
    assert "application/pdf" in res_pdf.headers["content-type"]
    assert len(res_pdf.content) > 1000