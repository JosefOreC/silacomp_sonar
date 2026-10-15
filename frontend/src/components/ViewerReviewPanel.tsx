import React, { useState } from 'react';
import { Check, Edit3, HelpCircle, X, Send } from 'lucide-react';
import { api } from '../services/api';
import type { ContentMatch, CorrectionType, MatchClassification } from '../types';

interface ViewerReviewPanelProps {
  match: ContentMatch;
  onReviewSubmitted: () => void;
  reviewerId: string;
  onReviewerChange: (value: string) => void;
}

export const ViewerReviewPanel: React.FC<ViewerReviewPanelProps> = ({
  match,
  onReviewSubmitted,
  reviewerId,
  onReviewerChange,
}) => {
  const [decision, setDecision] = useState<MatchClassification>(match.classification);
  const [justification, setJustification] = useState<string>('');
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const getCorrectionType = (newDecision: MatchClassification): CorrectionType => {
    if (newDecision === match.classification) return 'CONFIRMED';
    if (newDecision === 'NO_MATCH') return 'FALSE_POSITIVE';
    if (match.classification === 'NO_MATCH') return 'FALSE_NEGATIVE';
    if (newDecision === 'PARTIAL_MATCH' && match.classification === 'MATCH') return 'OVERESTIMATION';
    if (newDecision === 'MATCH' && match.classification === 'PARTIAL_MATCH') return 'UNDERESTIMATION';
    return 'OVERESTIMATION';
  };

  const handleSubmit = async () => {
    if (!reviewerId.trim()) {
      setStatusMessage({ type: 'error', text: 'Identifique al revisor antes de registrar la decisión.' });
      return;
    }
    if (decision !== match.classification && justification.trim().length < 5) {
      setStatusMessage({
        type: 'error',
        text: 'La justificación académica es obligatoria (mínimo 5 caracteres) al modificar el dictamen del algoritmo.',
      });
      return;
    }

    setSubmitting(true);
    setStatusMessage(null);

    try {
      await api.submitReview({
        comparison_id: match.comparison_id,
        match_id: match.id,
        prediction_before: match.classification,
        human_decision: decision,
        correction_type: getCorrectionType(decision),
        justification: justification.trim() || 'Dictamen ratificado por el evaluador desde el visor PDF.',
        reviewer_id: reviewerId.trim(),
      });

      setStatusMessage({
        type: 'success',
        text: 'Dictamen registrado exitosamente en el módulo de auditoría.',
      });
      setJustification('');
      onReviewSubmitted();
    } catch (err: unknown) {
      setStatusMessage({
        type: 'error',
        text: err instanceof Error ? err.message : 'Error al guardar la revisión.',
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      style={{
        backgroundColor: '#111827',
        borderTop: '1px solid #374151',
        padding: '12px 18px',
        borderRadius: 0,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <div style={{ color: '#f3f4f6', fontSize: '13px', fontWeight: 600 }}>
          Dictamen y Calibración Docente (Fase 1.5)
        </div>
        <div style={{ color: '#9ca3af', fontSize: '11px' }}>
          * Las decisiones humanas no modifican las predicciones base de la IA (Principio de Inmutabilidad).
        </div>
      </div>

      <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', flexWrap: 'wrap' }}>
        <label style={{ color: 'var(--text-secondary)', fontSize: 12 }}>
          Revisor{' '}
          <input value={reviewerId} onChange={(e) => onReviewerChange(e.target.value)} aria-label="Identificador del revisor" />
        </label>
        {/* Botones de Selección de Dictamen */}
        <div style={{ display: 'flex', gap: '6px' }}>
          <button
            type="button"
            onClick={() => setDecision('MATCH')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              backgroundColor: decision === 'MATCH' ? '#065f46' : '#1f2937',
              border: decision === 'MATCH' ? '1px solid #10b981' : '1px solid #374151',
              color: decision === 'MATCH' ? '#ecfdf5' : '#d1d5db',
              padding: '6px 10px',
              fontSize: '11px',
              fontWeight: 600,
              cursor: 'pointer',
              borderRadius: 0,
            }}
          >
            <Check size={13} /> Ratificar Match
          </button>

          <button
            type="button"
            onClick={() => setDecision('PARTIAL_MATCH')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              backgroundColor: decision === 'PARTIAL_MATCH' ? '#78350f' : '#1f2937',
              border: decision === 'PARTIAL_MATCH' ? '1px solid #f59e0b' : '1px solid #374151',
              color: decision === 'PARTIAL_MATCH' ? '#fffbeb' : '#d1d5db',
              padding: '6px 10px',
              fontSize: '11px',
              fontWeight: 600,
              cursor: 'pointer',
              borderRadius: 0,
            }}
          >
            <Edit3 size={13} /> Ajustar a Parcial
          </button>

          <button
            type="button"
            onClick={() => setDecision('UNCERTAIN')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              backgroundColor: decision === 'UNCERTAIN' ? '#334155' : '#1f2937',
              border: decision === 'UNCERTAIN' ? '1px dashed #94a3b8' : '1px solid #374151',
              color: decision === 'UNCERTAIN' ? '#f8fafc' : '#d1d5db',
              padding: '6px 10px',
              fontSize: '11px',
              fontWeight: 600,
              cursor: 'pointer',
              borderRadius: 0,
            }}
          >
            <HelpCircle size={13} /> Marcar Dudoso
          </button>

          <button
            type="button"
            onClick={() => setDecision('NO_MATCH')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              backgroundColor: decision === 'NO_MATCH' ? '#7f1d1d' : '#1f2937',
              border: decision === 'NO_MATCH' ? '1px solid #ef4444' : '1px solid #374151',
              color: decision === 'NO_MATCH' ? '#fef2f2' : '#d1d5db',
              padding: '6px 10px',
              fontSize: '11px',
              fontWeight: 600,
              cursor: 'pointer',
              borderRadius: 0,
            }}
          >
            <X size={13} /> Descartar
          </button>
        </div>

        {/* Campo de Justificación Académica */}
        <div style={{ flex: 1, minWidth: '280px', display: 'flex', gap: '8px' }}>
          <input
            type="text"
            placeholder={
              decision !== match.classification
                ? 'Fundamento académico del cambio (obligatorio)...'
                : 'Observación opcional para el informe formal...'
            }
            value={justification}
            onChange={(e) => setJustification(e.target.value)}
            style={{
              flex: 1,
              backgroundColor: '#1f2937',
              border: '1px solid #4b5563',
              color: '#f9fafb',
              padding: '6px 10px',
              fontSize: '12px',
              borderRadius: 0,
              outline: 'none',
            }}
          />

          <button
            type="button"
            onClick={handleSubmit}
            disabled={submitting}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: '#374151',
              border: '1px solid #4b5563',
              color: '#ffffff',
              padding: '6px 14px',
              fontSize: '11px',
              fontWeight: 700,
              cursor: submitting ? 'wait' : 'pointer',
              borderRadius: 0,
              whiteSpace: 'nowrap',
            }}
          >
            <Send size={12} /> {submitting ? 'Guardando...' : 'Registrar Dictamen'}
          </button>
        </div>
      </div>

      {statusMessage && (
        <div
          style={{
            marginTop: '8px',
            fontSize: '12px',
            color: statusMessage.type === 'success' ? '#34d399' : '#f87171',
          }}
        >
          {statusMessage.text}
        </div>
      )}
    </div>
  );
};
