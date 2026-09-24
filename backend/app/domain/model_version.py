"""
Entidades de dominio para Versionado de Algoritmos/Modelos e Informes Formales.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class ReportFormat(str, Enum):
    HTML = "HTML"
    PDF = "PDF"


@dataclass(frozen=True)
class ModelVersion:
    """Representa una configuración o versión de algoritmo registrada para reproducibilidad."""
    version_id: str  # Ej: "baseline-001"
    algorithm_name: str  # Ej: "Hybrid-TfIdf-SentenceTransformer"
    description: str
    parameters: Dict[str, Any]  # Pesos de features, modelos base, etc.
    thresholds: Dict[str, float]  # Umbrales para MATCH, PARTIAL_MATCH, UNCERTAIN
    is_active: bool
    created_at: datetime


@dataclass
class Report:
    """Entidad que registra un informe formal generado, evitando recálculos innecesarios."""
    report_id: str
    comparison_id: str
    report_format: ReportFormat
    report_version: str
    file_path: str
    generated_at: datetime
    model_version: str
    file_size_bytes: int = 0
