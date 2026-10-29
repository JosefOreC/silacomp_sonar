import { useEffect, useState } from 'react';
import { ArrowRight, Download, FileText, GitCompareArrows, History, LoaderCircle, RefreshCw, X } from 'lucide-react';
import { api } from '../services/api';
import type { ComparisonBatch, ComparisonBatchRequest, Syllabus } from '../types';

interface BatchComparisonViewProps {
  syllabi: Syllabus[];
  onOpenComparison: (id: string) => void;
  onGoToUpload: () => void;
}

const statusLabels: Record<ComparisonBatch['status'], string> = {
  RUNNING: 'Pendiente de finalización', COMPLETED: 'Completado', PARTIAL: 'Con errores parciales',
  FAILED: 'Sin comparaciones completadas',
};
const normalize = (text: string) => text.normalize('NFD').replace(/\p{M}/gu, '').toLocaleLowerCase();
const percentage = (value: number | null | undefined, ratio = false) =>
  value === null || value === undefined ? '—' : `${(value * (ratio ? 100 : 1)).toFixed(1)}%`;

const BatchResults = ({ batch, onOpen, onRefresh, refreshing }: {
  batch: ComparisonBatch; onOpen: (id: string) => void; onRefresh: () => void; refreshing: boolean;
}) => {
  const successful = batch.results.filter(result => result.comparison_id !== null).length;
  const failed = batch.results.length - successful;
  const candidates = new Map(batch.candidates.map(candidate => [candidate.id, candidate]));
  const results = new Map(batch.results.map(result => [result.compared_syllabus_id, result]));
  const ordered = [...batch.ranking, ...batch.candidates.map(candidate => candidate.id).filter(id => !batch.ranking.includes(id))];
  return <section className="batch-results card" aria-labelledby="batch-results-title">
    <div className="batch-section-heading"><div><span className="section-eyebrow">RESULTADOS INDEPENDIENTES</span>
      <h2 id="batch-results-title">Candidatos para {batch.objective.title}</h2>
      <p>Ordenados por cobertura del objetivo y, en caso de empate, por afinidad global.</p></div>
      <span className={`batch-status batch-status-${batch.status.toLowerCase()}`}>{statusLabels[batch.status]}</span>
    </div>
    <div className="batch-counters">
      <span><strong>{batch.candidates.length}</strong> candidatos</span>
      <span><strong>{successful}</strong> comparaciones completadas</span>
      <span><strong>{failed}</strong> con error</span>
      <span><strong>{batch.candidates.length - batch.results.length}</strong> pendientes</span>
    </div>
    <p className="batch-scope-note">Cada fila corresponde a un análisis distinto. Las coberturas de varios candidatos no se suman ni constituyen una resolución de convalidación.</p>
    {batch.status === 'RUNNING' && <p className="batch-scope-note" role="status">Los avances guardados pueden consultarse aunque la solicitud se haya interrumpido. El lote no se reanuda automáticamente; para continuar, crea otro solo con los candidatos pendientes.</p>}
    <div className="batch-table-scroll"><table className="batch-table">
      <thead><tr><th>Orden</th><th>Asignatura candidata</th><th>Cobertura del objetivo</th><th>Cobertura del candidato</th><th>Afinidad global</th><th>Evidencia</th></tr></thead>
      <tbody>{ordered.map(id => {
        const candidate = candidates.get(id);
        const result = results.get(id);
        const comparisonId = result?.comparison_id;
        return <tr key={id}>
          <td>{comparisonId ? <span className="rank-badge">{batch.ranking.indexOf(id) + 1}</span> : '—'}</td>
          <td><strong>{candidate?.title ?? id}</strong><span className="batch-subtext">{candidate?.university ?? 'Universidad no registrada'}</span>
            {result?.error && <span className="batch-result-error">{result.error}</span>}
            {!result && <span className="batch-subtext">Sin resultado guardado todavía</span>}
          </td>
          <td>{percentage(result?.objective_coverage)}</td><td>{percentage(result?.compared_coverage)}</td><td>{percentage(result?.global_score, true)}</td>
          <td>{comparisonId ? <div className="batch-row-actions">
            <button type="button" className="btn btn-primary" aria-label={`Ver análisis de ${candidate?.title ?? id}`} onClick={() => onOpen(comparisonId)}>Ver análisis <ArrowRight size={13} /></button>
            <a className="btn btn-secondary" href={api.getReportPdfUrl(comparisonId)} target="_blank" rel="noopener noreferrer">Informe PDF</a>
          </div> : <span className="batch-subtext">{result ? 'Sin comparación' : 'Pendiente'}</span>}</td>
        </tr>;
      })}</tbody>
    </table></div>
    <div className="batch-result-footer"><span>Modelo: <code>{batch.model_version}</code><br />{batch.id}</span>
      <div className="batch-row-actions">
        <button type="button" className="btn btn-secondary" onClick={onRefresh} disabled={refreshing}><RefreshCw size={14} /> Actualizar resultado</button>
        <a className="btn btn-secondary" href={api.getComparisonBatchExportUrl(batch.id)} download><Download size={14} /> Exportar lote JSON</a>
      </div>
    </div>
  </section>;
};

export const BatchComparisonView = ({ syllabi, onOpenComparison, onGoToUpload }: BatchComparisonViewProps) => {
  const [objectiveId, setObjectiveId] = useState('');
  const [candidateIds, setCandidateIds] = useState<string[]>([]);
  const [search, setSearch] = useState('');
  const [request, setRequest] = useState<ComparisonBatchRequest | null>(null);
  const [batch, setBatch] = useState<ComparisonBatch | null>(null);
  const [history, setHistory] = useState<ComparisonBatch[]>([]);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    let cancelled = false;
    api.listComparisonBatches().then(data => { if (!cancelled) setHistory(data); })
      .catch((failure: unknown) => { if (!cancelled) setHistoryError(failure instanceof Error ? failure.message : 'No se pudieron consultar los lotes.'); });
    return () => { cancelled = true; };
  }, []);

  const resetRequest = () => { setRequest(null); setBatch(null); setError(null); };
  const selectCandidate = (id: string) => {
    setCandidateIds(previous => previous.includes(id) ? previous.filter(value => value !== id) : [...previous, id]);
    resetRequest();
  };
  const remember = (value: ComparisonBatch) => {
    setBatch(value);
    setHistory(previous => [value, ...previous.filter(item => item.id !== value.id)]);
  };
  const run = async () => {
    const payload = request ?? { request_id: crypto.randomUUID(), objective_syllabus_id: objectiveId, compared_syllabus_ids: candidateIds };
    setRequest(payload);
    setBusy(true);
    setError(null);
    try { remember(await api.createComparisonBatch(payload)); }
    catch (failure: unknown) { setError(failure instanceof Error ? failure.message : 'No se pudo ejecutar la comparación por lotes.'); }
    finally { setBusy(false); }
  };
  const loadBatch = async (id: string) => {
    setRefreshing(true);
    setError(null);
    try { remember(await api.getComparisonBatch(id)); }
    catch (failure: unknown) { setError(failure instanceof Error ? failure.message : 'No se pudo recuperar el lote.'); }
    finally { setRefreshing(false); }
  };
  const refreshHistory = async () => {
    setRefreshing(true);
    setHistoryError(null);
    try { setHistory(await api.listComparisonBatches()); }
    catch (failure: unknown) { setHistoryError(failure instanceof Error ? failure.message : 'No se pudieron consultar los lotes.'); }
    finally { setRefreshing(false); }
  };
  const filtered = syllabi.filter(syllabus => syllabus.id !== objectiveId && normalize(
    `${syllabus.course_name ?? ''} ${syllabus.university ?? ''} ${syllabus.filename}`,
  ).includes(normalize(search)));

  return <div className="batch-page page-container">
    <div className="batch-page-heading"><div><span className="section-eyebrow">COMPARACIÓN POR LOTES</span>
      <h1 className="page-heading">Un objetivo. Varias posibilidades.</h1>
      <p>Contrasta un sílabo con hasta cinco candidatos y consulta la evidencia de cada comparación.</p></div>
      <span className="batch-heading-icon"><GitCompareArrows size={28} strokeWidth={1.5} /></span>
    </div>
    {syllabi.length < 2 ? <section className="card batch-empty"><FileText size={34} /><h2>Prepara tus documentos</h2>
      <p>Necesitas al menos dos sílabos registrados para iniciar un lote.</p><button type="button" className="btn btn-primary" onClick={onGoToUpload}>Cargar sílabos <ArrowRight size={15} /></button>
    </section> : <section className="card batch-selection" aria-labelledby="batch-selection-title">
      <div className="batch-section-heading"><div><span className="section-eyebrow">01 · DOCUMENTOS DEL LOTE</span><h2 id="batch-selection-title">Define qué quieres contrastar</h2></div>
        <span className="batch-selection-count">{candidateIds.length}/5 candidatos seleccionados</span>
      </div>
      <div className="field-group batch-objective"><label htmlFor="batch-objective">Sílabo objetivo del lote</label>
        <select id="batch-objective" value={objectiveId} disabled={busy || refreshing} onChange={event => {
          setObjectiveId(event.target.value); setCandidateIds(previous => previous.filter(id => id !== event.target.value)); resetRequest();
        }}><option value="">Selecciona la asignatura requerida</option>{syllabi.map(syllabus => <option key={syllabus.id} value={syllabus.id}>{syllabus.course_name || syllabus.filename} · {syllabus.university || 'Universidad no registrada'}</option>)}</select>
      </div>
      {objectiveId ? <>
        <div className="field-group batch-search"><label htmlFor="batch-search">Buscar candidatos</label><input id="batch-search" value={search} onChange={event => setSearch(event.target.value)} placeholder="Asignatura, universidad o archivo" /></div>
        {candidateIds.length > 0 && <div className="batch-selected-chips">{candidateIds.map(id => {
          const syllabus = syllabi.find(item => item.id === id);
          const title = syllabus?.course_name || syllabus?.filename || id;
          return <button type="button" className="batch-selected-chip" key={id} disabled={busy || refreshing} onClick={() => selectCandidate(id)} aria-label={`Quitar ${title}`}>{title} <X size={12} /></button>;
        })}</div>}
        <div className="batch-candidate-grid">{filtered.map(syllabus => <label key={syllabus.id}
          aria-label={`Seleccionar ${syllabus.course_name || syllabus.filename} de ${syllabus.university || 'Universidad no registrada'}`}
          className={`batch-candidate${candidateIds.includes(syllabus.id) ? ' is-selected' : ''}`}>
          <input type="checkbox" checked={candidateIds.includes(syllabus.id)} disabled={busy || refreshing || (candidateIds.length >= 5 && !candidateIds.includes(syllabus.id))} onChange={() => selectCandidate(syllabus.id)} />
          <span><strong>{syllabus.course_name || syllabus.filename}</strong><span>{syllabus.university || 'Universidad no registrada'} · {syllabus.total_pages} páginas</span></span>
        </label>)}</div>
        {filtered.length === 0 && <p className="batch-empty-search">No se encontraron candidatos con ese texto.</p>}
      </> : <p className="batch-scope-note">Selecciona primero el objetivo para elegir los candidatos.</p>}
      <div className="batch-run-actions"><p>Se usará el mismo modelo y los mismos parámetros de referencia para todo el lote.</p>
        {batch && <button type="button" className="btn btn-secondary" onClick={resetRequest}>Preparar otro lote</button>}
        <button type="button" className="btn btn-primary" disabled={busy || refreshing || batch !== null || !objectiveId || candidateIds.length === 0 || candidateIds.length > 5} onClick={run}>
          {busy ? <><LoaderCircle size={16} className="spin" /> Comparando candidatos...</> : <>Comparar candidatos seleccionados <ArrowRight size={16} /></>}
        </button>
      </div>
    </section>}
    {error && <p className="feedback feedback-error" role="alert">{error}</p>}
    {request && !batch && !busy && <button type="button" className="btn btn-secondary batch-recover" disabled={refreshing}
      onClick={() => loadBatch(`CB-${request.request_id.replaceAll('-', '')}`)}><RefreshCw size={14} /> Consultar solicitud guardada</button>}
    {batch && <BatchResults batch={batch} onOpen={onOpenComparison} onRefresh={() => loadBatch(batch.id)} refreshing={refreshing} />}
    <section className="card batch-history" aria-labelledby="batch-history-title">
      <div className="batch-section-heading"><div><span className="section-eyebrow">RECUPERA TU TRABAJO</span><h2 id="batch-history-title"><History size={19} /> Lotes guardados</h2><p>Últimos 20 lotes. Cada comparación conserva su análisis e informe propios.</p></div>
        <button type="button" className="btn btn-secondary" onClick={refreshHistory} disabled={refreshing || busy}><RefreshCw size={14} /> Actualizar lotes</button>
      </div>
      {historyError && <p className="feedback feedback-error" role="alert">{historyError}</p>}
      {history.length === 0 ? <p className="batch-scope-note">Todavía no hay lotes guardados. Sus resultados aparecerán aquí después de iniciar una solicitud.</p> :
        <div className="batch-history-list">{history.map(item => <button type="button" className="batch-history-item" key={item.id} disabled={refreshing || busy} onClick={() => loadBatch(item.id)}>
          <span><strong>{item.objective.title}</strong><span>{item.candidates.length} candidatos · {new Date(item.created_at).toLocaleString('es-PE')}</span></span>
          <span className={`batch-status batch-status-${item.status.toLowerCase()}`}>{statusLabels[item.status]}</span><ArrowRight size={15} />
        </button>)}</div>}
    </section>
  </div>;
};
