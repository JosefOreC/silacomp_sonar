"""
Router de API para gestión, entrenamiento, versionado y evaluación de Modelos de Machine Learning (Fase 2.0).
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    get_model_inference_service,
    get_model_repository,
    get_model_trainer,
    get_review_repository,
    get_reserved_evaluation_policy,
)
from app.api.schemas import ModelVersionResponse, TrainModelRequest
from app.application.train_model_use_case import TrainModelUseCase
from app.domain.scoring import BASELINE_VERSION, DEFAULT_WEIGHTS, DEFAULT_THRESHOLDS
from app.infrastructure.ml.model_inference_service import ModelInferenceService
from app.infrastructure.ml.supervised_trainer import SklearnSupervisedTrainer
from app.infrastructure.persistence.sqlite_model_repository import SqliteModelVersionRepository
from app.infrastructure.persistence.sqlite_review_repository import SqliteReviewRepository
from app.application.reserved_evaluation_policy import ReservedEvaluationPolicy

router = APIRouter(prefix="/models", tags=["Modelos de Aprendizaje Supervisado"])


def _baseline_response() -> ModelVersionResponse:
    """Describe el algoritmo disponible sin atribuirle resultados de un experimento."""
    return ModelVersionResponse(
        version_id=BASELINE_VERSION,
        algorithm_name="Hybrid-Bipartite-Adaptive",
        description="Motor heurístico con scoring adaptativo y asignación global bipartita.",
        is_active=True,
        created_at="2026-10-01T00:00:00",
        metrics={"type": "heuristic_baseline", "evaluation_status": "not_evaluated"},
        parameters={"weights": dict(DEFAULT_WEIGHTS), "thresholds": dict(DEFAULT_THRESHOLDS)},
    )


@router.get("", response_model=List[ModelVersionResponse])
def list_models(
    repo: SqliteModelVersionRepository = Depends(get_model_repository),
) -> List[ModelVersionResponse]:
    """Lista todas las versiones de modelos registradas en el sistema."""
    versions = repo.list_all()
    return [
        ModelVersionResponse(
            version_id=v.version_id,
            algorithm_name=v.algorithm_name,
            description=v.description,
            is_active=v.is_active,
            created_at=v.created_at,
            metrics=v.metrics,
            parameters=v.parameters,
        )
        for v in versions
    ] + ([_baseline_response()] if not any(v.is_active for v in versions) else [])


@router.get("/active", response_model=ModelVersionResponse)
def get_active_model(
    repo: SqliteModelVersionRepository = Depends(get_model_repository),
) -> ModelVersionResponse:
    """Retorna los datos del modelo actualmente activo en inferencia de producción."""
    active = repo.get_active_model()
    if active:
        return ModelVersionResponse(
            version_id=active.version_id,
            algorithm_name=active.algorithm_name,
            description=active.description,
            is_active=active.is_active,
            created_at=active.created_at,
            metrics=active.metrics,
            parameters=active.parameters,
        )

    return _baseline_response()


@router.post("/train", response_model=ModelVersionResponse, status_code=status.HTTP_201_CREATED)
def train_model(
    request: TrainModelRequest,
    dataset_repo: SqliteReviewRepository = Depends(get_review_repository),
    model_repo: SqliteModelVersionRepository = Depends(get_model_repository),
    trainer: SklearnSupervisedTrainer = Depends(get_model_trainer),
    inference: ModelInferenceService = Depends(get_model_inference_service),
    reserved_policy: ReservedEvaluationPolicy = Depends(get_reserved_evaluation_policy),
) -> ModelVersionResponse:
    """
    Ejecuta un ciclo de entrenamiento supervisado sobre las observaciones del dataset científico,
    calibra probabilidades, evalúa contra el baseline y registra la versión en la base de datos.
    """
    use_case = TrainModelUseCase(
        dataset_repo=dataset_repo,
        model_version_repo=model_repo,
        trainer=trainer,
        review_repo=dataset_repo,
        reserved_policy=reserved_policy,
    )
    try:
        model_version, metrics = use_case.execute(
            algorithm=request.algorithm,
            test_size=request.test_size,
            use_bootstrap_if_sparse=request.use_bootstrap,
            auto_activate=request.auto_activate,
            ground_truth_policy=request.ground_truth_policy,
        )

        if model_version.is_active:
            inference.load_model(model_version)

        return ModelVersionResponse(
            version_id=model_version.version_id,
            algorithm_name=model_version.algorithm_name,
            description=model_version.description,
            is_active=model_version.is_active,
            created_at=model_version.created_at,
            metrics=model_version.metrics,
            parameters=model_version.parameters,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error durante el entrenamiento del modelo: {str(e)}",
        )


@router.post("/{version_id}/activate")
def activate_model(
    version_id: str,
    repo: SqliteModelVersionRepository = Depends(get_model_repository),
    inference: ModelInferenceService = Depends(get_model_inference_service),
) -> Dict[str, Any]:
    """Activa una versión de modelo existente para su uso en comparaciones futuras."""
    version = repo.get_by_id(version_id)
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La versión de modelo '{version_id}' no fue encontrada.",
        )

    if not inference.load_model(version):
        raise HTTPException(status_code=409, detail="No se puede cargar el artefacto del modelo; la versión activa no se cambió.")
    repo.set_active_model(version_id)

    return {"status": "success", "message": f"Modelo {version_id} activado como versión de producción."}


@router.get("/{version_id}/evaluation")
def get_model_evaluation(
    version_id: str,
    repo: SqliteModelVersionRepository = Depends(get_model_repository),
) -> Dict[str, Any]:
    """Retorna las métricas científicas detalladas, matriz de confusión y benchmarking frente al baseline."""
    version = repo.get_by_id(version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Versión de modelo '{version_id}' no encontrada.",
        )

    return {
        "version_id": version.version_id,
        "algorithm_name": version.algorithm_name,
        "is_active": version.is_active,
        "created_at": version.created_at.isoformat(),
        "metrics": version.metrics,
    }
