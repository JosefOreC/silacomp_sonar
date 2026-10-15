"""Exclusión transitiva de grupos reservados antes de entrenar o calibrar."""

from typing import List

from app.domain.academic_sources import academic_source_tokens
from app.domain.ports import IReservedEvaluationPolicy, IScientificEvaluationRepository
from app.domain.review import DatasetExample


class ReservedEvaluationPolicy(IReservedEvaluationPolicy):
    def __init__(self, repository: IScientificEvaluationRepository) -> None:
        self.repository = repository

    def filter_examples(self, examples: List[DatasetExample]) -> List[DatasetExample]:
        reserved = {tuple(token) for snapshot in self.repository.list_snapshots()
                    for token in snapshot.payload["reserved_source_tokens"]}
        remaining = list(examples)
        while True:
            kept = []
            for example in remaining:
                tokens = set(academic_source_tokens(example))
                if tokens & reserved:
                    reserved.update(tokens)
                else:
                    kept.append(example)
            if len(kept) == len(remaining):
                return kept
            remaining = kept
