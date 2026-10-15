"""Selección de anotaciones y medición reproducible de lotes."""

from datetime import datetime
from typing import List, Optional
import uuid

from app.application.ground_truth_service import GroundTruthService
from app.domain.active_learning import (
    AnnotationCase, PriorityReason, STRATEGY_VERSION, annotation_coverage, build_annotation_cases, prioritize_cases,
)
from app.domain.annotation_batch import (
    AnnotationBatch, AnnotationBatchCompletion, AnnotationBatchProgress, AnnotationBatchNotFoundError,
    AnnotationSourceUnavailableError, NoAnnotationCandidatesError,
)
from app.domain.ports import IAnnotationBatchRepository, IComparisonRepository
from app.domain.scoring import DEFAULT_THRESHOLDS


class ActiveLearningService:
    def __init__(
        self, comparisons: IComparisonRepository, ground_truth: GroundTruthService,
        batches: IAnnotationBatchRepository,
    ) -> None:
        self.comparisons = comparisons
        self.ground_truth = ground_truth
        self.batches = batches

    def get_cases(self, comparison_id: Optional[str] = None) -> List[AnnotationCase]:
        if comparison_id is not None:
            comparison = self.comparisons.get_by_id(comparison_id)
            if comparison is None:
                raise AnnotationSourceUnavailableError("Comparación no encontrada.")
            comparisons = [comparison]
        else:
            # El historial devuelve resúmenes; la cola necesita también las correspondencias no revisadas.
            comparisons = []
            for summary in self.comparisons.list_all():
                comparison = self.comparisons.get_by_id(summary.id)
                if comparison is not None:
                    comparisons.append(comparison)
        return build_annotation_cases(comparisons, self.ground_truth.get_pairs(comparison_id))

    def create_batch(
        self, reviewer_id: str, limit: int, comparison_id: Optional[str] = None,
        reason: Optional[PriorityReason] = None,
    ) -> AnnotationBatchProgress:
        if not reviewer_id.strip() or not 1 <= limit <= 100:
            raise ValueError("Indique un revisor y un tamaño de lote entre 1 y 100.")
        cases = self.get_cases(comparison_id)
        selected = prioritize_cases(cases, reviewer_id, reason)[:limit]
        if not selected:
            raise NoAnnotationCandidatesError("No hay pares pendientes para este revisor y estos filtros.")
        batch = AnnotationBatch(
            id="BATCH-" + uuid.uuid4().hex, reviewer_id=reviewer_id.strip(), comparison_id=comparison_id,
            strategy_version=STRATEGY_VERSION, reference_thresholds=dict(DEFAULT_THRESHOLDS),
            created_at=datetime.now(), cases=selected,
            coverage_before=annotation_coverage(selected), scope_before=annotation_coverage(cases),
        )
        self.batches.save(batch)
        return AnnotationBatchProgress(batch, None, selected, batch.coverage_before, batch.scope_before,
                                       [case.case_id for case in selected])

    def get_batch_progress(self, batch_id: str) -> AnnotationBatchProgress:
        batch = self.batches.get_by_id(batch_id)
        if batch is None:
            raise AnnotationBatchNotFoundError("Lote no encontrado.")
        cases = self.get_cases(batch.comparison_id)
        by_id = {c.case_id: c for c in cases}
        if any(c.case_id not in by_id for c in batch.cases):
            raise AnnotationSourceUnavailableError("Alguna comparación o contenido del lote ya no está disponible.")
        selected = [by_id[c.case_id] for c in batch.cases]
        return AnnotationBatchProgress(
            batch, self.batches.get_completion(batch_id), selected,
            annotation_coverage(selected), annotation_coverage(cases),
            [case.case_id for case in prioritize_cases(selected, batch.reviewer_id)],
        )

    def complete_batch(self, batch_id: str) -> AnnotationBatchProgress:
        progress = self.get_batch_progress(batch_id)
        if progress.completion is None:
            self.batches.complete(AnnotationBatchCompletion(
                batch_id, datetime.now(), progress.coverage_current, progress.scope_current,
            ))
        return self.get_batch_progress(batch_id)
