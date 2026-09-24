/**
 * Servicio de comunicación con la API REST de ConvComp.
 */

import type { Comparison, HumanReviewPayload, HumanReviewResponse, Syllabus } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = {
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
  async listComparisons(): Promise<any[]> {
    const res = await fetch(`${API_BASE_URL}/comparisons`);
    if (!res.ok) throw new Error('Error al obtener lista de comparaciones');
    return res.json();
  },

  /**
   * Obtiene estadísticas del dataset de calibración.
   */
  async getDatasetStats(): Promise<any> {
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
};
