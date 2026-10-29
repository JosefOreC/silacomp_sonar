import type { ComparisonBatch, Syllabus } from '../src/types';
import { syllabi } from './fixtures';

export const batchSyllabi: Syllabus[] = [...syllabi, { ...syllabi[1], id: 'B', course_name: 'Cálculo', university: 'Universidad B' }];
export const batch: ComparisonBatch = {
  id: 'CB-00000000000040008000000000000001', objective: { id: 'O', title: 'Objetivo', university: 'Universidad' },
  candidates: [{ id: 'S', title: 'Origen', university: 'Universidad' }, { id: 'B', title: 'Cálculo', university: 'Universidad B' }],
  model_version: 'bipartite-adaptive-002', weights: { semantic: .45, lexical: .3, keyword: .15, structural: .1 },
  thresholds: { match: .75, partial: .58, uncertain: .45 }, created_at: '2026-10-28T23:00:00Z',
  completed_at: '2026-10-28T23:01:00Z', status: 'COMPLETED',
  ranking_rule: 'objective_coverage_desc_global_score_desc_id_asc', ranking: ['B', 'S'],
  results: [{ compared_syllabus_id: 'S', comparison_id: 'CS', global_score: .9, objective_coverage: 70, compared_coverage: 90,
    counts: { MATCH: 1 }, error: null, error_code: null },
  { compared_syllabus_id: 'B', comparison_id: 'CB', global_score: .7, objective_coverage: 90, compared_coverage: 40,
    counts: { PARTIAL_MATCH: 1 }, error: null, error_code: null }],
};
