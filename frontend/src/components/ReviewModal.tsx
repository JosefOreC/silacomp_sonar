import React, { useState } from 'react';
import type { ContentMatch, CorrectionType, MatchClassification } from '../types';
import { api } from '../services/api';
import { CLASSIFICATIONS_ES, CORRECTIONS_ES } from '../utils/translations';

interface ReviewModalProps {
  match: ContentMatch;
  onClose: () => void;
  onReviewSaved: (matchId: string, decision: MatchClassification) => void;
}

export const ReviewModal: React.FC<ReviewModalProps> = ({
  match,
  onClose,
  onReviewSaved,
}) => {
  const [decision, setDecision] = useState<MatchClassification>(match.classification);
  const [correctionType, setCorrectionType] = useState<CorrectionType>('CONFIRMED');
  const [reviewerId, setReviewerId] = useState('DOCENTE_EVALUADOR_01');
  const [justification, setJustification] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const origClassInfo = CLASSIFICATIONS_ES[match.classification] || {
    label: match.classification,
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!justification.trim() || justification.trim().length < 8) {
      setErrorMsg('Debe ingresar una justificación académica válida de al menos 8 caracteres.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);
    try {
      await api.submitReview({
        comparison_id: match.comparison_id,
        match_id: match.id,
        prediction_before: match.classification,
        human_decision: decision,
        correction_type: correctionType,
        justification: justification.trim(),
        reviewer_id: reviewerId.trim() || 'DOCENTE_ANONIMO',
      });
      onReviewSaved(match.id, decision);
      onClose();
    } catch (err: any) {
      setErrorMsg(err.message || 'Error al guardar la revisión');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div style={{
        background: 'var(--bg-secondary)',
        border: '1px solid #4b5563',
        borderRadius: 'var(--radius-md)',
        maxWidth: '560px',
        width: '100%',
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)',
        padding: '24px',
        color: 'var(--text-primary)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '16px' }}>
          <div>
            <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-secondary)', fontWeight: 700, letterSpacing: '0.04em' }}>
              Dictamen Docente y Resolución
            </span>
            <h3 style={{ margin: '2px 0 0 0', fontSize: '17px', fontWeight: 700 }}>
              Calificación de Equivalencia Curricular
            </h3>
          </div>
          <button onClick={onClose} className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '12px' }}>
            ✕
          </button>
        </div>

        {/* Resumen Inmutable */}
        <div style={{ background: 'var(--bg-primary)', padding: '12px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', marginBottom: '16px', fontSize: '12px' }}>
          <div style={{ marginBottom: '4px' }}>
            <strong>Contenido Requerido:</strong> {match.objective_title} · Página {match.objective_page}
          </div>
          <div style={{ marginBottom: '4px' }}>
            <strong>Contenido de Origen:</strong> {match.compared_title} · Página {match.compared_page}
          </div>
          <div style={{ display: 'flex', gap: '16px', marginTop: '8px', color: 'var(--text-muted)' }}>
            <span>Pre-Evaluación Automatizada: <strong style={{ color: 'var(--text-primary)' }}>{origClassInfo.label}</strong></span>
            <span>Afinidad Calculada: <strong style={{ color: 'var(--text-primary)' }}>{(match.score_breakdown.composite_score * 100).toFixed(1)}%</strong></span>
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label htmlFor="reviewmodal-field-1" style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                Dictamen Final *
              </label>
              <select id="reviewmodal-field-1"
                value={decision}
                onChange={(e) => setDecision(e.target.value as MatchClassification)}
                style={{
                  width: '100%',
                  background: '#FFFFFF',
                  border: '1px solid #CBD5E1',
                  color: '#000000',
                  padding: '8px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {Object.values(CLASSIFICATIONS_ES).map((cls) => (
                  <option key={cls.code} value={cls.code} style={{ color: '#000000', background: '#FFFFFF' }}>
                    {cls.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="reviewmodal-field-2" style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                Criterio Evaluativo *
              </label>
              <select id="reviewmodal-field-2"
                value={correctionType}
                onChange={(e) => setCorrectionType(e.target.value as CorrectionType)}
                style={{
                  width: '100%',
                  background: '#FFFFFF',
                  border: '1px solid #CBD5E1',
                  color: '#000000',
                  padding: '8px',
                  borderRadius: 'var(--radius-md)',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {Object.values(CORRECTIONS_ES).map((cor) => (
                  <option key={cor.code} value={cor.code} style={{ color: '#000000', background: '#FFFFFF' }}>
                    {cor.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="reviewmodal-field-3" style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
              Identificación del Docente o Comisión Evaluadora
            </label>
            <input id="reviewmodal-field-3"
              type="text"
              value={reviewerId}
              onChange={(e) => setReviewerId(e.target.value)}
              placeholder="Ej. COMISION_EVALUADORA_01"
              style={{
                width: '100%',
                background: '#FFFFFF',
                border: '1px solid #CBD5E1',
                color: '#000000',
                padding: '8px 10px',
                borderRadius: 'var(--radius-md)',
                fontSize: '12px',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div>
            <label htmlFor="reviewmodal-field-4" style={{ display: 'block', fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
              Fundamentación Académica del Dictamen *
            </label>
            <textarea id="reviewmodal-field-4"
              rows={3}
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
              placeholder="Detalle el criterio técnico (ej. Los contenidos presentados demuestran suficiencia temática respecto al alcance de la unidad obligatoria)..."
              style={{
                width: '100%',
                background: '#FFFFFF',
                border: '1px solid #CBD5E1',
                color: '#000000',
                padding: '8px 10px',
                borderRadius: 'var(--radius-md)',
                fontSize: '12px',
                boxSizing: 'border-box',
                resize: 'vertical'
              }}
            />
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Este dictamen se incorpora de manera inmutable al expediente para constancia y trazabilidad de la resolución académica.
            </div>
          </div>

          {errorMsg && (
            <div style={{ padding: '8px 12px', background: 'rgba(239, 68, 68, 0.1)', borderLeft: '3px solid #ef4444', borderRadius: 'var(--radius-md)', fontSize: '12px', color: 'var(--nomatch-color)' }}>
              {errorMsg}
            </div>
          )}

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px', borderTop: '1px solid var(--border-color)', paddingTop: '14px' }}>
            <button type="button" onClick={onClose} className="btn btn-secondary" style={{ fontSize: '12px' }}>
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary"
              style={{ fontSize: '12px', fontWeight: 600 }}
            >
              {isSubmitting ? 'Registrando Dictamen...' : 'Registrar Dictamen Académico'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};