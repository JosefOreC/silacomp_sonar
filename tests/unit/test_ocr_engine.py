"""
Pruebas unitarias para el motor OCR y la extracción de PDFs escaneados (Fase 2.0).
"""

import os
import tempfile
import pymupdf as fitz
import pytest

from app.domain.exceptions import InsufficientDigitalTextError
from app.infrastructure.ocr.rapid_ocr_engine import RapidOcrEngine
from app.infrastructure.pdf.extractor import PyMuPdfExtractor


@pytest.fixture
def synthetic_scanned_pdf() -> str:
    """
    Genera un archivo PDF sintético 100% rasterizado (escaneado puro, sin capa de texto digital).
    """
    # 1. Crear documento fuente y renderizar a imagen rasterizada
    doc_src = fitz.open()
    page_src = doc_src.new_page(width=595, height=842)
    page_src.insert_text((50, 100), "UNIVERSIDAD NACIONAL DE INGENIERIA", fontsize=16)
    page_src.insert_text((50, 140), "SILABO DE ESTRUCTURAS DISCRETAS", fontsize=14)
    page_src.insert_text((50, 180), "UNIDAD I: TEORIA DE CONJUNTOS Y RELACIONES", fontsize=12)
    page_src.insert_text((50, 210), "Operaciones con conjuntos, relaciones de equivalencia y orden parcial.", fontsize=11)
    
    pix = page_src.get_pixmap(dpi=150)
    img_bytes = pix.tobytes("png")
    doc_src.close()

    # 2. Insertar únicamente la imagen sin capa vectorial de texto
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    doc_dest = fitz.open()
    page_dest = doc_dest.new_page(width=595, height=842)
    page_dest.insert_image(page_dest.rect, stream=img_bytes)
    doc_dest.save(pdf_path)
    doc_dest.close()

    # Verificar que el PDF efectivamente no tiene capa de texto digital nativo
    doc_verify = fitz.open(pdf_path)
    assert doc_verify[0].get_text("text").strip() == ""
    doc_verify.close()

    yield pdf_path

    if os.path.exists(pdf_path):
        os.remove(pdf_path)


def test_rapid_ocr_engine_extract_page(synthetic_scanned_pdf: str) -> None:
    """Verifica que RapidOcrEngine extrae texto y coordenadas tipográficas a 72 DPI de un PDF escaneado."""
    engine = RapidOcrEngine(default_dpi=150)
    full_text, blocks, pw, ph = engine.extract_page_ocr(synthetic_scanned_pdf, page_number=1)

    assert pw == 595.0
    assert ph == 842.0
    assert len(blocks) > 0
    assert "ESTRUCTURAS" in full_text or "CONJUNTOS" in full_text or "UNIVERSIDAD" in full_text

    # Validar que los cuadros delimitadores son válidos en el sistema tipográfico
    for b in blocks:
        assert b.confidence > 0.0
        assert 0.0 <= b.x0 < b.x1 <= pw
        assert 0.0 <= b.y0 < b.y1 <= ph


def test_pymupdf_extractor_with_ocr(synthetic_scanned_pdf: str) -> None:
    """Verifica que PyMuPdfExtractor activa el fallback de OCR para un PDF escaneado y crea la capa indexable."""
    engine = RapidOcrEngine()
    extractor = PyMuPdfExtractor(min_digital_characters=30, ocr_engine=engine)

    syllabus = extractor.extract_from_pdf(
        file_path=synthetic_scanned_pdf,
        syllabus_id="syl-ocr-01",
        filename="scanned_syllabus.pdf",
        enable_ocr=True,
    )

    assert syllabus.id == "syl-ocr-01"
    assert syllabus.is_scanned is True
    assert syllabus.ocr_applied is True
    assert syllabus.ocr_engine_name == "RapidOcrEngine"
    assert len(syllabus.pages) == 1
    assert syllabus.pages[0].is_ocr is True
    assert syllabus.total_characters >= 30

    # Verificar que tras el proceso, el PDF posee una capa de texto indexable
    doc_check = fitz.open(synthetic_scanned_pdf)
    extracted_text = doc_check[0].get_text("text")
    assert len(extracted_text.strip()) > 0
    doc_check.close()


def test_pymupdf_extractor_scanned_without_ocr_raises_error(synthetic_scanned_pdf: str) -> None:
    """Verifica que si no hay motor OCR o enable_ocr=False, se produce InsufficientDigitalTextError."""
    extractor = PyMuPdfExtractor(min_digital_characters=50, ocr_engine=None)
    with pytest.raises(InsufficientDigitalTextError, match="Fase 2"):
        extractor.extract_from_pdf(
            file_path=synthetic_scanned_pdf,
            syllabus_id="syl-fail",
            filename="fail.pdf",
            enable_ocr=False,
        )
