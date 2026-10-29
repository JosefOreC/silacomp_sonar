import { beforeEach, describe, expect, it, vi } from 'vitest';
import { api } from '../src/services/api';
import type { EvaluationCriteria, HumanReviewPayload } from '../src/types';

const fetchMock = vi.fn<typeof fetch>();
beforeEach(() => { fetchMock.mockReset(); vi.stubGlobal('fetch', fetchMock); });
const criteria: EvaluationCriteria = { min_f1_gain: .01, max_recall_drop: 0,
  max_coverage_mae_increase: 0, max_per_comparison_f1_drop: .05,
  max_per_comparison_coverage_increase: 0, min_independent_groups: 2 };
const review: HumanReviewPayload = { comparison_id: 'C1', match_id: 'M1',
  prediction_before: 'MATCH', human_decision: 'NO_MATCH', correction_type: 'FALSE_POSITIVE',
  justification: 'Falta evidencia temática', reviewer_id: 'DOCENTE' };
const requests: [string, () => Promise<unknown>, string, string][] = [
  ['lotes de comparación', () => api.listComparisonBatches(), '/comparison-batches', 'GET'],
  ['recuperar comparación por lotes', () => api.getComparisonBatch('A/B'), '/comparison-batches/A%2FB', 'GET'],
  ['comparar candidatos', () => api.createComparisonBatch({ request_id: 'request-1', objective_syllabus_id: 'O', compared_syllabus_ids: ['S'] }), '/comparison-batches', 'POST'],
  ['sílabos', () => api.listSyllabi(), '/syllabi', 'GET'],
  ['comparaciones', () => api.listComparisons(), '/comparisons', 'GET'],
  ['comparación', () => api.getComparison('C1'), '/comparisons/C1', 'GET'],
  ['estadísticas', () => api.getDatasetStats(), '/dataset/statistics', 'GET'],
  ['evidencias', () => api.getComparisonEvidence('C1'), '/comparisons/C1/evidence', 'GET'],
  ['evidencia de par', () => api.getMatchEvidence('C1', 'M1'), '/comparisons/C1/matches/M1/evidence', 'GET'],
  ['modelos', () => api.listModels(), '/models', 'GET'],
  ['modelo activo', () => api.getActiveModel(), '/models/active', 'GET'],
  ['métricas', () => api.getModelEvaluation('V1'), '/models/V1/evaluation', 'GET'],
  ['crear comparación', () => api.createComparison('S1', 'S2'), '/comparisons', 'POST'],
  ['revisión', () => api.submitReview(review), '/reviews', 'POST'],
  ['entrenar', () => api.trainModel({ algorithm: 'calibrated_logistic', test_size: .25,
    use_bootstrap: false, auto_activate: false, ground_truth_policy: 'consensus' }), '/models/train', 'POST'],
  ['activar', () => api.activateModel('V1'), '/models/V1/activate', 'POST'],
  ['reservas', () => api.listEvaluationSnapshots(), '/evaluation/snapshots', 'GET'],
  ['experimentos', () => api.listEvaluationExperiments(), '/evaluation/experiments', 'GET'],
  ['crear reserva', () => api.createEvaluationSnapshot('Reserva', ['C1']), '/evaluation/snapshots', 'POST'],
  ['crear experimento', () => api.createEvaluationExperiment('S1', 'base', 'V1', criteria), '/evaluation/experiments', 'POST'],
  ['lotes', () => api.listAnnotationBatches(), '/active-learning/batches', 'GET'],
  ['lote', () => api.getAnnotationBatch('A/B'), '/active-learning/batches/A%2FB', 'GET'],
  ['completar lote', () => api.completeAnnotationBatch('A/B'), '/active-learning/batches/A%2FB/complete', 'POST'],
  ['crear lote', () => api.createAnnotationBatch('DOC', '', '', 10), '/active-learning/batches', 'POST'],
  ['acuerdo', () => api.getReviewerAgreement('C1'), '/dataset/agreement?comparison_id=C1', 'GET'],
  ['ground truth', () => api.getGroundTruth('C1', 'CONSENSUS', 20), '/dataset/ground-truth?limit=20&offset=20&comparison_id=C1&status=CONSENSUS', 'GET'],
  ['cola', () => api.getAnnotationQueue({ comparisonId: 'C1', reason: 'DISAGREEMENT', reviewerId: 'DOC' }, 20),
    '/active-learning/queue?limit=20&offset=20&comparison_id=C1&reason=DISAGREEMENT&reviewer_id=DOC', 'GET'],
];

describe.each(requests)('%s', (_name, request, path, method) => {
  it('entrega la respuesta y respeta ruta y método HTTP', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ id: 'respuesta' })));
    expect(await request()).toEqual({ id: 'respuesta' });
    const [url, options] = fetchMock.mock.calls[0];
    expect(String(url)).toBe(`http://localhost:8000/api${path}`);
    expect(options?.method ?? 'GET').toBe(method);
  });
  it('rechaza una respuesta HTTP fallida', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ detail: 'Conflicto de datos' }), { status: 409 }));
    await expect(request()).rejects.toThrow();
  });
});

it('envía decisiones humanas y predicciones originales por separado', async () => {
  fetchMock.mockResolvedValue(new Response('{}'));
  await api.submitReview(review);
  expect(JSON.parse(String(fetchMock.mock.calls[0][1]?.body))).toEqual(review);
  expect(review.prediction_before).toBe('MATCH');
});

it('envía las fuentes y criterios congelados en el experimento', async () => {
  fetchMock.mockResolvedValue(new Response('{}'));
  await api.createEvaluationExperiment('S1', 'base', 'V1', criteria);
  expect(JSON.parse(String(fetchMock.mock.calls[0][1]?.body))).toEqual({
    snapshot_id: 'S1', reference_version: 'base', candidate_version: 'V1', criteria,
  });
});

it('envía el PDF y sus metadatos como multipart', async () => {
  fetchMock.mockResolvedValue(new Response('{"id":"S1"}'));
  const file = new File(['%PDF'], 'curso.pdf', { type: 'application/pdf' });
  await api.uploadSyllabus(file, 'Universidad', 'Cálculo');
  const body = fetchMock.mock.calls[0][1]?.body as FormData;
  expect(body.get('file')).toBe(file);
  expect(body.get('university')).toBe('Universidad');
  expect(body.get('course_name')).toBe('Cálculo');
});

it.each([
  () => api.uploadSyllabus(new File(['pdf'], 'a.pdf')),
  () => api.createComparison('S1', 'S2'), () => api.submitReview(review),
  () => api.activateModel('V1'),
  () => api.trainModel({ algorithm: 'random_forest', test_size: .2, use_bootstrap: false, auto_activate: false, ground_truth_policy: 'consensus' }),
  () => api.listEvaluationSnapshots(), () => api.listAnnotationBatches(),
])('muestra un error útil aunque el servidor no entregue JSON', async (request) => {
  fetchMock.mockResolvedValue(new Response('Servicio fuera de línea', { status: 503 }));
  await expect(request()).rejects.toThrow(/Error|No se pudo/);
});

it('construye enlaces de exportación y conserva filtros codificados', () => {
  expect(api.getComparisonBatchExportUrl('A/B')).toContain('/comparison-batches/A%2FB/export');
  expect(api.getEvaluationExportUrl('snapshots', 'A/B')).toContain('/snapshots/A%2FB/export');
  expect(api.getGroundTruthExportUrl('csv', 'C 1')).toContain('format=csv&comparison_id=C+1');
  expect(api.getGroundTruthExportUrl('json', '')).toContain('format=json');
  expect(api.getReportPdfUrl('C1')).toContain('/C1/report/pdf');
  expect(api.getReportHtmlUrl('C1')).toContain('/C1/report/html');
  expect(api.getDatasetExportUrl()).toContain('/dataset/export');
  expect(api.getDatasetExportFormatUrl('csv')).toContain('/dataset/export?format=csv');
  expect(api.getSyllabusPdfUrl('S1')).toContain('/syllabi/S1/pdf');
});

it('permite consultar sin filtros opcionales', async () => {
  fetchMock.mockImplementation(async () => new Response('[]'));
  await api.getGroundTruth('', '');
  await api.getReviewerAgreement('');
  await api.getAnnotationQueue({ comparisonId: '', reason: '', reviewerId: '  ' });
  expect(fetchMock.mock.calls.map(([url]) => String(url))).toEqual([
    'http://localhost:8000/api/dataset/ground-truth?limit=20&offset=0',
    'http://localhost:8000/api/dataset/agreement?',
    'http://localhost:8000/api/active-learning/queue?limit=20&offset=0',
  ]);
});
