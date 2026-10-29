"""Contratos de comparación por lotes, sin porcentajes académicos agregados."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


SyllabusId = Annotated[str, Field(min_length=1, max_length=100)]


class CreateComparisonBatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: UUID
    objective_syllabus_id: SyllabusId
    compared_syllabus_ids: list[SyllabusId] = Field(min_length=1, max_length=5)


class BatchSyllabusResponse(BaseModel):
    id: str
    title: str
    university: str | None


class BatchResultResponse(BaseModel):
    compared_syllabus_id: str
    comparison_id: str | None
    global_score: float | None
    objective_coverage: float | None
    compared_coverage: float | None
    counts: dict[str, int]
    error_code: str | None
    error: str | None


class ComparisonBatchResponse(BaseModel):
    id: str
    objective: BatchSyllabusResponse
    candidates: list[BatchSyllabusResponse]
    model_version: str
    weights: dict[str, float]
    thresholds: dict[str, float]
    created_at: datetime
    completed_at: datetime | None
    status: Literal["RUNNING", "COMPLETED", "PARTIAL", "FAILED"]
    ranking_rule: str
    ranking: list[str]
    results: list[BatchResultResponse]
