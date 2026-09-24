"""
Entidades y objetos de valor para Comparaciones, Puntuaciones y Evidencias.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class MatchClassification(str, Enum):
    """Categorías formales de correspondencia entre dos contenidos."""
    MATCH = "MATCH"                    # Correspondencia alta (>= 0.85)
    PARTIAL_MATCH = "PARTIAL_MATCH"    # Correspondencia parcial (0.70 - 0.849)
    UNCERTAIN = "UNCERTAIN"            # Incierto / requiere revisión (0.50 - 0.699)
    NO_MATCH = "NO_MATCH"              # Sin correspondencia (< 0.50)


@dataclass(frozen=True)
class ScoreBreakdown:
    """Desglose transparente y auditable de los componentes del score compuesto."""
    semantic_similarity: float
    lexical_similarity: float
    keyword_overlap: float
    structural_similarity: float
    composite_score: float
    weights: Dict[str, float]

    def __post_init__(self) -> None:
        for val in (self.semantic_similarity, self.lexical_similarity, self.keyword_overlap, self.structural_similarity, self.composite_score):
            if not (0.0 <= round(val, 4) <= 1.05):
                raise ValueError(f"Los componentes de score deben estar en el rango [0.0, 1.0], recibido: {val}")


class EvidenceType(str, Enum):
    """Tipos de evidencia formal para la Fase 1.5."""
    LEXICAL = "LEXICAL"
    SEMANTIC = "SEMANTIC"
    STRUCTURAL = "STRUCTURAL"
    COMBINED = "COMBINED"


@dataclass(frozen=True)
class EvidenceRegion:
    """Región espacial delimitada (bounding box) dentro de una página de un sílabo PDF."""
    id: str
    match_id: str
    syllabus_id: str
    content_id: str
    page_number: int
    page_width: float
    page_height: float
    x0: float
    y0: float
    x1: float
    y1: float
    text: str
    evidence_type: str = "COMBINED"


@dataclass(frozen=True)
class MatchEvidence:
    """Evidencia verificable y observable que sustenta una correspondencia."""
    evidence_type: str  # "LEXICAL", "SEMANTIC", "HYBRID"
    shared_keywords: List[str]
    semantic_score: float
    lexical_score: float
    objective_snippet: str
    compared_snippet: str
    objective_page: int
    compared_page: int
    objective_regions: List[EvidenceRegion] = field(default_factory=list)
    compared_regions: List[EvidenceRegion] = field(default_factory=list)


@dataclass
class ContentMatch:
    """Representa el emparejamiento evaluado entre un contenido objetivo y uno comparado."""
    id: str
    comparison_id: str
    objective_item_id: str
    compared_item_id: str
    objective_title: str
    compared_title: str
    objective_section: str
    compared_section: str
    objective_page: int
    compared_page: int
    score_breakdown: ScoreBreakdown
    classification: MatchClassification
    evidence: MatchEvidence

    @property
    def score(self) -> float:
        return self.score_breakdown.composite_score


@dataclass(frozen=True)
class UnmatchedItem:
    """Representa un contenido que no encontró correspondencia suficiente."""
    item_id: str
    syllabus_id: str
    section_name: str
    title: str
    text_snippet: str
    page: int
    best_candidate_id: Optional[str] = None
    best_candidate_title: Optional[str] = None
    best_score: Optional[float] = None


@dataclass
class Comparison:
    """Entidad principal que almacena el resultado integral de la comparación entre dos sílabos."""
    id: str
    objective_syllabus_id: str
    compared_syllabus_id: str
    global_score: float
    objective_coverage: float
    compared_coverage: float
    model_version: str
    created_at: datetime
    matches: List[ContentMatch] = field(default_factory=list)
    unmatched_objective: List[UnmatchedItem] = field(default_factory=list)
    unmatched_compared: List[UnmatchedItem] = field(default_factory=list)

    @property
    def total_matches(self) -> int:
        return len(self.matches)

    @property
    def count_by_classification(self) -> Dict[str, int]:
        counts: Dict[str, int] = {cat.value: 0 for cat in MatchClassification}
        for match in self.matches:
            counts[match.classification.value] += 1
        return counts

    def is_acceptable_pre_evaluation(self, threshold_percentage: float = 70.0) -> bool:
        """Determina si la pre-evaluación supera el umbral de correspondencia configurado."""
        return self.global_score >= (threshold_percentage / 100.0)
