import { beforeEach, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import App from '../src/App';
import { api } from '../src/services/api';
import { comparison, match, syllabi } from './fixtures';

vi.mock('../src/components/PdfDocumentViewer', () => ({
  PdfDocumentViewer: ({ title }: { title: string }) => <section aria-label={title}>PDF original</section>,
}));

beforeEach(() => {
  vi.spyOn(api, 'listComparisonBatches').mockResolvedValue([]);
  vi.spyOn(api, 'listSyllabi').mockResolvedValue(syllabi);
  vi.spyOn(api, 'createComparison').mockResolvedValue(comparison);
  vi.spyOn(api, 'getComparison').mockResolvedValue(comparison);
  vi.spyOn(api, 'listComparisons').mockResolvedValue([{ ...comparison,
    objective_course: 'Objetivo', compared_course: 'Origen',
    objective_university: 'Universidad', compared_university: 'Universidad',
  }]);
});

async function compareCatalog() {
  await waitFor(() => expect(screen.getAllByRole('option', { name: /Objetivo/ })).toHaveLength(2));
  const selects = screen.getAllByRole('combobox');
  fireEvent.change(selects[0], { target: { value: 'O' } });
  fireEvent.change(selects[1], { target: { value: 'S' } });
  fireEvent.click(screen.getByRole('button', { name: 'Generar Dictamen de Correspondencia' }));
  await screen.findByRole('button', { name: 'Informe Técnico' });
}

it('integra comparación, evidencia y revisión PDF sin sobrescribir la predicción', async () => {
  const submit = vi.spyOn(api, 'submitReview').mockResolvedValue({} as Awaited<ReturnType<typeof api.submitReview>>);
  render(<App />);
  await compareCatalog();
  fireEvent.click(within(screen.getByRole('table')).getByText('Álgebra lineal'));
  expect(screen.getByText(/Operaciones con matrices/)).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Ver en Visor PDF' }));
  await screen.findByRole('button', { name: 'CERRAR VISOR' });
  fireEvent.click(screen.getByRole('button', { name: 'Descartar' }));
  fireEvent.change(screen.getByPlaceholderText(/Fundamento académico/), { target: { value: 'Los temas no corresponden' } });
  fireEvent.click(screen.getByRole('button', { name: 'Registrar Dictamen' }));
  await waitFor(() => expect(submit).toHaveBeenCalledOnce());
  fireEvent.click(screen.getByRole('button', { name: 'CERRAR VISOR' }));
  expect(await screen.findByText(/Dictamen Docente: Sin Equivalencia/)).toBeTruthy();
  expect(match.classification).toBe('MATCH');
  fireEvent.click(within(screen.getByRole('table')).getByText('Álgebra lineal'));
  expect(screen.queryByText(/Dictamen Docente:/)).toBeNull();
  fireEvent.click(screen.getByRole('button', { name: 'Registro de Sílabos' }));
  fireEvent.click(await screen.findByRole('button', { name: 'Ver Informe' }));
  await waitFor(() => expect(api.getComparison).toHaveBeenCalled());
});

it('recupera una comparación del historial y permite revisar desde el modal', async () => {
  vi.spyOn(api, 'submitReview').mockResolvedValue({} as Awaited<ReturnType<typeof api.submitReview>>);
  render(<App />);
  fireEvent.click(screen.getByRole('button', { name: 'Registro de Sílabos' }));
  fireEvent.click(await screen.findByRole('button', { name: 'Ver Informe' }));
  await screen.findByText('Álgebra lineal');
  fireEvent.click(screen.getByText('Álgebra lineal'));
  fireEvent.click(screen.getByRole('button', { name: 'Emitir Dictamen' }));
  fireEvent.change(screen.getByLabelText('Fundamentación Académica del Dictamen *'), { target: { value: 'Revisión académica confirmada' } });
  fireEvent.click(screen.getByRole('button', { name: 'Registrar Dictamen Académico' }));
  expect(await screen.findByText(/Dictamen Docente: Equivalencia Total/)).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Nueva Evaluación' }));
  expect(screen.getByRole('button', { name: 'Generar Dictamen de Correspondencia' })).toBeTruthy();
});

it('mantiene el historial utilizable si falla recuperar un informe', async () => {
  const error = vi.spyOn(console, 'error').mockImplementation(() => {});
  vi.spyOn(api, 'getComparison').mockRejectedValueOnce(new Error('Servidor no disponible')).mockResolvedValue(comparison);
  render(<App />);
  fireEvent.click(screen.getByRole('button', { name: 'Registro de Sílabos' }));
  fireEvent.click(await screen.findByRole('button', { name: 'Ver Informe' }));
  await waitFor(() => expect(error).toHaveBeenCalled());
  expect(screen.getByRole('alert').textContent).toBe('Servidor no disponible');
  fireEvent.click(screen.getByRole('button', { name: 'Ver Informe' }));
  expect(await screen.findByText('Álgebra lineal')).toBeTruthy();
  expect(screen.queryByRole('alert')).toBeNull();
});

it('abre y cierra la guía metodológica desde la navegación principal', () => {
  render(<App />);
  fireEvent.click(screen.getByRole('button', { name: 'Guía Metodológica' }));
  expect(screen.getByRole('button', { name: /Ponderaci.*Multivariada/ })).toBeTruthy();
  fireEvent.click(screen.getAllByRole('button').find(b => /Cerrar|✕/.test(b.textContent ?? ''))!);
  expect(screen.queryByRole('button', { name: /Ponderaci.*Multivariada/ })).toBeNull();
});

it('permite acceder a los lotes desde la navegación y desde el inicio', async () => {
  render(<App />);
  fireEvent.click(screen.getByRole('button', { name: 'Comparación por lotes' }));
  await screen.findByRole('heading', { name: 'Un objetivo. Varias posibilidades.' });
  fireEvent.click(screen.getByRole('button', { name: 'ConvComp, inicio' }));
  fireEvent.click(screen.getByRole('button', { name: /Varios candidatos/ }));
  expect(await screen.findByRole('heading', { name: 'Un objetivo. Varias posibilidades.' })).toBeTruthy();
});
