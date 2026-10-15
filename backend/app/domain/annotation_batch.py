"""Snapshots de selección y cierre de lotes de anotación."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

from app.domain.active_learning import AnnotationCase, AnnotationCoverage


@dataclass(frozen=True)
class AnnotationBatch:
    id: str
    reviewer_id: str
    comparison_id: Optional[str]
    strategy_version: str
    reference_thresholds: Dict[str, float]
    created_at: datetime
    cases: List[AnnotationCase]
    coverage_before: AnnotationCoverage
    scope_before: AnnotationCoverage


@dataclass(frozen=True)
class AnnotationBatchCompletion:
    batch_id: str
    completed_at: datetime
    coverage_after: AnnotationCoverage
    scope_after: AnnotationCoverage


@dataclass(frozen=True)
class AnnotationBatchProgress:
    batch: AnnotationBatch
    completion: Optional[AnnotationBatchCompletion]
    items: List[AnnotationCase]
    coverage_current: AnnotationCoverage
    scope_current: AnnotationCoverage
    eligible_case_ids: List[str]


class AnnotationBatchNotFoundError(ValueError):
    pass


class AnnotationSourceUnavailableError(ValueError):
    pass


class NoAnnotationCandidatesError(ValueError):
    pass
