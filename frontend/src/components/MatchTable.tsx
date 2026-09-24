import React, { useState } from 'react';
import type { ContentMatch, MatchClassification } from '../types';
import { CLASSIFICATIONS_ES } from '../utils/translations';

interface MatchTableProps {
  matches: ContentMatch[];
  selectedMatchId?: string;
  onSelectMatch: (match: ContentMatch) => void;
  humanReviews: Record<string, string>; // match_id -> human_decision
  onOpenPdfViewer?: (match: ContentMatch) => void;
}

export const MatchTable: React.FC<MatchTableProps> = ({
  matches,
  selectedMatchId,
  onSelectMatch,
  humanReviews,
  onOpenPdfViewer,
}) => {
  const [filter, setFilter] = useState<'ALL' | MatchClassification>('ALL');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredMatches = matches.filter((m) => {
    if (filter !== 'ALL' && m.classification !== filter) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      const inObj = m.objective_title.toLowerCase().includes(term);
      const inCmp = m.compared_title.toLowerCase().includes(term);
      const inKws = m.evidence.shared_keywords.some((k) => k.toLowerCase().includes(term));
      if (!inObj && !inCmp && !inKws) return false;
    }
    return true;
  });

  return (
    <div className="card" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', marginTop: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '16px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '16px', color: 'var(--text-primary)', fontWeight: 700, letterSpacing: '0.02em', textTransform: 'uppercase' }}>
            Matriz Analítica de Correspondencias Curriculares
          </h3>
          <p style={{ margin: '2px 0 0 0', fontSize: '12px', color: 'var(--text-muted)' }}>
            Seleccione una fila para desplegar el cotejo textual detallado y el dictamen técnico.
          </p>
        </div>

        {/* Buscador */}
        <input
          type="text"
          placeholder="Buscar tema o término..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            background: '#FFFFFF',
            border: '1px solid #CBD5E1',
            color: '#000000',
            padding: '6px 12px',
            borderRadius: '0px',
            fontSize: '12px',
            width: '240px'
          }}
        />
      </div>

      {/* Botones de Filtro Categorial */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
        <button
          onClick={() => setFilter('ALL')}
          className={`btn ${filter === 'ALL' ? 'btn-primary' : 'btn-secondary'}`}
          style={{ fontSize: '11px', padding: '5px 12px' }}
        >
          Todos · {matches.length}
        </button>
        <button
          onClick={() => setFilter('MATCH')}
          className="btn"
          style={{
            fontSize: '11px',
            padding: '5px 12px',
            background: filter === 'MATCH' ? '#10b981' : 'var(--bg-primary)',
            color: filter === 'MATCH' ? '#000000' : '#10b981',
            border: '1px solid #10b981',
            fontWeight: 600
          }}
        >
          {CLASSIFICATIONS_ES.MATCH.label} · {matches.filter((m) => m.classification === 'MATCH').length}
        </button>
        <button
          onClick={() => setFilter('PARTIAL_MATCH')}
          className="btn"
          style={{
            fontSize: '11px',
            padding: '5px 12px',
            background: filter === 'PARTIAL_MATCH' ? '#f59e0b' : 'var(--bg-primary)',
            color: filter === 'PARTIAL_MATCH' ? '#000000' : '#f59e0b',
            border: '1px solid #f59e0b',
            fontWeight: 600
          }}
        >
          {CLASSIFICATIONS_ES.PARTIAL_MATCH.label} · {matches.filter((m) => m.classification === 'PARTIAL_MATCH').length}
        </button>
        <button
          onClick={() => setFilter('UNCERTAIN')}
          className="btn"
          style={{
            fontSize: '11px',
            padding: '5px 12px',
            background: filter === 'UNCERTAIN' ? '#94a3b8' : 'var(--bg-primary)',
            color: filter === 'UNCERTAIN' ? '#000000' : '#94a3b8',
            border: '1px solid #94a3b8',
            fontWeight: 600
          }}
        >
          {CLASSIFICATIONS_ES.UNCERTAIN.label} · {matches.filter((m) => m.classification === 'UNCERTAIN').length}
        </button>
        <button
          onClick={() => setFilter('NO_MATCH')}
          className="btn"
          style={{
            fontSize: '11px',
            padding: '5px 12px',
            background: filter === 'NO_MATCH' ? '#ef4444' : 'var(--bg-primary)',
            color: filter === 'NO_MATCH' ? '#ffffff' : '#ef4444',
            border: '1px solid #ef4444',
            fontWeight: 600
          }}
        >
          {CLASSIFICATIONS_ES.NO_MATCH.label} · {matches.filter((m) => m.classification === 'NO_MATCH').length}
        </button>
      </div>

      {/* Tabla de Resultados */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
          <thead>
            <tr style={{ background: 'var(--bg-primary)', borderBottom: '2px solid var(--border-color)', textAlign: 'left' }}>
              <th style={{ padding: '10px 12px', color: 'var(--text-muted)', fontWeight: 600 }}>Contenido Requerido</th>
              <th style={{ padding: '10px 12px', color: 'var(--text-muted)', fontWeight: 600 }}>Contenido de Origen</th>
              <th style={{ padding: '10px 12px', color: 'var(--text-muted)', fontWeight: 600, textAlign: 'center' }}>Equivalencia</th>
              <th style={{ padding: '10px 12px', color: 'var(--text-muted)', fontWeight: 600, textAlign: 'center' }}>Afinidad</th>
              <th style={{ padding: '10px 12px', color: 'var(--text-muted)', fontWeight: 600 }}>Términos Coincidentes</th>
              <th style={{ padding: '10px 12px', color: 'var(--text-muted)', fontWeight: 600, textAlign: 'center' }}>Auditoría</th>
              <th style={{ padding: '10px 12px', color: 'var(--text-muted)', fontWeight: 600, textAlign: 'center' }}>Acción</th>
            </tr>
          </thead>
          <tbody>
            {filteredMatches.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No se encontraron registros con los criterios seleccionados.
                </td>
              </tr>
            ) : (
              filteredMatches.map((m) => {
                const isSelected = m.id === selectedMatchId;
                const humanDecision = humanReviews[m.id];
                const scorePct = Math.round(m.score_breakdown.composite_score * 100);
                const classInfo = CLASSIFICATIONS_ES[m.classification] || {
                  label: m.classification,
                  badgeClass: 'badge-uncertain',
                };

                return (
                  <tr
                    key={m.id}
                    onClick={() => onSelectMatch(m)}
                    style={{
                      borderBottom: '1px solid var(--border-color)',
                      background: isSelected ? 'rgba(75, 85, 99, 0.25)' : 'transparent',
                      cursor: 'pointer',
                      transition: 'background 0.15s ease',
                    }}
                  >
                    <td style={{ padding: '12px' }}>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{m.objective_title}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        {m.objective_section} · <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>Pág. {m.objective_page}</span>
                      </div>
                    </td>
                    <td style={{ padding: '12px' }}>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{m.compared_title}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        {m.compared_section} · <span style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>Pág. {m.compared_page}</span>
                      </div>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span className={`badge ${classInfo.badgeClass}`}>
                        {classInfo.label}
                      </span>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{scorePct}%</span>
                    </td>
                    <td style={{ padding: '12px' }}>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', maxWidth: '200px' }}>
                        {m.evidence.shared_keywords.slice(0, 3).map((kw, i) => (
                          <span
                            key={i}
                            style={{
                              fontSize: '10px',
                              background: 'var(--bg-primary)',
                              padding: '2px 5px',
                              borderRadius: '0px',
                              border: '1px solid var(--border-color)',
                              color: 'var(--text-secondary)'
                            }}
                          >
                            {kw}
                          </span>
                        ))}
                        {m.evidence.shared_keywords.length > 3 && (
                          <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                            +{m.evidence.shared_keywords.length - 3}
                          </span>
                        )}
                      </div>
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      {humanDecision ? (
                        <span style={{ fontSize: '11px', color: '#10b981', fontWeight: 600 }}>
                          ✓ {CLASSIFICATIONS_ES[humanDecision as MatchClassification]?.label || humanDecision}
                        </span>
                      ) : (
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Pendiente</span>
                      )}
                    </td>
                    <td style={{ padding: '12px', textAlign: 'center' }}>
                      <div style={{ display: 'inline-flex', gap: '4px' }}>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectMatch(m);
                          }}
                          className="btn btn-secondary"
                          style={{ fontSize: '11px', padding: '4px 8px' }}
                        >
                          {isSelected ? 'Cerrar' : 'Examinar'}
                        </button>

                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onOpenPdfViewer?.(m);
                          }}
                          className="btn btn-primary"
                          style={{ fontSize: '11px', padding: '4px 8px' }}
                          title="Abrir en Visor Pericial Doble PDF (Fase 1.5)"
                        >
                          Visor PDF
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};