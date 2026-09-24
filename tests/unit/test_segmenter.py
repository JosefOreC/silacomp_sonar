"""
Pruebas unitarias para SyllabusSegmenter y ProcessSyllabusUseCase.
"""

from datetime import datetime
from app.application.process_syllabus import ProcessSyllabusUseCase
from app.domain.syllabus import SectionType, Syllabus, SyllabusPage
from app.infrastructure.nlp.segmenter import SyllabusSegmenter
from app.infrastructure.pdf.extractor import PyMuPdfExtractor


def test_syllabus_segmenter_identifies_sections_and_items() -> None:
    p1 = SyllabusPage(
        page_number=1,
        raw_text=(
            "I. SUMILLA\n"
            "El curso presenta los fundamentos de diseño y desarrollo de bases de datos.\n\n"
            "II. COMPETENCIAS\n"
            "- Modela entidades y relaciones complejas.\n\n"
            "III. UNIDAD I: MODELO RELACIONAL\n"
            "Semana 1: Tablas, claves primarias y claves foráneas.\n"
            "Semana 2: Álgebra relacional y operadores de reunión.\n\n"
            "IV. UNIDAD II: NORMALIZACIÓN\n"
            "Semana 3: Primera y segunda forma normal.\n"
            "Semana 4: Tercera forma normal 3FN.\n"
        ),
        character_count=400,
    )

    syllabus = Syllabus(
        id="OBJ-001",
        filename="bd1.pdf",
        file_path="/tmp/bd1.pdf",
        file_size_bytes=5000,
        sha256_hash="hash001",
        total_pages=1,
        created_at=datetime.now(),
        pages=[p1],
    )

    segmenter = SyllabusSegmenter()
    items = segmenter.segment(syllabus)

    assert len(syllabus.sections) >= 3
    section_types = [s.section_type for s in syllabus.sections]
    assert SectionType.SUMILLA in section_types
    assert SectionType.UNIT in section_types

    # Debe haber generado múltiples ContentItem
    assert len(items) >= 4
    # Verificar que las unidades y temas tienen asignada la página
    for item in items:
        assert item.page_start == 1
        assert item.page_end == 1
        assert len(item.normalized_text) > 0

    # Comprobar presencia de temas clave
    titles = " ".join(item.title for item in items).lower()
    assert "sumilla" in titles or "fundamentos" in titles
    assert "semana" in titles or "claves" in titles or "tablas" in titles


def test_process_syllabus_use_case_flow(sample_digital_pdf: str) -> None:
    extractor = PyMuPdfExtractor(min_digital_characters=50)
    segmenter = SyllabusSegmenter()
    use_case = ProcessSyllabusUseCase(extractor=extractor, segmenter=segmenter)

    syllabus, items = use_case.execute(
        file_path=sample_digital_pdf,
        syllabus_id="SYL-TEST-USECASE",
        filename="silabo_test.pdf",
        university="Universidad Nacional de Ingeniería",
        course_name="Base de Datos I",
        course_code="INF-201",
    )

    assert syllabus.id == "SYL-TEST-USECASE"
    assert syllabus.university == "Universidad Nacional de Ingeniería"
    assert syllabus.course_name == "Base de Datos I"
    assert len(items) > 0
    assert any("normalizaci" in item.title.lower() or "normalizaci" in item.text.lower() for item in items)
