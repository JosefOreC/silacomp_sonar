import React from 'react';
import type { EvidenceRegion, MatchClassification } from '../types';

interface EvidenceOverlayProps {
  regions: EvidenceRegion[];
  pageNumber: number;
  canvasWidth: number;
  canvasHeight: number;
  classification?: MatchClassification;
}

export const EvidenceOverlay: React.FC<EvidenceOverlayProps> = ({
  regions,
  pageNumber,
  canvasWidth,
  canvasHeight,
  classification = 'MATCH',
}) => {
  // Filtrar únicamente las regiones correspondientes a la página actual renderizada
  const pageRegions = regions.filter((r) => r.page_number === pageNumber);

  if (pageRegions.length === 0 || canvasWidth <= 0 || canvasHeight <= 0) {
    return null;
  }

  // Estilos cromáticos formales de alto contraste con esquinas estrictamente rectas (0px)
  const getStylesByClassification = (type: MatchClassification) => {
    switch (type) {
      case 'MATCH':
        return {
          border: '2px solid #10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.14)',
          badgeBg: '#10b981',
          badgeText: '#ffffff',
          label: 'EVIDENCIA ALTA',
        };
      case 'PARTIAL_MATCH':
        return {
          border: '2px solid #f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.14)',
          badgeBg: '#f59e0b',
          badgeText: '#000000',
          label: 'EVIDENCIA PARCIAL',
        };
      case 'UNCERTAIN':
        return {
          border: '2px dashed #94a3b8',
          backgroundColor: 'rgba(148, 163, 184, 0.16)',
          badgeBg: '#475569',
          badgeText: '#ffffff',
          label: '? REVISAR',
        };
      case 'NO_MATCH':
      default:
        return {
          border: '2px solid #ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.14)',
          badgeBg: '#ef4444',
          badgeText: '#ffffff',
          label: 'DISCREPANCIA',
        };
    }
  };

  const styleConfig = getStylesByClassification(classification);

  return (
    <div
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: canvasWidth,
        height: canvasHeight,
        pointerEvents: 'none',
        zIndex: 10,
        borderRadius: 0,
      }}
    >
      {pageRegions.map((region, index) => {
        // Cálculo de escala proporcional respecto a las dimensiones de página del PDF
        const scaleX = region.page_width > 0 ? canvasWidth / region.page_width : 1;
        const scaleY = region.page_height > 0 ? canvasHeight / region.page_height : 1;

        const left = Math.max(0, region.x0 * scaleX);
        const top = Math.max(0, region.y0 * scaleY);
        const width = Math.max(30, (region.x1 - region.x0) * scaleX);
        const height = Math.max(16, (region.y1 - region.y0) * scaleY);
        const isNearTop = top < 24;

        return (
          <div
            key={region.id || `reg-${index}`}
            style={{
              position: 'absolute',
              left: `${left}px`,
              top: `${top}px`,
              width: `${width}px`,
              height: `${height}px`,
              border: styleConfig.border,
              backgroundColor: styleConfig.backgroundColor,
              boxShadow: '0 0 0 1px rgba(0,0,0,0.2), 0 2px 8px rgba(0,0,0,0.2)',
              borderRadius: 0,
              boxSizing: 'border-box',
              pointerEvents: 'auto',
              cursor: 'help',
              transition: 'all 0.15s ease',
            }}
            title={`Evidencia: ${region.text || 'Contenido detectado'} (Pág. ${region.page_number})`}
          >
            {/* Insignia indicadora con prevención de desborde superior */}
            <span
              style={{
                position: 'absolute',
                top: isNearTop ? '2px' : '-19px',
                left: isNearTop ? '2px' : '-2px',
                backgroundColor: styleConfig.badgeBg,
                color: styleConfig.badgeText,
                fontSize: '9px',
                fontWeight: 700,
                fontFamily: 'monospace',
                padding: '1px 5px',
                letterSpacing: '0.05em',
                borderRadius: 0,
                whiteSpace: 'nowrap',
                boxShadow: '0 1px 4px rgba(0,0,0,0.5)',
                pointerEvents: 'none',
                zIndex: 20,
              }}
            >
              {index === 0 ? styleConfig.label : `${styleConfig.label} #${index + 1}`}
            </span>
          </div>
        );
      })}
    </div>
  );
};
