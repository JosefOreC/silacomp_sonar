"""
Pruebas unitarias para el servicio de localización espacial PyMuPDF (Fase 1.5).
"""

from app.infrastructure.pdf.spatial_locator import SpatialLocatorService


def test_locate_regions_found(sample_digital_pdf: str) -> None:
    service = SpatialLocatorService()
    regions = service.locate_regions_for_item(
        pdf_path=sample_digital_pdf,
        match_id="MATCH-TEST-01",
        syllabus_id="SYL-TEST-01",
        content_id="ITEM-01",
        page_number=2,
        title="MODELO RELACIONAL",
        snippet="Semana 1: Conceptos de tablas, tuplas, atributos",
        keywords=["tablas", "tuplas"],
        evidence_type="COMBINED",
    )

    assert len(regions) > 0
    first = regions[0]
    assert first.match_id == "MATCH-TEST-01"
    assert first.page_number == 2
    assert first.page_width > 0
    assert first.page_height > 0
    assert first.x1 > first.x0
    assert first.y1 > first.y0
    assert first.evidence_type == "COMBINED"


def test_locate_regions_nonexistent_pdf() -> None:
    service = SpatialLocatorService()
    regions = service.locate_regions_for_item(
        pdf_path="nonexistent_file.pdf",
        match_id="MATCH-01",
        syllabus_id="SYL-01",
        content_id="ITEM-01",
        page_number=1,
        title="No title",
        snippet="No snippet",
    )
    assert regions == []


def test_locate_regions_out_of_bounds_page(sample_digital_pdf: str) -> None:
    service = SpatialLocatorService()
    regions = service.locate_regions_for_item(
        pdf_path=sample_digital_pdf,
        match_id="MATCH-01",
        syllabus_id="SYL-01",
        content_id="ITEM-01",
        page_number=99,
        title="No title",
        snippet="No snippet",
    )
    assert regions == []
