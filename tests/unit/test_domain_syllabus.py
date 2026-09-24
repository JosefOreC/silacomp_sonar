"""
Pruebas unitarias para entidades de dominio Syllabus y SyllabusPage.
"""

from datetime import datetime
import pytest
from app.domain.syllabus import SectionType, Syllabus, SyllabusPage, SyllabusSection


def test_syllabus_page_valid() -> None:
    page = SyllabusPage(page_number=1, raw_text="Contenido de prueba", character_count=19)
    assert page.page_number == 1
    assert page.character_count == 19


def test_syllabus_page_invalid_number() -> None:
    with pytest.raises(ValueError, match="El número de página debe ser mayor o igual a 1"):
        SyllabusPage(page_number=0, raw_text="Error", character_count=5)


def test_syllabus_is_digitally_readable() -> None:
    p1 = SyllabusPage(page_number=1, raw_text="A" * 100, character_count=100)
    p2 = SyllabusPage(page_number=2, raw_text="B" * 60, character_count=60)
    
    syllabus = Syllabus(
        id="syl-001",
        filename="silabo.pdf",
        file_path="/tmp/silabo.pdf",
        file_size_bytes=1024,
        sha256_hash="abc123hash",
        total_pages=2,
        created_at=datetime.now(),
        pages=[p1, p2],
    )

    assert syllabus.total_characters == 160
    assert syllabus.is_digitally_readable(min_characters=150) is True
    assert syllabus.is_digitally_readable(min_characters=200) is False
    assert "A" * 100 in syllabus.full_extracted_text
