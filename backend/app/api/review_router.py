"""
Router de API para registro de Revisiones Humanas inmutables.
"""

from datetime import datetime
from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_comparison_repository, get_review_repository, get_syllabus_repository
from app.api.schemas import CreateReviewRequest, ReviewResponse
from app.domain.review import Review
from app.infrastructure.persistence.sqlite_comparison_repository import SqliteComparisonRepository
from app.infrastructure.persistence.sqlite_review_repository import SqliteReviewRepository
from app.infrastructure.persistence.sqlite_syllabus_repository import SqliteSyllabusRepository

router = APIRouter(prefix="/reviews", tags=["Revisiones"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def submit_review(
    payload: CreateReviewRequest,
    rev_repo: SqliteReviewRepository = Depends(get_review_repository),
    comp_repo: SqliteComparisonRepository = Depends(get_comparison_repository),
    syl_repo: SqliteSyllabusRepository = Depends(get_syllabus_repository),
) -> ReviewResponse:
    """
    Registra una validación o corrección humana sobre una correspondencia propuesta.
    REGLA: No muta ni sobrescribe la predicción original de la IA en content_matches.
    """
    if not payload.reviewer_id.strip() or len(payload.justification.strip()) < 3:
        raise HTTPException(status_code=422, detail="Identifique al revisor y escriba una justificación de al menos tres caracteres.")
    comp = comp_repo.get_by_id(payload.comparison_id)
    if not comp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La comparación indicada no existe.",
        )

    # Si hay match_id, verificar que pertenezca a la comparación
    if payload.match_id:
        if payload.manual_objective_item_id or payload.manual_compared_item_id:
            raise HTTPException(status_code=422, detail="Indique una correspondencia o un enlace manual, sin combinarlos.")
        target_match = next((m for m in comp.matches if m.id == payload.match_id), None)
        if not target_match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"La correspondencia '{payload.match_id}' no pertenece a la comparación indicada.",
            )
        prediction_before = target_match.classification
    else:
        objective_ids = {item.id for item in syl_repo.get_content_items(comp.objective_syllabus_id)}
        compared_ids = {item.id for item in syl_repo.get_content_items(comp.compared_syllabus_id)}
        if payload.manual_objective_item_id not in objective_ids or payload.manual_compared_item_id not in compared_ids:
            raise HTTPException(status_code=422, detail="El enlace manual requiere dos contenidos pertenecientes a los sílabos de esta comparación.")
        prediction_before = None

    review_id = f"REV-{uuid.uuid4().hex[:10].upper()}"
    review = Review(
        id=review_id,
        comparison_id=payload.comparison_id,
        match_id=payload.match_id,
        prediction_before=prediction_before,
        human_decision=payload.human_decision,
        correction_type=payload.correction_type,
        justification=payload.justification,
        reviewer_id=payload.reviewer_id,
        model_version=comp.model_version,
        created_at=datetime.now(),
        manual_objective_item_id=payload.manual_objective_item_id,
        manual_compared_item_id=payload.manual_compared_item_id,
    )

    rev_repo.save(review)

    return ReviewResponse(
        id=review.id,
        comparison_id=review.comparison_id,
        match_id=review.match_id,
        prediction_before=review.prediction_before,
        human_decision=review.human_decision,
        correction_type=review.correction_type,
        justification=review.justification,
        reviewer_id=review.reviewer_id,
        model_version=review.model_version,
        created_at=review.created_at,
    )


@router.get("/comparison/{comparison_id}", response_model=List[ReviewResponse])
def get_reviews_for_comparison(
    comparison_id: str,
    rev_repo: SqliteReviewRepository = Depends(get_review_repository),
) -> List[ReviewResponse]:
    """Obtiene todas las revisiones y correcciones registradas para una comparación."""
    reviews = rev_repo.get_by_comparison_id(comparison_id)
    return [
        ReviewResponse(
            id=r.id,
            comparison_id=r.comparison_id,
            match_id=r.match_id,
            prediction_before=r.prediction_before,
            human_decision=r.human_decision,
            correction_type=r.correction_type,
            justification=r.justification,
            reviewer_id=r.reviewer_id,
            model_version=r.model_version,
            created_at=r.created_at,
        )
        for r in reviews
    ]
