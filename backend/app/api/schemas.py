"""
Esquemas Pydantic para serialización y validación de la API REST.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.domain.comparison import MatchClassification
from app.domain.review import CorrectionType


# --- Sílabos ---

class SyllabusResponse(BaseModel):
    id: str
    filename: str
    total_pages: int
    file_size_bytes: int
    sha256_hash: str
    university: Optional[str] = None
    course_name: Optional[str] = None
    course_code: Optional[str] = None
    total_characters: int
    created_at: datetime
    is_scanned: bool = False
    ocr_applied: bool = False
    ocr_engine_name: Optional[str] = None


class ContentItemResponse(BaseModel):
    id: str
    syllabus_id: str
    section_name: str
    title: str
    text: str
    page_start: int
    page_end: int
    order: int
    unit_number: Optional[int] = None


# --- Comparaciones ---

class CreateComparisonRequest(BaseModel):
    objective_syllabus_id: str
    compared_syllabus_id: str
    weights: Optional[Dict[str, float]] = None
    thresholds: Optional[Dict[str, float]] = None


class ScoreBreakdownResponse(BaseModel):
    semantic_similarity: float
    lexical_similarity: float
    keyword_overlap: float
    structural_similarity: float
    composite_score: float
    weights: Dict[str, float]


class EvidenceRegionResponse(BaseModel):
    id: str
    match_id: str
    syllabus_id: str
    content_id: str
    page_number: int
    page_width: float
    page_height: float
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    evidence_type: str = "COMBINED"


class MatchEvidenceResponse(BaseModel):
    evidence_type: str
    shared_keywords: List[str]
    semantic_score: float
    lexical_score: float
    objective_snippet: str
    compared_snippet: str
    objective_page: int
    compared_page: int
    objective_regions: List[EvidenceRegionResponse] = Field(default_factory=list)
    compared_regions: List[EvidenceRegionResponse] = Field(default_factory=list)


class MatchSpatialEvidenceResponse(BaseModel):
    match_id: str
    composite_score: float
    classification: MatchClassification
    objective_title: str
    compared_title: str
    objective_page: int
    compared_page: int
    objective_regions: List[EvidenceRegionResponse] = Field(default_factory=list)
    compared_regions: List[EvidenceRegionResponse] = Field(default_factory=list)


class ComparisonEvidenceCatalogResponse(BaseModel):
    comparison_id: str
    total_matches: int
    evidence_items: List[MatchSpatialEvidenceResponse]


class ContentMatchResponse(BaseModel):
    id: str
    comparison_id: str
    objective_item_id: str
    compared_item_id: str
    objective_title: str
    compared_title: str
    objective_section: str
    compared_section: str
    objective_page: int
    compared_page: int
    score_breakdown: ScoreBreakdownResponse
    classification: MatchClassification
    evidence: MatchEvidenceResponse


class UnmatchedItemResponse(BaseModel):
    item_id: str
    syllabus_id: str
    section_name: str
    title: str
    text_snippet: str
    page: int
    best_candidate_id: Optional[str] = None
    best_candidate_title: Optional[str] = None
    best_score: Optional[float] = None


class ComparisonResponse(BaseModel):
    id: str
    objective_syllabus_id: str
    compared_syllabus_id: str
    global_score: float
    objective_coverage: float
    compared_coverage: float
    model_version: str
    created_at: datetime
    counts: Dict[str, int]
    matches: List[ContentMatchResponse]
    unmatched_objective: List[UnmatchedItemResponse]
    unmatched_compared: List[UnmatchedItemResponse]


# --- Revisiones ---

class CreateReviewRequest(BaseModel):
    comparison_id: str
    match_id: Optional[str] = None
    prediction_before: Optional[MatchClassification] = None
    human_decision: MatchClassification
    correction_type: CorrectionType
    justification: str = Field(min_length=3)
    reviewer_id: str = "DOCENTE_REVISOR"
    manual_objective_item_id: Optional[str] = None
    manual_compared_item_id: Optional[str] = None


class ReviewResponse(BaseModel):
    id: str
    comparison_id: str
    match_id: Optional[str]
    prediction_before: Optional[MatchClassification]
    human_decision: MatchClassification
    correction_type: CorrectionType
    justification: str
    reviewer_id: str
    model_version: str
    created_at: datetime


# --- Dataset ---

class DatasetStatsResponse(BaseModel):
    total_examples: int
    by_ground_truth: Dict[str, int]
    model_version: str


# --- Modelos y Machine Learning (Fase 2.0) ---

class TrainModelRequest(BaseModel):
    algorithm: str = Field(default="calibrated_logistic", description="calibrated_logistic o random_forest")
    test_size: float = Field(default=0.25, ge=0.1, le=0.5)
    use_bootstrap: bool = Field(default=True, description="Usar bootstrap si los ejemplos de revisiones son pocos")
    auto_activate: bool = Field(default=False, description="Activar automáticamente si supera al baseline")


class ModelVersionResponse(BaseModel):
    version_id: str
    algorithm_name: str
    description: str
    is_active: bool
    created_at: datetime
    metrics: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
