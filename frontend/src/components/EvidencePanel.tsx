import React from 'react';
import type { ContentMatch, MatchClassification } from '../types';
import { CLASSIFICATIONS_ES, getEvidenceLabel } from '../utils/translations';

interface EvidencePanelProps {
  match: ContentMatch;
  onClose: () => void;
  onOpenReview: (match: ContentMatch) => void;
  humanReviewDecision?: string;
  onOpenPdfViewer?: (match: ContentMatch) => void;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  match,
  onClose,
  onOpenReview,
  humanReviewDecision,
  onOpenPdfViewer,
}) => {
  const { score_breakdown, evidence } = match;
  const classInfo = CLASSIFICATIONS_ES[match.classification] || {
    label: match.classification,
    badgeClass: 'badge-uncertain',
  };

  const renderProgressBar = (label: string, value: number, weight: number, color: string) => {
    const pct = Math.round(value * 100);
    return (
      <div style={{ marginBottom: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', marginBottom: '4px' }}>
          <span style={{ color: 'var(--text-secondary)' }}>
            {label} <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>· Ponderación {Math.round(weight * 100)}%</span>
          </span>
          <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{pct}%</span>
        </div>
        <div style={{ width: '100%', height: '5px', background: 'var(--bg-primary)', borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
          <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 'var(--radius-md)' }} />
        </div>
      </div>
    );
  };

  return (
    <div className="card" style={{ border: '1px solid var(--border-color)', background: 'var(--bg-secondary)', marginTop: '20px', borderRadius: 'var(--radius-md)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-color)', paddingBottom: '14px', marginBottom: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '0.04em' }}>
              Ficha Técnica de Cotejo y Evidencia Textual
            </span>
            <span className={`badge ${classInfo.badgeClass}`}>
              {classInfo.label}
            </span>
            {humanReviewDecision && (
              <span className="badge badge-match" style={{ background: 'rgba(52, 211, 153, 0.15)', border: '1px solid #34d399' }}>
                ✓ Dictamen Docente: {CLASSIFICATIONS_ES[humanReviewDecision as MatchClassification]?.label || humanReviewDecision}
              </span>
            )}
          </div>
          <h3 style={{ fontSize: '17px', margin: '6px 0 0 0', color: 'var(--text-primary)', fontWeight: 600 }}>
            {match.objective_title} <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>—</span> {match.compared_title}
          </h3>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => onOpenPdfViewer?.(match)}
            className="btn btn-secondary"
            style={{ fontSize: '12px', padding: '6px 14px', border: '1px solid var(--match-border)', color: 'var(--match-color)', fontWeight: 600 }}
            title="Abrir ambos sílabos en el Visor Pericial Doble PDF con resaltado espacial (Fase 1.5)"
          >
            Ver en Visor PDF
          </button>
          <button
            onClick={() => onOpenReview(match)}
            className="btn btn-primary"
            style={{ fontSize: '12px', padding: '6px 14px' }}
          >
            Emitir Dictamen
          </button>
          <button
            onClick={onClose}
            className="btn btn-secondary"
            style={{ fontSize: '12px', padding: '6px 12px' }}
          >
            Cerrar
          </button>
        </div>
      </div>

      {/* Grid Comparativo Lado a Lado con Citas Textuales y Páginas */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(320px, 100%), 1fr))', gap: '16px', marginBottom: '20px' }}>
        {/* Lado Objetivo */}
        <div style={{ background: 'var(--bg-primary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '0.03em' }}>
              CONTENIDO DEL PLAN DESTINO
            </span>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)', background: 'var(--bg-secondary)', padding: '2px 6px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
              Página {match.objective_page}
            </span>
          </div>
          <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
            {match.objective_title}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '8px' }}>
            Sección: {match.objective_section}
          </div>
          <div style={{
            fontSize: '12px',
            color: 'var(--text-main)',
            background: 'var(--bg-secondary)',
            padding: '10px 12px',
            borderRadius: 'var(--radius-md)',
            borderLeft: '3px solid #6b7280',
            lineHeight: 1.5
          }}>
            "{evidence.objective_snippet || 'Sin fragmento disponible'}"
          </div>
        </div>

        {/* Lado Comparado */}
        <div style={{ background: 'var(--bg-primary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '0.03em' }}>
              CONTENIDO DE LA INSTITUCIÓN DE ORIGEN
            </span>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)', background: 'var(--bg-secondary)', padding: '2px 6px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
              Página {match.compared_page}
            </span>
          </div>
          <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
            {match.compared_title}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '8px' }}>
            Sección: {match.compared_section}
          </div>
          <div style={{
            fontSize: '12px',
            color: 'var(--text-main)',
            background: 'var(--bg-secondary)',
            padding: '10px 12px',
            borderRadius: 'var(--radius-md)',
            borderLeft: '3px solid #9ca3af',
            lineHeight: 1.5
          }}>
            "{evidence.compared_snippet || 'Sin fragmento disponible'}"
          </div>
        </div>
      </div>

      {/* Desglose de Criterios y Términos Clave */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(min(280px, 100%), 1fr))', gap: '16px' }}>
        {/* Barras de Puntuación */}
        <div style={{ background: 'var(--bg-primary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Criterios de Evaluación Multivariada
          </div>
          {renderProgressBar('Similitud Conceptual y Semántica', score_breakdown.semantic_similarity, 0.40, '#cbd5e1')}
          {renderProgressBar('Concordancia Textual y Léxica', score_breakdown.lexical_similarity, 0.30, 'var(--match-color)')}
          {renderProgressBar('Coincidencia de Vocabulario Especializado', score_breakdown.keyword_overlap, 0.15, '#f59e0b')}
          {renderProgressBar('Correspondencia Estructural del Programa', score_breakdown.structural_similarity, 0.15, '#c084fc')}

          <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-primary)' }}>
              Afinidad Temática Ponderada:
            </span>
            <span style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
              {(score_breakdown.composite_score * 100).toFixed(1)}%
            </span>
          </div>
        </div>

        {/* Términos Especializados Coincidentes */}
        <div style={{ background: 'var(--bg-primary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-secondary)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Términos Especializados Coincidentes · {evidence.shared_keywords.length}
          </div>
          {evidence.shared_keywords.length > 0 ? (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {evidence.shared_keywords.map((kw, i) => (
                <span
                  key={i}
                  style={{
                    background: 'var(--bg-elevated)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    padding: '3px 8px',
                    borderRadius: 'var(--radius-md)',
                    fontSize: '11px'
                  }}
                >
                  {kw}
                </span>
              ))}
            </div>
          ) : (
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: 0 }}>
              Equivalencia fundamentada primordialmente por correspondencia conceptual de contenidos temáticos.
            </p>
          )}

          <div style={{ marginTop: '16px', fontSize: '11px', color: 'var(--text-muted)', borderTop: '1px solid var(--border-color)', paddingTop: '8px' }}>
            Nivel de Evidencia: <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{getEvidenceLabel(evidence.evidence_type)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};