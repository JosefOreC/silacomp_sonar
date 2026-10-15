"""Consultas reproducibles de ground truth y observaciones consensuadas."""

from dataclasses import replace
import hashlib
import json
from typing import List, Optional

from app.domain.ground_truth import ConsensusStatus, GroundTruthPair, consolidate_reviews
from app.domain.ports import IDatasetRepository, IReviewRepository
from app.domain.review import DatasetExample


class GroundTruthService:
    def __init__(self, review_repo: IReviewRepository, dataset_repo: IDatasetRepository) -> None:
        self.review_repo = review_repo
        self.dataset_repo = dataset_repo

    def get_pairs(self, comparison_id: Optional[str] = None) -> List[GroundTruthPair]:
        reviews = []
        offset = 0
        while True:
            batch = self.review_repo.list_all(limit=500, offset=offset)
            reviews.extend(r for r in batch if comparison_id is None or r.comparison_id == comparison_id)
            if len(batch) < 500:
                break
            offset += 500
        examples = []
        offset = 0
        while True:
            batch = self.dataset_repo.list_examples(limit=500, offset=offset)
            examples.extend(batch)
            if len(batch) < 500:
                break
            offset += 500
        return consolidate_reviews(reviews, examples)

    def consensus_examples(self, pairs: List[GroundTruthPair]) -> List[DatasetExample]:
        result = []
        for pair in pairs:
            if pair.status != ConsensusStatus.CONSENSUS:
                continue
            required = {"semantic_sim", "lexical_sim", "structural_sim", "keyword_overlap"}
            if not required <= pair.example.features.keys():
                raise ValueError("Hay pares consensuados sin características de comparación. Procese estos contenidos antes de entrenar.")
            identity = json.dumps([pair.comparison_id, pair.objective_item_id, pair.compared_item_id])
            result.append(replace(
                pair.example, id="GT-" + hashlib.sha256(identity.encode()).hexdigest()[:20],
                ground_truth_label=pair.consensus_label.value,
                source_review_ids=sorted(v.id for v in pair.votes),
            ))
        return result
