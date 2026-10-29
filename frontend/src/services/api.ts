/**
 * Servicio de comunicación con la API REST de ConvComp.
 */

import type {
  ComparisonBatch,
  ComparisonBatchRequest,
  Comparison,
  ComparisonSummary,
  ComparisonEvidenceCatalog,
  DatasetStats,
  HumanReviewPayload,
  HumanReviewResponse,
  MatchSpatialEvidence,
  ModelVersion,
  Syllabus,
  TrainModelRequest,
  ConsensusStatus,
  GroundTruthPage,
  ReviewerAgreement,
  AnnotationBatch,
  AnnotationBatchProgress,
  AnnotationQueue,
  AnnotationReason,
  EvaluationSnapshot,
  EvaluationExperiment,
  EvaluationCriteria,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

async function jsonRequest<T>(path: string, fallback: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}/${path}`, options);
  if (!res.ok) {
    const body: unknown = await res.json().catch(() => null);
    const detail = body && typeof body === 'object' && 'detail' in body ? body.detail : null;
    throw new Error(typeof detail === 'string' ? detail : fallback);
  }
  return res.json();
}

function annotationRequest<T>(path: string, options?: RequestInit): Promise<T> {
  return jsonRequest(`active-learning/${path}`, 'No se pudo consultar o guardar el lote de anotación', options);
}

function evaluationRequest<T>(path: string, options?: RequestInit): Promise<T> {
  return jsonRequest(`evaluation/${path}`, 'No se pudo completar la evaluación científica', options);
}

export const api = {
  listComparisonBatches(): Promise<ComparisonBatch[]> {
    return jsonRequest('comparison-batches', 'No se pudieron consultar los lotes de comparación');
  },
  createComparisonBatch(request: ComparisonBatchRequest): Promise<ComparisonBatch> {
    return jsonRequest('comparison-batches', 'No se pudo ejecutar el lote de comparación', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(request),
    });
  },
  getComparisonBatch(id: string): Promise<ComparisonBatch> {
    return jsonRequest(`comparison-batches/${encodeURIComponent(id)}`, 'No se pudo recuperar el lote de comparación');
  },
  getComparisonBatchExportUrl(id: string): string {
    return `${API_BASE_URL}/comparison-batches/${encodeURIComponent(id)}/export`;
  },
  listEvaluationSnapshots(): Promise<EvaluationSnapshot[]> {
    return evaluationRequest('snapshots');
  },
  createEvaluationSnapshot(name: string, comparisonIds: string[]): Promise<EvaluationSnapshot> {
    return evaluationRequest('snapshots', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, comparison_ids: comparisonIds }) });
  },
  listEvaluationExperiments(): Promise<EvaluationExperiment[]> {
    return evaluationRequest('experiments');
  },
  createEvaluationExperiment(snapshotId: string, referenceVersion: string, candidateVersion: string, criteria: EvaluationCriteria): Promise<EvaluationExperiment> {
    return evaluationRequest('experiments', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ snapshot_id: snapshotId, reference_version: referenceVersion, candidate_version: candidateVersion, criteria }) });
  },
  getEvaluationExportUrl(kind: 'snapshots' | 'experiments', id: string): string {
    return `${API_BASE_URL}/evaluation/${kind}/${encodeURIComponent(id)}/export`;
  },
  getAnnotationQueue(filters: { comparisonId: string; reason: AnnotationReason | ''; reviewerId: string }, offset = 0): Promise<AnnotationQueue> {
    const params = new URLSearchParams({ limit: '20', offset: String(offset) });
    if (filters.comparisonId) params.set('comparison_id', filters.comparisonId);
    if (filters.reason) params.set('reason', filters.reason);
    if (filters.reviewerId.trim()) params.set('reviewer_id', filters.reviewerId.trim());
    return annotationRequest(`queue?${params}`);
  },

  createAnnotationBatch(reviewerId: string, comparisonId: string, reason: AnnotationReason | '', limit: number): Promise<AnnotationBatchProgress> {
    return annotationRequest('batches', { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId, comparison_id: comparisonId || null, reason: reason || null, limit }) });
  },

  listAnnotationBatches(): Promise<AnnotationBatch[]> {
    return annotationRequest('batches');
  },

  getAnnotationBatch(id: string): Promise<AnnotationBatchProgress> {
    return annotationRequest(`batches/${encodeURIComponent(id)}`);
  },

  completeAnnotationBatch(id: string): Promise<AnnotationBatchProgress> {
    return annotationRequest(`batches/${encodeURIComponent(id)}/complete`, { method: 'POST' });
  },
  async getGroundTruth(comparisonId: string, status: ConsensusStatus | '', offset = 0): Promise<GroundTruthPage> {
    const params = new URLSearchParams({ limit: '20', offset: String(offset) });
    if (comparisonId) params.set('comparison_id', comparisonId);
    if (status) params.set('status', status);
    const res = await fetch(`${API_BASE_URL}/dataset/ground-truth?${params}`);
    if (!res.ok) throw new Error('Error al consultar el ground truth');
    return res.json();
  },

  async getReviewerAgreement(comparisonId: string): Promise<ReviewerAgreement[]> {
    const params = new URLSearchParams();
    if (comparisonId) params.set('comparison_id', comparisonId);
    const res = await fetch(`${API_BASE_URL}/dataset/agreement?${params}`);
    if (!res.ok) throw new Error('Error al consultar el acuerdo entre revisores');
    return res.json();
  },

  getGroundTruthExportUrl(format: 'json' | 'csv', comparisonId: string): string {
    const params = new URLSearchParams({ format });
    if (comparisonId) params.set('comparison_id', comparisonId);
    return `${API_BASE_URL}/dataset/ground-truth/export?${params}`;
  },
  /**
   * Sube un archivo de sílabo PDF y devuelve los metadatos registrados.
   */
  async uploadSyllabus(file: File, university?: string, courseName?: string): Promise<Syllabus> {
    const formData = new FormData();
    formData.append('file', file);
    if (university) formData.append('university', university);
    if (courseName) formData.append('course_name', courseName);

    const res = await fetch(`${API_BASE_URL}/syllabi/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al subir sílabo' }));
      throw new Error(err.detail || 'Error en la carga del documento');
    }

    return res.json();
  },

  /**
   * Solicita la ejecución de la comparación entre dos sílabos.
   */
  async createComparison(objectiveSyllabusId: string, comparedSyllabusId: string): Promise<Comparison> {
    const res = await fetch(`${API_BASE_URL}/comparisons`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        objective_syllabus_id: objectiveSyllabusId,
        compared_syllabus_id: comparedSyllabusId,
      }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al crear comparación' }));
      throw new Error(err.detail || 'Error al procesar la comparación');
    }

    return res.json();
  },

  /**
   * Obtiene el resultado completo de una comparación por ID.
   */
  async getComparison(comparisonId: string): Promise<Comparison> {
    const res = await fetch(`${API_BASE_URL}/comparisons/${comparisonId}`);
    if (!res.ok) {
      throw new Error('No se encontró la comparación solicitada');
    }
    return res.json();
  },

  /**
   * Registra una validación o corrección humana.
   */
  async submitReview(review: HumanReviewPayload): Promise<HumanReviewResponse> {
    const res = await fetch(`${API_BASE_URL}/reviews`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(review),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al registrar revisión' }));
      throw new Error(err.detail || 'Error en el registro de la revisión');
    }

    return res.json();
  },

  /**
   * Obtiene la lista de todos los sílabos registrados.
   */
  async listSyllabi(): Promise<Syllabus[]> {
    const res = await fetch(`${API_BASE_URL}/syllabi`);
    if (!res.ok) throw new Error('Error al obtener lista de sílabos');
    return res.json();
  },

  /**
   * Obtiene el historial de comparaciones ejecutadas.
   */
  async listComparisons(): Promise<ComparisonSummary[]> {
    const res = await fetch(`${API_BASE_URL}/comparisons`);
    if (!res.ok) throw new Error('Error al obtener lista de comparaciones');
    return res.json();
  },

  /**
   * Obtiene estadísticas del dataset de calibración.
   */
  async getDatasetStats(): Promise<DatasetStats> {
    const res = await fetch(`${API_BASE_URL}/dataset/statistics`);
    if (!res.ok) throw new Error('Error al obtener estadísticas del dataset');
    return res.json();
  },

  /**
   * Retorna la URL para descargar el informe en PDF.
   */
  getReportPdfUrl(comparisonId: string): string {
    return `${API_BASE_URL}/comparisons/${comparisonId}/report/pdf`;
  },

  /**
   * Retorna la URL para previsualizar el informe en HTML imprimible.
   */
  getReportHtmlUrl(comparisonId: string): string {
    return `${API_BASE_URL}/comparisons/${comparisonId}/report/html`;
  },

  /**
   * Retorna la URL para exportar el dataset de calibración JSON.
   */
  getDatasetExportUrl(): string {
    return `${API_BASE_URL}/dataset/export`;
  },

  /**
   * Retorna la URL del archivo PDF original de un sílabo para visualización.
   */
  getSyllabusPdfUrl(syllabusId: string): string {
    return `${API_BASE_URL}/syllabi/${syllabusId}/pdf`;
  },

  /**
   * Obtiene el catálogo completo de evidencias espaciales de una comparación.
   */
  async getComparisonEvidence(comparisonId: string): Promise<ComparisonEvidenceCatalog> {
    const res = await fetch(`${API_BASE_URL}/comparisons/${comparisonId}/evidence`);
    if (!res.ok) throw new Error('Error al obtener catálogo de evidencias');
    return res.json();
  },

  /**
   * Obtiene el detalle de evidencias de una correspondencia específica.
   */
  async getMatchEvidence(comparisonId: string, matchId: string): Promise<MatchSpatialEvidence> {
    const res = await fetch(`${API_BASE_URL}/comparisons/${comparisonId}/matches/${matchId}/evidence`);
    if (!res.ok) throw new Error('Error al obtener evidencia de la correspondencia');
    return res.json();
  },

  // ─── Fase 2.0: Gestión de Modelos de Aprendizaje Supervisado ──────────────

  /**
   * Lista todas las versiones de modelos registradas (o el baseline por defecto).
   */
  async listModels(): Promise<ModelVersion[]> {
    const res = await fetch(`${API_BASE_URL}/models`);
    if (!res.ok) throw new Error('Error al obtener lista de modelos');
    return res.json();
  },

  /**
   * Obtiene el modelo activo actualmente en inferencia de producción.
   */
  async getActiveModel(): Promise<ModelVersion> {
    const res = await fetch(`${API_BASE_URL}/models/active`);
    if (!res.ok) throw new Error('Error al obtener el modelo activo');
    return res.json();
  },

  /**
   * Dispara un ciclo de entrenamiento supervisado sobre el dataset acumulado.
   */
  async trainModel(request: TrainModelRequest): Promise<ModelVersion> {
    const res = await fetch(`${API_BASE_URL}/models/train`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al entrenar modelo' }));
      throw new Error(err.detail || 'Error durante el entrenamiento del modelo supervisado');
    }
    return res.json();
  },

  /**
   * Activa una versión de modelo existente para producción.
   */
  async activateModel(versionId: string): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE_URL}/models/${versionId}/activate`, { method: 'POST' });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Error al activar modelo' }));
      throw new Error(err.detail || 'Error al activar la versión de modelo');
    }
    return res.json();
  },

  /**
   * Obtiene las métricas científicas detalladas de una versión de modelo.
   */
  async getModelEvaluation(versionId: string): Promise<Record<string, unknown>> {
    const res = await fetch(`${API_BASE_URL}/models/${versionId}/evaluation`);
    if (!res.ok) throw new Error('Error al obtener evaluación del modelo');
    return res.json();
  },

  /**
   * Retorna la URL de exportación del dataset en formato específico.
   */
  getDatasetExportFormatUrl(format: 'json' | 'csv'): string {
    return `${API_BASE_URL}/dataset/export?format=${format}`;
  },
};
