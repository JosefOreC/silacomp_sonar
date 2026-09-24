import type { MatchClassification, CorrectionType } from '../types';

export interface ClassificationInfo {
  code: MatchClassification;
  label: string;
  shortLabel: string;
  description: string;
  badgeClass: string;
  color: string;
}

export const CLASSIFICATIONS_ES: Record<MatchClassification, ClassificationInfo> = {
  MATCH: {
    code: 'MATCH',
    label: 'Equivalencia Total',
    shortLabel: 'Equivalente',
    description: 'Coincidencia temática directa y completa con concordancia igual o superior al 85%. El tema se encuentra plenamente acreditado.',
    badgeClass: 'badge-match',
    color: '#34d399',
  },
  PARTIAL_MATCH: {
    code: 'PARTIAL_MATCH',
    label: 'Equivalencia Parcial',
    shortLabel: 'Parcial',
    description: 'Coincidencia sustancial con concordancia entre el 70% y el 84%. Cubre los fundamentos esenciales de la materia.',
    badgeClass: 'badge-partial',
    color: '#fbbf24',
  },
  UNCERTAIN: {
    code: 'UNCERTAIN',
    label: 'Correspondencia Dudosa',
    shortLabel: 'A Evaluar',
    description: 'Similitud temática preliminar entre el 50% y el 69%. Requiere revisión o indagación colegiada.',
    badgeClass: 'badge-uncertain',
    color: '#94a3b8',
  },
  NO_MATCH: {
    code: 'NO_MATCH',
    label: 'Sin Equivalencia',
    shortLabel: 'Brecha',
    description: 'Sin correspondencia identificable con concordancia inferior al 50%. Constituye una brecha curricular.',
    badgeClass: 'badge-nomatch',
    color: '#f87171',
  },
};

export interface CorrectionInfo {
  code: CorrectionType;
  label: string;
  description: string;
}

export const CORRECTIONS_ES: Record<CorrectionType, CorrectionInfo> = {
  CONFIRMED: {
    code: 'CONFIRMED',
    label: 'Dictamen Ratificado',
    description: 'El evaluador ratifica la clasificación y afinidad computacional de la pre-evaluación.',
  },
  FALSE_POSITIVE: {
    code: 'FALSE_POSITIVE',
    label: 'Contenido No Equivalente',
    description: 'Se detectó afinidad computacional pero tras la revisión académica los contenidos no son homologables.',
  },
  FALSE_NEGATIVE: {
    code: 'FALSE_NEGATIVE',
    label: 'Equivalencia Reconocida',
    description: 'No se detectó afinidad computacional suficiente pero el docente valida que sí existe equivalencia real.',
  },
  OVERESTIMATION: {
    code: 'OVERESTIMATION',
    label: 'Afinidad Sobreestimada',
    description: 'El porcentaje asignado por el sistema es superior al alcance formativo real del tema.',
  },
  UNDERESTIMATION: {
    code: 'UNDERESTIMATION',
    label: 'Afinidad Subestimada',
    description: 'El porcentaje asignado por el sistema es inferior al alcance formativo real del tema.',
  },
  MANUAL_LINK: {
    code: 'MANUAL_LINK',
    label: 'Vinculación Directa',
    description: 'Asociación forzada por el evaluador entre dos contenidos no vinculados automáticamente.',
  },
};

export const EVIDENCE_TYPES_ES: Record<string, string> = {
  HYBRID: 'Híbrida: Semántica y Léxica',
  SEMANTIC: 'Semántica Conceptual',
  LEXICAL: 'Léxica Directa',
  SEMANTIC_AND_KEYWORD: 'Semántica y Vocabulario Especializado',
};

export function getClassificationLabel(code?: MatchClassification): string {
  if (!code) return 'No especificado';
  return CLASSIFICATIONS_ES[code]?.label || code;
}

export function getCorrectionLabel(code?: CorrectionType): string {
  if (!code) return 'No especificado';
  return CORRECTIONS_ES[code]?.label || code;
}

export function getEvidenceLabel(code?: string): string {
  if (!code) return 'Análisis Multivariado';
  return EVIDENCE_TYPES_ES[code] || code;
}