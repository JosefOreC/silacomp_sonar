import { beforeEach, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { BatchComparisonView } from '../src/components/BatchComparisonView';
import { api } from '../src/services/api';
import type { ComparisonBatch } from '../src/types';
import { batch, batchSyllabi } from './batch-fixtures';

beforeEach(() => {
  vi.spyOn(api, 'listComparisonBatches').mockResolvedValue([]);
  vi.spyOn(api, 'createComparisonBatch').mockResolvedValue(batch);
  vi.spyOn(api, 'getComparisonBatch').mockResolvedValue(batch);
});

function selectCandidates() {
  fireEvent.change(screen.getByLabelText('Sílabo objetivo del lote'), { target: { value: 'O' } });
  for (const checkbox of screen.getAllByRole('checkbox')) fireEvent.click(checkbox);
}

it('compara candidatos con coberturas independientes, conserva el ranking y enlaza sus evidencias', async () => {
  const open = vi.fn();
  render(<BatchComparisonView syllabi={batchSyllabi} onOpenComparison={open} onGoToUpload={vi.fn()} />);
  const run = screen.getByRole('button', { name: 'Comparar candidatos seleccionados' });
  expect((run as HTMLButtonElement).disabled).toBe(true);
  selectCandidates();
  expect(screen.getAllByRole('checkbox')).toHaveLength(2);
  fireEvent.click(run);
  await screen.findByText('Candidatos para Objetivo');
  expect(api.createComparisonBatch).toHaveBeenCalledWith({ request_id: expect.any(String), objective_syllabus_id: 'O', compared_syllabus_ids: ['S', 'B'] });
  const rows = screen.getAllByRole('row');
  expect(within(rows[1]).getByText('Cálculo')).toBeTruthy();
  expect(within(rows[1]).getByText('90.0%')).toBeTruthy();
  expect(within(rows[1]).getByText('40.0%')).toBeTruthy();
  expect(within(rows[1]).getByText('70.0%')).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Ver análisis de Cálculo' }));
  expect(open).toHaveBeenCalledWith('CB');
  expect(within(rows[1]).getByRole('link', { name: 'Informe PDF' }).getAttribute('href')).toContain('/CB/report/pdf');
  expect(screen.getByRole('link', { name: 'Exportar lote JSON' }).getAttribute('href')).toContain(batch.id + '/export');
  fireEvent.click(run);
  expect(api.createComparisonBatch).toHaveBeenCalledOnce();
});

it('limita la selección a cinco y permite quitar candidatos aunque estén ocultos por la búsqueda', () => {
  const many = [...batchSyllabi, ...['C', 'D', 'E', 'F', 'G'].map(id => ({ ...batchSyllabi[1], id, course_name: `Curso ${id}` }))];
  render(<BatchComparisonView syllabi={many} onOpenComparison={vi.fn()} onGoToUpload={vi.fn()} />);
  fireEvent.change(screen.getByLabelText('Sílabo objetivo del lote'), { target: { value: 'O' } });
  const checks = screen.getAllByRole('checkbox');
  for (const checkbox of checks.slice(0, 5)) fireEvent.click(checkbox);
  expect((checks[5] as HTMLInputElement).disabled).toBe(true);
  fireEvent.change(screen.getByLabelText('Buscar candidatos'), { target: { value: 'CALCULO' } });
  expect(screen.getAllByRole('checkbox')).toHaveLength(1);
  fireEvent.click(screen.getByRole('button', { name: 'Quitar Origen' }));
  expect(screen.getByText('4/5 candidatos seleccionados')).toBeTruthy();
  fireEvent.change(screen.getByLabelText('Sílabo objetivo del lote'), { target: { value: 'B' } });
  expect(screen.getByText('3/5 candidatos seleccionados')).toBeTruthy();
  expect(screen.queryByRole('checkbox')).toBeNull();
  expect(screen.getByText('No se encontraron candidatos con ese texto.')).toBeTruthy();
});

it('reintenta una solicitud con la misma clave después de perder la respuesta', async () => {
  vi.mocked(api.createComparisonBatch).mockRejectedValueOnce(new Error('Se perdió la respuesta')).mockResolvedValue(batch);
  render(<BatchComparisonView syllabi={batchSyllabi} onOpenComparison={vi.fn()} onGoToUpload={vi.fn()} />);
  selectCandidates();
  fireEvent.click(screen.getByRole('button', { name: 'Comparar candidatos seleccionados' }));
  expect((await screen.findByRole('alert')).textContent).toBe('Se perdió la respuesta');
  const first = vi.mocked(api.createComparisonBatch).mock.calls[0][0];
  fireEvent.click(screen.getByRole('button', { name: 'Comparar candidatos seleccionados' }));
  await screen.findByText('Candidatos para Objetivo');
  expect(api.createComparisonBatch).toHaveBeenLastCalledWith(first);
  expect(screen.queryByRole('alert')).toBeNull();
});

it('recupera avances guardados y prepara una ejecución nueva solo mediante una acción explícita', async () => {
  vi.mocked(api.createComparisonBatch).mockRejectedValueOnce(new Error('Conexión interrumpida')).mockResolvedValue(batch);
  vi.mocked(api.getComparisonBatch).mockImplementationOnce(async id => ({ ...batch, id, status: 'RUNNING', completed_at: null, ranking: ['S'], results: [batch.results[0]] }));
  render(<BatchComparisonView syllabi={batchSyllabi} onOpenComparison={vi.fn()} onGoToUpload={vi.fn()} />);
  selectCandidates();
  fireEvent.click(screen.getByRole('button', { name: 'Comparar candidatos seleccionados' }));
  await screen.findByRole('alert');
  const request = vi.mocked(api.createComparisonBatch).mock.calls[0][0];
  fireEvent.click(screen.getByRole('button', { name: 'Consultar solicitud guardada' }));
  await screen.findByText(/El lote no se reanuda automáticamente/);
  expect(api.getComparisonBatch).toHaveBeenCalledWith('CB-' + request.request_id.replaceAll('-', ''));
  expect(screen.getByText('Sin resultado guardado todavía')).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Actualizar resultado' }));
  await screen.findByRole('button', { name: 'Ver análisis de Cálculo' });
  fireEvent.click(screen.getByRole('button', { name: 'Preparar otro lote' }));
  fireEvent.click(screen.getByRole('button', { name: 'Comparar candidatos seleccionados' }));
  await waitFor(() => expect(api.createComparisonBatch).toHaveBeenCalledTimes(2));
  expect(vi.mocked(api.createComparisonBatch).mock.calls[1][0].request_id).not.toBe(request.request_id);
});

it('recupera lotes del historial y permite reintentar una consulta fallida', async () => {
  vi.mocked(api.listComparisonBatches).mockResolvedValue([batch]);
  render(<BatchComparisonView syllabi={batchSyllabi} onOpenComparison={vi.fn()} onGoToUpload={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: /Objetivo.*2 candidatos/ }));
  await screen.findByText('Candidatos para Objetivo');
  expect(api.createComparisonBatch).not.toHaveBeenCalled();
  vi.mocked(api.getComparisonBatch).mockRejectedValueOnce(new Error('No disponible')).mockResolvedValue(batch);
  fireEvent.click(screen.getByRole('button', { name: 'Actualizar resultado' }));
  expect((await screen.findByRole('alert')).textContent).toBe('No disponible');
  fireEvent.click(screen.getByRole('button', { name: 'Actualizar resultado' }));
  await waitFor(() => expect(screen.queryByRole('alert')).toBeNull());
});

it('muestra un fallo sin inventar puntuaciones ni informes', async () => {
  const failed: ComparisonBatch = { ...batch, status: 'FAILED', candidates: [batch.candidates[0]], ranking: [],
    results: [{ compared_syllabus_id: 'S', comparison_id: null, global_score: null, objective_coverage: null,
      compared_coverage: null, counts: {}, error_code: 'NO_CONTENT', error: 'El documento no contiene temas.' }] };
  vi.mocked(api.listComparisonBatches).mockResolvedValue([failed]);
  vi.mocked(api.getComparisonBatch).mockResolvedValue(failed);
  render(<BatchComparisonView syllabi={batchSyllabi} onOpenComparison={vi.fn()} onGoToUpload={vi.fn()} />);
  fireEvent.click(await screen.findByRole('button', { name: /Objetivo.*1 candidatos/ }));
  expect(await screen.findByText('El documento no contiene temas.')).toBeTruthy();
  expect(screen.queryByRole('link', { name: 'Informe PDF' })).toBeNull();
  expect(screen.getAllByText('—')).toHaveLength(4);
});

it('orienta la carga cuando falta catálogo y reintenta el historial sin bloquear la vista', async () => {
  vi.mocked(api.listComparisonBatches).mockRejectedValueOnce(new Error('Historial no disponible')).mockResolvedValue([]);
  const upload = vi.fn();
  render(<BatchComparisonView syllabi={[]} onOpenComparison={vi.fn()} onGoToUpload={upload} />);
  expect((await screen.findByRole('alert')).textContent).toBe('Historial no disponible');
  fireEvent.click(screen.getByRole('button', { name: 'Cargar sílabos' }));
  expect(upload).toHaveBeenCalledOnce();
  fireEvent.click(screen.getByRole('button', { name: 'Actualizar lotes' }));
  await waitFor(() => expect(screen.queryByRole('alert')).toBeNull());
});
