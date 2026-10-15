"""Priorización explicable de anotación, independiente de persistencia y modelos."""

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import List, Optional

from app.domain.comparison import Comparison, MatchClassification
from app.domain.ground_truth import GroundTruthPair, reviewer_key
from app.domain.scoring import DEFAULT_THRESHOLDS

STRATEGY_VERSION = "annotation-priority-001"


class PriorityReason(str, Enum):
    DISAGREEMENT = "DISAGREEMENT"
    SECOND_REVIEW = "SECOND_REVIEW"
    UNREVIEWED = "UNREVIEWED"


@dataclass
class AnnotationCase:
    case_id: str
    comparison_id: str
    model_version: str
    match_id: Optional[str]
    objective_item_id: str
    compared_item_id: str
    objective_text: str
    compared_text: str
    objective_page: Optional[int]
    compared_page: Optional[int]
    classification: Optional[str]
    score: Optional[float]
    status: str
    reviewer_ids: List[str]
    review_count: int
    reason: Optional[PriorityReason] = None
    boundary_distance: Optional[float] = None
    uncertain_prediction: bool = False
    near_boundary: bool = False


@dataclass(frozen=True)
class AnnotationCoverage:
    total_pairs: int
    reviewed_pairs: int
    consensus_pairs: int
    disagreement_pairs: int
    pending_pairs: int
    review_events: int
    reviewed_percentage: Optional[float]
    consensus_percentage: Optional[float]


def case_identity(comparison_id: str, objective_id: str, compared_id: str) -> str:
    key = json.dumps([comparison_id, objective_id, compared_id])
    return "CASE-" + hashlib.sha256(key.encode()).hexdigest()[:24]


def build_annotation_cases(comparisons: List[Comparison], pairs: List[GroundTruthPair]) -> List[AnnotationCase]:
    cases = {}
    for comparison in sorted(comparisons, key=lambda c: c.id):
        for match in sorted(comparison.matches, key=lambda m: m.id):
            case_id = case_identity(comparison.id, match.objective_item_id, match.compared_item_id)
            if case_id in cases:
                continue
            cases[case_id] = AnnotationCase(
                case_id, comparison.id, comparison.model_version, match.id,
                match.objective_item_id, match.compared_item_id,
                match.evidence.objective_snippet, match.evidence.compared_snippet,
                match.objective_page, match.compared_page, match.classification.value, match.score,
                "UNREVIEWED", [], 0,
            )
    known_comparisons = {c.id: c for c in comparisons}
    for pair in pairs:
        if pair.comparison_id not in known_comparisons:
            continue
        case_id = case_identity(pair.comparison_id, pair.objective_item_id, pair.compared_item_id)
        if case_id not in cases:
            example = pair.example
            cases[case_id] = AnnotationCase(
                case_id, pair.comparison_id, known_comparisons[pair.comparison_id].model_version,
                pair.match_id, pair.objective_item_id, pair.compared_item_id,
                example.objective_text, example.compared_text, example.source_page_obj, example.source_page_cmp,
                example.prediction_label if example.prediction_label in MatchClassification._value2member_map_ else None,
                None, "UNREVIEWED", [], 0,
            )
        case = cases[case_id]
        case.status = pair.status.value
        case.reviewer_ids = sorted(reviewer_key(v.reviewer_id) for v in pair.votes)
        case.review_count = pair.review_count
    for case in cases.values():
        case.reason = {"DISAGREEMENT": PriorityReason.DISAGREEMENT,
                       "SINGLE_REVIEW": PriorityReason.SECOND_REVIEW,
                       "UNREVIEWED": PriorityReason.UNREVIEWED}.get(case.status)
        if case.score is not None:
            case.boundary_distance = round(min(abs(case.score - t) for t in DEFAULT_THRESHOLDS.values()), 6)
            case.near_boundary = case.boundary_distance <= .05
        case.uncertain_prediction = case.classification == MatchClassification.UNCERTAIN.value
    return list(cases.values())


def prioritize_cases(
    cases: List[AnnotationCase], reviewer_id: Optional[str] = None, reason: Optional[PriorityReason] = None,
) -> List[AnnotationCase]:
    reviewer = reviewer_key(reviewer_id) if reviewer_id else None
    eligible = [case for case in cases if case.reason is not None
                and (reason is None or case.reason == reason)
                and not (case.status == "SINGLE_REVIEW" and reviewer in case.reviewer_ids)]
    order = {PriorityReason.DISAGREEMENT: 0, PriorityReason.SECOND_REVIEW: 1, PriorityReason.UNREVIEWED: 2}
    return sorted(eligible, key=lambda c: (
        order[c.reason], not c.uncertain_prediction,
        c.boundary_distance if c.boundary_distance is not None else 1.0,
        c.comparison_id, c.objective_item_id, c.compared_item_id, c.case_id,
    ))


def annotation_coverage(cases: List[AnnotationCase]) -> AnnotationCoverage:
    total = len(cases)
    reviewed = sum(c.status != "UNREVIEWED" for c in cases)
    consensus = sum(c.status == "CONSENSUS" for c in cases)
    return AnnotationCoverage(
        total, reviewed, consensus, sum(c.status == "DISAGREEMENT" for c in cases),
        total - consensus, sum(c.review_count for c in cases),
        round(100 * reviewed / total, 2) if total else None,
        round(100 * consensus / total, 2) if total else None,
    )
