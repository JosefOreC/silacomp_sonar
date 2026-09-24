"""
Pruebas unitarias para el extractor de PDFs con PyMuPDF.
"""

import os
import fitz  # PyMuPDF
import pytest
from app.domain.exceptions import InsufficientDigitalTextError, PdfValidationError
from app.infrastructure.pdf.extractor import PyMuPdfExtractor


def test_extract_digital_pdf_success(sample_digital_pdf: str) -> None:
    extractor = PyMuPdfExtractor(min_digital_characters=50)
    syllabus = extractor.extract_from_pdf(
        file_path=sample_digital_pdf,
        syllabus_id="syl-test-01",
        filename="sample_syllabus.pdf",
    )

    assert syllabus.id == "syl-test-01"
    assert syllabus.total_pages == 2
    assert len(syllabus.pages) == 2
    assert syllabus.pages[0].page_number == 1
    assert "SUMILLA" in syllabus.pages[0].raw_text
    assert syllabus.pages[1].page_number == 2
    assert "UNIDAD I: MODELO RELACIONAL" in syllabus.pages[1].raw_text
    assert syllabus.sha256_hash is not None
    assert len(syllabus.sha256_hash) == 64


def test_extract_scanned_pdf_raises_insufficient_digital_text(blank_scanned_pdf: str) -> None:
    extractor = PyMuPdfExtractor(min_digital_characters=100)
    with pytest.raises(InsufficientDigitalTextError, match="Fase 2"):
        extractor.extract_from_pdf(
            file_path=blank_scanned_pdf,
            syllabus_id="syl-scanned",
            filename="blank.pdf",
        )


def test_extract_non_existent_file() -> None:
    extractor = PyMuPdfExtractor()
    with pytest.raises(PdfValidationError, match="no existe"):
        extractor.extract_from_pdf(
            file_path="/tmp/non_existent_path.pdf",
            syllabus_id="syl-404",
            filename="404.pdf",
        )
