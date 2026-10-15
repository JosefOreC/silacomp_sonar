"""Consolidación de anotaciones y acuerdo nominal, sin dependencias de infraestructura."""

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from typing import Dict, List, Optional, Tuple

from app.domain.comparison import MatchClassification
from app.domain.review import DatasetExample, Review


class ConsensusStatus(str, Enum):
    SINGLE_REVIEW = "SINGLE_REVIEW"
    CONSENSUS = "CONSENSUS"
    DISAGREEMENT = "DISAGREEMENT"


def reviewer_key(reviewer_id: str) -> str:
    return " ".join(reviewer_id.casefold().split())


@dataclass
class GroundTruthPair:
    comparison_id: str
    objective_item_id: str
    compared_item_id: str
    match_id: Optional[str]
    status: ConsensusStatus
    consensus_label: Optional[MatchClassification]
    votes: List[Review]
    review_count: int
    example: DatasetExample


@dataclass(frozen=True)
class ReviewerAgreement:
    reviewer_a: str
    reviewer_b: str
    common_pairs: int
    agreements: int
    observed_agreement: Optional[float]
    expected_agreement: Optional[float]
    cohen_kappa: Optional[float]


def consolidate_reviews(reviews: List[Review], examples: List[DatasetExample]) -> List[GroundTruthPair]:
    """Un voto vigente por autor y por par; nunca sobreescribe los eventos fuente."""
    examples_by_review = {ex.review_id: ex for ex in sorted(examples, key=lambda ex: ex.id)}
    grouped: Dict[Tuple[str, str, str], List[Tuple[Review, DatasetExample]]] = {}
    for review in reviews:
        example = examples_by_review.get(review.id)
        if not example or not reviewer_key(review.reviewer_id):
            continue
        if example.objective_item_id == "UNKNOWN" or example.compared_item_id == "UNKNOWN":
            continue
        key = (review.comparison_id, example.objective_item_id, example.compared_item_id)
        grouped.setdefault(key, []).append((review, example))

    pairs = []
    for (comparison_id, objective_id, compared_id), entries in sorted(grouped.items()):
        entries.sort(key=lambda entry: (entry[0].created_at, entry[0].id))
        latest = {reviewer_key(review.reviewer_id): review for review, _ in entries}
        votes = [latest[key] for key in sorted(latest)]
        labels = {review.human_decision for review in votes}
        if len(votes) == 1:
            status = ConsensusStatus.SINGLE_REVIEW
        elif len(labels) == 1:
            status = ConsensusStatus.CONSENSUS
        else:
            status = ConsensusStatus.DISAGREEMENT
        required_features = {"semantic_sim", "lexical_sim", "structural_sim", "keyword_overlap"}
        example = next((ex for _, ex in reversed(entries) if required_features <= ex.features.keys()), entries[-1][1])
        match_id = next((review.match_id for review, _ in reversed(entries) if review.match_id), None)
        pairs.append(GroundTruthPair(
            comparison_id=comparison_id, objective_item_id=objective_id, compared_item_id=compared_id,
            match_id=match_id, status=status,
            consensus_label=votes[0].human_decision if status == ConsensusStatus.CONSENSUS else None,
            votes=votes, review_count=len(entries), example=example,
        ))
    return pairs


def reviewer_agreements(pairs: List[GroundTruthPair]) -> List[ReviewerAgreement]:
    """Kappa nominal de Cohen por pareja, usando únicamente pares compartidos."""
    reviewers = sorted({reviewer_key(v.reviewer_id) for pair in pairs for v in pair.votes})
    result = []
    for a, b in combinations(reviewers, 2):
        labels_a, labels_b = [], []
        for pair in pairs:
            votes = {reviewer_key(v.reviewer_id): v.human_decision.value for v in pair.votes}
            if a in votes and b in votes:
                labels_a.append(votes[a])
                labels_b.append(votes[b])
        n = len(labels_a)
        agreements = sum(a_label == b_label for a_label, b_label in zip(labels_a, labels_b))
        observed = agreements / n if n else None
        expected = None
        kappa = None
        if n:
            count_a, count_b = Counter(labels_a), Counter(labels_b)
            expected = sum(count_a[label] * count_b[label] for label in set(count_a) | set(count_b)) / (n * n)
            if expected < 1.0:
                kappa = (observed - expected) / (1.0 - expected)
        result.append(ReviewerAgreement(
            a, b, n, agreements, observed, expected, kappa,
        ))
    return result
