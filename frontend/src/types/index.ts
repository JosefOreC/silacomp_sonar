/**
 * Contratos de tipos para el Frontend de Comparación de Sílabos (ConvComp).
 * Sincronizado estrictamente con los contratos de dominio del backend.
 */

export type MatchClassification = 'MATCH' | 'PARTIAL_MATCH' | 'UNCERTAIN' | 'NO_MATCH';

export type AppTab = 'upload' | 'dashboard' | 'results' | 'dataset' | 'models' | 'batches';

export interface ComparisonBatchRequest {
  request_id: string;
  objective_syllabus_id: string;
  compared_syllabus_ids: string[];
}

export interface BatchSyllabus {
  id: string;
  title: string;
  university: string | null;
}

export interface BatchResult {
  compared_syllabus_id: string;
  comparison_id: string | null;
  global_score: number | null;
  objective_coverage: number | null;
  compared_coverage: number | null;
  counts: Partial<Record<MatchClassification, number>>;
  error_code: string | null;
  error: string | null;
}

export interface ComparisonBatch {
  id: string;
  objective: BatchSyllabus;
  candidates: BatchSyllabus[];
  model_version: string;
  weights: Record<string, number>;
  thresholds: Record<string, number>;
  created_at: string;
  completed_at: string | null;
  status: 'RUNNING' | 'COMPLETED' | 'PARTIAL' | 'FAILED';
  ranking_rule: string;
  ranking: string[];
  results: BatchResult[];
}

export type CorrectionType =
  | 'CONFIRMED'
  | 'FALSE_POSITIVE'
  | 'FALSE_NEGATIVE'
  | 'OVERESTIMATION'
  | 'UNDERESTIMATION'
  | 'MANUAL_LINK';

export interface ScoreBreakdown {
  semantic_similarity: number;
  lexical_similarity: number;
  keyword_overlap: number;
  structural_similarity: number;
  composite_score: number;
  weights: Record<string, number>;
}

export interface EvidenceRegion {
  id: string;
  match_id: string;
  syllabus_id: string;
  content_id: string;
  page_number: number;
  page_width: number;
  page_height: number;
  x0: number;
  y0: number;
  x1: number;
  y1: number;
  text: string;
  evidence_type: string;
}

export interface MatchEvidence {
  evidence_type: 'LEXICAL' | 'SEMANTIC' | 'HYBRID';
  shared_keywords: string[];
  semantic_score: number;
  lexical_score: number;
  objective_snippet: string;
  compared_snippet: string;
  objective_page: number;
  compared_page: number;
  objective_regions?: EvidenceRegion[];
  compared_regions?: EvidenceRegion[];
}

export interface MatchSpatialEvidence {
  match_id: string;
  composite_score: number;
  classification: MatchClassification;
  objective_title: string;
  compared_title: string;
  objective_page: number;
  compared_page: number;
  objective_regions: EvidenceRegion[];
  compared_regions: EvidenceRegion[];
}

export interface ComparisonEvidenceCatalog {
  comparison_id: string;
  total_matches: number;
  evidence_items: MatchSpatialEvidence[];
}

export interface ContentMatch {
  id: string;
  comparison_id: string;
  objective_item_id: string;
  compared_item_id: string;
  objective_title: string;
  compared_title: string;
  objective_section: string;
  compared_section: string;
  objective_page: number;
  compared_page: number;
  score_breakdown: ScoreBreakdown;
  classification: MatchClassification;
  evidence: MatchEvidence;
}

export interface UnmatchedItem {
  item_id: string;
  syllabus_id: string;
  section_name: string;
  title: string;
  text_snippet: string;
  page: number;
  best_candidate_id?: string;
  best_candidate_title?: string;
  best_score?: number;
}

export interface Comparison {
  id: string;
  objective_syllabus_id: string;
  compared_syllabus_id: string;
  global_score: number;
  objective_coverage: number;
  compared_coverage: number;
  model_version: string;
  created_at: string;
  matches: ContentMatch[];
  unmatched_objective: UnmatchedItem[];
  unmatched_compared: UnmatchedItem[];
  counts: Record<MatchClassification, number>;
}

export interface ComparisonSummary {
  id: string;
  objective_course: string | null;
  compared_course: string | null;
  objective_university: string | null;
  compared_university: string | null;
  global_score: number;
  objective_coverage: number;
  compared_coverage: number;
  model_version: string;
  created_at: string;
}

export interface Syllabus {
  id: string;
  filename: string;
  total_pages: number;
  file_size_bytes: number;
  university?: string;
  course_name?: string;
  course_code?: string;
  total_characters: number;
  created_at: string;
}

export interface HumanReviewPayload {
  comparison_id: string;
  match_id?: string;
  prediction_before?: MatchClassification;
  human_decision: MatchClassification;
  correction_type: CorrectionType;
  justification: string;
  reviewer_id: string;
  manual_objective_item_id?: string;
  manual_compared_item_id?: string;
}

export interface HumanReviewResponse {
  id: string;
  comparison_id: string;
  match_id?: string;
  human_decision: MatchClassification;
  correction_type: CorrectionType;
  justification: string;
  created_at: string;
}

// ─── Fase 2.0: Modelos de Aprendizaje Supervisado ────────────────────────────

export interface BaselineComparison {
  baseline_version?: string;
  evaluation_unit?: 'content_pair';
  includes_global_assignment?: boolean;
  uncertain_label_mapping?: string;
  baseline_accuracy: number;
  baseline_f1_macro: number;
  baseline_precision_macro: number;
  baseline_recall_macro: number;
  f1_gain: number;
  accuracy_gain: number;
  superior_to_baseline: boolean;
}

export interface ModelMetrics {
  data_provenance_schema?: number;
  ground_truth_policy?: 'individual' | 'consensus';
  source_review_ids?: string[];
  split?: {
    strategy: 'synthetic_stratified' | 'academic_connected_groups';
    evaluation_scope: 'synthetic' | 'human_reviews';
    eligible_for_auto_activation: boolean;
    train_groups?: number[];
    test_groups?: number[];
    synthetic_train_count?: number;
    synthetic_test_count?: number;
    train_example_ids?: string[];
    test_example_ids?: string[];
  };
  calibration_method?: string;
  accuracy?: number;
  f1_macro?: number;
  f1_weighted?: number;
  precision_macro?: number;
  recall_macro?: number;
  confusion_matrix?: number[][];
  feature_importances?: Record<string, number>;
  baseline_comparison?: BaselineComparison;
  train_sample_count?: number;
  test_sample_count?: number;
  /** Para el baseline heurístico */
  type?: string;
}

export interface ModelVersion {
  version_id: string;
  algorithm_name: string;
  description: string;
  is_active: boolean;
  created_at: string;
  metrics: ModelMetrics;
  parameters: Record<string, unknown>;
}

export interface TrainModelRequest {
  algorithm: 'calibrated_logistic' | 'random_forest';
  test_size: number;
  use_bootstrap: boolean;
  auto_activate: boolean;
  ground_truth_policy: 'individual' | 'consensus';
}

export interface DatasetStats {
  total_examples: number;
  by_ground_truth: Record<string, number>;
  model_version: string;
}

export type ConsensusStatus = 'SINGLE_REVIEW' | 'CONSENSUS' | 'DISAGREEMENT';

export interface GroundTruthPair {
  comparison_id: string;
  objective_item_id: string;
  compared_item_id: string;
  match_id: string | null;
  objective_text: string;
  compared_text: string;
  prediction_label: string;
  features: Record<string, number>;
  feature_source_review_id: string;
  source_university_obj: string | null;
  source_university_cmp: string | null;
  source_course_obj: string | null;
  source_course_cmp: string | null;
  source_syllabus_obj: string | null;
  source_syllabus_cmp: string | null;
  source_page_obj: number | null;
  source_page_cmp: number | null;
  status: ConsensusStatus;
  consensus_label: MatchClassification | null;
  reviewer_count: number;
  review_count: number;
  votes: {
    review_id: string;
    reviewer_id: string;
    human_decision: MatchClassification;
    justification: string;
    created_at: string;
  }[];
}

export interface GroundTruthPage {
  summary: {
    total_pairs: number;
    consensus_pairs: number;
    disagreement_pairs: number;
    single_review_pairs: number;
    linked_review_events: number;
  };
  total: number;
  limit: number;
  offset: number;
  items: GroundTruthPair[];
}

export interface ReviewerAgreement {
  reviewer_a: string;
  reviewer_b: string;
  common_pairs: number;
  agreements: number;
  observed_agreement: number | null;
  expected_agreement: number | null;
  cohen_kappa: number | null;
}

export type AnnotationReason = 'DISAGREEMENT' | 'SECOND_REVIEW' | 'UNREVIEWED';

export interface AnnotationCoverage {
  total_pairs: number;
  reviewed_pairs: number;
  consensus_pairs: number;
  disagreement_pairs: number;
  pending_pairs: number;
  review_events: number;
  reviewed_percentage: number | null;
  consensus_percentage: number | null;
}

export interface AnnotationCase {
  case_id: string;
  comparison_id: string;
  model_version: string;
  match_id: string | null;
  objective_item_id: string;
  compared_item_id: string;
  objective_text: string;
  compared_text: string;
  objective_page: number | null;
  compared_page: number | null;
  classification: MatchClassification | null;
  score: number | null;
  status: 'UNREVIEWED' | 'SINGLE_REVIEW' | 'DISAGREEMENT' | 'CONSENSUS';
  reviewer_ids: string[];
  review_count: number;
  reason: AnnotationReason | null;
  boundary_distance: number | null;
  uncertain_prediction: boolean;
  near_boundary: boolean;
}

export interface AnnotationQueue {
  strategy_version: string;
  reference_thresholds: Record<string, number>;
  coverage: AnnotationCoverage;
  total: number;
  limit: number;
  offset: number;
  items: AnnotationCase[];
}

export interface AnnotationBatch {
  id: string;
  reviewer_id: string;
  comparison_id: string | null;
  strategy_version: string;
  reference_thresholds: Record<string, number>;
  created_at: string;
  cases: AnnotationCase[];
  coverage_before: AnnotationCoverage;
  scope_before: AnnotationCoverage;
}

export interface AnnotationBatchProgress {
  batch: AnnotationBatch;
  completion: {
    batch_id: string;
    completed_at: string;
    coverage_after: AnnotationCoverage;
    scope_after: AnnotationCoverage;
  } | null;
  items: AnnotationCase[];
  coverage_current: AnnotationCoverage;
  scope_current: AnnotationCoverage;
  eligible_case_ids: string[];
}

export interface EvaluationSnapshot {
  id: string;
  name: string;
  created_at: string;
  content_hash: string;
  comparison_count: number;
  pair_count: number;
  independent_groups: number;
}

export interface EvaluationCriteria {
  min_f1_gain: number;
  max_recall_drop: number;
  max_coverage_mae_increase: number;
  max_per_comparison_f1_drop: number;
  max_per_comparison_coverage_increase: number;
  min_independent_groups: number;
}

export interface EvaluationExperiment {
  id: string;
  snapshot_id: string;
  created_at: string;
  report: {
    snapshot_hash: string;
    fingerprint_hash: string;
    protocol: string;
    sample: { comparisons: number; pairs: number; independent_groups: number; positive_pairs: number; negative_pairs: number };
    evaluations: Record<'reference' | 'candidate', {
      manifest: { version_id: string; artifact_sha256: string | null; manifest_hash: string };
      aggregate: Record<string, number>;
      comparisons: { comparison_id: string; precision: number; recall: number; f1: number;
        objective_coverage_error: number; compared_coverage_error: number }[];
    }>;
    criteria: EvaluationCriteria;
    checks: Record<string, boolean>;
    regressions: { comparison_id: string; f1_delta: number; objective_error_delta: number; compared_error_delta: number }[];
    promotion_recommended: boolean;
    automatic_activation: false;
  };
}
