import React, { lazy, Suspense, useEffect, useState } from 'react';
import { Header } from './components/Header';
import { SyllabusUploader } from './components/SyllabusUploader';
import { Dashboard } from './components/Dashboard';
import { ComparisonScore } from './components/ComparisonScore';
import { MatchTable } from './components/MatchTable';
import { EvidencePanel } from './components/EvidencePanel';
import { UnmatchedPanel } from './components/UnmatchedPanel';
import { ReviewModal } from './components/ReviewModal';
import { AuditDatasetView } from './components/AuditDatasetView';
import { SupportGuideModal } from './components/SupportGuideModal';
import { api } from './services/api';
import type { AppTab, Comparison, ContentMatch, MatchClassification, Syllabus } from './types';

const DualPdfViewer = lazy(() => import('./components/DualPdfViewer').then((m) => ({ default: m.DualPdfViewer })));
const ModelManagementView = lazy(() => import('./components/ModelManagementView').then((m) => ({ default: m.ModelManagementView })));
const BatchComparisonView = lazy(() => import('./components/BatchComparisonView').then(m => ({ default: m.BatchComparisonView })));

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<AppTab>('upload');
  const [comparisonError, setComparisonError] = useState<string | null>(null);
  const [syllabi, setSyllabi] = useState<Syllabus[]>([]);
  const [activeComparison, setActiveComparison] = useState<Comparison | null>(null);
  const [selectedMatch, setSelectedMatch] = useState<ContentMatch | null>(null);
  const [reviewingMatch, setReviewingMatch] = useState<ContentMatch | null>(null);
  const [pdfViewerMatch, setPdfViewerMatch] = useState<ContentMatch | null>(null);
  const [humanReviews, setHumanReviews] = useState<Record<string, MatchClassification>>({});
  const [loadingComparison, setLoadingComparison] = useState(false);
  const [isGuideOpen, setIsGuideOpen] = useState(false);

  useEffect(() => {
    let cancelled = false;
    api.listSyllabi().then((data) => {
      if (!cancelled) setSyllabi(data);
    }).catch((err: unknown) => console.error('Error fetching syllabi:', err));
    return () => { cancelled = true; };
  }, []);

  const fetchSyllabi = async () => {
    try {
      const data = await api.listSyllabi();
      setSyllabi(data);
    } catch (err) {
      console.error('Error fetching syllabi:', err);
    }
  };

  const handleComparisonCreated = (comp: Comparison) => {
    setComparisonError(null);
    setActiveComparison(comp);
    setSelectedMatch(null);
    setCurrentTab('results');
  };

  const handleSelectComparison = async (comparisonId: string) => {
    setLoadingComparison(true);
    setComparisonError(null);
    try {
      const comp = await api.getComparison(comparisonId);
      setActiveComparison(comp);
      setSelectedMatch(null);
      setCurrentTab('results');
    } catch (err) {
      console.error('Error loading comparison:', err);
      setComparisonError(err instanceof Error ? err.message : 'No se pudo recuperar el análisis. Vuelva a intentarlo.');
    } finally {
      setLoadingComparison(false);
    }
  };

  const handleReviewSaved = (matchId: string, decision: MatchClassification) => {
    setHumanReviews((prev) => ({ ...prev, [matchId]: decision }));
  };

  const objSyllabus = syllabi.find((s) => s.id === activeComparison?.objective_syllabus_id);
  const cmpSyllabus = syllabi.find((s) => s.id === activeComparison?.compared_syllabus_id);

  return (
    <div className="app-shell" data-view={currentTab}>
      <Header
        currentTab={currentTab}
        onSelectTab={tab => { setCurrentTab(tab); setComparisonError(null); }}
        hasActiveComparison={Boolean(activeComparison)}
        onOpenGuide={() => setIsGuideOpen(true)}
      />

      <main id="main-content" className="app-main">
        {comparisonError && <p className="feedback feedback-error page-container" role="alert">{comparisonError}</p>}
        {currentTab === 'upload' && (
          <SyllabusUploader
            onComparisonCreated={handleComparisonCreated}
            existingSyllabi={syllabi}
            onSyllabusUploaded={fetchSyllabi}
            onOpenGuide={() => setIsGuideOpen(true)}
            onOpenBatch={() => setCurrentTab('batches')}
          />
        )}

        {currentTab === 'dashboard' && (
          <Dashboard
            onSelectComparison={handleSelectComparison}
            onGoToUpload={() => setCurrentTab('upload')}
            syllabi={syllabi}
          />
        )}

        {currentTab === 'results' && (
          <div className="results-page page-container">
            {loadingComparison ? (
              <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>
                Cargando análisis de correspondencia...
              </div>
            ) : activeComparison ? (
              <>
                <ComparisonScore
                  comparison={activeComparison}
                  objectiveCourseName={objSyllabus?.course_name || activeComparison.objective_syllabus_id}
                  comparedCourseName={cmpSyllabus?.course_name || activeComparison.compared_syllabus_id}
                  onOpenHelp={() => setIsGuideOpen(true)}
                />

                {selectedMatch && (
                  <EvidencePanel
                    match={selectedMatch}
                    onClose={() => setSelectedMatch(null)}
                    onOpenReview={(m) => setReviewingMatch(m)}
                    humanReviewDecision={humanReviews[selectedMatch.id]}
                    onOpenPdfViewer={(m) => setPdfViewerMatch(m)}
                  />
                )}

                <MatchTable
                  matches={activeComparison.matches}
                  selectedMatchId={selectedMatch?.id}
                  onSelectMatch={(m) => setSelectedMatch(selectedMatch?.id === m.id ? null : m)}
                  humanReviews={humanReviews}
                  onOpenPdfViewer={(m) => setPdfViewerMatch(m)}
                />

                <UnmatchedPanel
                  unmatchedObjective={activeComparison.unmatched_objective}
                  unmatchedCompared={activeComparison.unmatched_compared}
                />
              </>
            ) : (
              <div style={{ textAlign: 'center', padding: '60px' }}>
                <p style={{ color: 'var(--text-muted)' }}>No hay ninguna comparación activa seleccionada.</p>
                <button onClick={() => setCurrentTab('upload')} className="btn btn-primary">
                  Cargar y Comparar Sílabos
                </button>
              </div>
            )}
          </div>
        )}

        {currentTab === 'dataset' && <AuditDatasetView onOpenComparison={handleSelectComparison} />}

        {currentTab === 'batches' && <Suspense fallback={<p role="status">Cargando comparación por lotes...</p>}>
          <BatchComparisonView syllabi={syllabi} onOpenComparison={handleSelectComparison}
            onGoToUpload={() => setCurrentTab('upload')} />
        </Suspense>}

        {currentTab === 'models' && (
          <Suspense fallback={<p role="status">Cargando gestión de modelos...</p>}>
            <ModelManagementView />
          </Suspense>
        )}
      </main>

      {/* Visor Pericial Doble PDF (Fase 1.5) */}
      {pdfViewerMatch && activeComparison && (
        <Suspense fallback={<p role="status">Cargando visor PDF...</p>}>
        <DualPdfViewer
          key={`${activeComparison.id}:${pdfViewerMatch.id}`}
          comparison={activeComparison}
          initialMatchId={pdfViewerMatch.id}
          onClose={() => setPdfViewerMatch(null)}
          onReviewSubmitted={handleReviewSaved}
          objectiveSyllabus={objSyllabus}
          comparedSyllabus={cmpSyllabus}
        />
        </Suspense>
      )}

      {reviewingMatch && (
        <ReviewModal
          match={reviewingMatch}
          onClose={() => setReviewingMatch(null)}
          onReviewSaved={handleReviewSaved}
        />
      )}

      {/* Modal de Soporte Académico y Glosario */}
      <SupportGuideModal
        isOpen={isGuideOpen}
        onClose={() => setIsGuideOpen(false)}
      />

      {/* Footer */}
      <footer className="site-footer">
        <div><strong>ConvComp<span>.</span></strong><span>Correspondencia académica con evidencia.</span></div>
        <p>El presente resultado es una pre-evaluación computacional explicable de correspondencia académica. No sustituye la evaluación oficial ni constituye resolución vinculante de convalidación.</p>
      </footer>
    </div>
  );
};

export default App;
