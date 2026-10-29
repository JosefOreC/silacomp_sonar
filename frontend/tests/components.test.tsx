import { expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { api } from '../src/services/api';
import { ComparisonScore } from '../src/components/ComparisonScore';
import { MatchTable } from '../src/components/MatchTable';
import { UnmatchedPanel } from '../src/components/UnmatchedPanel';
import { ReviewModal } from '../src/components/ReviewModal';
import { SyllabusUploader } from '../src/components/SyllabusUploader';
import { EvidencePanel } from '../src/components/EvidencePanel';
import { SupportGuideModal } from '../src/components/SupportGuideModal';
import { Dashboard } from '../src/components/Dashboard';
import { comparison, match, syllabi } from './fixtures';
import { getClassificationLabel, getCorrectionLabel, getEvidenceLabel } from '../src/utils/translations';

it.each([.9, .75, .55, .2])('desglosa puntuación y enlaces de informe con score %s', (score) => {
  render(<ComparisonScore comparison={{ ...comparison, global_score: score }} />);
  expect(screen.getAllByText(`${Math.round(score * 100)}%`).length).toBeGreaterThan(0);
  expect(screen.getByText('80%')).toBeTruthy();
  expect(screen.getByText('70%')).toBeTruthy();
  expect(screen.getAllByRole('link').some((a) => a.getAttribute('href')?.endsWith('/C1/report/pdf'))).toBe(true);
});

it('filtra correspondencias por texto y preserva la selección del par', () => {
  const select = vi.fn();
  render(<MatchTable matches={[match, { ...match, id: 'M2', classification: 'NO_MATCH', objective_title: 'Cálculo', compared_title: 'Derivadas', evidence: { ...match.evidence, shared_keywords: [] } }]}
    onSelectMatch={select} humanReviews={{ M1: 'NO_MATCH' }} />);
  fireEvent.change(screen.getByPlaceholderText('Buscar tema o término...'), { target: { value: 'matrices' } });
  expect(screen.queryByText('Cálculo')).toBeNull();
  fireEvent.click(screen.getByText('Álgebra lineal'));
  expect(select).toHaveBeenCalledWith(match);
  fireEvent.change(screen.getByPlaceholderText('Buscar tema o término...'), { target: { value: 'inexistente' } });
  expect(screen.queryByText('Álgebra lineal')).toBeNull();
});

it('muestra brechas con páginas y sugerencias del mejor candidato', () => {
  render(<UnmatchedPanel unmatchedObjective={[{ item_id: 'U1', syllabus_id: 'O', section_name: 'Unidad I',
    title: 'Integrales', text_snippet: 'Integración definida', page: 3, best_candidate_title: 'Derivadas', best_score: .3 }]}
    unmatchedCompared={[]} />);
  expect(screen.getByText('Integrales')).toBeTruthy();
  expect(screen.getByText(/Derivadas/)).toBeTruthy();
});

it('valida justificación y guarda la decisión sin modificar la predicción', async () => {
  const submit = vi.spyOn(api, 'submitReview').mockResolvedValue({} as Awaited<ReturnType<typeof api.submitReview>>);
  const saved = vi.fn(); const close = vi.fn();
  render(<ReviewModal match={match} onClose={close} onReviewSaved={saved} />);
  fireEvent.click(screen.getByRole('button', { name: 'Registrar Dictamen Académico' }));
  expect(screen.getByText(/al menos 8 caracteres/)).toBeTruthy();
  expect(submit).not.toHaveBeenCalled();
  fireEvent.change(screen.getByLabelText('Dictamen Final *'), { target: { value: 'NO_MATCH' } });
  fireEvent.change(screen.getByLabelText('Fundamentación Académica del Dictamen *'), { target: { value: 'Falta contenido requerido' } });
  fireEvent.click(screen.getByRole('button', { name: 'Registrar Dictamen Académico' }));
  await waitFor(() => expect(saved).toHaveBeenCalledWith('M1', 'NO_MATCH'));
  expect(submit).toHaveBeenCalledWith(expect.objectContaining({ prediction_before: 'MATCH', human_decision: 'NO_MATCH' }));
  expect(match.classification).toBe('MATCH');
  expect(close).toHaveBeenCalled();
});

it('permite reintentar una revisión rechazada por el servidor', async () => {
  vi.spyOn(api, 'submitReview').mockRejectedValue(new Error('No se pudo guardar'));
  const close = vi.fn();
  render(<ReviewModal match={match} onClose={close} onReviewSaved={vi.fn()} />);
  fireEvent.change(screen.getByLabelText('Fundamentación Académica del Dictamen *'), { target: { value: 'Revisión fundamentada' } });
  fireEvent.click(screen.getByRole('button', { name: 'Registrar Dictamen Académico' }));
  expect(await screen.findByText('No se pudo guardar')).toBeTruthy();
  expect(close).not.toHaveBeenCalled();
});

it('compara sílabos del catálogo y rechaza comparar el mismo documento', async () => {
  const create = vi.spyOn(api, 'createComparison').mockResolvedValue(comparison);
  const created = vi.fn();
  render(<SyllabusUploader existingSyllabi={syllabi} onSyllabusUploaded={vi.fn()} onComparisonCreated={created} />);
  const selects = screen.getAllByRole('combobox');
  fireEvent.change(selects[0], { target: { value: 'O' } });
  fireEvent.change(selects[1], { target: { value: 'O' } });
  const button = screen.getByRole('button', { name: 'Generar Dictamen de Correspondencia' });
  fireEvent.click(button);
  expect(await screen.findByText(/consigo mismo/)).toBeTruthy();
  expect(create).not.toHaveBeenCalled();
  fireEvent.change(selects[1], { target: { value: 'S' } });
  fireEvent.click(button);
  await waitFor(() => expect(created).toHaveBeenCalledWith(comparison));
  expect(create).toHaveBeenCalledWith('O', 'S');
});

it('carga un PDF seleccionado y notifica al catálogo', async () => {
  vi.spyOn(api, 'uploadSyllabus').mockResolvedValue(syllabi[0]);
  const uploaded = vi.fn();
  render(<SyllabusUploader existingSyllabi={[]} onSyllabusUploaded={uploaded} onComparisonCreated={vi.fn()} />);
  fireEvent.change(screen.getByLabelText('Documento PDF objetivo'), { target: { files: [new File(['%PDF'], 'curso.pdf')] } });
  fireEvent.click(screen.getByRole('button', { name: 'Cargar y Registrar Sílabo' }));
  await waitFor(() => expect(uploaded).toHaveBeenCalledOnce());
});

it('presenta evidencia y permite abrir la revisión del par original', () => {
  const open = vi.fn();
  render(<EvidencePanel match={match} onClose={vi.fn()} onOpenReview={open} humanReviewDecision="NO_MATCH" />);
  expect(screen.getAllByText(/Operaciones con matrices/).length).toBeGreaterThan(0);
  const button = screen.getAllByRole('button').find((b) => /Dictamen|Revis|Evaluar/.test(b.textContent ?? ''))!;
  fireEvent.click(button);
  expect(open).toHaveBeenCalledWith(match);
});

it('la guía se puede consultar y cerrar', () => {
  const close = vi.fn();
  const { rerender } = render(<SupportGuideModal isOpen={false} onClose={close} />);
  expect(screen.queryAllByRole('button')).toHaveLength(0);
  rerender(<SupportGuideModal isOpen onClose={close} />);
  expect(screen.getByRole('button', { name: /Ponderaci.*Multivariada/ })).toBeTruthy();
  fireEvent.click(screen.getAllByRole('button').find((b) => /Cerrar|✕/.test(b.textContent ?? ''))!);
  expect(close).toHaveBeenCalledOnce();
});

it('consulta el historial y permite iniciar una nueva evaluación', async () => {
  vi.spyOn(api, 'listComparisons').mockResolvedValue([]);
  const upload = vi.fn();
  render(<Dashboard syllabi={syllabi} onSelectComparison={vi.fn()} onGoToUpload={upload} />);
  await waitFor(() => expect(api.listComparisons).toHaveBeenCalled());
  fireEvent.click(screen.getByRole('button', { name: 'Nueva Evaluación Curricular' }));
  expect(upload).toHaveBeenCalledOnce();
});

it('traduce códigos conocidos y da valores predeterminados cuando faltan', () => {
  expect(getClassificationLabel('MATCH')).toBe('Equivalencia Total');
  expect(getClassificationLabel()).toBe('No especificado');
  expect(getCorrectionLabel('CONFIRMED')).toBe('Dictamen Ratificado');
  expect(getCorrectionLabel()).toBe('No especificado');
  expect(getEvidenceLabel('HYBRID')).toContain('Híbrida');
  expect(getEvidenceLabel('OTRO')).toBe('OTRO');
  expect(getEvidenceLabel()).toBe('Análisis Multivariado');
});
