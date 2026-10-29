"""Creación idempotente y consulta de comparaciones independientes por lote."""

from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import JSONResponse

from app.api.comparison_batch_schemas import ComparisonBatchResponse, CreateComparisonBatchRequest
from app.api.deps import get_comparison_repository, get_db_manager, get_model_repository, get_syllabus_repository, get_vector_service
from app.application.compare_syllabi import CompareSyllabiUseCase
from app.application.comparison_batch_service import CompareSyllabusBatch, ComparisonBatchQuery
from app.domain.comparison_batch import (
    BatchNotFoundError, BatchRequestConflictError, BatchSourceNotFoundError, BatchValidationError,
    ComparisonBatchView, RANKING_RULE,
)
from app.domain.scoring import BASELINE_VERSION
from app.infrastructure.ml.model_inference_service import ModelInferenceService
from app.infrastructure.nlp.vector_service import NlpVectorService
from app.infrastructure.persistence.sqlite_comparison_batch_repository import SqliteComparisonBatchRepository
from app.application.comparison_batch_ports import PairComparisonRunner

router = APIRouter(prefix="/comparison-batches", tags=["Comparación por lotes"])


def get_batch_repository() -> SqliteComparisonBatchRepository:
    return SqliteComparisonBatchRepository(get_db_manager())


def get_batch_query() -> ComparisonBatchQuery:
    return ComparisonBatchQuery(get_batch_repository())


def get_batch_executor(vectors: NlpVectorService = Depends(get_vector_service)) -> CompareSyllabusBatch:
    def runner_factory() -> tuple[PairComparisonRunner, str]:
        active = get_model_repository().get_active_model()
        inference = ModelInferenceService()
        if active is not None and not inference.load_model(active):
            raise BatchRequestConflictError("No se pudo cargar el modelo activo. Revise su disponibilidad antes de comparar.")
        version = active.version_id if active is not None else BASELINE_VERSION
        return CompareSyllabiUseCase(
            vector_service=vectors, comparison_repository=get_comparison_repository(), model_version=version,
            inference_service=inference if active is not None else None,
        ), version
    return CompareSyllabusBatch(get_syllabus_repository(), get_batch_repository(), runner_factory)


def _response(view: ComparisonBatchView) -> ComparisonBatchResponse:
    return ComparisonBatchResponse(**asdict(view.batch), completed_at=view.completed_at,
                                   status=view.status, ranking_rule=RANKING_RULE, ranking=view.ranking,
                                   results=[asdict(result) for result in view.results])


@router.post("", response_model=ComparisonBatchResponse, status_code=201)
def compare_batch(
    payload: CreateComparisonBatchRequest, response: Response,
    service: CompareSyllabusBatch = Depends(get_batch_executor),
) -> ComparisonBatchResponse:
    try:
        view, created = service.execute(payload.request_id, payload.objective_syllabus_id, tuple(payload.compared_syllabus_ids))
        response.status_code = 201 if created else 200
        return _response(view)
    except BatchSourceNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except BatchRequestConflictError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except BatchValidationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.get("", response_model=list[ComparisonBatchResponse])
def list_batches(limit: int = Query(20, ge=1, le=50), query: ComparisonBatchQuery = Depends(get_batch_query)) -> list[ComparisonBatchResponse]:
    return [_response(view) for view in query.list_recent(limit)]


@router.get("/{batch_id}", response_model=ComparisonBatchResponse)
def get_batch(batch_id: str, query: ComparisonBatchQuery = Depends(get_batch_query)) -> ComparisonBatchResponse:
    try:
        return _response(query.get(batch_id))
    except BatchNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{batch_id}/export")
def export_batch(batch_id: str, query: ComparisonBatchQuery = Depends(get_batch_query)) -> JSONResponse:
    report = get_batch(batch_id, query)
    return JSONResponse(report.model_dump(mode="json"), headers={
        "Content-Disposition": f'attachment; filename="{report.id}.json"',
    })
