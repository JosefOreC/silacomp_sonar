import React from 'react';
import type { UnmatchedItem } from '../types';

interface UnmatchedPanelProps {
  unmatchedObjective: UnmatchedItem[];
  unmatchedCompared: UnmatchedItem[];
}

export const UnmatchedPanel: React.FC<UnmatchedPanelProps> = ({
  unmatchedObjective,
  unmatchedCompared,
}) => {
  return (
    <div className="card" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', marginTop: '20px', borderRadius: 'var(--radius-md)' }}>
      <div style={{ marginBottom: '16px' }}>
        <h3 style={{ margin: 0, fontSize: '16px', color: 'var(--text-primary)', fontWeight: 700, letterSpacing: '0.02em', textTransform: 'uppercase' }}>
          Análisis de Brechas Curriculares y Contenidos Sin Equivalencia
        </h3>
        <p style={{ margin: '2px 0 0 0', fontSize: '12px', color: 'var(--text-muted)' }}>
          Unidades temáticas que no alcanzaron el umbral mínimo de afinidad computacional establecido para convalidación.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(420px, 100%), 1fr))', gap: '20px' }}>
        {/* Brechas en el Sílabo Objetivo */}
        <div style={{ background: 'var(--bg-primary)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid #4b5563' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h4 style={{ margin: 0, fontSize: '13px', color: 'var(--nomatch-color)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.03em' }}>
              Contenidos Requeridos No Acreditados · {unmatchedObjective.length}
            </h4>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>No cubiertos por la asignatura de origen</span>
          </div>

          {unmatchedObjective.length === 0 ? (
            <div style={{ fontSize: '12px', color: 'var(--match-color)', padding: '12px 0' }}>
              Todos los contenidos del plan de estudios destino cuentan con correspondencia acreditada.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {unmatchedObjective.map((u, i) => (
                <div
                  key={i}
                  style={{
                    background: 'var(--bg-secondary)',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-md)',
                    borderLeft: '3px solid #ef4444',
                    fontSize: '12px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>{u.title}</strong>
                    <span style={{ fontSize: '10px', color: 'var(--text-secondary)', background: 'var(--bg-primary)', padding: '2px 5px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                      Página {u.page}
                    </span>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', margin: '2px 0 6px 0' }}>
                    Sección: {u.section_name}
                  </div>
                  {u.best_candidate_title && (
                    <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                      Tema más cercano identificado: <em>{u.best_candidate_title}</em> · Afinidad: {u.best_score ? Math.round(u.best_score * 100) : 0}%
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Contenidos Adicionales en el Sílabo Comparado */}
        <div style={{ background: 'var(--bg-primary)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid #4b5563' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h4 style={{ margin: 0, fontSize: '13px', color: 'var(--text-primary)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.03em' }}>
              Contenidos de Origen No Exigidos · {unmatchedCompared.length}
            </h4>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Temas no requeridos por el plan destino</span>
          </div>

          {unmatchedCompared.length === 0 ? (
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', padding: '12px 0' }}>
              No se registran temas adicionales de origen sin correspondencia.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {unmatchedCompared.map((u, i) => (
                <div
                  key={i}
                  style={{
                    background: 'var(--bg-secondary)',
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-md)',
                    borderLeft: '3px solid #6b7280',
                    fontSize: '12px'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <strong style={{ color: 'var(--text-primary)' }}>{u.title}</strong>
                    <span style={{ fontSize: '10px', color: 'var(--text-secondary)', background: 'var(--bg-primary)', padding: '2px 5px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                      Página {u.page}
                    </span>
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', margin: '2px 0 6px 0' }}>
                    Sección: {u.section_name}
                  </div>
                  {u.best_candidate_title && (
                    <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                      Tema más cercano identificado: <em>{u.best_candidate_title}</em> · Afinidad: {u.best_score ? Math.round(u.best_score * 100) : 0}%
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};