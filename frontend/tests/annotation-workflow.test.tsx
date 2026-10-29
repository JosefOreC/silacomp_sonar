import { beforeEach, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { ActiveLearningPanel } from '../src/components/ActiveLearningPanel';
import { AuditDatasetView } from '../src/components/AuditDatasetView';
import { GroundTruthPanel } from '../src/components/GroundTruthPanel';
import { ViewerReviewPanel } from '../src/components/ViewerReviewPanel';
import { App } from '../src/App';
import { api } from '../src/services/api';
import { comparison, match, syllabi } from './fixtures';
import type { AnnotationBatchProgress, AnnotationCase, AnnotationCoverage, GroundTruthPage, MatchClassification } from '../src/types';

const coverage: AnnotationCoverage = { total_pairs: 1, reviewed_pairs: 0, consensus_pairs: 0,
  disagreement_pairs: 0, pending_pairs: 1, review_events: 0, reviewed_percentage: 0, consensus_percentage: 0 };
const item: AnnotationCase = { case_id: 'CASE-1', comparison_id: 'C1', model_version: 'baseline',
  match_id: 'M1', objective_item_id: 'O1', compared_item_id: 'S1', objective_text: 'Matrices',
  compared_text: 'Vectores', objective_page: 1, compared_page: 2, classification: 'UNCERTAIN',
  score: .55, status: 'UNREVIEWED', reviewer_ids: [], review_count: 0, reason: 'UNREVIEWED',
  boundary_distance: .05, uncertain_prediction: true, near_boundary: true };
const progress: AnnotationBatchProgress = {
  batch: { id: 'B1', reviewer_id: 'DOC', comparison_id: 'C1', strategy_version: 'v1',
    reference_thresholds: { match: .85 }, created_at: '2026-10-17T12:00:00Z', cases: [item],
    coverage_before: coverage, scope_before: coverage },
  completion: null, items: [item], coverage_current: coverage, scope_current: coverage,
  eligible_case_ids: ['CASE-1'],
};
const truth: GroundTruthPage = { summary: { total_pairs: 0, consensus_pairs: 0, disagreement_pairs: 0,
  single_review_pairs: 0, linked_review_events: 0 }, total: 0, limit: 20, offset: 0, items: [] };

beforeEach(() => {
  vi.spyOn(api, 'listComparisons').mockResolvedValue([{ ...comparison, objective_course: 'Objetivo', compared_course: 'Origen', objective_university: null, compared_university: null }]);
  vi.spyOn(api, 'getAnnotationQueue').mockResolvedValue({ strategy_version: 'v1', reference_thresholds: { match: .85 }, coverage, total: 1, limit: 20, offset: 0, items: [item] });
  vi.spyOn(api, 'listAnnotationBatches').mockResolvedValue([progress.batch]);
  vi.spyOn(api, 'getAnnotationBatch').mockResolvedValue(progress);
  vi.spyOn(api, 'getGroundTruth').mockResolvedValue(truth);
  vi.spyOn(api, 'getReviewerAgreement').mockResolvedValue([]);
  vi.spyOn(api, 'getDatasetStats').mockResolvedValue({ total_examples: 1, by_ground_truth: { MATCH: 1 }, model_version: 'base' });
});

it('identifica al revisor antes de crear un lote y guarda una revisión trazable', async () => {
  const create = vi.spyOn(api, 'createAnnotationBatch').mockResolvedValue(progress);
  vi.spyOn(api, 'submitReview').mockResolvedValue({} as Awaited<ReturnType<typeof api.submitReview>>);
  const changed = vi.fn();
  const open = vi.fn();
  render(<ActiveLearningPanel onAnnotationsChanged={changed} onOpenComparison={open} />);
  await screen.findByText(/1 casos elegibles/);
  expect((screen.getByRole('button', { name: 'Crear lote para un revisor identificado' }) as HTMLButtonElement).disabled).toBe(true);
  fireEvent.change(screen.getByLabelText('Revisor'), { target: { value: ' DOC ' } });
  fireEvent.click(screen.getByRole('button', { name: 'Consultar cola' }));
  const createButton = await screen.findByRole('button', { name: 'Crear lote para DOC' });
  fireEvent.click(createButton);
  await screen.findByRole('button', { name: 'Registrar revisión' });
  expect(create).toHaveBeenCalledWith('DOC', '', '', 10);
  fireEvent.change(screen.getByLabelText('Decisión'), { target: { value: 'NO_MATCH' } });
  fireEvent.change(screen.getByLabelText('Justificación académica'), { target: { value: 'Falta evidencia de correspondencia' } });
  fireEvent.click(screen.getByRole('button', { name: 'Registrar revisión' }));
  await waitFor(() => expect(changed).toHaveBeenCalledOnce());
  expect(api.submitReview).toHaveBeenCalledWith(expect.objectContaining({ reviewer_id: 'DOC', human_decision: 'NO_MATCH', correction_type: 'FALSE_POSITIVE', match_id: 'M1' }));
  expect(item.classification).toBe('UNCERTAIN');
  fireEvent.click(screen.getByRole('button', { name: 'Abrir informe y evidencias PDF' }));
  expect(open).toHaveBeenCalledWith('C1');
});

it('recupera un lote, captura errores de cierre y conserva el estado', async () => {
  vi.spyOn(api, 'completeAnnotationBatch').mockRejectedValue(new Error('No se pudo cerrar'));
  render(<ActiveLearningPanel onAnnotationsChanged={vi.fn()} />);
  fireEvent.change(await screen.findByLabelText('Recuperar un lote reciente'), { target: { value: 'B1' } });
  await screen.findByRole('button', { name: 'Cerrar lote y guardar medición' });
  fireEvent.click(screen.getByRole('button', { name: 'Cerrar lote y guardar medición' }));
  expect((await screen.findByRole('alert')).textContent).toBe('No se pudo cerrar');
  fireEvent.click(screen.getByRole('button', { name: 'Actualizar lote' }));
  await waitFor(() => expect(screen.queryByRole('alert')).toBeNull());
});

it('recupera la cola tras un error y comunica el estado vacío', async () => {
  vi.mocked(api.getAnnotationQueue).mockRejectedValueOnce(new Error('Cola no disponible')).mockResolvedValue({ strategy_version: 'v1', reference_thresholds: {}, coverage, total: 0, items: [], offset: 0, limit: 20 });
  render(<ActiveLearningPanel onAnnotationsChanged={vi.fn()} />);
  expect((await screen.findByRole('alert')).textContent).toBe('Cola no disponible');
  fireEvent.click(screen.getByRole('button', { name: 'Consultar cola' }));
  expect(await screen.findByText('No hay casos pendientes con estos filtros.')).toBeTruthy();
});

it('filtra el ground truth y distingue kappa no calculable de un valor numérico', async () => {
  vi.mocked(api.getReviewerAgreement).mockResolvedValue([
    { reviewer_a: 'A', reviewer_b: 'B', common_pairs: 0, agreements: 0, observed_agreement: null, expected_agreement: null, cohen_kappa: null },
    { reviewer_a: 'C', reviewer_b: 'D', common_pairs: 10, agreements: 8, observed_agreement: .8, expected_agreement: .5, cohen_kappa: .6 },
  ]);
  render(<GroundTruthPanel />);
  expect(await screen.findByText('0.600')).toBeTruthy();
  expect(screen.getAllByText('No calculable')).toHaveLength(2);
  fireEvent.change(screen.getByLabelText('Estado'), { target: { value: 'CONSENSUS' } });
  await waitFor(() => expect(api.getGroundTruth).toHaveBeenLastCalledWith('', 'CONSENSUS', 0));
});

it('muestra los dictámenes auditados sin confundirlos con predicciones originales', async () => {
  render(<AuditDatasetView />);
  expect(await screen.findByText('Dictámenes Auditados')).toBeTruthy();
  expect(screen.getByRole('link', { name: 'Exportar Registro JSON' }).getAttribute('href')).toContain('/dataset/export');
  expect(screen.getByText('Principio de Inmutabilidad y Trazabilidad Institucional')).toBeTruthy();
});

it.each<[MatchClassification, string, string]>([
  ['MATCH', 'Ratificar Match', 'CONFIRMED'], ['MATCH', 'Descartar', 'FALSE_POSITIVE'],
  ['NO_MATCH', 'Ratificar Match', 'FALSE_NEGATIVE'], ['MATCH', 'Ajustar a Parcial', 'OVERESTIMATION'],
  ['PARTIAL_MATCH', 'Ratificar Match', 'UNDERESTIMATION'], ['MATCH', 'Marcar Dudoso', 'OVERESTIMATION'],
])('registra la corrección adecuada desde %s usando %s', async (original, button, correction) => {
  const submit = vi.spyOn(api, 'submitReview').mockResolvedValue({} as Awaited<ReturnType<typeof api.submitReview>>);
  const saved = vi.fn();
  render(<ViewerReviewPanel match={{ ...match, classification: original }} reviewerId="DOC" onReviewerChange={vi.fn()} onReviewSubmitted={saved} />);
  fireEvent.click(screen.getByRole('button', { name: button }));
  const input = screen.getAllByRole('textbox')[1];
  fireEvent.change(input, { target: { value: 'Justificación de la revisión' } });
  fireEvent.click(screen.getByRole('button', { name: 'Registrar Dictamen' }));
  await waitFor(() => expect(saved).toHaveBeenCalledOnce());
  expect(submit).toHaveBeenCalledWith(expect.objectContaining({ prediction_before: original, correction_type: correction }));
});

it('requiere identificación antes de guardar desde el visor PDF', async () => {
  const submit = vi.spyOn(api, 'submitReview');
  render(<ViewerReviewPanel match={match} reviewerId=" " onReviewerChange={vi.fn()} onReviewSubmitted={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'Registrar Dictamen' }));
  expect(await screen.findByText('Identifique al revisor antes de registrar la decisión.')).toBeTruthy();
  expect(submit).not.toHaveBeenCalled();
});

it('recupera un informe desde el registro y mantiene su evidencia visible', async () => {
  vi.spyOn(api, 'listSyllabi').mockResolvedValue(syllabi);
  vi.spyOn(api, 'getComparison').mockResolvedValue(comparison);
  render(<App />);
  fireEvent.click(screen.getByRole('button', { name: 'Registro de Sílabos' }));
  fireEvent.click(await screen.findByRole('button', { name: 'Ver Informe' }));
  await screen.findByText('Álgebra lineal');
  fireEvent.click(screen.getByText('Álgebra lineal'));
  expect(screen.getAllByText(/Operaciones con/).length).toBeGreaterThan(0);
  expect(api.getComparison).toHaveBeenCalledWith('C1');
});
