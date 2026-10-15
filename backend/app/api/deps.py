"""
Inyección de dependencias para los routers de FastAPI.
"""

from functools import lru_cache
from fastapi import Depends
import os
from app.infrastructure.nlp.segmenter import SyllabusSegmenter
from app.infrastructure.nlp.vector_service import NlpVectorService
from app.infrastructure.ocr.rapid_ocr_engine import RapidOcrEngine
from app.infrastructure.pdf.extractor import PyMuPdfExtractor
from app.infrastructure.ml.model_inference_service import ModelInferenceService
from app.infrastructure.ml.supervised_trainer import SklearnSupervisedTrainer
from app.infrastructure.persistence.database import DatabaseManager
from app.infrastructure.persistence.sqlite_comparison_repository import SqliteComparisonRepository
from app.infrastructure.persistence.sqlite_model_repository import SqliteModelVersionRepository
from app.infrastructure.persistence.sqlite_review_repository import SqliteReviewRepository
from app.infrastructure.persistence.sqlite_syllabus_repository import SqliteSyllabusRepository
from app.infrastructure.persistence.sqlite_annotation_batch_repository import SqliteAnnotationBatchRepository
from app.application.ground_truth_service import GroundTruthService
from app.application.active_learning_service import ActiveLearningService
from app.infrastructure.persistence.sqlite_scientific_repository import SqliteScientificRepository
from app.infrastructure.ml.comparison_evaluation_engine import ComparisonEvaluationEngine
from app.application.scientific_evaluation_service import ScientificEvaluationService
from app.application.reserved_evaluation_policy import ReservedEvaluationPolicy


@lru_cache()
def get_db_manager() -> DatabaseManager:
    return DatabaseManager()


def get_syllabus_repository() -> SqliteSyllabusRepository:
    return SqliteSyllabusRepository(get_db_manager())


def get_comparison_repository() -> SqliteComparisonRepository:
    return SqliteComparisonRepository(get_db_manager())


def get_review_repository() -> SqliteReviewRepository:
    return SqliteReviewRepository(get_db_manager())


def get_annotation_batch_repository() -> SqliteAnnotationBatchRepository:
    return SqliteAnnotationBatchRepository(get_db_manager())


def get_active_learning_service() -> ActiveLearningService:
    reviews = get_review_repository()
    return ActiveLearningService(get_comparison_repository(), GroundTruthService(reviews, reviews),
                                 get_annotation_batch_repository())


def get_scientific_repository() -> SqliteScientificRepository:
    return SqliteScientificRepository(get_db_manager())


def get_reserved_evaluation_policy() -> ReservedEvaluationPolicy:
    return ReservedEvaluationPolicy(get_scientific_repository())


@lru_cache()
def get_vector_service() -> NlpVectorService:
    return NlpVectorService()


def get_scientific_evaluation_service(vectors: NlpVectorService = Depends(get_vector_service)) -> ScientificEvaluationService:
    reviews = get_review_repository()
    return ScientificEvaluationService(
        get_scientific_repository(), get_comparison_repository(), get_syllabus_repository(),
        GroundTruthService(reviews, reviews), get_model_repository(), ComparisonEvaluationEngine(vectors),
    )


@lru_cache()
def get_ocr_engine() -> RapidOcrEngine:
    return RapidOcrEngine()


@lru_cache()
def get_syllabus_extractor() -> PyMuPdfExtractor:
    return PyMuPdfExtractor(ocr_engine=get_ocr_engine())


@lru_cache()
def get_syllabus_segmenter() -> SyllabusSegmenter:
    return SyllabusSegmenter()


@lru_cache()
def get_model_repository() -> SqliteModelVersionRepository:
    return SqliteModelVersionRepository(get_db_manager())


@lru_cache()
def get_model_trainer() -> SklearnSupervisedTrainer:
    return SklearnSupervisedTrainer()


@lru_cache()
def get_model_inference_service() -> ModelInferenceService:
    service = ModelInferenceService()
    active_version = get_model_repository().get_active_model()
    if active_version:
        service.load_model(active_version)
    return service
