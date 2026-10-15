import { useEffect, useState } from 'react';
import { api } from '../services/api';
import type {
  AnnotationBatch, AnnotationBatchProgress, AnnotationCase, AnnotationCoverage, AnnotationQueue,
  AnnotationReason, ComparisonSummary, CorrectionType, MatchClassification,
} from '../types';
import { CLASSIFICATIONS_ES } from '../utils/translations';

const reasons: Record<AnnotationReason, string> = {
  DISAGREEMENT: 'Resolver desacuerdo', SECOND_REVIEW: 'Necesita otro revisor', UNREVIEWED: 'Sin revisión',
};

const Coverage = ({ value }: { value: AnnotationCoverage }) => <span>
  {value.reviewed_pairs}/{value.total_pairs} pares revisados ({value.reviewed_percentage === null ? 'sin muestra' : `${value.reviewed_percentage}%`})
  {' · '}{value.consensus_pairs}/{value.total_pairs} con consenso ({value.consensus_percentage === null ? 'sin muestra' : `${value.consensus_percentage}%`})
  {' · '}{value.disagreement_pairs} desacuerdos · {value.review_events} revisiones registradas
</span>;

const CaseDetails = ({ item }: { item: AnnotationCase }) => <>
  <p><strong>{item.reason ? reasons[item.reason] : 'Con consenso'}</strong>
    {item.uncertain_prediction && ' · Predicción incierta'}{item.near_boundary && ' · Cerca de un umbral de referencia'}</p>
  <p><strong>Objetivo · página {item.objective_page ?? 'sin referencia'}:</strong> {item.objective_text}</p>
  <p><strong>Comparado · página {item.compared_page ?? 'sin referencia'}:</strong> {item.compared_text}</p>
  <p>Predicción original: {item.classification ? CLASSIFICATIONS_ES[item.classification].label : 'Sin predicción'}
    {' · '}Score: {item.score === null ? 'No disponible' : item.score.toFixed(3)}
    {' · '}{item.reviewer_ids.length} revisores · Versión: {item.model_version}</p>
</>;

const BatchReview = ({ item, reviewer, onSaved, onPending }: {
  item: AnnotationCase; reviewer: string; onSaved: () => Promise<void>; onPending: (value: boolean) => void;
}) => {
  const [decision, setDecision] = useState<MatchClassification>(item.classification ?? 'UNCERTAIN');
  const [justification, setJustification] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (justification.trim().length < 8) {
      setError('Escriba una justificación de al menos ocho caracteres.');
      return;
    }
    let correction: CorrectionType = 'OVERESTIMATION';
    if (!item.match_id) correction = 'MANUAL_LINK';
    else if (decision === item.classification) correction = 'CONFIRMED';
    else if (decision === 'NO_MATCH') correction = 'FALSE_POSITIVE';
    else if (item.classification === 'NO_MATCH') correction = 'FALSE_NEGATIVE';
    else if (decision === 'MATCH' || (decision === 'PARTIAL_MATCH' && item.classification === 'UNCERTAIN')) correction = 'UNDERESTIMATION';
    setSubmitting(true);
    onPending(true);
    setError(null);
    try {
      await api.submitReview({ comparison_id: item.comparison_id, reviewer_id: reviewer,
        human_decision: decision, correction_type: correction, justification: justification.trim(),
        ...(item.match_id ? { match_id: item.match_id } : {
          manual_objective_item_id: item.objective_item_id, manual_compared_item_id: item.compared_item_id,
        }),
      });
      setSaved(true);
      await onSaved();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'No se pudo registrar la revisión');
    } finally {
      setSubmitting(false);
      onPending(false);
    }
  };
  return <form onSubmit={submit} style={{ display: 'grid', gap: 10 }}>
    <p>Revisor del lote: <strong>{reviewer}</strong></p>
    <label>Decisión{' '}
      <select value={decision} disabled={submitting || saved} onChange={(e) => setDecision(e.target.value as MatchClassification)}>
        {(Object.keys(CLASSIFICATIONS_ES) as MatchClassification[]).map((key) => <option key={key} value={key}>{CLASSIFICATIONS_ES[key].label}</option>)}
      </select>
    </label>
    <label>Justificación académica
      <textarea value={justification} disabled={submitting || saved} required minLength={8}
        onChange={(e) => setJustification(e.target.value)} style={{ display: 'block', width: '100%', minHeight: 70 }} />
    </label>
    {error && <p role="alert">{error}</p>}
    {saved && <p role="status">Revisión registrada. Las predicciones originales se conservan.</p>}
    <button className="btn btn-primary" disabled={submitting || saved} type="submit">{submitting ? 'Guardando...' : 'Registrar revisión'}</button>
  </form>;
};

export const ActiveLearningPanel = ({ onOpenComparison, onAnnotationsChanged }: {
  onOpenComparison?: (id: string) => void; onAnnotationsChanged: () => void;
}) => {
  const [comparisons, setComparisons] = useState<ComparisonSummary[]>([]);
  const [draft, setDraft] = useState<{ comparisonId: string; reason: AnnotationReason | ''; reviewerId: string }>({ comparisonId: '', reason: '', reviewerId: '' });
  const [filters, setFilters] = useState(draft);
  const [offset, setOffset] = useState(0);
  const [refresh, setRefresh] = useState(0);
  const key = JSON.stringify([filters, offset, refresh]);
  const [result, setResult] = useState<{ key: string; queue: AnnotationQueue | null; batches: AnnotationBatch[]; error: string | null } | null>(null);
  const current = result?.key === key ? result : null;
  const [batch, setBatch] = useState<AnnotationBatchProgress | null>(null);
  const [size, setSize] = useState(10);
  const [caseIndex, setCaseIndex] = useState(0);
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const activeCase = batch?.items[caseIndex];

  useEffect(() => {
    let cancelled = false;
    api.listComparisons().then((data) => { if (!cancelled) setComparisons(data); })
      .catch((err: unknown) => console.error('Error al cargar comparaciones:', err));
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    Promise.all([api.getAnnotationQueue(filters, offset), api.listAnnotationBatches()]).then(([queue, batches]) => {
      if (!cancelled) setResult({ key, queue, batches, error: null });
    }).catch((err: unknown) => {
      if (!cancelled) setResult({ key, queue: null, batches: [], error: err instanceof Error ? err.message : 'No se pudo cargar la cola' });
    });
    return () => { cancelled = true; };
  }, [filters, offset, key]);

  const openBatch = async (id: string) => {
    setBusy(true);
    setActionError(null);
    try { setBatch(await api.getAnnotationBatch(id)); setCaseIndex(0); }
    catch (err: unknown) { setActionError(err instanceof Error ? err.message : 'No se pudo recuperar el lote'); }
    finally { setBusy(false); }
  };
  const createBatch = async () => {
    setBusy(true);
    setActionError(null);
    try {
      setBatch(await api.createAnnotationBatch(filters.reviewerId, filters.comparisonId, filters.reason, size));
      setCaseIndex(0);
      setRefresh((v) => v + 1);
    } catch (err: unknown) { setActionError(err instanceof Error ? err.message : 'No se pudo crear el lote'); }
    finally { setBusy(false); }
  };
  const reviewSaved = async () => {
    onAnnotationsChanged();
    setRefresh((v) => v + 1);
    if (!batch) return;
    try { setBatch(await api.getAnnotationBatch(batch.batch.id)); }
    catch { setActionError('La revisión se guardó, pero no se pudo actualizar el lote. Pulse Actualizar lote.'); }
  };
  const completeBatch = async () => {
    if (!batch) return;
    setBusy(true);
    setActionError(null);
    try { setBatch(await api.completeAnnotationBatch(batch.batch.id)); setRefresh((v) => v + 1); }
    catch (err: unknown) { setActionError(err instanceof Error ? err.message : 'No se pudo cerrar el lote'); }
    finally { setBusy(false); }
  };

  return <section className="card" style={{ marginTop: 24 }} aria-labelledby="active-learning-title">
    <h3 id="active-learning-title">Cola de revisión y aprendizaje activo</h3>
    <p>Primero se atienden desacuerdos, después pares con un revisor y luego pares sin revisar. La clasificación incierta y la cercanía a umbrales ordenan cada grupo; el score no representa una probabilidad.</p>
    <form onSubmit={(e) => { e.preventDefault(); setFilters({ ...draft, reviewerId: draft.reviewerId.trim() }); setOffset(0); setRefresh((v) => v + 1); }}
      style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center' }}>
      <label>Comparación{' '}<select value={draft.comparisonId} disabled={busy} onChange={(e) => setDraft((v) => ({ ...v, comparisonId: e.target.value }))}>
        <option value="">Todas</option>{comparisons.map((c) => <option key={c.id} value={c.id}>{c.objective_course} / {c.compared_course} · {c.id}</option>)}
      </select></label>
      <label>Motivo{' '}<select value={draft.reason} disabled={busy} onChange={(e) => setDraft((v) => ({ ...v, reason: e.target.value as AnnotationReason | '' }))}>
        <option value="">Todos</option>{Object.entries(reasons).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
      </select></label>
      <label>Revisor{' '}<input value={draft.reviewerId} maxLength={200} disabled={busy} onChange={(e) => setDraft((v) => ({ ...v, reviewerId: e.target.value }))} /></label>
      <button className="btn btn-secondary" disabled={busy} type="submit">Consultar cola</button>
    </form>
    {!current ? <p role="status">Consultando casos...</p> : current.error ? <p role="alert">{current.error}</p> : current.queue && <>
      <p><strong>Cobertura de los pares propuestos en el ámbito seleccionado:</strong> <Coverage value={current.queue.coverage} /></p>
      <p>Umbrales de referencia para priorizar: {Object.values(current.queue.reference_thresholds).join(', ')}. No sustituyen los parámetros del análisis original.</p>
      <p>{current.queue.total} casos elegibles. Los pares consensuados se excluyen; un autor no puede aportar un segundo voto independiente a su propia revisión única.</p>
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
        <label>Tamaño del lote{' '}<input type="number" min={1} max={100} value={size} disabled={busy} onChange={(e) => setSize(Number(e.target.value))} style={{ width: 64 }} /></label>
        <button className="btn btn-primary" disabled={busy || !filters.reviewerId || !current.queue.total || size < 1 || size > 100}
          onClick={createBatch}>Crear lote para {filters.reviewerId || 'un revisor identificado'}</button>
      </div>
      {!filters.reviewerId && <p>Indique su identificador y pulse Consultar cola para crear un lote.</p>}
      {current.queue.items.length === 0 ? <p>No hay casos pendientes con estos filtros.</p> : <ol start={offset + 1}>
        {current.queue.items.map((item) => <li key={item.case_id} style={{ marginTop: 12 }}>
          <strong>{item.objective_item_id} / {item.compared_item_id}</strong> · {item.reason ? reasons[item.reason] : ''}
          {item.uncertain_prediction && ' · Predicción incierta'}{item.near_boundary && ' · Cerca de un umbral'}
          {onOpenComparison && <button className="btn btn-secondary" disabled={busy} onClick={() => onOpenComparison(item.comparison_id)} style={{ marginLeft: 10 }}>Abrir informe</button>}
        </li>)}
      </ol>}
      <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
        <button className="btn btn-secondary" disabled={busy || offset === 0} onClick={() => setOffset((v) => Math.max(0, v - 20))}>Anterior</button>
        <span>{current.queue.total === 0 ? '0 casos' : `${offset + 1}–${Math.min(offset + 20, current.queue.total)} de ${current.queue.total}`}</span>
        <button className="btn btn-secondary" disabled={busy || offset + 20 >= current.queue.total} onClick={() => setOffset((v) => v + 20)}>Siguiente</button>
      </div>
      <label style={{ display: 'block', marginTop: 18 }}>Recuperar un lote reciente{' '}
        <select value={batch?.batch.id ?? ''} disabled={busy} onChange={(e) => { if (e.target.value) void openBatch(e.target.value); }}>
          <option value="">Seleccione un lote</option>{current.batches.map((b) => <option key={b.id} value={b.id}>{b.reviewer_id} · {b.cases.length} pares · {b.id}</option>)}
        </select>
      </label>
    </>}
    {actionError && <p role="alert">{actionError}</p>}
    {batch && <div style={{ borderTop: '1px solid var(--border-color)', marginTop: 20, paddingTop: 12 }}>
      <h4>Lote {batch.batch.id} · {batch.batch.reviewer_id} · {batch.completion ? 'Cerrado' : 'Abierto'}</h4>
      <p><strong>Antes:</strong> <Coverage value={batch.batch.coverage_before} /></p>
      <p><strong>{batch.completion ? 'Al cerrar:' : 'Ahora:'}</strong> <Coverage value={batch.completion?.coverage_after ?? batch.coverage_current} /></p>
      {batch.completion && <p><strong>Estado actual:</strong> <Coverage value={batch.coverage_current} /></p>}
      <p>Estas medidas corresponden a la selección fija del lote. Pueden incluir anotaciones de otros revisores realizadas en el mismo periodo.</p>
      <div style={{ display: 'flex', gap: 12 }}>
        <button className="btn btn-secondary" disabled={busy} onClick={() => void openBatch(batch.batch.id)}>Actualizar lote</button>
        <button className="btn btn-secondary" disabled={busy || !!batch.completion} onClick={completeBatch}>Cerrar lote y guardar medición</button>
      </div>
      {activeCase && <article style={{ marginTop: 18 }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <button className="btn btn-secondary" disabled={busy || caseIndex === 0} onClick={() => setCaseIndex((v) => v - 1)}>Caso anterior</button>
          <span>{caseIndex + 1}/{batch.items.length}</span>
          <button className="btn btn-secondary" disabled={busy || caseIndex + 1 >= batch.items.length} onClick={() => setCaseIndex((v) => v + 1)}>Caso siguiente</button>
        </div>
        <CaseDetails item={activeCase} />
        {onOpenComparison && <button className="btn btn-secondary" disabled={busy} onClick={() => onOpenComparison(activeCase.comparison_id)}>Abrir informe y evidencias PDF</button>}
        {!batch.completion && batch.eligible_case_ids.includes(activeCase.case_id) ? <BatchReview
          key={`${batch.batch.id}:${activeCase.case_id}`} item={activeCase} reviewer={batch.batch.reviewer_id} onSaved={reviewSaved} onPending={setBusy}
        /> : <p>{batch.completion ? 'El lote está cerrado.' : activeCase.status === 'CONSENSUS' ? 'Este par ya tiene consenso.' : 'Ya aportó su voto. Se necesita otro revisor.'}</p>}
      </article>}
    </div>}
    <p>La cobertura mide anotación de pares propuestos, no cobertura curricular. No se reentrenan ni activan modelos al revisar casos.</p>
  </section>;
};
