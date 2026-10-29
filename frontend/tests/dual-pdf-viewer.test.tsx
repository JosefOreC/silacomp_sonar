import { expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { DualPdfViewer } from '../src/components/DualPdfViewer';
import { api } from '../src/services/api';
import type { ContentMatch } from '../src/types';
import { comparison, match, syllabi } from './fixtures';

// El renderizador de PDF tiene sus propias pruebas; aquí se comprueba la
// coordinación entre ambos documentos, el navegador y el panel de revisión.
vi.mock('../src/components/PdfDocumentViewer', () => ({
  PdfDocumentViewer: ({ title, courseName, pdfUrl, pageNumber, onPageChange, classification }: {
    title: string; courseName: string; pdfUrl: string; pageNumber: number;
    onPageChange: (page: number) => void; classification: string;
  }) => <section aria-label={title}>
    <span>{courseName}</span>
    <a href={pdfUrl}>Original</a>
    <output>{pageNumber}:{classification}</output>
    <button onClick={() => onPageChange(pageNumber + 1)}>Página siguiente de {courseName}</button>
  </section>,
}));

const second: ContentMatch = { ...match, id: 'M2', objective_page: 3, compared_page: 5,
  classification: 'PARTIAL_MATCH', objective_title: 'Integrales', compared_title: 'Cálculo' };
const documentPair = { ...comparison, matches: [match, second] };

it('abre el par solicitado y sincroniza ambos PDF al cambiar correspondencia', () => {
  render(<DualPdfViewer comparison={documentPair} initialMatchId="M2" onClose={vi.fn()}
    onReviewSubmitted={vi.fn()} objectiveSyllabus={syllabi[0]} comparedSyllabus={syllabi[1]} />);
  expect(screen.getByText('3:PARTIAL_MATCH')).toBeTruthy();
  expect(screen.getByText('5:PARTIAL_MATCH')).toBeTruthy();
  expect(screen.getAllByRole('link').map(a => a.getAttribute('href'))).toEqual([
    api.getSyllabusPdfUrl('O'), api.getSyllabusPdfUrl('S'),
  ]);
  fireEvent.keyDown(window, { key: 'ArrowLeft' });
  expect(screen.getByText('1:MATCH')).toBeTruthy();
  expect(screen.getByText('2:MATCH')).toBeTruthy();
  fireEvent.click(screen.getByRole('button', { name: 'Página siguiente de Objetivo' }));
  expect(screen.getAllByText('2:MATCH')).toHaveLength(2);
  fireEvent.keyDown(window, { key: 'ArrowRight' });
  expect(screen.getByText('3:PARTIAL_MATCH')).toBeTruthy();
  expect(screen.getByText('5:PARTIAL_MATCH')).toBeTruthy();
});

it.each([undefined, 'desconocido'])('usa el primer par si no hay selección válida (%s)', (id) => {
  render(<DualPdfViewer comparison={documentPair} initialMatchId={id} onClose={vi.fn()} onReviewSubmitted={vi.fn()} />);
  expect(screen.getByText('Asignatura Objetivo')).toBeTruthy();
  expect(screen.getByText('Asignatura Comparada')).toBeTruthy();
  expect(screen.getByText('1:MATCH')).toBeTruthy();
});

it('conserva al revisor y reinicia la decisión para el siguiente par sin mutar la IA', async () => {
  const submit = vi.spyOn(api, 'submitReview').mockResolvedValue({} as Awaited<ReturnType<typeof api.submitReview>>);
  const saved = vi.fn();
  render(<DualPdfViewer comparison={documentPair} onClose={vi.fn()} onReviewSubmitted={saved} />);
  const reviewer = screen.getByLabelText('Identificador del revisor');
  fireEvent.change(reviewer, { target: { value: 'DOCENTE_2' } });
  fireEvent.click(screen.getByRole('button', { name: 'Descartar' }));
  fireEvent.change(screen.getByPlaceholderText(/Fundamento académico/), { target: { value: 'No cubre los temas requeridos' } });
  fireEvent.click(screen.getByRole('button', { name: 'Registrar Dictamen' }));
  await waitFor(() => expect(saved).toHaveBeenCalledOnce());
  expect(saved).toHaveBeenCalledWith('M1', 'NO_MATCH');
  expect(submit).toHaveBeenCalledWith(expect.objectContaining({ match_id: 'M1', reviewer_id: 'DOCENTE_2',
    prediction_before: 'MATCH', human_decision: 'NO_MATCH' }));
  fireEvent.keyDown(window, { key: 'ArrowRight' });
  expect((screen.getByLabelText('Identificador del revisor') as HTMLInputElement).value).toBe('DOCENTE_2');
  fireEvent.click(screen.getByRole('button', { name: 'Registrar Dictamen' }));
  await waitFor(() => expect(saved).toHaveBeenCalledTimes(2));
  expect(submit).toHaveBeenLastCalledWith(expect.objectContaining({ match_id: 'M2',
    prediction_before: 'PARTIAL_MATCH', human_decision: 'PARTIAL_MATCH' }));
  expect(match.classification).toBe('MATCH');
  expect(second.classification).toBe('PARTIAL_MATCH');
});

it('cierra por botón y Escape y retira el listener al desmontar', () => {
  const close = vi.fn();
  const { unmount } = render(<DualPdfViewer comparison={comparison} onClose={close} onReviewSubmitted={vi.fn()} />);
  fireEvent.click(screen.getByRole('button', { name: 'CERRAR VISOR' }));
  fireEvent.keyDown(window, { key: 'Escape' });
  expect(close).toHaveBeenCalledTimes(2);
  unmount();
  fireEvent.keyDown(window, { key: 'Escape' });
  expect(close).toHaveBeenCalledTimes(2);
});

it('permite cerrar una comparación sin correspondencias', () => {
  const close = vi.fn();
  render(<DualPdfViewer comparison={{ ...comparison, matches: [] }} onClose={close} onReviewSubmitted={vi.fn()} />);
  expect(screen.getByText(/No se encontraron correspondencias/)).toBeTruthy();
  expect(screen.queryAllByRole('link')).toHaveLength(0);
  fireEvent.click(screen.getByRole('button', { name: 'Cerrar' }));
  expect(close).toHaveBeenCalledOnce();
});
