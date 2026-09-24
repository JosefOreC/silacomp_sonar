import React, { useState, useEffect } from 'react';
import { X, FileText } from 'lucide-react';
import { api } from '../services/api';
import { PdfDocumentViewer } from './PdfDocumentViewer';
import { EvidenceNavigator } from './EvidenceNavigator';
import { ViewerReviewPanel } from './ViewerReviewPanel';
import type { Comparison, Syllabus } from '../types';

interface DualPdfViewerProps {
  comparison: Comparison;
  initialMatchId?: string;
  onClose: () => void;
  onReviewSubmitted: () => void;
  objectiveSyllabus?: Syllabus;
  comparedSyllabus?: Syllabus;
}

export const DualPdfViewer: React.FC<DualPdfViewerProps> = ({
  comparison,
  initialMatchId,
  onClose,
  onReviewSubmitted,
  objectiveSyllabus,
  comparedSyllabus,
}) => {
  const matches = comparison.matches || [];

  // Encontrar índice inicial según match_id
  const findInitialIndex = () => {
    if (!initialMatchId) return 0;
    const idx = matches.findIndex((m) => m.id === initialMatchId);
    return idx >= 0 ? idx : 0;
  };

  const [currentIndex, setCurrentIndex] = useState<number>(findInitialIndex);

  const currentMatch = matches[currentIndex] || null;

  // Estados de página activa para cada visor
  const [objPage, setObjPage] = useState<number>(currentMatch ? currentMatch.objective_page : 1);
  const [cmpPage, setCmpPage] = useState<number>(currentMatch ? currentMatch.compared_page : 1);

  // Sincronizar páginas al cambiar de correspondencia
  useEffect(() => {
    if (currentMatch) {
      setObjPage(currentMatch.objective_page || 1);
      setCmpPage(currentMatch.compared_page || 1);
    }
  }, [currentIndex, currentMatch]);

  // Soporte de tecla Escape para cerrar
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!currentMatch) {
    return (
      <div
        style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0,0,0,0.85)',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          borderRadius: 0,
        }}
      >
        <div style={{ backgroundColor: '#1e293b', padding: '24px', border: '1px solid #475569', borderRadius: 0 }}>
          <p>No se encontraron correspondencias evaluadas para visualizar.</p>
          <button
            onClick={onClose}
            style={{
              marginTop: '12px',
              padding: '6px 16px',
              backgroundColor: '#334155',
              color: '#ffffff',
              border: '1px solid #64748b',
              borderRadius: 0,
              cursor: 'pointer',
            }}
          >
            Cerrar
          </button>
        </div>
      </div>
    );
  }

  const objPdfUrl = api.getSyllabusPdfUrl(comparison.objective_syllabus_id);
  const cmpPdfUrl = api.getSyllabusPdfUrl(comparison.compared_syllabus_id);

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: '#020617',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 0,
        overflow: 'hidden',
      }}
    >
      {/* 1. Barra Superior Principal de Navegación y Control */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#0f172a',
          borderBottom: '1px solid #1e293b',
          padding: '10px 18px',
          borderRadius: 0,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div
            style={{
              backgroundColor: '#1e293b',
              padding: '6px',
              border: '1px solid #334155',
              display: 'flex',
              alignItems: 'center',
              borderRadius: 0,
            }}
          >
            <FileText size={18} color="#94a3b8" />
          </div>
          <div>
            <div style={{ color: '#ffffff', fontSize: '14px', fontWeight: 700, letterSpacing: '0.02em' }}>
              VISOR PERICIAL DOBLE DE SÍLABOS (FASE 1.5)
            </div>
            <div style={{ color: '#94a3b8', fontSize: '11px' }}>
              Trazabilidad y Contrastación Espacial sobre Documentos PDF Originales
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ color: '#64748b', fontSize: '11px', fontFamily: 'monospace' }}>
            ID Comparación: {comparison.id}
          </span>
          <button
            onClick={onClose}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              backgroundColor: '#1e293b',
              border: '1px solid #475569',
              color: '#f8fafc',
              padding: '6px 14px',
              fontSize: '12px',
              fontWeight: 700,
              cursor: 'pointer',
              borderRadius: 0,
            }}
            title="Cerrar visor (Esc)"
          >
            <X size={14} /> CERRAR VISOR
          </button>
        </div>
      </div>

      {/* 2. Barra de Navegación entre Correspondencias */}
      <EvidenceNavigator
        matches={matches}
        currentIndex={currentIndex}
        onSelectIndex={setCurrentIndex}
      />

      {/* 3. Área Central: Los Dos Visores PDF Lado a Lado */}
      <div
        style={{
          flex: 1,
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '8px',
          padding: '8px',
          backgroundColor: '#090d16',
          overflow: 'hidden',
          borderRadius: 0,
        }}
      >
        {/* Panel Izquierdo: Sílabo Objetivo (Asignatura Requerida) */}
        <PdfDocumentViewer
          title="Sílabo Objetivo (Asignatura Requerida · Plan Destino)"
          courseName={objectiveSyllabus?.course_name || 'Asignatura Objetivo'}
          university={objectiveSyllabus?.university}
          pdfUrl={objPdfUrl}
          pageNumber={objPage}
          onPageChange={setObjPage}
          regions={currentMatch.evidence.objective_regions || []}
          classification={currentMatch.classification}
        />

        {/* Panel Derecho: Sílabo Comparado (Asignatura Cursada) */}
        <PdfDocumentViewer
          title="Sílabo Comparado (Asignatura Cursada · Institución Origen)"
          courseName={comparedSyllabus?.course_name || 'Asignatura Comparada'}
          university={comparedSyllabus?.university}
          pdfUrl={cmpPdfUrl}
          pageNumber={cmpPage}
          onPageChange={setCmpPage}
          regions={currentMatch.evidence.compared_regions || []}
          classification={currentMatch.classification}
        />
      </div>

      {/* 4. Panel Inferior de Dictamen Humano Directo */}
      <ViewerReviewPanel
        match={currentMatch}
        onReviewSubmitted={onReviewSubmitted}
      />
    </div>
  );
};
