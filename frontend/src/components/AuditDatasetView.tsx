import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { CLASSIFICATIONS_ES, CORRECTIONS_ES } from '../utils/translations';
import type { MatchClassification } from '../types';

export const AuditDatasetView: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    setLoading(true);
    try {
      const data = await api.getDatasetStats();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Error al cargar estadísticas');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '30px auto', padding: '0 20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 700, margin: '0 0 4px 0', color: 'var(--text-primary)', letterSpacing: '0.02em', textTransform: 'uppercase' }}>
            Registro Institucional de Auditoría y Dictámenes
          </h2>
          <p style={{ margin: 0, fontSize: '12px', color: 'var(--text-muted)' }}>
            Trazabilidad histórica de dictámenes docentes y resoluciones académicas colegiadas.
          </p>
        </div>

        <a
          href={api.getDatasetExportUrl()}
          download="registro_auditoria_convcomp.json"
          className="btn btn-primary"
          style={{ fontSize: '12px', padding: '8px 16px' }}
        >
          Exportar Registro JSON
        </a>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          Consultando registro de auditoría...
        </div>
      ) : error ? (
        <div style={{ padding: '16px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: '0px', color: '#fca5a5' }}>
          {error}
        </div>
      ) : stats ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Métricas Globales */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div className="card" style={{ textAlign: 'center', background: 'var(--bg-secondary)', borderRadius: '0px' }}>
              <div style={{ fontSize: '32px', fontWeight: 800, color: 'var(--text-primary)' }}>
                {stats.total_examples}
              </div>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, marginTop: '4px', letterSpacing: '0.04em' }}>
                Dictámenes Auditados
              </div>
            </div>

            <div className="card" style={{ textAlign: 'center', background: 'var(--bg-secondary)', borderRadius: '0px' }}>
              <div style={{ fontSize: '32px', fontWeight: 800, color: '#34d399' }}>
                {(stats.confirmation_rate * 100).toFixed(1)}%
              </div>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, marginTop: '4px', letterSpacing: '0.04em' }}>
                Tasa de Ratificación
              </div>
            </div>

            <div className="card" style={{ textAlign: 'center', background: 'var(--bg-secondary)', borderRadius: '0px' }}>
              <div style={{ fontSize: '32px', fontWeight: 800, color: 'var(--accent-warning)' }}>
                {stats.correction_distribution?.OVERESTIMATION || 0}
              </div>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, marginTop: '4px', letterSpacing: '0.04em' }}>
                {CORRECTIONS_ES.OVERESTIMATION.label}
              </div>
            </div>

            <div className="card" style={{ textAlign: 'center', background: 'var(--bg-secondary)', borderRadius: '0px' }}>
              <div style={{ fontSize: '32px', fontWeight: 800, color: 'var(--accent-danger)' }}>
                {stats.correction_distribution?.FALSE_POSITIVE || 0}
              </div>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, marginTop: '4px', letterSpacing: '0.04em' }}>
                {CORRECTIONS_ES.FALSE_POSITIVE.label}
              </div>
            </div>
          </div>

          {/* Desglose por Decisión Humana */}
          <div className="card" style={{ background: 'var(--bg-secondary)', borderRadius: '0px' }}>
            <h3 style={{ fontSize: '14px', color: 'var(--text-primary)', marginBottom: '14px', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
              Distribución por Dictamen Docente Definitivo
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
              {Object.entries(stats.decision_distribution || {}).map(([dec, count]: any) => {
                const conf = CLASSIFICATIONS_ES[dec as MatchClassification];
                return (
                  <div key={dec} style={{ background: 'var(--bg-primary)', padding: '12px', borderRadius: '0px', textAlign: 'center', border: '1px solid var(--border-color)' }}>
                    <div style={{ fontSize: '20px', fontWeight: 700, color: conf?.color || 'var(--text-primary)' }}>{count}</div>
                    <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
                      {conf?.label || dec}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Información Metodológica Institucional */}
          <div className="card" style={{ background: 'var(--bg-secondary)', fontSize: '13px', lineHeight: 1.6, color: 'var(--text-secondary)', borderRadius: '0px' }}>
            <h4 style={{ margin: '0 0 8px 0', color: 'var(--text-primary)', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '0.03em' }}>
              Principio de Inmutabilidad y Trazabilidad Institucional
            </h4>
            <p style={{ margin: 0 }}>
              Cada vez que una comisión académica o docente evaluador califica una correspondencia curricular, el sistema registra el dictamen preservando intacta la pre-evaluación automatizada inicial, la resolución adoptada y la respectiva fundamentación académica. Esto garantiza una trazabilidad de auditoría absoluta sin sobreescritura de antecedentes y asegura la consistencia de los dictámenes universitarios.
            </p>
          </div>
        </div>
      ) : null}
    </div>
  );
};