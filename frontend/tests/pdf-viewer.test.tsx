import { beforeEach, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { PdfDocumentViewer } from '../src/components/PdfDocumentViewer';

const pdf = vi.hoisted(() => ({ getDocument: vi.fn(), getPage: vi.fn(), destroy: vi.fn(),
  render: vi.fn(), cancel: vi.fn() }));
vi.mock('../src/utils/pdfSetup', () => ({ pdfjsLib: { getDocument: pdf.getDocument } }));

beforeEach(() => {
  pdf.destroy.mockReset().mockResolvedValue(undefined);
  pdf.cancel.mockReset();
  pdf.render.mockReset().mockReturnValue({ promise: Promise.resolve(), cancel: pdf.cancel });
  pdf.getPage.mockReset().mockResolvedValue({
    getViewport: ({ scale }: { scale: number }) => ({ width: 600 * scale, height: 800 * scale }),
    render: pdf.render,
  });
  pdf.getDocument.mockReset().mockReturnValue({
    promise: Promise.resolve({ numPages: 3, getPage: pdf.getPage }), destroy: pdf.destroy,
  });
  vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({ imageSmoothingEnabled: false } as CanvasRenderingContext2D);
});

it('carga y renderiza una página, cambia zoom y navega dentro de los límites', async () => {
  const change = vi.fn();
  render(<PdfDocumentViewer pdfUrl="/document.pdf" pageNumber={1} title="Objetivo" onPageChange={change} />);
  await waitFor(() => expect(pdf.render).toHaveBeenCalled());
  expect(pdf.getPage).toHaveBeenCalledWith(1);
  expect(screen.getByText('Objetivo')).toBeTruthy();
  fireEvent.click(screen.getByTitle('Ajustar a la Página Completa'));
  fireEvent.click(screen.getByTitle('Aumentar Zoom'));
  fireEvent.click(screen.getByTitle('Reducir Zoom'));
  fireEvent.click(screen.getByTitle('Restablecer 100%'));
  fireEvent.click(screen.getByTitle('Ajustar al Ancho'));
  const buttons = screen.getAllByRole('button');
  expect((buttons[buttons.length - 2] as HTMLButtonElement).disabled).toBe(true);
  fireEvent.click(buttons[buttons.length - 1]);
  expect(change).toHaveBeenCalledWith(2);
});

it('muestra un error recuperable si falla la descarga del PDF', async () => {
  vi.spyOn(console, 'error').mockImplementation(() => {});
  pdf.getDocument.mockReturnValue({ promise: Promise.reject(new Error('No disponible')), destroy: pdf.destroy });
  render(<PdfDocumentViewer pdfUrl="/missing.pdf" pageNumber={1} title="Origen" onPageChange={vi.fn()} />);
  expect(await screen.findByText('No se pudo visualizar el archivo PDF original en el servidor.')).toBeTruthy();
  expect(pdf.render).not.toHaveBeenCalled();
});

it('libera el documento al cambiar de URL y al desmontar el visor', async () => {
  const { rerender, unmount } = render(<PdfDocumentViewer pdfUrl="/one.pdf" pageNumber={9} title="Objetivo" onPageChange={vi.fn()} />);
  await waitFor(() => expect(pdf.getPage).toHaveBeenCalledWith(3));
  rerender(<PdfDocumentViewer pdfUrl="/two.pdf" pageNumber={1} title="Origen" onPageChange={vi.fn()} />);
  await waitFor(() => expect(pdf.getDocument).toHaveBeenCalledTimes(2));
  expect(pdf.destroy).toHaveBeenCalledOnce();
  unmount();
  expect(pdf.destroy).toHaveBeenCalledTimes(2);
});
