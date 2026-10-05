"""
Puertos e Interfaces Abstractas del Dominio (Clean Architecture).
Define los contratos que debe implementar la capa de infraestructura.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from app.domain.syllabus import Syllabus
from app.domain.content import ContentItem
from app.domain.comparison import Comparison, ContentMatch, ScoreBreakdown, MatchEvidence
from app.domain.review import Review, DatasetExample
from app.domain.model_version import ModelVersion, Report, ReportFormat


@dataclass(frozen=True)
class OCRTextBlock:
    """Bloque de texto reconocido por OCR con coordenadas normalizadas en puntos tipográficos (72 DPI)."""
    text: str
    confidence: float
    x0: float
    y0: float
    x1: float
    y1: float


class IOCREngine(ABC):
    """Puerto para motores de reconocimiento óptico de caracteres (OCR)."""

    @abstractmethod
    def extract_page_ocr(self, pdf_path: str, page_number: int, dpi: int = 150) -> Tuple[str, List[OCRTextBlock], float, float]:
        """
        Ejecuta OCR sobre una página de un documento PDF.
        Retorna:
          (texto_completo, lista_bloques_con_coords_72dpi, page_width_pt, page_height_pt)
        """
        pass


class ISyllabusExtractor(ABC):
    """Puerto para extractores de texto de documentos PDF."""

    @abstractmethod
    def extract_from_pdf(self, file_path: str, syllabus_id: str, filename: str, enable_ocr: bool = True) -> Syllabus:
        """Extrae el contenido textual y las páginas de un archivo PDF."""
        pass


class ISegmentationService(ABC):
    """Puerto para segmentación y estructuración de sílabos en contenidos discretos."""

    @abstractmethod
    def segment(self, syllabus: Syllabus) -> List[ContentItem]:
        """Identifica secciones canónicas y descompone las unidades en ítems temáticos."""
        pass


class INlpVectorService(ABC):
    """Puerto para servicios de similitud léxica, semántica y cálculo de características."""

    @abstractmethod
    def compute_lexical_similarity(self, text_a: str, text_b: str) -> float:
        """Calcula la similitud léxica (TF-IDF + Coseno)."""
        pass

    @abstractmethod
    def compute_semantic_similarity(self, text_a: str, text_b: str) -> float:
        """Calcula la similitud semántica (Embeddings densos + Coseno)."""
        pass

    @abstractmethod
    def extract_shared_keywords(self, text_a: str, text_b: str) -> List[str]:
        """Extrae palabras clave y términos técnicos compartidos."""
        pass


class ISyllabusRepository(ABC):
    """Puerto para persistencia y consulta de sílabos."""

    @abstractmethod
    def save(self, syllabus: Syllabus) -> None:
        pass

    @abstractmethod
    def get_by_id(self, syllabus_id: str) -> Optional[Syllabus]:
        pass

    @abstractmethod
    def list_all(self) -> List[Syllabus]:
        pass


class IComparisonRepository(ABC):
    """Puerto para persistencia y consulta de comparaciones y correspondencias."""

    @abstractmethod
    def save(self, comparison: Comparison) -> None:
        pass

    @abstractmethod
    def get_by_id(self, comparison_id: str) -> Optional[Comparison]:
        pass

    @abstractmethod
    def list_all(self) -> List[Comparison]:
        pass


class IReviewRepository(ABC):
    """Puerto para registro y consulta de revisiones humanas."""

    @abstractmethod
    def save(self, review: Review) -> None:
        pass

    @abstractmethod
    def get_by_comparison_id(self, comparison_id: str) -> List[Review]:
        pass

    @abstractmethod
    def get_by_id(self, review_id: str) -> Optional[Review]:
        pass


class IDatasetRepository(ABC):
    """Puerto para gestión del dataset científico de observaciones."""

    @abstractmethod
    def save_example(self, example: DatasetExample) -> None:
        pass

    @abstractmethod
    def count_examples(self) -> int:
        pass

    @abstractmethod
    def list_examples(self, limit: int = 100, offset: int = 0) -> List[DatasetExample]:
        pass


class IReportGenerator(ABC):
    """Puerto para generación de informes formales descargables."""

    @abstractmethod
    def generate(self, comparison: Comparison, obj_syllabus: Syllabus, cmp_syllabus: Syllabus, report_format: ReportFormat) -> Report:
        pass


class IModelVersionRepository(ABC):
    """Puerto para persistencia y gestión de ciclo de vida de versiones de modelos de ML."""

    @abstractmethod
    def save(self, model_version: ModelVersion) -> None:
        pass

    @abstractmethod
    def get_by_id(self, version_id: str) -> Optional[ModelVersion]:
        pass

    @abstractmethod
    def get_active_model(self) -> Optional[ModelVersion]:
        pass

    @abstractmethod
    def set_active_model(self, version_id: str) -> bool:
        pass

    @abstractmethod
    def list_all(self) -> List[ModelVersion]:
        pass


class ISupervisedModelTrainer(ABC):
    """Puerto para entrenamiento, calibración y evaluación de modelos supervisados."""

    @abstractmethod
    def train_and_evaluate(
        self,
        examples: List[DatasetExample],
        algorithm: str = "calibrated_logistic",
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Tuple[ModelVersion, Dict[str, Any]]:
        """
        Entrena el modelo sobre los ejemplos, evalúa métricas vs baseline y retorna la versión registrada con su reporte de métricas.
        """
        pass
