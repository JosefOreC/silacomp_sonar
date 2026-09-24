"""
Entidades de dominio para el ciclo de revisión humana inmutable y dataset staging.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from app.domain.comparison import MatchClassification


class CorrectionType(str, Enum):
    """Categorización analítica de la corrección realizada por el evaluador humano."""
    CONFIRMED = "CONFIRMED"                                # La predicción de la IA fue corroborada
    FALSE_POSITIVE = "FALSE_POSITIVE"                      # La IA asignó MATCH pero no hay relación
    FALSE_NEGATIVE = "FALSE_NEGATIVE"                      # La IA ignoró un par que sí tiene relación
    OVERESTIMATION = "OVERESTIMATION"                      # Ej. IA predijo MATCH y correspondía PARTIAL_MATCH
    UNDERESTIMATION = "UNDERESTIMATION"                    # Ej. IA predijo PARTIAL_MATCH y correspondía MATCH
    MANUAL_LINK = "MANUAL_LINK"                            # El usuario vinculó manualmente dos contenidos no emparejados


@dataclass
class Review:
    """
    Representa una validación o corrección humana sobre una correspondencia.
    REGLA: Nunca sobrescribe la predicción original de la IA en ContentMatch.
    """
    id: str
    comparison_id: str
    match_id: Optional[str]  # Puede ser None si es un enlace manual nuevo
    prediction_before: Optional[MatchClassification]
    human_decision: MatchClassification
    correction_type: CorrectionType
    justification: str
    reviewer_id: str
    model_version: str
    created_at: datetime
    manual_objective_item_id: Optional[str] = None
    manual_compared_item_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.justification.strip():
            raise ValueError("Toda decisión o corrección humana debe incluir una justificación académica mínima.")


@dataclass
class DatasetExample:
    """
    Observación estructurada para entrenamiento y evaluación supervisada (Fase 2).
    Generada a partir de validaciones humanas consolidadas.
    """
    id: str
    review_id: str
    objective_item_id: str
    compared_item_id: str
    objective_text: str
    compared_text: str
    features: Dict[str, float] = field(default_factory=dict)
    prediction_label: str = ""
    ground_truth_label: str = ""
    model_version: str = ""
    source_university_obj: Optional[str] = None
    source_university_cmp: Optional[str] = None
    created_at: Optional[datetime] = None
