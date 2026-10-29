import { expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { EvidenceNavigator } from '../src/components/EvidenceNavigator';
import { EvidenceOverlay } from '../src/components/EvidenceOverlay';
import { Header } from '../src/components/Header';
import { match } from './fixtures';
import type { MatchClassification } from '../src/types';

it('navega evidencias con teclado sin interferir con la escritura', () => {
  const select = vi.fn();
  render(<EvidenceNavigator matches={[match, { ...match, id: 'M2' }]} currentIndex={0} onSelectIndex={select} />);
  fireEvent.keyDown(window, { key: 'ArrowRight' });
  expect(select).toHaveBeenCalledWith(1);
  select.mockClear();
  fireEvent.keyDown(window, { key: 'ArrowLeft' });
  expect(select).not.toHaveBeenCalled();
});

it.each<MatchClassification>(['MATCH', 'PARTIAL_MATCH', 'UNCERTAIN', 'NO_MATCH'])('proyecta coordenadas PDF para %s', (classification) => {
  const region = { id: 'R1', match_id: 'M1', syllabus_id: 'O', content_id: 'I1', page_number: 1,
    page_width: 600, page_height: 800, x0: 60, y0: 80, x1: 180, y1: 160, text: 'Evidencia original', evidence_type: 'COMBINED' };
  const { container, rerender } = render(<EvidenceOverlay regions={[region]} pageNumber={1} canvasWidth={300} canvasHeight={400} classification={classification} />);
  const labels = { MATCH: 'EVIDENCIA ALTA', PARTIAL_MATCH: 'EVIDENCIA PARCIAL', UNCERTAIN: 'REVISAR', NO_MATCH: 'DISCREPANCIA' };
  expect(container.textContent).toContain(labels[classification]);
  expect(container.innerHTML).toContain('30px');
  rerender(<EvidenceOverlay regions={[region]} pageNumber={2} canvasWidth={300} canvasHeight={400} />);
  expect(container.innerHTML).toBe('');
});

it('habilita las pestañas de resultados solo con comparación activa', () => {
  const select = vi.fn();
  render(<Header currentTab="upload" hasActiveComparison={false} onSelectTab={select} />);
  fireEvent.click(screen.getByRole('button', { name: 'Modelos IA' }));
  expect(select).toHaveBeenCalledWith('models');
});
