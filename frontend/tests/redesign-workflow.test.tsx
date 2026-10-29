import { expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { SyllabusUploader } from '../src/components/SyllabusUploader';
import { SupportGuideModal } from '../src/components/SupportGuideModal';
import { api } from '../src/services/api';
import { comparison, syllabi } from './fixtures';

it('registra ambos PDF con sus metadatos independientes antes de compararlos', async () => {
  const upload = vi.spyOn(api, 'uploadSyllabus').mockResolvedValueOnce(syllabi[0]).mockResolvedValueOnce(syllabi[1]);
  vi.spyOn(api, 'createComparison').mockResolvedValue(comparison);
  const created = vi.fn();
  const uploaded = vi.fn();
  render(<SyllabusUploader existingSyllabi={[]} onSyllabusUploaded={uploaded} onComparisonCreated={created} />);
  const objective = within(screen.getByRole('region', { name: 'Sílabo objetivo' }));
  const compared = within(screen.getByRole('region', { name: 'Sílabo comparado' }));
  const files = [new File(['%PDF'], 'destino.pdf'), new File(['%PDF'], 'origen.pdf')];
  for (const [index, panel] of [objective, compared].entries()) {
    fireEvent.change(panel.getByLabelText(index === 0 ? 'Documento PDF objetivo' : 'Documento PDF comparado'), { target: { files: [files[index]] } });
    fireEvent.change(panel.getByLabelText('Universidad / Institución'), { target: { value: `Universidad ${index}` } });
    fireEvent.change(panel.getByLabelText('Nombre de Asignatura'), { target: { value: `Curso ${index}` } });
    fireEvent.click(panel.getByRole('button', { name: 'Cargar y Registrar Sílabo' }));
    await waitFor(() => expect(panel.getByText('Listo')).toBeTruthy());
    expect(upload).toHaveBeenNthCalledWith(index + 1, files[index], `Universidad ${index}`, `Curso ${index}`);
  }
  expect(uploaded).toHaveBeenCalledTimes(2);
  fireEvent.click(screen.getByRole('button', { name: 'Generar Dictamen de Correspondencia' }));
  await waitFor(() => expect(created).toHaveBeenCalledWith(comparison));
  expect(api.createComparison).toHaveBeenCalledWith('O', 'S');
});

it('mantiene el archivo y los metadatos para reintentar una carga fallida', async () => {
  const upload = vi.spyOn(api, 'uploadSyllabus').mockRejectedValueOnce(new Error('No se pudo leer el PDF')).mockResolvedValue(syllabi[0]);
  render(<SyllabusUploader existingSyllabi={[]} onSyllabusUploaded={vi.fn()} onComparisonCreated={vi.fn()} />);
  fireEvent.change(screen.getByLabelText('Documento PDF objetivo'), { target: { files: [new File(['pdf'], 'curso.pdf')] } });
  fireEvent.change(screen.getAllByLabelText('Nombre de Asignatura')[0], { target: { value: 'Álgebra' } });
  fireEvent.click(screen.getByRole('button', { name: 'Cargar y Registrar Sílabo' }));
  expect((await screen.findByRole('alert')).textContent).toBe('No se pudo leer el PDF');
  expect((screen.getAllByLabelText('Nombre de Asignatura')[0] as HTMLInputElement).value).toBe('Álgebra');
  fireEvent.click(screen.getByRole('button', { name: 'Cargar y Registrar Sílabo' }));
  await screen.findByText('Listo');
  expect(upload).toHaveBeenCalledTimes(2);
  expect(screen.queryByRole('alert')).toBeNull();
});

it('permite reintentar la comparación sin perder los documentos elegidos', async () => {
  vi.spyOn(api, 'createComparison').mockRejectedValueOnce(new Error('Comparación no disponible')).mockResolvedValue(comparison);
  const created = vi.fn();
  render(<SyllabusUploader existingSyllabi={syllabi} onSyllabusUploaded={vi.fn()} onComparisonCreated={created} />);
  const selects = screen.getAllByRole('combobox');
  fireEvent.change(selects[0], { target: { value: 'O' } });
  fireEvent.change(selects[1], { target: { value: 'S' } });
  fireEvent.click(screen.getByRole('button', { name: 'Generar Dictamen de Correspondencia' }));
  expect((await screen.findByRole('alert')).textContent).toBe('Comparación no disponible');
  expect(created).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button', { name: 'Generar Dictamen de Correspondencia' }));
  await waitFor(() => expect(created).toHaveBeenCalledWith(comparison));
  expect((selects[0] as HTMLSelectElement).value).toBe('O');
  expect((selects[1] as HTMLSelectElement).value).toBe('S');
});

it('contiene el foco de la guía, cierra con Escape y devuelve el foco al control de origen', () => {
  const close = vi.fn();
  const { rerender } = render(<><button>Origen</button><SupportGuideModal isOpen={false} onClose={close} /></>);
  const origin = screen.getByRole('button', { name: 'Origen' });
  origin.focus();
  rerender(<><button>Origen</button><SupportGuideModal isOpen onClose={close} /></>);
  const dialog = screen.getByRole('dialog');
  expect(document.activeElement).toBe(dialog);
  fireEvent.keyDown(window, { key: 'Tab', shiftKey: true });
  const buttons = within(dialog).getAllByRole('button');
  expect(document.activeElement).toBe(buttons[buttons.length - 1]);
  fireEvent.keyDown(window, { key: 'Tab' });
  expect(document.activeElement).toBe(buttons[0]);
  fireEvent.keyDown(window, { key: 'Escape' });
  expect(close).toHaveBeenCalledOnce();
  rerender(<><button>Origen</button><SupportGuideModal isOpen={false} onClose={close} /></>);
  expect(document.activeElement).toBe(origin);
  fireEvent.keyDown(window, { key: 'Escape' });
  expect(close).toHaveBeenCalledOnce();
});
