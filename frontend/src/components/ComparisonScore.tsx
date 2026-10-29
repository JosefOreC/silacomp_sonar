import React from 'react';
import type { Comparison } from '../types';
import { api } from '../services/api';
import { CLASSIFICATIONS_ES } from '../utils/translations';

interface ComparisonScoreProps {
  comparison: Comparison;
  objectiveCourseName?: string;
  comparedCourseName?: string;
  onOpenHelp?: () => void;
}

export const ComparisonScore: React.FC<ComparisonScoreProps> = ({
  comparison,
  objectiveCourseName,
  comparedCourseName,
  onOpenHelp,
}) => {
  const globalPct = Math.round(comparison.global_score * 100);
  const objCovPct = Math.round(comparison.objective_coverage);
  const cmpCovPct = Math.round(comparison.compared_coverage);

  const getScoreColor = (pct: number) => {
    if (pct >= 85) return 'var(--accent-success)';
    if (pct >= 70) return 'var(--accent-warning)';
    if (pct >= 50) return 'var(--text-muted)';
    return 'var(--accent-danger)';
  };

  const counts = comparison.counts || {
    MATCH: 0,
    PARTIAL_MATCH: 0,
    UNCERTAIN: 0,
    NO_MATCH: 0,
  };

  const dossierNumber = `EXP-${comparison.id.slice(0, 8).toUpperCase()}`;

  return (
    <div className="card" style={{ marginBottom: '24px', background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)' }}>
      {/* Encabezado Formal de Reporte Técnico */}
      <div style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', marginBottom: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary)', fontWeight: 600 }}>
              Informe Técnico de Correspondencia Curricular
            </div>
            <h2 style={{ fontSize: '20px', fontWeight: 700, margin: '6px 0 4px 0', color: 'var(--text-primary)', letterSpacing: '-0.01em' }}>
              Dictamen Comparativo de Contenidos Académicos
            </h2>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '18px', fontSize: '12px', color: 'var(--text-secondary)', marginTop: '6px' }}>
              <span>
                <strong style={{ color: 'var(--text-primary)' }}>Expediente:</strong> {dossierNumber}
              </span>
              <span>
                <strong style={{ color: 'var(--text-primary)' }}>Fecha de Emisión:</strong> {new Date(comparison.created_at).toLocaleDateString()} {new Date(comparison.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
              <span>
                <strong style={{ color: 'var(--text-primary)' }}>Estado:</strong> Pre-Evaluación Registrada
              </span>
            </div>
          </div>

          {/* Acciones de Reporte */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {onOpenHelp && (
              <button
                onClick={onOpenHelp}
                className="btn btn-secondary"
                style={{ fontSize: '12px', padding: '6px 12px', borderColor: 'var(--border-color)' }}
              >
                Criterios de Evaluación
              </button>
            )}
            <a
              href={api.getReportPdfUrl(comparison.id)}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-secondary"
              style={{ fontSize: '12px', padding: '6px 12px' }}
            >
              Exportar PDF
            </a>
            <a
              href={api.getReportHtmlUrl(comparison.id)}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
              style={{ fontSize: '12px', padding: '6px 12px' }}
            >
              Vista Imprimible
            </a>
          </div>
        </div>

        {/* Bloque Comparativo de Asignaturas */}
        <div style={{
          marginTop: '16px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(min(280px, 100%), 1fr))',
          gap: '12px',
          background: 'var(--bg-primary)',
          padding: '12px 16px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-color)'
        }}>
          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>
              Asignatura Requerida · Plan Destino
            </div>
            <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
              {objectiveCourseName || 'Asignatura Objetivo del Plan de Estudios'}
            </div>
          </div>
          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.04em' }}>
              Asignatura Cursada · Institución de Origen
            </div>
            <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
              {comparedCourseName || 'Asignatura Presentada por el Postulante'}
            </div>
          </div>
        </div>
      </div>

      {/* Grid de Indicadores Oficiales */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
        {/* Score Global */}
        <div style={{ background: 'var(--bg-primary)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', textAlign: 'center' }}>
          <div style={{ fontSize: '36px', fontWeight: 800, color: getScoreColor(globalPct), lineHeight: 1 }}>
            {globalPct}%
          </div>
          <div style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-primary)', fontWeight: 700, marginTop: '8px', letterSpacing: '0.03em' }}>
            Afinidad Global de Contenidos
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px', lineHeight: 1.4 }}>
            Grado global de concordancia temática evaluado de forma computacional en los contenidos analizados.
          </div>
        </div>

        {/* Indicador 1: Cumplimiento de la Exigencia del Plan Destino */}
        <div style={{ background: 'var(--bg-primary)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', textAlign: 'center' }}>
          <div style={{ fontSize: '36px', fontWeight: 800, color: getScoreColor(objCovPct), lineHeight: 1 }}>
            {objCovPct}%
          </div>
          <div style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-primary)', fontWeight: 700, marginTop: '8px', letterSpacing: '0.03em' }}>
            Exigencia Curricular Acreditada
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.4 }}>
            Porcentaje de temas obligatorios del curso requerido que el alumno ya cursó y demostró equivalencia comprobada.
          </div>
        </div>

        {/* Indicador 2: Aprovechamiento del Curso de Procedencia */}
        <div style={{ background: 'var(--bg-primary)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', textAlign: 'center' }}>
          <div style={{ fontSize: '36px', fontWeight: 800, color: getScoreColor(cmpCovPct), lineHeight: 1 }}>
            {cmpCovPct}%
          </div>
          <div style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-primary)', fontWeight: 700, marginTop: '8px', letterSpacing: '0.03em' }}>
            Aprovechamiento Curricular de Origen
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '4px', lineHeight: 1.4 }}>
            Porcentaje de temas aprobados por el postulante en su institución de origen que resultan computables y reconocidos.
          </div>
        </div>

        {/* Distribución Categorial */}
        <div style={{ background: 'var(--bg-primary)', padding: '14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '8px', letterSpacing: '0.03em' }}>
            Distribución de Equivalencias
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '6px', fontSize: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="badge badge-match">{CLASSIFICATIONS_ES.MATCH.label}</span>
              <strong style={{ color: 'var(--text-primary)' }}>{counts.MATCH || 0}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="badge badge-partial">{CLASSIFICATIONS_ES.PARTIAL_MATCH.label}</span>
              <strong style={{ color: 'var(--text-primary)' }}>{counts.PARTIAL_MATCH || 0}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="badge badge-uncertain">{CLASSIFICATIONS_ES.UNCERTAIN.label}</span>
              <strong style={{ color: 'var(--text-primary)' }}>{counts.UNCERTAIN || 0}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="badge badge-nomatch">{CLASSIFICATIONS_ES.NO_MATCH.label}</span>
              <strong style={{ color: 'var(--text-primary)' }}>{counts.NO_MATCH || 0}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};