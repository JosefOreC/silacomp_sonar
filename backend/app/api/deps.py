"""
Inyección de dependencias para los routers de FastAPI.
"""

from functools import lru_cache
import os
from app.infrastructure.nlp.segmenter import SyllabusSegmenter
from app.infrastructure.nlp.vector_service import NlpVectorService
from app.infrastructure.pdf.extractor import PyMuPdfExtractor
from app.infrastructure.persistence.database import DatabaseManager
from app.infrastructure.persistence.sqlite_comparison_repository import SqliteComparisonRepository
from app.infrastructure.persistence.sqlite_review_repository import SqliteReviewRepository
from app.infrastructure.persistence.sqlite_syllabus_repository import SqliteSyllabusRepository


@lru_cache()
def get_db_manager() -> DatabaseManager:
    return DatabaseManager()


def get_syllabus_repository() -> SqliteSyllabusRepository:
    return SqliteSyllabusRepository(get_db_manager())


def get_comparison_repository() -> SqliteComparisonRepository:
    return SqliteComparisonRepository(get_db_manager())


def get_review_repository() -> SqliteReviewRepository:
    return SqliteReviewRepository(get_db_manager())


@lru_cache()
def get_vector_service() -> NlpVectorService:
    return NlpVectorService()


@lru_cache()
def get_syllabus_extractor() -> PyMuPdfExtractor:
    return PyMuPdfExtractor()


@lru_cache()
def get_syllabus_segmenter() -> SyllabusSegmenter:
    return SyllabusSegmenter()
