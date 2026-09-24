"""
Pruebas de integración para repositorios de persistencia SQLite.
"""

from datetime import datetime
import os
import pytest

from app.domain.comparison import (
    Comparison,
    ContentMatch,
    MatchClassification,
    MatchEvidence,
    ScoreBreakdown,
    UnmatchedItem,
)
from app.domain.review import CorrectionType, Review
from app.domain.syllabus import SectionType, Syllabus, SyllabusPage, SyllabusSection
from app.infrastructure.persistence.database import DatabaseManager
from app.infrastructure.persistence.sqlite_comparison_repository import SqliteComparisonRepository
from app.infrastructure.persistence.sqlite_review_repository import SqliteReviewRepository
from app.infrastructure.persistence.sqlite_syllabus_repository import SqliteSyllabusRepository


@pytest.fixture
def test_db(tmp_path: str) -> DatabaseManager:
    db_file = os.path.join(str(tmp_path), "test_convcomp.db")
    return DatabaseManager(db_path=db_file)


def test_syllabus_repository_save_and_get(test_db: DatabaseManager) -> None:
    repo = SqliteSyllabusRepository(test_db)

    p1 = SyllabusPage(page_number=1, raw_text="Texto página 1", character_count=14)
    p2 = SyllabusPage(page_number=2, raw_text="Texto página 2", character_count=14)
    sec = SyllabusSection(
        id="syl-1-SEC-01",
        syllabus_id="syl-1",
        title="Unidad I",
        section_type=SectionType.UNIT,
        order=1,
        page_start=1,
        page_end=2,
    )

    syl = Syllabus(
        id="syl-1",
        filename="syl1.pdf",
        file_path="/tmp/syl1.pdf",
        file_size_bytes=2048,
        sha256_hash="hash123",
        total_pages=2,
        created_at=datetime.now(),
        university="UNAL",
        course_name="Bases de Datos",
        course_code="BD-101",
        pages=[p1, p2],
        sections=[sec],
    )

    repo.save(syl)

    retrieved = repo.get_by_id("syl-1")
    assert retrieved is not None
    assert retrieved.id == "syl-1"
    assert retrieved.course_name == "Bases de Datos"
    assert len(retrieved.pages) == 2
    assert len(retrieved.sections) == 1
    assert retrieved.sections[0].section_type == SectionType.UNIT


def test_comparison_repository_save_and_get(test_db: DatabaseManager) -> None:
    syl_repo = SqliteSyllabusRepository(test_db)
    comp_repo = SqliteComparisonRepository(test_db)

    # Insertar sílabos base para cumplir claves foráneas
    syl_a = Syllabus(id="syl-A", filename="a.pdf", file_path="/tmp/a.pdf", file_size_bytes=100, sha256_hash="hA", total_pages=1, created_at=datetime.now())
    syl_b = Syllabus(id="syl-B", filename="b.pdf", file_path="/tmp/b.pdf", file_size_bytes=100, sha256_hash="hB", total_pages=1, created_at=datetime.now())
    syl_repo.save(syl_a)
    syl_repo.save(syl_b)

    breakdown = ScoreBreakdown(0.95, 0.90, 0.85, 0.80, 0.91, {"semantic": 0.4, "lexical": 0.3, "keyword": 0.15, "structural": 0.15})
    evidence = MatchEvidence("HYBRID", ["sql", "claves"], 0.95, 0.90, "snippet obj", "snippet cmp", 1, 1)

    match = ContentMatch(
        id="M-01",
        comparison_id="COMP-01",
        objective_item_id="OBJ-01",
        compared_item_id="CMP-01",
        objective_title="Modelo Relacional",
        compared_title="Modelo Relacional",
        objective_section="Unidad I",
        compared_section="Unidad I",
        objective_page=1,
        compared_page=1,
        score_breakdown=breakdown,
        classification=MatchClassification.MATCH,
        evidence=evidence,
    )

    unmatched = UnmatchedItem("OBJ-99", "syl-A", "Unidad IV", "NoSQL", "Texto nosql", 1, None, None, 0.1)

    comp = Comparison(
        id="COMP-01",
        objective_syllabus_id="syl-A",
        compared_syllabus_id="syl-B",
        global_score=0.88,
        objective_coverage=85.0,
        compared_coverage=80.0,
        model_version="baseline-001",
        created_at=datetime.now(),
        matches=[match],
        unmatched_objective=[unmatched],
        unmatched_compared=[],
    )

    comp_repo.save(comp)

    retrieved = comp_repo.get_by_id("COMP-01")
    assert retrieved is not None
    assert retrieved.global_score == 0.88
    assert len(retrieved.matches) == 1
    assert retrieved.matches[0].classification == MatchClassification.MATCH
    assert "sql" in retrieved.matches[0].evidence.shared_keywords
    assert len(retrieved.unmatched_objective) == 1


def test_review_repository_immutability(test_db: DatabaseManager) -> None:
    syl_repo = SqliteSyllabusRepository(test_db)
    comp_repo = SqliteComparisonRepository(test_db)
    rev_repo = SqliteReviewRepository(test_db)

    syl_a = Syllabus(id="syl-A", filename="a.pdf", file_path="/tmp/a.pdf", file_size_bytes=100, sha256_hash="hA", total_pages=1, created_at=datetime.now())
    syl_b = Syllabus(id="syl-B", filename="b.pdf", file_path="/tmp/b.pdf", file_size_bytes=100, sha256_hash="hB", total_pages=1, created_at=datetime.now())
    syl_repo.save(syl_a)
    syl_repo.save(syl_b)

    breakdown = ScoreBreakdown(0.86, 0.80, 0.70, 0.70, 0.81, {"semantic": 0.4, "lexical": 0.3, "keyword": 0.15, "structural": 0.15})
    evidence = MatchEvidence("HYBRID", ["sql"], 0.86, 0.80, "snippet obj", "snippet cmp", 1, 1)

    match = ContentMatch(
        id="M-TEST",
        comparison_id="COMP-TEST",
        objective_item_id="OBJ-01",
        compared_item_id="CMP-01",
        objective_title="Tema",
        compared_title="Tema",
        objective_section="Sec",
        compared_section="Sec",
        objective_page=1,
        compared_page=1,
        score_breakdown=breakdown,
        classification=MatchClassification.MATCH,
        evidence=evidence,
    )

    comp = Comparison(
        id="COMP-TEST",
        objective_syllabus_id="syl-A",
        compared_syllabus_id="syl-B",
        global_score=0.81,
        objective_coverage=80.0,
        compared_coverage=80.0,
        model_version="baseline-001",
        created_at=datetime.now(),
        matches=[match],
        unmatched_objective=[],
        unmatched_compared=[],
    )
    comp_repo.save(comp)

    # Registrar corrección humana: el humano dice PARTIAL_MATCH en vez de MATCH
    review = Review(
        id="REV-01",
        comparison_id="COMP-TEST",
        match_id="M-TEST",
        prediction_before=MatchClassification.MATCH,
        human_decision=MatchClassification.PARTIAL_MATCH,
        correction_type=CorrectionType.OVERESTIMATION,
        justification="Solo coincide en álgebra relacional básica, no avanzada.",
        reviewer_id="PROF-007",
        model_version="baseline-001",
        created_at=datetime.now(),
    )
    rev_repo.save(review)

    # REGLA CRÍTICA: Verificar que la predicción original en content_matches SIGUE siendo MATCH
    comp_after = comp_repo.get_by_id("COMP-TEST")
    assert comp_after is not None
    assert comp_after.matches[0].classification == MatchClassification.MATCH

    # Verificar que la revisión humana fue registrada
    reviews = rev_repo.get_by_comparison_id("COMP-TEST")
    assert len(reviews) == 1
    assert reviews[0].human_decision == MatchClassification.PARTIAL_MATCH
    assert reviews[0].prediction_before == MatchClassification.MATCH

    # Verificar que se creó el staging en dataset_examples
    assert rev_repo.count_examples() == 1
    example = rev_repo.list_examples()[0]
    assert example.ground_truth_label == "PARTIAL_MATCH"
    assert example.prediction_label == "MATCH"
