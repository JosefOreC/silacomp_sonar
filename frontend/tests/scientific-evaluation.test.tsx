import { beforeEach, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { api } from '../src/services/api';
import { ScientificEvaluationPanel } from '../src/components/ScientificEvaluationPanel';
import { ModelManagementView } from '../src/components/ModelManagementView';
import type { EvaluationExperiment, EvaluationSnapshot, ModelVersion } from '../src/types';

const models: ModelVersion[] = [{ version_id: 'candidate-1', algorithm_name: 'Modelo candidato',
  description: 'Modelo de prueba', is_active: false, created_at: '2026-10-17T12:00:00Z',
  metrics: { accuracy: .9, f1_macro: .8, precision_macro: .85 }, parameters: {} }];
const snapshot: EvaluationSnapshot = { id: 'S1', name: 'Reserva', created_at: '2026-10-17T12:00:00Z',
  content_hash: 'abc', comparison_count: 2, pair_count: 8, independent_groups: 2 };
const aggregate = { f1: .8, precision: .8, recall: .8, objective_coverage_mae: 0, compared_coverage_mae: 0 };
const experiment: EvaluationExperiment = { id: 'E1', snapshot_id: 'S1', created_at: '2026-10-17T12:00:00Z', report: {
  promotion_recommended: true, snapshot_hash: 'abc', fingerprint_hash: 'fingerprint', protocol: 'reserved-v1',
  automatic_activation: false,
  criteria: { min_f1_gain: .01, max_recall_drop: 0, max_coverage_mae_increase: 0,
    max_per_comparison_f1_drop: .05, max_per_comparison_coverage_increase: 0, min_independent_groups: 2 },
  sample: { comparisons: 2, pairs: 8, independent_groups: 2, positive_pairs: 4, negative_pairs: 4 },
  evaluations: {
    reference: { manifest: { version_id: 'baseline', artifact_sha256: null, manifest_hash: 'ref' }, aggregate, comparisons: [] },
    candidate: { manifest: { version_id: 'candidate-1', artifact_sha256: 'sha', manifest_hash: 'cand' }, aggregate, comparisons: [] },
  },
  checks: { f1_gain: true, recall: false }, regressions: [{ comparison_id: 'C1', f1_delta: .1, objective_error_delta: 0, compared_error_delta: 0 }],
} };

beforeEach(() => {
  vi.spyOn(api, 'listEvaluationSnapshots').mockResolvedValue([snapshot]);
  vi.spyOn(api, 'listEvaluationExperiments').mockResolvedValue([]);
  vi.spyOn(api, 'listComparisons').mockResolvedValue([{ id: 'C1', objective_course: 'Cálculo', compared_course: 'Análisis' } as Awaited<ReturnType<typeof api.listComparisons>>[number]]);
});

it('crea una reserva y ejecuta el candidato con criterios explícitos', async () => {
  const reserve = vi.spyOn(api, 'createEvaluationSnapshot').mockResolvedValue(snapshot);
  const run = vi.spyOn(api, 'createEvaluationExperiment').mockResolvedValue(experiment);
  render(<ScientificEvaluationPanel models={models} />);
  const create = await screen.findByRole('button', { name: 'Crear conjunto reservado' });
  expect((create as HTMLButtonElement).disabled).toBe(true);
  fireEvent.change(screen.getByLabelText('Nombre del conjunto'), { target: { value: ' Reserva ' } });
  const select = screen.getByLabelText(/Comparaciones a reservar/) as HTMLSelectElement;
  select.options[0].selected = true;
  fireEvent.change(select);
  fireEvent.click(create);
  await waitFor(() => expect(reserve).toHaveBeenCalledWith('Reserva', ['C1']));
  const execute = screen.getByRole('button', { name: 'Ejecutar comparación reservada' });
  expect((execute as HTMLButtonElement).disabled).toBe(true);
  fireEvent.change(screen.getByLabelText('Candidato'), { target: { value: 'candidate-1' } });
  fireEvent.change(screen.getByLabelText('Ganancia mínima de F1 (0–1)'), { target: { value: '.02' } });
  fireEvent.click(execute);
  expect(await screen.findByText('Cumple los criterios de promoción')).toBeTruthy();
  expect(run).toHaveBeenCalledWith('S1', 'bipartite-adaptive-002', 'candidate-1', expect.objectContaining({ min_f1_gain: .02 }));
  expect(screen.getByText('No cumple: Recall sin regresión fuera de tolerancia')).toBeTruthy();
  expect(screen.getByRole('link', { name: 'Descargar informe completo JSON' }).getAttribute('href')).toContain('/experiments/E1/export');
});

it('muestra el conflicto al reservar y permite recuperarse', async () => {
  vi.spyOn(api, 'createEvaluationSnapshot').mockRejectedValue(new Error('Matriz incompleta'));
  render(<ScientificEvaluationPanel models={models} />);
  await screen.findByRole('button', { name: 'Crear conjunto reservado' });
  fireEvent.change(screen.getByLabelText('Nombre del conjunto'), { target: { value: 'Reserva' } });
  const select = screen.getByLabelText(/Comparaciones a reservar/) as HTMLSelectElement;
  select.options[0].selected = true; fireEvent.change(select);
  fireEvent.click(screen.getByRole('button', { name: 'Crear conjunto reservado' }));
  expect((await screen.findByRole('alert')).textContent).toBe('Matriz incompleta');
  fireEvent.click(screen.getByRole('button', { name: 'Actualizar estudios' }));
  await waitFor(() => expect(screen.queryByRole('alert')).toBeNull());
});

it('reintenta una consulta fallida y muestra el estado sin reservas', async () => {
  vi.mocked(api.listEvaluationSnapshots).mockRejectedValueOnce(new Error('Sin conexión')).mockResolvedValue([]);
  render(<ScientificEvaluationPanel models={models} />);
  expect((await screen.findByRole('alert')).textContent).toBe('Sin conexión');
  fireEvent.click(screen.getByRole('button', { name: 'Consultar estudios' }));
  expect(await screen.findByText(/Aún no hay conjuntos reservados/)).toBeTruthy();
});

it('consulta y selecciona modelos mediante un botón accesible', async () => {
  vi.spyOn(api, 'listModels').mockResolvedValue(models);
  vi.spyOn(api, 'getDatasetStats').mockResolvedValue({ total_examples: 20, by_ground_truth: {}, model_version: 'base' });
  render(<ModelManagementView />);
  const select = await screen.findByRole('button', { name: 'Modelo candidato' });
  fireEvent.click(select);
  expect(select.getAttribute('aria-pressed')).toBe('true');
  expect(screen.getByLabelText('Algoritmo')).toBeTruthy();
});
