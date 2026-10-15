"""Cola de revisión priorizada y lotes con medición de anotación."""

from dataclasses import asdict
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_active_learning_service, get_annotation_batch_repository
from app.api.schemas import (
    AnnotationBatchProgressResponse, AnnotationBatchResponse, AnnotationQueueResponse, CreateAnnotationBatchRequest,
)
from app.application.active_learning_service import ActiveLearningService
from app.domain.active_learning import PriorityReason, STRATEGY_VERSION, annotation_coverage, prioritize_cases
from app.domain.annotation_batch import (
    AnnotationBatchNotFoundError, AnnotationSourceUnavailableError, NoAnnotationCandidatesError,
)
from app.domain.scoring import DEFAULT_THRESHOLDS
from app.infrastructure.persistence.sqlite_annotation_batch_repository import SqliteAnnotationBatchRepository

router = APIRouter(prefix="/active-learning", tags=["Aprendizaje activo"])


@router.get("/queue", response_model=AnnotationQueueResponse)
def get_annotation_queue(
    comparison_id: Optional[str] = None, reason: Optional[PriorityReason] = None,
    reviewer_id: Optional[str] = Query(None, min_length=1, max_length=200),
    limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
    service: ActiveLearningService = Depends(get_active_learning_service),
) -> AnnotationQueueResponse:
    if reviewer_id is not None and not reviewer_id.strip():
        raise HTTPException(status_code=422, detail="Identifique al revisor.")
    try:
        cases = service.get_cases(comparison_id)
    except AnnotationSourceUnavailableError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    queue = prioritize_cases(cases, reviewer_id, reason)
    return AnnotationQueueResponse(
        strategy_version=STRATEGY_VERSION, reference_thresholds=DEFAULT_THRESHOLDS,
        coverage=asdict(annotation_coverage(cases)), total=len(queue), limit=limit, offset=offset,
        items=[asdict(case) for case in queue[offset:offset + limit]],
    )


@router.post("/batches", response_model=AnnotationBatchProgressResponse, status_code=201)
def create_annotation_batch(
    request: CreateAnnotationBatchRequest, service: ActiveLearningService = Depends(get_active_learning_service),
) -> AnnotationBatchProgressResponse:
    try:
        return AnnotationBatchProgressResponse(**asdict(service.create_batch(
            request.reviewer_id, request.limit, request.comparison_id, request.reason,
        )))
    except AnnotationSourceUnavailableError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except NoAnnotationCandidatesError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/batches", response_model=List[AnnotationBatchResponse])
def list_annotation_batches(
    limit: int = Query(20, ge=1, le=100),
    repo: SqliteAnnotationBatchRepository = Depends(get_annotation_batch_repository),
) -> List[AnnotationBatchResponse]:
    return [AnnotationBatchResponse(**asdict(batch)) for batch in repo.list_recent(limit)]


def _progress(service: ActiveLearningService, batch_id: str, complete: bool) -> AnnotationBatchProgressResponse:
    try:
        result = service.complete_batch(batch_id) if complete else service.get_batch_progress(batch_id)
        return AnnotationBatchProgressResponse(**asdict(result))
    except AnnotationBatchNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AnnotationSourceUnavailableError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/batches/{batch_id}", response_model=AnnotationBatchProgressResponse)
def get_annotation_batch(
    batch_id: str, service: ActiveLearningService = Depends(get_active_learning_service),
) -> AnnotationBatchProgressResponse:
    return _progress(service, batch_id, False)


@router.post("/batches/{batch_id}/complete", response_model=AnnotationBatchProgressResponse)
def complete_annotation_batch(
    batch_id: str, service: ActiveLearningService = Depends(get_active_learning_service),
) -> AnnotationBatchProgressResponse:
    return _progress(service, batch_id, True)
