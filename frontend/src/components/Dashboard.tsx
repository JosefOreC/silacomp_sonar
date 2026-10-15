import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { ComparisonSummary, Syllabus } from '../types';

interface DashboardProps {
  onSelectComparison: (comparisonId: string) => void;
  onGoToUpload: () => void;
  syllabi: Syllabus[];
}

export const Dashboard: React.FC<DashboardProps> = ({
  onSelectComparison,
  onGoToUpload,
  syllabi,
}) => {
  const [comparisons, setComparisons] = useState<ComparisonSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeSubTab, setActiveSubTab] = useState<'comparisons' | 'syllabi'>('comparisons');

  useEffect(() => {
    let cancelled = false;
    api.listComparisons().then((data) => {
      if (!cancelled) setComparisons(data);
    }).catch((err: unknown) => console.error(err)).finally(() => {
      if (!cancelled) setLoading(false);
    });
    return () => { cancelled = true; };
  }, []);

  return (
    <div style={{ maxWidth: '1200px', margin: '30px auto', padding: '0 20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, margin: '0 0 4px 0', color: 'var(--text-primary)', letterSpacing: '0.02em', textTransform: 'uppercase' }}>
            Registro de Expedientes y Catálogo Curricular
          </h2>
          <p style={{ margin: 0, fontSize: '12px', color: 'var(--text-muted)' }}>
            Consulta de dictámenes técnicos emitidos y programas analíticos archivados.
          </p>
        </div>

        <button onClick={onGoToUpload} className="btn btn-primary" style={{ fontSize: '12px', padding: '8px 16px' }}>
          Nueva Evaluación Curricular
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px' }}>
        <button
          onClick={() => setActiveSubTab('comparisons')}
          className={`btn ${activeSubTab === 'comparisons' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ fontSize: '12px', padding: '6px 14px' }}
        >
          Expedientes Evaluados · {comparisons.length}
        </button>
        <button
          onClick={() => setActiveSubTab('syllabi')}
          className={`btn ${activeSubTab === 'syllabi' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ fontSize: '12px', padding: '6px 14px' }}
        >
          Catálogo de Sílabos · {syllabi.length}
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          Cargando registros...
        </div>
      ) : activeSubTab === 'comparisons' ? (
        <div className="card" style={{ background: 'var(--bg-secondary)', overflowX: 'auto', borderRadius: '0px' }}>
          {comparisons.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
              No se registran evaluaciones previas. Seleccione "Nueva Evaluación Curricular" para iniciar un expediente.
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ background: 'var(--bg-primary)', borderBottom: '2px solid var(--border-color)', textAlign: 'left' }}>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Expediente</th>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Asignatura Requerida · Plan Destino</th>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Asignatura Cursada · Origen</th>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)', textAlign: 'center' }}>Afinidad</th>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)', textAlign: 'center' }}>Exigencia Acreditada</th>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Fecha</th>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)', textAlign: 'center' }}>Acción</th>
                </tr>
              </thead>
              <tbody>
                {comparisons.map((c) => {
                  const scorePct = Math.round(c.global_score * 100);
                  const dossierCode = `EXP-${c.id.substring(0, 8).toUpperCase()}`;
                  return (
                    <tr key={c.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                      <td style={{ padding: '12px', fontWeight: 600, fontSize: '12px', color: 'var(--text-primary)' }}>
                        {dossierCode}
                      </td>
                      <td style={{ padding: '12px' }}>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{c.objective_course}</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{c.objective_university || 'Institución Destino'}</div>
                      </td>
                      <td style={{ padding: '12px' }}>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{c.compared_course}</div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{c.compared_university || 'Institución de Origen'}</div>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <span style={{
                          fontWeight: 800,
                          fontSize: '14px',
                          color: scorePct >= 85 ? 'var(--accent-success)' : scorePct >= 70 ? 'var(--accent-warning)' : '#94a3b8'
                        }}>
                          {scorePct}%
                        </span>
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center', fontSize: '12px' }}>
                        <strong style={{ color: 'var(--text-primary)' }}>{Math.round(c.objective_coverage)}%</strong>
                        <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>Aprov: {Math.round(c.compared_coverage)}%</div>
                      </td>
                      <td style={{ padding: '12px', fontSize: '12px', color: 'var(--text-muted)' }}>
                        {new Date(c.created_at).toLocaleDateString()}
                      </td>
                      <td style={{ padding: '12px', textAlign: 'center' }}>
                        <button
                          onClick={() => onSelectComparison(c.id)}
                          className="btn btn-secondary"
                          style={{ fontSize: '11px', padding: '4px 10px' }}
                        >
                          Ver Informe
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      ) : (
        <div className="card" style={{ background: 'var(--bg-secondary)', overflowX: 'auto', borderRadius: '0px' }}>
          {syllabi.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
              No hay documentos archivados en el catálogo.
            </div>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
              <thead>
                <tr style={{ background: 'var(--bg-primary)', borderBottom: '2px solid var(--border-color)', textAlign: 'left' }}>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Documento</th>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Asignatura</th>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Universidad / Institución</th>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)', textAlign: 'center' }}>Páginas</th>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)', textAlign: 'center' }}>Caracteres</th>
                  <th style={{ padding: '10px 12px', color: 'var(--text-muted)' }}>Fecha Registro</th>
                </tr>
              </thead>
              <tbody>
                {syllabi.map((s) => (
                  <tr key={s.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                    <td style={{ padding: '12px' }}>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{s.filename}</div>
                    </td>
                    <td style={{ padding: '12px', color: 'var(--text-primary)', fontWeight: 500 }}>
                      {s.course_name || 'Sin especificar'}
                    </td>
                    <td style={{ padding: '12px', color: 'var(--text-muted)' }}>
                      {s.university || 'No especificada'}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span className="badge badge-uncertain">{s.total_pages}</span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center', fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {s.total_characters.toLocaleString()}
                    </td>
                    <td style={{ padding: '12px', fontSize: '12px', color: 'var(--text-muted)' }}>
                      {new Date(s.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
};
