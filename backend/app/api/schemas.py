"""
Esquemas Pydantic para serialización y validación de la API REST.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from app.domain.comparison import MatchClassification
from app.domain.review import CorrectionType
from app.domain.ground_truth import ConsensusStatus
from app.domain.active_learning import PriorityReason


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


class GroundTruthVoteResponse(BaseModel):
    review_id: str
    reviewer_id: str
    human_decision: MatchClassification
    justification: str
    created_at: datetime


class GroundTruthPairResponse(BaseModel):
    comparison_id: str
    objective_item_id: str
    compared_item_id: str
    match_id: Optional[str]
    objective_text: str
    compared_text: str
    prediction_label: str
    features: Dict[str, float]
    feature_source_review_id: str
    source_university_obj: Optional[str]
    source_university_cmp: Optional[str]
    source_course_obj: Optional[str]
    source_course_cmp: Optional[str]
    source_syllabus_obj: Optional[str]
    source_syllabus_cmp: Optional[str]
    source_page_obj: Optional[int]
    source_page_cmp: Optional[int]
    status: ConsensusStatus
    consensus_label: Optional[MatchClassification]
    reviewer_count: int
    review_count: int
    votes: List[GroundTruthVoteResponse]


class GroundTruthSummaryResponse(BaseModel):
    total_pairs: int
    consensus_pairs: int
    disagreement_pairs: int
    single_review_pairs: int
    linked_review_events: int


class GroundTruthPageResponse(BaseModel):
    summary: GroundTruthSummaryResponse
    total: int
    limit: int
    offset: int
    items: List[GroundTruthPairResponse]


class ReviewerAgreementResponse(BaseModel):
    reviewer_a: str
    reviewer_b: str
    common_pairs: int
    agreements: int
    observed_agreement: Optional[float]
    expected_agreement: Optional[float]
    cohen_kappa: Optional[float]


class AnnotationCoverageResponse(BaseModel):
    total_pairs: int
    reviewed_pairs: int
    consensus_pairs: int
    disagreement_pairs: int
    pending_pairs: int
    review_events: int
    reviewed_percentage: Optional[float]
    consensus_percentage: Optional[float]


class AnnotationCaseResponse(BaseModel):
    case_id: str
    comparison_id: str
    model_version: str
    match_id: Optional[str]
    objective_item_id: str
    compared_item_id: str
    objective_text: str
    compared_text: str
    objective_page: Optional[int]
    compared_page: Optional[int]
    classification: Optional[MatchClassification]
    score: Optional[float]
    status: Literal["UNREVIEWED", "SINGLE_REVIEW", "DISAGREEMENT", "CONSENSUS"]
    reviewer_ids: List[str]
    review_count: int
    reason: Optional[PriorityReason]
    boundary_distance: Optional[float]
    uncertain_prediction: bool
    near_boundary: bool


class AnnotationQueueResponse(BaseModel):
    strategy_version: str
    reference_thresholds: Dict[str, float]
    coverage: AnnotationCoverageResponse
    total: int
    limit: int
    offset: int
    items: List[AnnotationCaseResponse]


class CreateAnnotationBatchRequest(BaseModel):
    reviewer_id: str = Field(min_length=1, max_length=200)
    limit: int = Field(default=10, ge=1, le=100)
    comparison_id: Optional[str] = None
    reason: Optional[PriorityReason] = None


class AnnotationBatchResponse(BaseModel):
    id: str
    reviewer_id: str
    comparison_id: Optional[str]
    strategy_version: str
    reference_thresholds: Dict[str, float]
    created_at: datetime
    cases: List[AnnotationCaseResponse]
    coverage_before: AnnotationCoverageResponse
    scope_before: AnnotationCoverageResponse


class AnnotationBatchCompletionResponse(BaseModel):
    batch_id: str
    completed_at: datetime
    coverage_after: AnnotationCoverageResponse
    scope_after: AnnotationCoverageResponse


class AnnotationBatchProgressResponse(BaseModel):
    batch: AnnotationBatchResponse
    completion: Optional[AnnotationBatchCompletionResponse]
    items: List[AnnotationCaseResponse]
    coverage_current: AnnotationCoverageResponse
    scope_current: AnnotationCoverageResponse
    eligible_case_ids: List[str]


class CreateEvaluationSnapshotRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    comparison_ids: List[str] = Field(min_length=1, max_length=20)


class EvaluationSnapshotResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    content_hash: str
    comparison_count: int
    pair_count: int
    independent_groups: int


class EvaluationCriteria(BaseModel):
    min_f1_gain: float = Field(default=0.01, gt=0, le=1)
    max_recall_drop: float = Field(default=0, ge=0, le=1)
    max_coverage_mae_increase: float = Field(default=0, ge=0, le=100)
    max_per_comparison_f1_drop: float = Field(default=0.05, ge=0, le=1)
    max_per_comparison_coverage_increase: float = Field(default=0, ge=0, le=100)
    min_independent_groups: int = Field(default=2, ge=2)


class CreateEvaluationExperimentRequest(BaseModel):
    snapshot_id: str
    reference_version: str = "bipartite-adaptive-002"
    candidate_version: str
    criteria: EvaluationCriteria = Field(default_factory=EvaluationCriteria)


class EvaluationExperimentResponse(BaseModel):
    id: str
    snapshot_id: str
    created_at: datetime
    report: Dict[str, Any]


# --- Modelos y Machine Learning (Fase 2.0) ---

class TrainModelRequest(BaseModel):
    algorithm: str = Field(default="calibrated_logistic", description="calibrated_logistic o random_forest")
    test_size: float = Field(default=0.25, ge=0.1, le=0.5)
    use_bootstrap: bool = Field(default=True, description="Usar bootstrap si los ejemplos de revisiones son pocos")
    auto_activate: bool = Field(default=False, description="Activar automáticamente si supera al baseline")
    ground_truth_policy: Literal["individual", "consensus"] = "individual"


class ModelVersionResponse(BaseModel):
    version_id: str
    algorithm_name: str
    description: str
    is_active: bool
    created_at: datetime
    metrics: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
