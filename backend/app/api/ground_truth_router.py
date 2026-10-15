"""Consultas de anotación consolidada y acuerdo entre revisores."""

import csv
from dataclasses import asdict
import io
import json
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.api.deps import get_comparison_repository, get_review_repository
from app.api.schemas import (
    GroundTruthPageResponse, GroundTruthPairResponse, GroundTruthSummaryResponse,
    GroundTruthVoteResponse, ReviewerAgreementResponse,
)
from app.application.ground_truth_service import GroundTruthService
from app.domain.ground_truth import ConsensusStatus, GroundTruthPair, reviewer_agreements
from app.infrastructure.persistence.sqlite_comparison_repository import SqliteComparisonRepository
from app.infrastructure.persistence.sqlite_review_repository import SqliteReviewRepository

router = APIRouter(prefix="/dataset", tags=["Ground truth y acuerdo"])


def _map_pair(pair: GroundTruthPair) -> GroundTruthPairResponse:
    return GroundTruthPairResponse(
        comparison_id=pair.comparison_id, objective_item_id=pair.objective_item_id,
        compared_item_id=pair.compared_item_id, match_id=pair.match_id,
        objective_text=pair.example.objective_text, compared_text=pair.example.compared_text,
        prediction_label=pair.example.prediction_label, features=pair.example.features,
        feature_source_review_id=pair.example.review_id,
        source_university_obj=pair.example.source_university_obj, source_university_cmp=pair.example.source_university_cmp,
        source_course_obj=pair.example.source_course_obj, source_course_cmp=pair.example.source_course_cmp,
        source_syllabus_obj=pair.example.source_syllabus_obj, source_syllabus_cmp=pair.example.source_syllabus_cmp,
        source_page_obj=pair.example.source_page_obj, source_page_cmp=pair.example.source_page_cmp,
        status=pair.status, consensus_label=pair.consensus_label,
        reviewer_count=len(pair.votes), review_count=pair.review_count,
        votes=[GroundTruthVoteResponse(
            review_id=v.id, reviewer_id=v.reviewer_id, human_decision=v.human_decision,
            justification=v.justification, created_at=v.created_at,
        ) for v in pair.votes],
    )


def _pairs(
    comparison_id: Optional[str], repo: SqliteReviewRepository, comparisons: SqliteComparisonRepository,
) -> List[GroundTruthPair]:
    if comparison_id is not None and comparisons.get_by_id(comparison_id) is None:
        raise HTTPException(status_code=404, detail="Comparación no encontrada.")
    return GroundTruthService(repo, repo).get_pairs(comparison_id)


@router.get("/ground-truth", response_model=GroundTruthPageResponse)
def get_ground_truth(
    comparison_id: Optional[str] = None,
    status: Optional[ConsensusStatus] = None,
    limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
    repo: SqliteReviewRepository = Depends(get_review_repository),
    comparisons: SqliteComparisonRepository = Depends(get_comparison_repository),
) -> GroundTruthPageResponse:
    pairs = _pairs(comparison_id, repo, comparisons)
    summary = GroundTruthSummaryResponse(
        total_pairs=len(pairs),
        consensus_pairs=sum(p.status == ConsensusStatus.CONSENSUS for p in pairs),
        disagreement_pairs=sum(p.status == ConsensusStatus.DISAGREEMENT for p in pairs),
        single_review_pairs=sum(p.status == ConsensusStatus.SINGLE_REVIEW for p in pairs),
        linked_review_events=sum(p.review_count for p in pairs),
    )
    filtered = [p for p in pairs if status is None or p.status == status]
    return GroundTruthPageResponse(
        summary=summary, total=len(filtered), limit=limit, offset=offset,
        items=[_map_pair(p) for p in filtered[offset:offset + limit]],
    )


@router.get("/ground-truth/export")
def export_ground_truth(
    format: Literal["json", "csv"] = "json", comparison_id: Optional[str] = None,
    repo: SqliteReviewRepository = Depends(get_review_repository),
    comparisons: SqliteComparisonRepository = Depends(get_comparison_repository),
) -> Response:
    pairs = [_map_pair(p).model_dump(mode="json") for p in _pairs(comparison_id, repo, comparisons)]
    if format == "json":
        return Response(json.dumps(pairs, ensure_ascii=False), media_type="application/json",
                        headers={"Content-Disposition": "attachment; filename=ground_truth.json"})
    output = io.StringIO()
    fields = list(GroundTruthPairResponse.model_fields)
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for pair in pairs:
        writer.writerow({**pair, "votes": json.dumps(pair["votes"], ensure_ascii=False),
                         "features": json.dumps(pair["features"], ensure_ascii=False)})
    return Response(output.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=ground_truth.csv"})


@router.get("/agreement", response_model=List[ReviewerAgreementResponse])
def get_reviewer_agreement(
    comparison_id: Optional[str] = None,
    repo: SqliteReviewRepository = Depends(get_review_repository),
    comparisons: SqliteComparisonRepository = Depends(get_comparison_repository),
) -> List[ReviewerAgreementResponse]:
    pairs = _pairs(comparison_id, repo, comparisons)
    return [ReviewerAgreementResponse(**asdict(row)) for row in reviewer_agreements(pairs)]
