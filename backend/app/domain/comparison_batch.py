"""Comparaciones independientes de un objetivo frente a varios candidatos."""

from dataclasses import dataclass, field
from datetime import datetime
import math

MAX_BATCH_CANDIDATES = 5
MAX_BATCH_CONTENT_PAIRS = 20_000
RANKING_RULE = "objective_coverage_desc_global_score_desc_id_asc"


class BatchValidationError(ValueError):
    """La solicitud no satisface los límites del lote."""


class BatchNotFoundError(LookupError):
    """No existe el lote solicitado."""


class BatchSourceNotFoundError(LookupError):
    """No existe uno de los documentos solicitados."""


class BatchRequestConflictError(ValueError):
    """Una clave de solicitud ya identifica otros documentos."""


def validate_batch_ids(objective_id: str, candidate_ids: tuple[str, ...]) -> None:
    if not objective_id.strip() or any(not value.strip() for value in candidate_ids):
        raise BatchValidationError("Identifique el objetivo y todos los candidatos.")
    if not 1 <= len(candidate_ids) <= MAX_BATCH_CANDIDATES:
        raise BatchValidationError("Seleccione entre uno y cinco candidatos.")
    if len(set(candidate_ids)) != len(candidate_ids):
        raise BatchValidationError("No repita candidatos dentro del lote.")
    if objective_id in candidate_ids:
        raise BatchValidationError("El objetivo no puede compararse consigo mismo.")


@dataclass(frozen=True)
class BatchSyllabus:
    id: str
    title: str
    university: str | None


@dataclass(frozen=True)
class ComparisonBatch:
    id: str
    objective: BatchSyllabus
    candidates: tuple[BatchSyllabus, ...]
    model_version: str
    weights: dict[str, float]
    thresholds: dict[str, float]
    created_at: datetime

    def __post_init__(self) -> None:
        validate_batch_ids(self.objective.id, tuple(candidate.id for candidate in self.candidates))


@dataclass(frozen=True)
class BatchResult:
    compared_syllabus_id: str
    comparison_id: str | None = None
    global_score: float | None = None
    objective_coverage: float | None = None
    compared_coverage: float | None = None
    counts: dict[str, int] = field(default_factory=dict)
    error_code: str | None = None
    error: str | None = None

    def __post_init__(self) -> None:
        values = (self.global_score, self.objective_coverage, self.compared_coverage)
        if self.comparison_id is None:
            if any(value is not None for value in values) or not self.error or not self.error_code:
                raise BatchValidationError("Un resultado fallido requiere una causa y no contiene puntuaciones.")
        elif self.error is not None or self.error_code is not None or any(
            value is None or not math.isfinite(value) or not 0 <= value <= maximum
            for value, maximum in zip(values, (1, 100, 100))
        ):
            raise BatchValidationError("El resultado debe conservar puntuaciones válidas de una comparación.")


@dataclass(frozen=True)
class ComparisonBatchView:
    batch: ComparisonBatch
    results: tuple[BatchResult, ...]
    completed_at: datetime | None

    @property
    def status(self) -> str:
        if self.completed_at is None:
            return "RUNNING"
        successful = sum(result.comparison_id is not None for result in self.results)
        if successful == len(self.batch.candidates):
            return "COMPLETED"
        return "PARTIAL" if successful else "FAILED"

    @property
    def ranking(self) -> list[str]:
        successful = [result for result in self.results if result.comparison_id is not None]
        ordered = sorted(successful, key=lambda result: (
            -(result.objective_coverage or 0), -(result.global_score or 0), result.compared_syllabus_id,
        ))
        return [result.compared_syllabus_id for result in ordered]
