import { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { ComparisonSummary, ConsensusStatus, GroundTruthPage, ReviewerAgreement } from '../types';
import { CLASSIFICATIONS_ES } from '../utils/translations';

const statuses: Record<ConsensusStatus, string> = {
  SINGLE_REVIEW: 'Un revisor', CONSENSUS: 'Acuerdo', DISAGREEMENT: 'Desacuerdo',
};

export const GroundTruthPanel = ({ onOpenComparison, annotationRevision = 0 }: { onOpenComparison?: (id: string) => void; annotationRevision?: number }) => {
  const [comparisons, setComparisons] = useState<ComparisonSummary[]>([]);
  const [comparisonId, setComparisonId] = useState('');
  const [status, setStatus] = useState<ConsensusStatus | ''>('');
  const [offset, setOffset] = useState(0);
  const [refresh, setRefresh] = useState(0);
  const queryKey = JSON.stringify([comparisonId, status, offset, refresh, annotationRevision]);
  const [result, setResult] = useState<{
    key: string; page: GroundTruthPage | null; agreement: ReviewerAgreement[]; error: string | null;
  } | null>(null);
  const current = result?.key === queryKey ? result : null;

  useEffect(() => {
    let cancelled = false;
    api.listComparisons().then((data) => {
      if (!cancelled) setComparisons(data);
    }).catch((err: unknown) => console.error('Error al cargar comparaciones:', err));
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    Promise.all([api.getGroundTruth(comparisonId, status, offset), api.getReviewerAgreement(comparisonId)])
      .then(([page, agreement]) => {
        if (!cancelled) setResult({ key: queryKey, page, agreement, error: null });
      }).catch((err: unknown) => {
        if (!cancelled) setResult({ key: queryKey, page: null, agreement: [],
          error: err instanceof Error ? err.message : 'No se pudo consultar la evaluación humana' });
      });
    return () => { cancelled = true; };
  }, [comparisonId, status, offset, queryKey]);

  return (
    <section className="card" aria-labelledby="ground-truth-title" style={{ marginTop: 24 }}>
      <h3 id="ground-truth-title">Acuerdo entre revisores y ground truth</h3>
      <p>Se utiliza el último voto de cada revisor por par. Se requieren al menos dos revisores con decisiones coincidentes para formar consenso.</p>
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
        <label>Comparación{' '}
          <select value={comparisonId} onChange={(e) => { setComparisonId(e.target.value); setOffset(0); }}>
            <option value="">Todas</option>
            {comparisons.map((c) => <option key={c.id} value={c.id}>{c.objective_course} / {c.compared_course} · {c.id}</option>)}
          </select>
        </label>
        <label>Estado{' '}
          <select value={status} onChange={(e) => { setStatus(e.target.value as ConsensusStatus | ''); setOffset(0); }}>
            <option value="">Todos</option>
            {Object.entries(statuses).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </label>
        <button className="btn btn-secondary" onClick={() => setRefresh((v) => v + 1)}>Actualizar</button>
        <a className="btn btn-secondary" href={api.getGroundTruthExportUrl('json', comparisonId)}>Exportar pares JSON</a>
        <a className="btn btn-secondary" href={api.getGroundTruthExportUrl('csv', comparisonId)}>Exportar pares CSV</a>
      </div>
      {!current ? <p role="status">Consultando revisiones...</p> : current.error ? <p role="alert">{current.error}</p> : current.page && <>
        <p>{current.page.summary.total_pairs} pares · {current.page.summary.consensus_pairs} con acuerdo · {current.page.summary.disagreement_pairs} con desacuerdo · {current.page.summary.single_review_pairs} con un revisor.</p>
        {current.page.items.length === 0 ? <p>No hay pares revisados para estos filtros. Registre revisiones desde el informe o el visor PDF.</p> : current.page.items.map((pair) => (
          <article key={JSON.stringify([pair.comparison_id, pair.objective_item_id, pair.compared_item_id])}
            style={{ padding: 12, marginTop: 12, border: '1px solid var(--border-color)' }}>
            <strong>{statuses[pair.status]} · {pair.reviewer_count} revisores · {pair.review_count} eventos</strong>
            {pair.consensus_label && <span> · {CLASSIFICATIONS_ES[pair.consensus_label].label}</span>}
            <p><strong>Objetivo · página {pair.source_page_obj ?? 'sin referencia'}:</strong> {pair.objective_text}</p>
            <p><strong>Comparado · página {pair.source_page_cmp ?? 'sin referencia'}:</strong> {pair.compared_text}</p>
            <ul>{pair.votes.map((vote) => <li key={vote.review_id}>
              {vote.reviewer_id}: {CLASSIFICATIONS_ES[vote.human_decision].label}. {vote.justification}
            </li>)}</ul>
            {onOpenComparison && <button className="btn btn-secondary" onClick={() => onOpenComparison(pair.comparison_id)}>Abrir informe para revisar</button>}
          </article>
        ))}
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginTop: 12 }}>
          <button className="btn btn-secondary" disabled={offset === 0} onClick={() => setOffset((v) => Math.max(0, v - 20))}>Anterior</button>
          <span>{current.page.total === 0 ? '0 pares' : `${offset + 1}–${Math.min(offset + 20, current.page.total)} de ${current.page.total}`}</span>
          <button className="btn btn-secondary" disabled={offset + 20 >= current.page.total} onClick={() => setOffset((v) => v + 20)}>Siguiente</button>
        </div>
        <h4>Acuerdo por pareja de revisores</h4>
        <p>El cálculo considera los pares compartidos de la comparación seleccionada. Kappa no se puede calcular sin muestras comunes o si el acuerdo esperado es 100%.</p>
        {current.agreement.length === 0 ? <p>Aún no hay dos revisores para calcular acuerdo.</p> : <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', textAlign: 'left' }}>
            <thead><tr><th>Revisores</th><th>Pares comunes</th><th>Acuerdo observado</th><th>Kappa</th></tr></thead>
            <tbody>{current.agreement.map((a) => <tr key={JSON.stringify([a.reviewer_a, a.reviewer_b])}>
              <td>{a.reviewer_a} / {a.reviewer_b}</td><td>{a.common_pairs}</td>
              <td>{a.observed_agreement === null ? 'No calculable' : `${(a.observed_agreement * 100).toFixed(1)}%`}</td>
              <td>{a.cohen_kappa === null ? 'No calculable' : a.cohen_kappa.toFixed(3)}</td>
            </tr>)}</tbody>
          </table>
        </div>}
      </>}
      <p style={{ marginTop: 16 }}>El consenso sirve como etiqueta para aprendizaje y no constituye una decisión oficial de convalidación.</p>
    </section>
  );
};
