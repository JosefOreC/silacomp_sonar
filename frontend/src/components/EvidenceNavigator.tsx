import React, { useEffect } from 'react';
import { ArrowLeft, ArrowRight, CheckCircle2, AlertTriangle, HelpCircle, XCircle } from 'lucide-react';
import type { ContentMatch, MatchClassification } from '../types';

interface EvidenceNavigatorProps {
  matches: ContentMatch[];
  currentIndex: number;
  onSelectIndex: (index: number) => void;
}

export const EvidenceNavigator: React.FC<EvidenceNavigatorProps> = ({
  matches,
  currentIndex,
  onSelectIndex,
}) => {
  const currentMatch = matches[currentIndex];
  const total = matches.length;

  // Soporte de navegación por teclado (Flechas izquierda y derecha)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignorar si el usuario está escribiendo en un input o textarea
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) {
        return;
      }

      if (e.key === 'ArrowLeft' && currentIndex > 0) {
        onSelectIndex(currentIndex - 1);
      } else if (e.key === 'ArrowRight' && currentIndex < total - 1) {
        onSelectIndex(currentIndex + 1);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, total, onSelectIndex]);

  if (!currentMatch) return null;

  const getClassificationBadge = (classification: MatchClassification) => {
    switch (classification) {
      case 'MATCH':
        return (
          <span
            style={{
              backgroundColor: 'rgba(16, 185, 129, 0.15)',
              border: '1px solid #10b981',
              color: '#34d399',
              padding: '2px 8px',
              fontSize: '11px',
              fontWeight: 700,
              borderRadius: 0,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <CheckCircle2 size={12} /> ALTA CORRESPONDENCIA
          </span>
        );
      case 'PARTIAL_MATCH':
        return (
          <span
            style={{
              backgroundColor: 'rgba(245, 158, 11, 0.15)',
              border: '1px solid #f59e0b',
              color: '#fbbf24',
              padding: '2px 8px',
              fontSize: '11px',
              fontWeight: 700,
              borderRadius: 0,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <AlertTriangle size={12} /> CORRESPONDENCIA PARCIAL
          </span>
        );
      case 'UNCERTAIN':
        return (
          <span
            style={{
              backgroundColor: 'rgba(148, 163, 184, 0.15)',
              border: '1px dashed #94a3b8',
              color: '#cbd5e1',
              padding: '2px 8px',
              fontSize: '11px',
              fontWeight: 700,
              borderRadius: 0,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <HelpCircle size={12} /> ? REVISAR
          </span>
        );
      case 'NO_MATCH':
      default:
        return (
          <span
            style={{
              backgroundColor: 'rgba(239, 68, 68, 0.15)',
              border: '1px solid #ef4444',
              color: '#f87171',
              padding: '2px 8px',
              fontSize: '11px',
              fontWeight: 700,
              borderRadius: 0,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
          >
            <XCircle size={12} /> DISCREPANCIA
          </span>
        );
    }
  };

  const pct = Math.round(currentMatch.score_breakdown.composite_score * 100);

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        backgroundColor: '#111827',
        borderBottom: '1px solid #374151',
        padding: '10px 16px',
        borderRadius: 0,
        gap: '12px',
        flexWrap: 'wrap',
      }}
    >
      {/* Botón Anterior */}
      <button
        onClick={() => onSelectIndex(Math.max(0, currentIndex - 1))}
        disabled={currentIndex === 0}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          background: currentIndex === 0 ? '#1f2937' : '#374151',
          color: currentIndex === 0 ? '#6b7280' : '#f9fafb',
          border: '1px solid #4b5563',
          padding: '6px 12px',
          fontSize: '12px',
          fontWeight: 600,
          cursor: currentIndex === 0 ? 'not-allowed' : 'pointer',
          borderRadius: 0,
        }}
        title="Correspondencia anterior (←)"
      >
        <ArrowLeft size={14} /> Anterior
      </button>

      {/* Indicador Central de Posición y Título */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '4px',
          flex: 1,
          textAlign: 'center',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap', justifyContent: 'center' }}>
          <span style={{ color: '#9ca3af', fontSize: '12px' }}>
            Correspondencia <strong style={{ color: '#ffffff' }}>{currentIndex + 1}</strong> de {total}
          </span>

          <span
            style={{
              backgroundColor: '#1f2937',
              border: '1px solid #4b5563',
              color: '#f9fafb',
              padding: '1px 6px',
              fontFamily: 'monospace',
              fontSize: '11px',
              fontWeight: 700,
              borderRadius: 0,
            }}
          >
            Score: {pct}%
          </span>

          {getClassificationBadge(currentMatch.classification)}
        </div>

        <div style={{ display: 'flex', gap: '8px', fontSize: '12px', color: '#e5e7eb', maxWidth: '750px' }}>
          <div style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
            <span style={{ color: '#9ca3af' }}>Objetivo:</span> <strong>{currentMatch.objective_title}</strong> (Pág.{' '}
            {currentMatch.objective_page})
          </div>
          <span style={{ color: '#6b7280' }}>↔</span>
          <div style={{ textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
            <span style={{ color: '#9ca3af' }}>Comparado:</span> <strong>{currentMatch.compared_title}</strong> (Pág.{' '}
            {currentMatch.compared_page})
          </div>
        </div>
      </div>

      {/* Botón Siguiente */}
      <button
        onClick={() => onSelectIndex(Math.min(total - 1, currentIndex + 1))}
        disabled={currentIndex >= total - 1}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          background: currentIndex >= total - 1 ? '#1f2937' : '#374151',
          color: currentIndex >= total - 1 ? '#6b7280' : '#f9fafb',
          border: '1px solid #4b5563',
          padding: '6px 12px',
          fontSize: '12px',
          fontWeight: 600,
          cursor: currentIndex >= total - 1 ? 'not-allowed' : 'pointer',
          borderRadius: 0,
        }}
        title="Correspondencia siguiente (→)"
      >
        Siguiente <ArrowRight size={14} />
      </button>
    </div>
  );
};
