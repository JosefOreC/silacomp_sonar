/**
 * Contratos de tipos para el Frontend de Comparación de Sílabos (ConvComp).
 * Sincronizado estrictamente con los contratos de dominio del backend.
 */

export type MatchClassification = 'MATCH' | 'PARTIAL_MATCH' | 'UNCERTAIN' | 'NO_MATCH';

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
