"""Conjuntos reservados y experimentos sin activación automática."""

from dataclasses import asdict
import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.api.deps import get_scientific_evaluation_service, get_scientific_repository
from app.api.schemas import (
    CreateEvaluationSnapshotRequest, EvaluationSnapshotResponse,
    CreateEvaluationExperimentRequest, EvaluationExperimentResponse,
)
from app.application.scientific_evaluation_service import ScientificEvaluationService
from app.domain.scientific_evaluation import EvaluationSnapshot, EvaluationValidationError
from app.infrastructure.persistence.sqlite_scientific_repository import SqliteScientificRepository

router = APIRouter(prefix="/evaluation", tags=["Evaluación científica reservada"])


def _summary(snapshot: EvaluationSnapshot) -> EvaluationSnapshotResponse:
    return EvaluationSnapshotResponse(
        id=snapshot.id, name=snapshot.name, created_at=snapshot.created_at, content_hash=snapshot.content_hash,
        comparison_count=len(snapshot.payload["cases"]), pair_count=snapshot.payload["pair_count"],
        independent_groups=snapshot.payload["independent_groups"],
    )


@router.post("/snapshots", response_model=EvaluationSnapshotResponse, status_code=201)
def create_snapshot(
    request: CreateEvaluationSnapshotRequest, service: ScientificEvaluationService = Depends(get_scientific_evaluation_service),
) -> EvaluationSnapshotResponse:
    try:
        return _summary(service.create_snapshot(request.name, request.comparison_ids))
    except EvaluationValidationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/snapshots", response_model=List[EvaluationSnapshotResponse])
def list_snapshots(
    limit: int = Query(20, ge=1, le=100), repository: SqliteScientificRepository = Depends(get_scientific_repository),
) -> List[EvaluationSnapshotResponse]:
    return [_summary(snapshot) for snapshot in repository.list_snapshots()[:limit]]


@router.get("/snapshots/{snapshot_id}", response_model=EvaluationSnapshotResponse)
def get_snapshot(
    snapshot_id: str, repository: SqliteScientificRepository = Depends(get_scientific_repository),
) -> EvaluationSnapshotResponse:
    snapshot = repository.get_snapshot(snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Snapshot no encontrado.")
    return _summary(snapshot)


@router.get("/snapshots/{snapshot_id}/export")
def export_snapshot(snapshot_id: str, repository: SqliteScientificRepository = Depends(get_scientific_repository)) -> Response:
    snapshot = repository.get_snapshot(snapshot_id)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Snapshot no encontrado.")
    data = asdict(snapshot)
    data["created_at"] = snapshot.created_at.isoformat()
    return Response(json.dumps(data, ensure_ascii=False, allow_nan=False), media_type="application/json",
                    headers={"Content-Disposition": f"attachment; filename={snapshot.id}.json"})


@router.post("/experiments", response_model=EvaluationExperimentResponse, status_code=201)
def create_experiment(
    request: CreateEvaluationExperimentRequest, service: ScientificEvaluationService = Depends(get_scientific_evaluation_service),
) -> EvaluationExperimentResponse:
    try:
        experiment = service.run_experiment(request.snapshot_id, request.reference_version,
                                            request.candidate_version, request.criteria.model_dump())
        return EvaluationExperimentResponse(**asdict(experiment))
    except EvaluationValidationError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/experiments", response_model=List[EvaluationExperimentResponse])
def list_experiments(
    limit: int = Query(20, ge=1, le=100), repository: SqliteScientificRepository = Depends(get_scientific_repository),
) -> List[EvaluationExperimentResponse]:
    return [EvaluationExperimentResponse(**asdict(experiment)) for experiment in repository.list_experiments(limit)]


@router.get("/experiments/{experiment_id}", response_model=EvaluationExperimentResponse)
def get_experiment(
    experiment_id: str, repository: SqliteScientificRepository = Depends(get_scientific_repository),
) -> EvaluationExperimentResponse:
    experiment = repository.get_experiment(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experimento no encontrado.")
    return EvaluationExperimentResponse(**asdict(experiment))


@router.get("/experiments/{experiment_id}/export")
def export_experiment(experiment_id: str, repository: SqliteScientificRepository = Depends(get_scientific_repository)) -> Response:
    experiment = repository.get_experiment(experiment_id)
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experimento no encontrado.")
    data = asdict(experiment)
    data["created_at"] = experiment.created_at.isoformat()
    return Response(json.dumps(data, ensure_ascii=False, allow_nan=False), media_type="application/json",
                    headers={"Content-Disposition": f"attachment; filename={experiment.id}.json"})
