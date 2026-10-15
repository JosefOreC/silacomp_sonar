import { test, expect } from '@playwright/test';
import type { Page } from '@playwright/test';

const openStudies = async (page: Page) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Modelos IA', exact: true }).click();
  const panel = page.getByRole('region', { name: 'Evaluación sobre conjuntos reservados' });
  await expect(panel.getByLabel('Nombre del conjunto')).toBeVisible();
  return panel;
};

test('reserva, compara, descarga y recupera un experimento sin activar el modelo', async ({ page, request }) => {
  const pageErrors: string[] = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
  const panel = await openStudies(page);
  await expect(page.getByText('[object Object]', { exact: false })).toHaveCount(0);
  await expect(page.getByText('weights · semantic', { exact: true })).toBeVisible();
  await expect(panel.getByRole('button', { name: 'Crear conjunto reservado' })).toBeDisabled();
  await panel.getByLabel('Nombre del conjunto').fill('Reserva de navegador');
  await panel.getByLabel('Comparaciones a reservar').selectOption(['COMP-1', 'COMP-2']);
  await panel.getByRole('button', { name: 'Crear conjunto reservado' }).click();
  await expect(panel.getByRole('combobox', { name: 'Conjunto', exact: true })).toContainText('Reserva de navegador');
  const snapshotId = await panel.getByRole('combobox', { name: 'Conjunto', exact: true }).inputValue();
  await expect(panel.getByRole('button', { name: 'Ejecutar comparación reservada' })).toBeDisabled();
  await panel.getByRole('combobox', { name: 'Candidato', exact: true }).selectOption('bipartite-adaptive-002');
  await expect(panel.getByRole('button', { name: 'Ejecutar comparación reservada' })).toBeDisabled();
  await panel.getByRole('combobox', { name: 'Candidato', exact: true }).selectOption('candidate-1');
  await panel.getByRole('button', { name: 'Ejecutar comparación reservada' }).click();
  await expect(panel.getByRole('heading', { name: 'Cumple los criterios de promoción', exact: true })).toBeVisible();
  await expect(panel.getByText('2 comparaciones · 8 pares · 2 grupos independientes', { exact: false })).toBeVisible();
  const f1 = panel.getByRole('row').filter({ has: page.getByRole('cell', { name: 'F1 (0–1)', exact: true }) });
  await expect(f1.getByRole('cell').nth(1)).toHaveText('0.000');
  await expect(f1.getByRole('cell').nth(2)).toHaveText('1.000');

  const downloadPromise = page.waitForEvent('download');
  await panel.getByRole('link', { name: 'Descargar informe completo JSON' }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/^EXP-.*\.json$/);
  expect(await download.failure()).toBeNull();
  const response = await request.get('http://127.0.0.1:18765/api/models/active');
  expect((await response.json()).version_id).toBe('bipartite-adaptive-002');

  await page.reload();
  const reloaded = await openStudies(page);
  await expect(reloaded.getByRole('combobox', { name: 'Conjunto', exact: true })).toHaveValue(snapshotId);
  // El informe se recupera del servidor, no del estado de la página anterior.
  await reloaded.getByRole('combobox').last().selectOption({ index: 1 });
  await expect(reloaded.getByRole('heading', { name: 'Cumple los criterios de promoción', exact: true })).toBeVisible();
  await page.screenshot({ path: test.info().outputPath('evaluacion-reservada.png'), fullPage: true });
  expect(pageErrors).toEqual([]);
});

test('una matriz incompleta muestra el conflicto y permite volver a intentar', async ({ page, request }) => {
  const panel = await openStudies(page);
  const before = await (await request.get('http://127.0.0.1:18765/api/evaluation/snapshots')).json();
  await panel.getByLabel('Nombre del conjunto').fill('Reserva incompleta');
  await panel.getByLabel('Comparaciones a reservar').selectOption(['COMP-3']);
  await panel.getByRole('button', { name: 'Crear conjunto reservado' }).click();
  await expect(panel.getByRole('alert')).toContainText('Se requiere la matriz completa');
  await expect(panel.getByRole('button', { name: 'Crear conjunto reservado' })).toBeEnabled();
  const after = await (await request.get('http://127.0.0.1:18765/api/evaluation/snapshots')).json();
  expect(after).toEqual(before);
});

test('el panel permite recuperarse de un fallo de consulta', async ({ page, request }) => {
  const created = await request.post('http://127.0.0.1:18765/api/evaluation/snapshots', {
    data: { name: 'Reserva para recuperación', comparison_ids: ['COMP-1', 'COMP-2'] },
  });
  expect(created.status()).toBe(201);
  const snapshot: { id: string } = await created.json();
  await page.route('**/api/evaluation/snapshots', (route) => route.fulfill({
    status: 503, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' },
    body: JSON.stringify({ detail: 'Servicio temporalmente no disponible' }),
  }));
  await page.goto('/');
  await page.getByRole('button', { name: 'Modelos IA', exact: true }).click();
  const panel = page.getByRole('region', { name: 'Evaluación sobre conjuntos reservados' });
  await expect(panel.getByRole('alert')).toHaveText('Servicio temporalmente no disponible');
  await page.unroute('**/api/evaluation/snapshots');
  await panel.getByRole('button', { name: 'Consultar estudios' }).click();
  await expect(panel.getByLabel('Nombre del conjunto')).toBeVisible();
  await expect(panel.getByRole('combobox', { name: 'Conjunto', exact: true })).toHaveValue(snapshot.id);
  await expect(panel.getByRole('alert')).toHaveCount(0);
});

test('sin estudios muestra instrucciones y mantiene deshabilitadas las acciones incompletas', async ({ page }) => {
  for (const resource of ['snapshots', 'experiments']) {
    await page.route(`**/api/evaluation/${resource}`, (route) => route.fulfill({
      status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: '[]',
    }));
  }
  const panel = await openStudies(page);
  await expect(panel.getByText('Aún no hay conjuntos reservados.', { exact: false })).toBeVisible();
  await expect(panel.getByText('Aún no hay experimentos guardados.')).toBeVisible();
  await expect(panel.getByRole('button', { name: 'Crear conjunto reservado' })).toBeDisabled();
  await expect(panel.getByRole('button', { name: 'Ejecutar comparación reservada' })).toHaveCount(0);
});
