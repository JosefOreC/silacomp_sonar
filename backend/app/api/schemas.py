"""
Esquemas Pydantic para serialización y validación de la API REST.
"""

from datetime import datetime
from typing import Dict, List, Optional
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


class MatchEvidenceResponse(BaseModel):
    evidence_type: str
    shared_keywords: List[str]
    semantic_score: float
    lexical_score: float
    objective_snippet: str
    compared_snippet: str
    objective_page: int
    compared_page: int


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
