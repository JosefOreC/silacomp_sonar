import { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { EvaluationCriteria, EvaluationExperiment, ModelVersion } from '../types';

const BASELINE = 'bipartite-adaptive-002';
const loadStudies = () => Promise.all([api.listEvaluationSnapshots(), api.listEvaluationExperiments(), api.listComparisons()]);
const checkLabels: Record<string, string> = {
  f1_gain: 'Mejora mínima de F1', recall: 'Recall sin regresión fuera de tolerancia',
  objective_coverage: 'Error de cobertura objetivo', compared_coverage: 'Error de cobertura comparado',
  per_comparison_f1: 'Límite de regresión de F1 por comparación',
  per_comparison_coverage: 'Límite de error de cobertura por comparación',
  independent_groups: 'Grupos académicos independientes suficientes',
  positive_and_negative_support: 'Casos positivos y negativos representados',
};

export const ScientificEvaluationPanel = ({ models }: { models: ModelVersion[] }) => {
  const [data, setData] = useState<Awaited<ReturnType<typeof loadStudies>> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [name, setName] = useState('');
  const [comparisonIds, setComparisonIds] = useState<string[]>([]);
  const [snapshotId, setSnapshotId] = useState('');
  const [reference, setReference] = useState(BASELINE);
  const [candidate, setCandidate] = useState('');
  const [report, setReport] = useState<EvaluationExperiment | null>(null);
  const [criteria, setCriteria] = useState<EvaluationCriteria>({ min_f1_gain: .01, max_recall_drop: 0,
    max_coverage_mae_increase: 0, max_per_comparison_f1_drop: .05, max_per_comparison_coverage_increase: 0,
    min_independent_groups: 2 });
  const versions = [BASELINE, ...models.map((model) => model.version_id).filter((id) => id !== BASELINE)];

  useEffect(() => {
    let cancelled = false;
    loadStudies().then((result) => {
      if (!cancelled) { setData(result); setSnapshotId((previous) => previous || result[0][0]?.id || ''); }
    }).catch((err: unknown) => { if (!cancelled) setError(err instanceof Error ? err.message : 'Error al consultar los experimentos'); });
    return () => { cancelled = true; };
  }, []);

  const refresh = async () => {
    setBusy(true); setError(null);
    try {
      const result = await loadStudies();
      setData(result);
      setSnapshotId((previous) => result[0].some((snapshot) => snapshot.id === previous) ? previous : result[0][0]?.id ?? '');
    }
    catch (err: unknown) { setError(err instanceof Error ? err.message : 'No se pudo actualizar el estudio'); }
    finally { setBusy(false); }
  };
  const createSnapshot = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true); setError(null);
    try {
      const created = await api.createEvaluationSnapshot(name.trim(), comparisonIds);
      setSnapshotId(created.id);
      setData(await loadStudies());
    } catch (err: unknown) { setError(err instanceof Error ? err.message : 'No se pudo reservar el conjunto'); }
    finally { setBusy(false); }
  };
  const run = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true); setError(null);
    try {
      const result = await api.createEvaluationExperiment(snapshotId, reference, candidate, criteria);
      setReport(result);
      setData(await loadStudies());
    } catch (err: unknown) { setError(err instanceof Error ? err.message : 'No se pudo ejecutar el experimento'); }
    finally { setBusy(false); }
  };

  return <section className="card" style={{ marginTop: 28 }} aria-labelledby="evaluation-title">
    <h3 id="evaluation-title">Evaluación sobre conjuntos reservados</h3>
    <p>Compare versiones sobre las mismas anotaciones y características congeladas, incluyendo selección de correspondencias y cobertura de ambos sílabos.</p>
    {error && <p role="alert">{error}</p>}
    {busy && <p role="status">Procesando el estudio...</p>}
    {!data ? <button className="btn btn-secondary" disabled={busy} onClick={refresh}>Consultar estudios</button> : <>
      <form onSubmit={createSnapshot} style={{ display: 'grid', gap: 12 }}>
        <h4>1. Reservar comparaciones revisadas</h4>
        <p>Se requiere consenso definitivo de al menos dos revisores en todos los pares posibles. Estas fuentes se excluirán de los entrenamientos posteriores.</p>
        <label>Nombre del conjunto{' '}<input required maxLength={100} value={name} disabled={busy} onChange={(e) => setName(e.target.value)} /></label>
        <label>Comparaciones a reservar (hasta 20)
          <select multiple required value={comparisonIds} disabled={busy} style={{ display: 'block', width: '100%', minHeight: 100 }}
            onChange={(e) => setComparisonIds(Array.from(e.target.selectedOptions, (option) => option.value))}>
            {data[2].map((c) => <option key={c.id} value={c.id}>{c.objective_course} / {c.compared_course} · {c.id}</option>)}
          </select>
        </label>
        <button type="submit" className="btn btn-secondary" disabled={busy || !name.trim() || comparisonIds.length === 0 || comparisonIds.length > 20}>Crear conjunto reservado</button>
      </form>
      <form onSubmit={run} style={{ display: 'grid', gap: 12, marginTop: 24 }}>
        <h4>2. Comparar versiones</h4>
        {data[0].length === 0 ? <p>Aún no hay conjuntos reservados. Complete las anotaciones y cree uno antes de comparar.</p> : <>
          <label>Conjunto{' '}<select value={snapshotId} required disabled={busy} onChange={(e) => setSnapshotId(e.target.value)}>
            <option value="">Seleccione un conjunto</option>{data[0].map((s) => <option key={s.id} value={s.id}>{s.name} · {s.comparison_count} comparaciones · {s.pair_count} pares · {s.independent_groups} grupos</option>)}
          </select></label>
          {snapshotId && <a href={api.getEvaluationExportUrl('snapshots', snapshotId)}>Descargar conjunto y trazabilidad JSON</a>}
          <label>Referencia{' '}<select value={reference} disabled={busy} onChange={(e) => setReference(e.target.value)}>
            {versions.map((id) => <option key={id} value={id}>{id === BASELINE ? 'Baseline heurístico' : id}</option>)}
          </select></label>
          <label>Candidato{' '}<select required value={candidate} disabled={busy} onChange={(e) => setCandidate(e.target.value)}>
            <option value="">Seleccione una versión</option>{versions.map((id) => <option key={id} value={id}>{id === BASELINE ? 'Baseline heurístico' : id}</option>)}
          </select></label>
          <label>Ganancia mínima de F1 (0–1){' '}<input type="number" min={.001} max={1} step={.001} value={criteria.min_f1_gain}
            disabled={busy} onChange={(e) => setCriteria((c) => ({ ...c, min_f1_gain: Number(e.target.value) }))} /></label>
          <label>Pérdida máxima de F1 por comparación{' '}<input type="number" min={0} max={1} step={.01} value={criteria.max_per_comparison_f1_drop}
            disabled={busy} onChange={(e) => setCriteria((c) => ({ ...c, max_per_comparison_f1_drop: Number(e.target.value) }))} /></label>
          <p>Se exigen al menos dos grupos independientes y ejemplos positivos y negativos. Recall y errores de cobertura deben mantenerse o mejorar, tanto globalmente como por comparación según los criterios registrados.</p>
          <button type="submit" className="btn btn-primary" disabled={busy || !snapshotId || !candidate || candidate === reference}>Ejecutar comparación reservada</button>
        </>}
      </form>
      <h4>Experimentos recientes</h4>
      {data[1].length === 0 ? <p>Aún no hay experimentos guardados.</p> : <select value={report?.id ?? ''} disabled={busy}
        onChange={(e) => setReport(data[1].find((r) => r.id === e.target.value) ?? null)}>
        <option value="">Seleccione un experimento</option>{data[1].map((r) => <option key={r.id} value={r.id}>{r.created_at} · {r.id}</option>)}
      </select>}
      <button className="btn btn-secondary" disabled={busy} onClick={refresh} style={{ marginLeft: 12 }}>Actualizar estudios</button>
    </>}
    {report && <div style={{ marginTop: 20 }}>
      <h4>{report.report.promotion_recommended ? 'Cumple los criterios de promoción' : 'No cumple todos los criterios de promoción'}</h4>
      <p>{report.report.sample.comparisons} comparaciones · {report.report.sample.pairs} pares · {report.report.sample.independent_groups} grupos independientes · {report.report.sample.positive_pairs} positivos / {report.report.sample.negative_pairs} negativos.</p>
      <p>Conjunto: {report.snapshot_id}</p>
      <p style={{ overflowWrap: 'anywhere' }}>SHA-256 del conjunto: {report.report.snapshot_hash}</p>
      <a href={api.getEvaluationExportUrl('experiments', report.id)}>Descargar informe completo JSON</a>
      <div style={{ overflowX: 'auto', marginTop: 12 }}><table style={{ width: '100%', textAlign: 'left' }}>
        <thead><tr><th>Métrica</th><th>Referencia: {report.report.evaluations.reference.manifest.version_id}</th><th>Candidato: {report.report.evaluations.candidate.manifest.version_id}</th></tr></thead>
        <tbody>{[['F1 (0–1)', 'f1'], ['Precisión (0–1)', 'precision'], ['Recall (0–1)', 'recall'],
          ['MAE cobertura objetivo (puntos porcentuales)', 'objective_coverage_mae'], ['MAE cobertura comparado (puntos porcentuales)', 'compared_coverage_mae']].map(([label, metric]) => <tr key={metric}>
          <td>{label}</td><td>{report.report.evaluations.reference.aggregate[metric].toFixed(3)}</td><td>{report.report.evaluations.candidate.aggregate[metric].toFixed(3)}</td>
        </tr>)}</tbody>
      </table></div>
      <ul>{Object.entries(report.report.checks).map(([check, passed]) => <li key={check}>{passed ? 'Cumple' : 'No cumple'}: {checkLabels[check] ?? check}</li>)}</ul>
      <h4>Cambios por comparación</h4>
      <div style={{ overflowX: 'auto' }}><table style={{ width: '100%', textAlign: 'left' }}>
        <thead><tr><th>Comparación</th><th>Δ F1</th><th>Δ error objetivo</th><th>Δ error comparado</th></tr></thead>
        <tbody>{report.report.regressions.map((r) => <tr key={r.comparison_id}><td>{r.comparison_id}</td>
          <td>{r.f1_delta.toFixed(3)}</td><td>{r.objective_error_delta.toFixed(1)}</td><td>{r.compared_error_delta.toFixed(1)}</td></tr>)}</tbody>
      </table></div>
      <p>La recomendación se limita a estos datos y criterios. No activa el modelo ni constituye una resolución académica.</p>
    </div>}
  </section>;
};
