"""Puertos del lote; independientes del transporte y la persistencia concreta."""

from datetime import datetime
from typing import Protocol

from app.domain.comparison import Comparison
from app.domain.comparison_batch import BatchResult, ComparisonBatch
from app.domain.content import ContentItem


class PairComparisonRunner(Protocol):
    def execute(
        self, *, objective_syllabus_id: str, compared_syllabus_id: str,
        objective_items: list[ContentItem], compared_items: list[ContentItem],
        weights: dict[str, float] | None = None, thresholds: dict[str, float] | None = None,
        objective_pdf_path: str | None = None, compared_pdf_path: str | None = None,
    ) -> Comparison: ...


class ComparisonBatchRepository(Protocol):
    def create(self, batch: ComparisonBatch) -> bool: ...
    def get(self, batch_id: str) -> ComparisonBatch | None: ...
    def list_recent(self, limit: int) -> list[ComparisonBatch]: ...
    def add_result(self, batch_id: str, result: BatchResult) -> None: ...
    def get_results(self, batch_id: str) -> tuple[BatchResult, ...]: ...
    def complete(self, batch_id: str, completed_at: datetime) -> None: ...
    def get_completion(self, batch_id: str) -> datetime | None: ...
