import { expect, test } from '@playwright/test';
import type { ComparisonBatch } from '../src/types/index.ts';

test('compara varios candidatos, exporta el lote y recupera los análisis después de recargar', async ({ page, request }) => {
  const errors: string[] = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await page.getByRole('button', { name: 'Comparación por lotes', exact: true }).click();
  await page.getByLabel('Sílabo objetivo del lote').selectOption('OBJ-SYL-1');
  await page.getByRole('checkbox', { name: /University-1-CMP/ }).check();
  await page.getByRole('checkbox', { name: /University-2-CMP/ }).check();
  const response = page.waitForResponse(value => value.url().endsWith('/api/comparison-batches') && value.request().method() === 'POST');
  await page.getByRole('button', { name: 'Comparar candidatos seleccionados' }).click();
  const data = await (await response).json() as ComparisonBatch;
  expect(data.status).toBe('COMPLETED');
  const panel = page.getByRole('region', { name: 'Candidatos para test.pdf' });
  await expect(panel.getByRole('button', { name: 'Ver análisis de test.pdf' })).toHaveCount(2);
  await page.screenshot({ path: '../.reports/session31-batch-desktop.png', fullPage: true });
  const download = page.waitForEvent('download');
  await panel.getByRole('link', { name: 'Exportar lote JSON' }).click();
  expect((await download).suggestedFilename()).toBe(data.id + '.json');
  const comparisonId = data.results.find(result => result.compared_syllabus_id === data.ranking[0])!.comparison_id!;
  const report = await request.get(`http://127.0.0.1:18765/api/comparisons/${comparisonId}/report/pdf`);
  expect(report.status()).toBe(200);
  expect(report.headers()['content-type']).toContain('application/pdf');
  await panel.getByRole('button', { name: 'Ver análisis de test.pdf' }).first().click();
  await expect(page.getByRole('link', { name: 'Exportar PDF' })).toHaveAttribute('href', new RegExp(`/${comparisonId}/report/pdf$`));
  await page.reload();
  await page.getByRole('button', { name: 'Comparación por lotes', exact: true }).click();
  await page.getByRole('button', { name: /test.pdf.*2 candidatos/ }).first().click();
  await expect(page.getByRole('link', { name: 'Exportar lote JSON' })).toHaveAttribute('href', new RegExp(`/${data.id}/export$`));
  const countBefore = (await (await request.get('http://127.0.0.1:18765/api/comparisons')).json()).length;
  const replay = await request.post('http://127.0.0.1:18765/api/comparison-batches', { data: {
    request_id: data.id.slice(3), objective_syllabus_id: 'OBJ-SYL-1', compared_syllabus_ids: ['CMP-SYL-1', 'CMP-SYL-2'],
  } });
  expect(replay.status()).toBe(200);
  expect((await (await request.get('http://127.0.0.1:18765/api/comparisons')).json()).length).toBe(countBefore);
  expect(errors).toEqual([]);
});

test('conserva los resultados válidos de un lote parcial en móvil', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await page.getByRole('button', { name: 'Comparación por lotes', exact: true }).click();
  await page.getByLabel('Sílabo objetivo del lote').selectOption('OBJ-SYL-1');
  await page.getByRole('checkbox', { name: /University-1-CMP/ }).check();
  await page.getByRole('checkbox', { name: /University-4-CMP/ }).check();
  await page.getByRole('button', { name: 'Comparar candidatos seleccionados' }).click();
  const panel = page.getByRole('region', { name: 'Candidatos para test.pdf' });
  await expect(panel.getByText('Con errores parciales')).toBeVisible();
  await expect(panel.getByText('El candidato no contiene contenidos temáticos identificables.')).toBeVisible();
  await expect(panel.getByRole('button', { name: 'Ver análisis de test.pdf' })).toHaveCount(1);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.screenshot({ path: '../.reports/session31-batch-mobile.png', fullPage: true });
});
