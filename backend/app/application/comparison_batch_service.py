"""Orquestación acotada de comparaciones, con avances e idempotencia durables."""

from collections.abc import Callable
from datetime import datetime, timezone
import logging
from uuid import UUID

from app.application.comparison_batch_ports import ComparisonBatchRepository, PairComparisonRunner
from app.domain.comparison_batch import (
    BatchNotFoundError, BatchRequestConflictError, BatchResult, BatchSourceNotFoundError,
    BatchSyllabus, BatchValidationError, ComparisonBatch, ComparisonBatchView,
    MAX_BATCH_CONTENT_PAIRS, validate_batch_ids,
)
from app.domain.ports import ISyllabusRepository
from app.domain.content import ContentItem
from app.domain.scoring import DEFAULT_THRESHOLDS, DEFAULT_WEIGHTS
from app.domain.syllabus import Syllabus

logger = logging.getLogger(__name__)


class ComparisonBatchQuery:
    def __init__(self, repository: ComparisonBatchRepository) -> None:
        self.repository = repository

    def get(self, batch_id: str) -> ComparisonBatchView:
        batch = self.repository.get(batch_id)
        if batch is None:
            raise BatchNotFoundError("El lote solicitado no existe.")
        # El cierre solo se inserta después de los resultados. Leerlo primero
        # evita anunciar un lote finalizado con una lectura parcial concurrente.
        completed_at = self.repository.get_completion(batch_id)
        return ComparisonBatchView(batch, self.repository.get_results(batch_id), completed_at)

    def list_recent(self, limit: int = 20) -> list[ComparisonBatchView]:
        return [self.get(batch.id) for batch in self.repository.list_recent(limit)]


class CompareSyllabusBatch:
    def __init__(
        self, syllabi: ISyllabusRepository, repository: ComparisonBatchRepository,
        runner_factory: Callable[[], tuple[PairComparisonRunner, str]],
    ) -> None:
        self.syllabi = syllabi
        self.repository = repository
        self.runner_factory = runner_factory
        self.query = ComparisonBatchQuery(repository)

    def _existing(self, batch_id: str, objective_id: str, candidates: tuple[str, ...]) -> ComparisonBatchView | None:
        existing = self.repository.get(batch_id)
        if existing is None:
            return None
        if existing.objective.id != objective_id or tuple(item.id for item in existing.candidates) != candidates:
            raise BatchRequestConflictError("La clave de solicitud ya corresponde a otro lote. Inicie una solicitud nueva.")
        return self.query.get(batch_id)

    def _source(self, syllabus_id: str) -> Syllabus:
        syllabus = self.syllabi.get_by_id(syllabus_id)
        if syllabus is None:
            raise BatchSourceNotFoundError(f"No existe el sílabo '{syllabus_id}'.")
        return syllabus

    @staticmethod
    def _summary(syllabus: Syllabus) -> BatchSyllabus:
        return BatchSyllabus(syllabus.id, syllabus.course_name or syllabus.filename, syllabus.university)

    @staticmethod
    def _compare_candidate(
        batch: ComparisonBatch, runner: PairComparisonRunner, objective: Syllabus, candidate: Syllabus,
        objective_items: list[ContentItem], items: list[ContentItem],
    ) -> BatchResult:
        if not items:
            return BatchResult(candidate.id, error_code="NO_CONTENT", error="El candidato no contiene contenidos temáticos identificables.")
        try:
            comparison = runner.execute(
                objective_syllabus_id=objective.id, compared_syllabus_id=candidate.id,
                objective_items=objective_items, compared_items=items,
                weights=dict(batch.weights), thresholds=dict(batch.thresholds),
                objective_pdf_path=objective.file_path, compared_pdf_path=candidate.file_path,
            )
            if (comparison.objective_syllabus_id, comparison.compared_syllabus_id, comparison.model_version) != (
                objective.id, candidate.id, batch.model_version,
            ):
                raise BatchValidationError("La comparación no corresponde a los documentos y modelo del lote.")
            return BatchResult(candidate.id, comparison.id, comparison.global_score,
                               comparison.objective_coverage, comparison.compared_coverage,
                               comparison.count_by_classification)
        except Exception:
            logger.exception("Falló el candidato %s del lote %s", candidate.id, batch.id)
            return BatchResult(candidate.id, error_code="COMPARISON_FAILED",
                               error="No se pudo completar esta comparación. Los demás resultados se conservan.")

    def execute(self, request_id: UUID, objective_id: str, candidate_ids: tuple[str, ...]) -> tuple[ComparisonBatchView, bool]:
        validate_batch_ids(objective_id, candidate_ids)
        batch_id = f"CB-{request_id.hex}"
        existing = self._existing(batch_id, objective_id, candidate_ids)
        if existing is not None:
            return existing, False
        objective = self._source(objective_id)
        candidates = [self._source(candidate_id) for candidate_id in candidate_ids]
        objective_items = self.syllabi.get_content_items(objective_id)
        if not objective_items:
            raise BatchValidationError("El sílabo objetivo no contiene contenidos temáticos identificables.")
        candidate_items = [self.syllabi.get_content_items(candidate.id) for candidate in candidates]
        if sum(len(objective_items) * len(items) for items in candidate_items) > MAX_BATCH_CONTENT_PAIRS:
            raise BatchValidationError("El lote supera el presupuesto de 20000 pares de contenidos; reduzca los candidatos.")
        runner, model_version = self.runner_factory()
        batch = ComparisonBatch(
            id=batch_id, objective=self._summary(objective), candidates=tuple(self._summary(item) for item in candidates),
            model_version=model_version, weights=dict(DEFAULT_WEIGHTS), thresholds=dict(DEFAULT_THRESHOLDS),
            created_at=datetime.now(timezone.utc),
        )
        if not self.repository.create(batch):
            existing = self._existing(batch_id, objective_id, candidate_ids)
            if existing is None:
                raise BatchRequestConflictError("No se pudo recuperar la solicitud existente; consulte el historial.")
            return existing, False
        for candidate, items in zip(candidates, candidate_items):
            self.repository.add_result(batch_id, self._compare_candidate(batch, runner, objective, candidate, objective_items, items))
        self.repository.complete(batch_id, datetime.now(timezone.utc))
        return self.query.get(batch_id), True
