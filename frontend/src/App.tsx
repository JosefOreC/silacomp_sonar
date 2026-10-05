import React, { useEffect, useState } from 'react';
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
import { DualPdfViewer } from './components/DualPdfViewer';
import { ModelManagementView } from './components/ModelManagementView';
import { api } from './services/api';
import type { Comparison, ContentMatch, MatchClassification, Syllabus } from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<'upload' | 'dashboard' | 'results' | 'dataset' | 'models'>('upload');
  const [syllabi, setSyllabi] = useState<Syllabus[]>([]);
  const [activeComparison, setActiveComparison] = useState<Comparison | null>(null);
  const [selectedMatch, setSelectedMatch] = useState<ContentMatch | null>(null);
  const [reviewingMatch, setReviewingMatch] = useState<ContentMatch | null>(null);
  const [pdfViewerMatch, setPdfViewerMatch] = useState<ContentMatch | null>(null);
  const [humanReviews, setHumanReviews] = useState<Record<string, MatchClassification>>({});
  const [loadingComparison, setLoadingComparison] = useState(false);
  const [isGuideOpen, setIsGuideOpen] = useState(false);

  useEffect(() => {
    fetchSyllabi();
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
    setActiveComparison(comp);
    setSelectedMatch(null);
    setCurrentTab('results');
  };

  const handleSelectComparison = async (comparisonId: string) => {
    setLoadingComparison(true);
    try {
      const comp = await api.getComparison(comparisonId);
      setActiveComparison(comp);
      setSelectedMatch(null);
      setCurrentTab('results');
    } catch (err) {
      console.error('Error loading comparison:', err);
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
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)', display: 'flex', flexDirection: 'column' }}>
      <Header
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        hasActiveComparison={Boolean(activeComparison)}
        onOpenGuide={() => setIsGuideOpen(true)}
      />

      <main style={{ flex: 1, paddingBottom: '60px' }}>
        {currentTab === 'upload' && (
          <SyllabusUploader
            onComparisonCreated={handleComparisonCreated}
            existingSyllabi={syllabi}
            onSyllabusUploaded={fetchSyllabi}
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
          <div style={{ maxWidth: '1360px', margin: '24px auto', padding: '0 20px' }}>
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

        {currentTab === 'dataset' && <AuditDatasetView />}

        {currentTab === 'models' && <ModelManagementView />}
      </main>

      {/* Visor Pericial Doble PDF (Fase 1.5) */}
      {pdfViewerMatch && activeComparison && (
        <DualPdfViewer
          comparison={activeComparison}
          initialMatchId={pdfViewerMatch.id}
          onClose={() => setPdfViewerMatch(null)}
          onReviewSubmitted={() => {
            // Refrescar lista de sílabos o datos si es necesario
          }}
          objectiveSyllabus={objSyllabus}
          comparedSyllabus={cmpSyllabus}
        />
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
      <footer style={{ borderTop: '1px solid var(--border-color)', background: 'var(--bg-secondary)', padding: '16px 24px', textAlign: 'center', fontSize: '12px', color: 'var(--text-muted)' }}>
        ConvComp · Sistema Institucional de Análisis y Pre-Evaluación de Correspondencia Curricular
      </footer>
    </div>
  );
};

export default App;