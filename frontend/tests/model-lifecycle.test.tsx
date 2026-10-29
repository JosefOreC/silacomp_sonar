import { beforeEach, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { ModelManagementView } from '../src/components/ModelManagementView';
import { api } from '../src/services/api';
import type { ModelVersion } from '../src/types';

const candidate: ModelVersion = { version_id: 'candidate', algorithm_name: 'Random Forest',
  description: 'Entrenamiento humano', created_at: '2026-10-28T12:00:00Z', is_active: false,
  parameters: {}, metrics: { accuracy: .9, f1_macro: .85, precision_macro: .8, recall_macro: .9,
    confusion_matrix: [[2, 1, 0], [0, 3, 0], [0, 1, 4]], feature_importances: { semantic: .7, lexical: .3 },
    train_sample_count: 30, test_sample_count: 10 } };
const baseline: ModelVersion = { ...candidate, version_id: 'baseline', algorithm_name: 'Baseline', is_active: true,
  metrics: { type: 'heuristic_baseline' }, parameters: { weights: { w_sem: .45 }, version: '001' } };

beforeEach(() => {
  vi.spyOn(api, 'listModels').mockResolvedValue([baseline, candidate]);
  vi.spyOn(api, 'getDatasetStats').mockResolvedValue({ total_examples: 40, by_ground_truth: {}, model_version: 'baseline' });
  vi.spyOn(api, 'listEvaluationSnapshots').mockResolvedValue([]);
  vi.spyOn(api, 'listEvaluationExperiments').mockResolvedValue([]);
  vi.spyOn(api, 'listComparisons').mockResolvedValue([]);
});

it('muestra los parámetros del baseline y las métricas del modelo elegido', async () => {
  render(<ModelManagementView />);
  expect(await screen.findByText('Motor Heurístico Bipartito-Adaptativo (Baseline)')).toBeTruthy();
  expect(screen.getByText('0.45')).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Random Forest' }));
  expect(screen.getByText('Matriz de Confusión')).toBeTruthy();
  expect(screen.getByText('Importancia de Características')).toBeTruthy();
  expect(screen.getByText('semantic')).toBeTruthy();
});

it('envía las opciones explícitas de entrenamiento sin activar el modelo por defecto', async () => {
  const train = vi.spyOn(api, 'trainModel').mockResolvedValue(candidate);
  const activate = vi.spyOn(api, 'activateModel');
  render(<ModelManagementView />);
  await screen.findByRole('button', { name: 'Random Forest' });
  fireEvent.change(screen.getByLabelText('Algoritmo'), { target: { value: 'random_forest' } });
  fireEvent.change(screen.getByRole('slider'), { target: { value: '.3' } });
  fireEvent.change(screen.getByLabelText(/Etiquetas para entrenamiento/), { target: { value: 'individual' } });
  fireEvent.click(screen.getByLabelText(/Bootstrap sintético/));
  fireEvent.click(screen.getByRole('button', { name: 'Entrenar Nuevo Modelo' }));
  await waitFor(() => expect(train).toHaveBeenCalledWith({ algorithm: 'random_forest', test_size: .3,
    ground_truth_policy: 'individual', use_bootstrap: false, auto_activate: false }));
  await screen.findByText('Matriz de Confusión');
  expect(activate).not.toHaveBeenCalled();
});

it('activa únicamente la versión solicitada y conserva la selección al actualizar', async () => {
  const activate = vi.spyOn(api, 'activateModel').mockResolvedValue({ status: 'ok', message: 'Activado' });
  render(<ModelManagementView />);
  fireEvent.click(await screen.findByRole('button', { name: 'Random Forest' }));
  vi.mocked(api.listModels).mockResolvedValue([{ ...baseline, is_active: false }, { ...candidate, is_active: true }]);
  fireEvent.click(screen.getByRole('button', { name: 'Activar en Producción' }));
  await waitFor(() => expect(activate).toHaveBeenCalledWith('candidate'));
  await waitFor(() => expect(screen.queryByRole('button', { name: 'Activar en Producción' })).toBeNull());
  expect(screen.getByRole('button', { name: 'Random Forest' }).getAttribute('aria-pressed')).toBe('true');
});

it('permite reintentar el entrenamiento tras un conflicto de datos', async () => {
  const train = vi.spyOn(api, 'trainModel').mockRejectedValueOnce(new Error('Falta consenso')).mockResolvedValue(candidate);
  render(<ModelManagementView />);
  await screen.findByRole('button', { name: 'Random Forest' });
  fireEvent.click(screen.getByRole('button', { name: 'Entrenar Nuevo Modelo' }));
  expect(await screen.findByText('Falta consenso')).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Entrenar Nuevo Modelo' }));
  await screen.findByText('Matriz de Confusión');
  expect(train).toHaveBeenCalledTimes(2);
  expect(screen.queryByText('Falta consenso')).toBeNull();
});

it('no oculta una activación fallida y permite reintentar', async () => {
  vi.spyOn(api, 'activateModel').mockRejectedValueOnce(new Error('Artefacto no disponible'))
    .mockResolvedValue({ status: 'ok', message: 'Activado' });
  render(<ModelManagementView />);
  fireEvent.click(await screen.findByRole('button', { name: 'Activar en Producción' }));
  expect(await screen.findByText('Artefacto no disponible')).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Activar en Producción' }));
  await waitFor(() => expect(api.listModels).toHaveBeenCalledTimes(2));
  await waitFor(() => expect(screen.queryByText('Artefacto no disponible')).toBeNull());
});

it('recupera una consulta fallida y presenta un catálogo vacío explícito', async () => {
  vi.mocked(api.listModels).mockRejectedValueOnce(new Error('Sin conexión')).mockResolvedValue([]);
  render(<ModelManagementView />);
  expect(await screen.findByText('Sin conexión')).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: /Actualizar$/ }));
  expect(await screen.findByText('No hay versiones de modelos registradas aún.')).toBeTruthy();
  expect(screen.queryByText('Sin conexión')).toBeNull();
});
