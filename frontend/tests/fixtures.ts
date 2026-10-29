import type { Comparison, ContentMatch, Syllabus } from '../src/types';

export const match: ContentMatch = {
  id: 'M1', comparison_id: 'C1', objective_item_id: 'O1', compared_item_id: 'S1',
  objective_title: 'Álgebra lineal', compared_title: 'Matrices y vectores',
  objective_section: 'Unidad I', compared_section: 'Unidad II', objective_page: 1, compared_page: 2,
  classification: 'MATCH', score_breakdown: { semantic_similarity: .9, lexical_similarity: .8,
    keyword_overlap: .7, structural_similarity: .6, composite_score: .85, weights: { semantic: .5 } },
  evidence: { evidence_type: 'HYBRID', shared_keywords: ['matrices'], semantic_score: .9,
    lexical_score: .8, objective_snippet: 'Operaciones con matrices', compared_snippet: 'Matrices y vectores',
    objective_page: 1, compared_page: 2 },
};
export const comparison: Comparison = { id: 'C1', objective_syllabus_id: 'O', compared_syllabus_id: 'S',
  global_score: .85, objective_coverage: 80, compared_coverage: 70, model_version: 'baseline',
  created_at: '2026-10-17T12:00:00Z', matches: [match], unmatched_objective: [], unmatched_compared: [],
  counts: { MATCH: 1, PARTIAL_MATCH: 0, UNCERTAIN: 0, NO_MATCH: 0 } };
export const syllabi: Syllabus[] = ['Objetivo', 'Origen'].map((name, index) => ({
  id: index === 0 ? 'O' : 'S', filename: `${name}.pdf`, total_pages: 2,
  file_size_bytes: 1024, sha256_hash: 'hash', course_name: name, university: 'Universidad',
  total_characters: 500, created_at: '2026-10-17T12:00:00Z',
}));
