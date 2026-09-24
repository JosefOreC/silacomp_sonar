"""
Router de API para consulta de estadísticas del dataset científico de observaciones.
"""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends

from app.api.deps import get_review_repository
from app.api.schemas import DatasetStatsResponse
from app.infrastructure.persistence.sqlite_review_repository import SqliteReviewRepository

router = APIRouter(prefix="/dataset", tags=["Dataset Científico"])


@router.get("/statistics", response_model=DatasetStatsResponse)
def get_dataset_statistics(
    rev_repo: SqliteReviewRepository = Depends(get_review_repository),
) -> DatasetStatsResponse:
    """Retorna las estadísticas del dataset recopilado mediante validaciones humanas."""
    total = rev_repo.count_examples()
    examples = rev_repo.list_examples(limit=1000)

    by_gt: Dict[str, int] = {}
    for ex in examples:
        label = ex.ground_truth_label or "UNKNOWN"
        by_gt[label] = by_gt.get(label, 0) + 1

    return DatasetStatsResponse(
        total_examples=total,
        by_ground_truth=by_gt,
        model_version="baseline-001",
    )


@router.get("/examples", response_model=List[Dict[str, Any]])
def list_dataset_examples(
    limit: int = 50,
    offset: int = 0,
    rev_repo: SqliteReviewRepository = Depends(get_review_repository),
) -> List[Dict[str, Any]]:
    """Lista las observaciones de entrenamiento consolidadas para la Fase 2."""
    examples = rev_repo.list_examples(limit=limit, offset=offset)
    return [
        {
            "id": ex.id,
            "review_id": ex.review_id,
            "objective_text": ex.objective_text,
            "compared_text": ex.compared_text,
            "features": ex.features,
            "prediction_label": ex.prediction_label,
            "ground_truth_label": ex.ground_truth_label,
            "model_version": ex.model_version,
            "created_at": ex.created_at.isoformat() if ex.created_at else None,
        }
        for ex in examples
    ]


@router.get("/export")
def export_dataset(
    rev_repo: SqliteReviewRepository = Depends(get_review_repository),
) -> List[Dict[str, Any]]:
    """Exporta el dataset completo en JSON para el entrenamiento supervisado en Fase 2."""
    examples = rev_repo.list_examples(limit=10000)
    exported = []
    for ex in examples:
        rev = rev_repo.get_by_id(ex.review_id) if ex.review_id else None
        exported.append({
            "id": ex.id,
            "review_id": ex.review_id,
            "objective_text": ex.objective_text,
            "compared_text": ex.compared_text,
            "features": ex.features,
            "prediction_before": ex.prediction_label,
            "human_decision": ex.ground_truth_label,
            "correction_type": rev.correction_type.value if rev else "CONFIRMED",
            "justification": rev.justification if rev else "",
            "reviewer_id": rev.reviewer_id if rev else "",
            "model_version": ex.model_version,
            "created_at": ex.created_at.isoformat() if ex.created_at else None,
        })
    return exported


