"""Consenso y acuerdo sobre revisiones humanas sin modelos ni base de datos."""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from app.application.ground_truth_service import GroundTruthService
from app.domain.comparison import MatchClassification as Label
from app.domain.ground_truth import ConsensusStatus, consolidate_reviews, reviewer_agreements
from app.domain.review import CorrectionType, DatasetExample, Review


def annotation(index: int, reviewer: str, label: Label, pair: int = 0) -> tuple[Review, DatasetExample]:
    review = Review(
        id=f"REV-{index:04}", comparison_id="COMP", match_id=f"MATCH-{pair}",
        prediction_before=Label.MATCH, human_decision=label, correction_type=CorrectionType.CONFIRMED,
        justification="Revisión de evidencia", reviewer_id=reviewer, model_version="baseline",
        created_at=datetime(2026, 10, 15) + timedelta(seconds=index),
    )
    example = DatasetExample(
        id=f"DATA-{index:04}", review_id=review.id, objective_item_id=f"OBJ-{pair}",
        compared_item_id=f"CMP-{pair}", objective_text="Objetivo", compared_text="Comparado",
        features={"semantic_sim": .9, "lexical_sim": .8, "keyword_overlap": .5, "structural_sim": .5},
        ground_truth_label=label.value,
    )
    return review, example


def pairs_from(annotations):
    return consolidate_reviews([r for r, _ in annotations], [ex for _, ex in annotations])


def test_latest_vote_deduplicates_author_without_mutating_history() -> None:
    annotations = [annotation(1, " DOCENTE A ", Label.MATCH), annotation(2, "docente   a", Label.NO_MATCH)]
    pair = pairs_from(annotations)[0]
    assert pair.status == ConsensusStatus.SINGLE_REVIEW
    assert len(pair.votes) == 1
    assert pair.votes[0].human_decision == Label.NO_MATCH
    assert pair.review_count == 2
    assert annotations[0][0].human_decision == Label.MATCH
    with pytest.raises(FrozenInstanceError):
        annotations[0][0].human_decision = Label.NO_MATCH


def test_disagreement_is_not_resolved_by_majority_and_can_be_corrected() -> None:
    annotations = [annotation(1, "A", Label.MATCH), annotation(2, "B", Label.MATCH), annotation(3, "C", Label.NO_MATCH)]
    pair = pairs_from(annotations)[0]
    assert pair.status == ConsensusStatus.DISAGREEMENT
    assert pair.consensus_label is None
    annotations.append(annotation(4, "C", Label.MATCH))
    pair = pairs_from(annotations)[0]
    assert pair.status == ConsensusStatus.CONSENSUS
    assert pair.consensus_label == Label.MATCH
    assert pair.review_count == 4


@pytest.mark.parametrize("labels_a,labels_b,expected", [
    ([Label.MATCH, Label.MATCH, Label.NO_MATCH, Label.NO_MATCH], [Label.MATCH, Label.MATCH, Label.MATCH, Label.NO_MATCH], .5),
    ([Label.MATCH, Label.NO_MATCH], [Label.MATCH, Label.NO_MATCH], 1.0),
    ([Label.MATCH, Label.MATCH], [Label.MATCH, Label.MATCH], None),
    ([Label.UNCERTAIN, Label.PARTIAL_MATCH], [Label.PARTIAL_MATCH, Label.UNCERTAIN], -1.0),
])
def test_cohen_kappa_uses_shared_pairs_and_preserves_four_labels(labels_a, labels_b, expected) -> None:
    annotations = []
    for index, (a, b) in enumerate(zip(labels_a, labels_b)):
        annotations.extend([annotation(index * 2, "A", a, index), annotation(index * 2 + 1, "B", b, index)])
    agreement = reviewer_agreements(pairs_from(annotations))[0]
    assert agreement.common_pairs == len(labels_a)
    if expected is None:
        assert agreement.cohen_kappa is None
    else:
        assert agreement.cohen_kappa == pytest.approx(expected)


def test_reviewers_without_common_pairs_have_undefined_agreement() -> None:
    pairs = pairs_from([annotation(1, "A", Label.MATCH, 1), annotation(2, "B", Label.MATCH, 2)])
    result = reviewer_agreements(pairs)[0]
    assert result.common_pairs == 0
    assert result.cohen_kappa is None
    assert result.observed_agreement is None


def test_manual_review_and_match_are_one_pair_with_feature_provenance() -> None:
    a = annotation(1, "A", Label.MATCH)
    b = annotation(2, "B", Label.MATCH)
    b = (replace(b[0], match_id=None, manual_objective_item_id="OBJ-0", manual_compared_item_id="CMP-0"),
         replace(b[1], features={}))
    pair = pairs_from([a, b])[0]
    assert pair.match_id == "MATCH-0"
    examples = GroundTruthService(Mock(), Mock()).consensus_examples([pair])
    assert len(examples) == 1
    assert examples[0].features == a[1].features
    assert examples[0].source_review_ids == ["REV-0001", "REV-0002"]


def test_ground_truth_service_reads_every_page() -> None:
    annotations = [annotation(i, "A", Label.MATCH, i) for i in range(501)]
    reviews, examples = [r for r, _ in annotations], [ex for _, ex in annotations]
    review_repo, dataset_repo = Mock(), Mock()
    review_repo.list_all.side_effect = lambda limit, offset: reviews[offset:offset + limit]
    dataset_repo.list_examples.side_effect = lambda limit, offset: examples[offset:offset + limit]
    pairs = GroundTruthService(review_repo, dataset_repo).get_pairs()
    assert len(pairs) == 501
    assert review_repo.list_all.call_count == 2
    assert dataset_repo.list_examples.call_count == 2
