import React, { useEffect, useRef, useState, useCallback } from 'react';
import { ZoomIn, ZoomOut, Maximize2, Minimize2, ChevronLeft, ChevronRight, RotateCcw, AlertCircle } from 'lucide-react';
import { pdfjsLib } from '../utils/pdfSetup';
import { EvidenceOverlay } from './EvidenceOverlay';
import type { EvidenceRegion, MatchClassification } from '../types';

interface PdfDocumentViewerProps {
  pdfUrl: string;
  pageNumber: number;
  onPageChange: (newPage: number) => void;
  regions?: EvidenceRegion[];
  classification?: MatchClassification;
  title: string;
  courseName?: string;
  university?: string;
}

export const PdfDocumentViewer: React.FC<PdfDocumentViewerProps> = ({
  pdfUrl,
  pageNumber,
  onPageChange,
  regions = [],
  classification = 'MATCH',
  title,
  courseName,
  university,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const renderTaskRef = useRef<any>(null);

  const [pdfDoc, setPdfDoc] = useState<any>(null);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [scale, setScale] = useState<number>(1.25);
  const [fitMode, setFitMode] = useState<'width' | 'page' | 'custom'>('width');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [canvasDimensions, setCanvasDimensions] = useState<{ width: number; height: number }>({
    width: 0,
    height: 0,
  });

  // 1. Cargar el documento PDF original desde la URL del backend
  useEffect(() => {
    let isCancelled = false;
    setLoading(true);
    setError(null);

    const loadingTask = pdfjsLib.getDocument({
      url: pdfUrl,
      cMapUrl: 'https://unpkg.com/pdfjs-dist@4.10.38/cmaps/',
      cMapPacked: true,
    });

    loadingTask.promise
      .then((doc: any) => {
        if (!isCancelled) {
          setPdfDoc(doc);
          setTotalPages(doc.numPages);
          setLoading(false);
        }
      })
      .catch((err: any) => {
        if (!isCancelled) {
          console.error('[PdfDocumentViewer] Error al cargar PDF:', err);
          setError('No se pudo visualizar el archivo PDF original en el servidor.');
          setLoading(false);
        }
      });

    return () => {
      isCancelled = true;
      try {
        loadingTask.destroy();
      } catch (e) {
        // ignore
      }
    };
  }, [pdfUrl]);

  // 2. Función para renderizar la página en el canvas
  const renderPage = useCallback(async () => {
    if (!pdfDoc || !canvasRef.current || !containerRef.current) return;

    try {
      // Cancelar render previo si estaba en curso
      if (renderTaskRef.current) {
        renderTaskRef.current.cancel();
      }

      const page = await pdfDoc.getPage(Math.min(Math.max(1, pageNumber), totalPages));
      const unscaledViewport = page.getViewport({ scale: 1.0 });

      // Calcular escala según fitMode
      let targetScale = scale;
      const containerWidth = containerRef.current.clientWidth - 32; // padding
      const containerHeight = containerRef.current.clientHeight - 80;

      if (fitMode === 'width' && containerWidth > 0) {
        targetScale = containerWidth / unscaledViewport.width;
      } else if (fitMode === 'page' && containerHeight > 0) {
        const scaleW = containerWidth / unscaledViewport.width;
        const scaleH = containerHeight / unscaledViewport.height;
        targetScale = Math.min(scaleW, scaleH);
      }

      const viewport = page.getViewport({ scale: targetScale });
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d', { alpha: false });

      if (!context) return;

      // Soporte HiDPI / Retina
      const outputScale = window.devicePixelRatio || 1;
      canvas.width = Math.floor(viewport.width * outputScale);
      canvas.height = Math.floor(viewport.height * outputScale);
      canvas.style.width = `${Math.floor(viewport.width)}px`;
      canvas.style.height = `${Math.floor(viewport.height)}px`;

      context.imageSmoothingEnabled = true;

      const transform = outputScale !== 1 ? [outputScale, 0, 0, outputScale, 0, 0] : undefined;

      const renderContext = {
        canvasContext: context,
        viewport,
        transform,
      };

      const renderTask = page.render(renderContext);
      renderTaskRef.current = renderTask;

      await renderTask.promise;

      setCanvasDimensions({
        width: Math.floor(viewport.width),
        height: Math.floor(viewport.height),
      });
      renderTaskRef.current = null;

      // Auto-centrar suavemente en la primera evidencia de esta página si existe
      const pageEvidences = regions.filter((r) => r.page_number === pageNumber);
      if (pageEvidences.length > 0 && containerRef.current) {
        const firstEvidence = pageEvidences[0];
        const scaleY = firstEvidence.page_height > 0 ? viewport.height / firstEvidence.page_height : 1;
        const targetScrollY = Math.max(0, firstEvidence.y0 * scaleY - 60);
        setTimeout(() => {
          if (containerRef.current) {
            containerRef.current.scrollTo({
              top: targetScrollY,
              behavior: 'smooth',
            });
          }
        }, 100);
      }
    } catch (err: any) {
      if (err?.name !== 'RenderingCancelledException') {
        console.error('[PdfDocumentViewer] Error al renderizar página:', err);
      }
    }
  }, [pdfDoc, pageNumber, totalPages, scale, fitMode, regions]);

  useEffect(() => {
    renderPage();
  }, [renderPage]);

  // Manejo de Zoom
  const handleZoomIn = () => {
    setFitMode('custom');
    setScale((prev) => Math.min(2.5, +(prev + 0.15).toFixed(2)));
  };

  const handleZoomOut = () => {
    setFitMode('custom');
    setScale((prev) => Math.max(0.5, +(prev - 0.15).toFixed(2)));
  };

  const handleResetZoom = () => {
    setFitMode('custom');
    setScale(1.0);
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: '#0f172a',
        border: '1px solid #334155',
        borderRadius: 0,
        overflow: 'hidden',
      }}
    >
      {/* Barra de Título y Metadatos del Documento */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#1e293b',
          borderBottom: '1px solid #334155',
          padding: '8px 12px',
          borderRadius: 0,
        }}
      >
        <div style={{ overflow: 'hidden' }}>
          <div style={{ color: '#f8fafc', fontSize: '13px', fontWeight: 600, whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
            {title}
          </div>
          <div style={{ color: '#94a3b8', fontSize: '11px', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
            {courseName || 'Asignatura'} {university ? `• ${university}` : ''}
          </div>
        </div>

        {/* Controles de Zoom */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <button
            onClick={() => setFitMode('width')}
            style={{
              background: fitMode === 'width' ? '#334155' : 'transparent',
              border: '1px solid #475569',
              color: '#e2e8f0',
              padding: '3px 7px',
              fontSize: '10px',
              fontWeight: 600,
              cursor: 'pointer',
              borderRadius: 0,
            }}
            title="Ajustar al Ancho"
          >
            <Maximize2 size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
            Ancho
          </button>

          <button
            onClick={() => setFitMode('page')}
            style={{
              background: fitMode === 'page' ? '#334155' : 'transparent',
              border: '1px solid #475569',
              color: '#e2e8f0',
              padding: '3px 7px',
              fontSize: '10px',
              fontWeight: 600,
              cursor: 'pointer',
              borderRadius: 0,
            }}
            title="Ajustar a la Página Completa"
          >
            <Minimize2 size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
            Página
          </button>

          <button
            onClick={handleZoomOut}
            style={{
              background: 'transparent',
              border: '1px solid #475569',
              color: '#cbd5e1',
              padding: '3px 6px',
              cursor: 'pointer',
              borderRadius: 0,
            }}
            title="Reducir Zoom"
          >
            <ZoomOut size={12} />
          </button>

          <button
            onClick={handleResetZoom}
            style={{
              background: 'transparent',
              border: '1px solid #475569',
              color: '#94a3b8',
              padding: '3px 6px',
              fontSize: '10px',
              fontFamily: 'monospace',
              cursor: 'pointer',
              borderRadius: 0,
            }}
            title="Restablecer 100%"
          >
            <RotateCcw size={11} style={{ marginRight: '3px', verticalAlign: 'middle' }} />
            {Math.round(scale * 100)}%
          </button>

          <button
            onClick={handleZoomIn}
            style={{
              background: 'transparent',
              border: '1px solid #475569',
              color: '#cbd5e1',
              padding: '3px 6px',
              cursor: 'pointer',
              borderRadius: 0,
            }}
            title="Aumentar Zoom"
          >
            <ZoomIn size={12} />
          </button>
        </div>
      </div>

      {/* Área del Lienzo PDF con Desplazamiento */}
      <div
        ref={containerRef}
        style={{
          flex: 1,
          overflow: 'auto',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'flex-start',
          padding: '16px',
          backgroundColor: '#090d16',
          position: 'relative',
        }}
      >
        {loading && (
          <div style={{ color: '#94a3b8', fontSize: '13px', marginTop: '60px', textAlign: 'center' }}>
            <div style={{ marginBottom: '8px' }}>Cargando PDF original...</div>
            <div style={{ fontSize: '11px', color: '#64748b' }}>Renderizando trazabilidad de evidencias</div>
          </div>
        )}

        {error && (
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              color: '#f87171',
              fontSize: '13px',
              marginTop: '60px',
              padding: '16px',
              border: '1px solid #ef4444',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              borderRadius: 0,
            }}
          >
            <AlertCircle size={24} style={{ marginBottom: '8px' }} />
            <div>{error}</div>
          </div>
        )}

        {!loading && !error && (
          <div
            style={{
              position: 'relative',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.6)',
              backgroundColor: '#ffffff',
              borderRadius: 0,
            }}
          >
            <canvas ref={canvasRef} style={{ display: 'block', borderRadius: 0 }} />

            {/* Capa de indicadores espaciales */}
            <EvidenceOverlay
              regions={regions}
              pageNumber={pageNumber}
              canvasWidth={canvasDimensions.width}
              canvasHeight={canvasDimensions.height}
              classification={classification}
            />
          </div>
        )}
      </div>

      {/* Barra Inferior de Navegación de Páginas */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#1e293b',
          borderTop: '1px solid #334155',
          padding: '6px 14px',
          borderRadius: 0,
        }}
      >
        <div style={{ color: '#94a3b8', fontSize: '11px' }}>
          {regions.filter((r) => r.page_number === pageNumber).length > 0 ? (
            <span style={{ color: '#10b981', fontWeight: 600 }}>
              • {regions.filter((r) => r.page_number === pageNumber).length} evidencia(s) en esta página
            </span>
          ) : (
            <span>Sin evidencias en esta página</span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={() => onPageChange(Math.max(1, pageNumber - 1))}
            disabled={pageNumber <= 1}
            style={{
              background: '#0f172a',
              border: '1px solid #475569',
              color: pageNumber <= 1 ? '#475569' : '#e2e8f0',
              padding: '4px 8px',
              cursor: pageNumber <= 1 ? 'not-allowed' : 'pointer',
              borderRadius: 0,
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <ChevronLeft size={14} />
          </button>

          <span style={{ color: '#e2e8f0', fontSize: '12px', fontWeight: 500 }}>
            Pág. <strong style={{ color: '#ffffff' }}>{pageNumber}</strong> de {totalPages}
          </span>

          <button
            onClick={() => onPageChange(Math.min(totalPages, pageNumber + 1))}
            disabled={pageNumber >= totalPages}
            style={{
              background: '#0f172a',
              border: '1px solid #475569',
              color: pageNumber >= totalPages ? '#475569' : '#e2e8f0',
              padding: '4px 8px',
              cursor: pageNumber >= totalPages ? 'not-allowed' : 'pointer',
              borderRadius: 0,
              display: 'flex',
              alignItems: 'center',
            }}
          >
            <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};
