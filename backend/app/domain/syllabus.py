"""
Entidades de dominio para Sílabos y Estructura de Documentos.
Libre de dependencias de frameworks externos o librerías de infraestructura.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional


class SectionType(str, Enum):
    """Tipos canónicos de sección identificables en un sílabo universitario."""
    GENERAL_DATA = "GENERAL_DATA"
    SUMILLA = "SUMILLA"
    COMPETENCIES = "COMPETENCIES"
    LEARNING_OUTCOMES = "LEARNING_OUTCOMES"
    UNIT = "UNIT"
    METHODOLOGY = "METHODOLOGY"
    EVALUATION = "EVALUATION"
    BIBLIOGRAPHY = "BIBLIOGRAPHY"
    OTHER = "OTHER"


@dataclass(frozen=True)
class SyllabusPage:
    """Representa una página física del documento PDF extraído."""
    page_number: int  # 1-indexed
    raw_text: str
    character_count: int

    def __post_init__(self) -> None:
        if self.page_number < 1:
            raise ValueError("El número de página debe ser mayor o igual a 1.")


@dataclass(frozen=True)
class SyllabusSection:
    """Sección académica detectada en el sílabo."""
    id: str
    syllabus_id: str
    title: str
    section_type: SectionType
    order: int
    page_start: int
    page_end: int


@dataclass
class Syllabus:
    """Entidad principal que representa un sílabo cargado en el sistema."""
    id: str
    filename: str
    file_path: str
    file_size_bytes: int
    sha256_hash: str
    total_pages: int
    created_at: datetime
    university: Optional[str] = None
    course_name: Optional[str] = None
    course_code: Optional[str] = None
    academic_term: Optional[str] = None
    pages: List[SyllabusPage] = field(default_factory=list)
    sections: List[SyllabusSection] = field(default_factory=list)

    @property
    def full_extracted_text(self) -> str:
        """Concatena el texto de todas las páginas preservando saltos."""
        return "\n\n".join(page.raw_text for page in sorted(self.pages, key=lambda p: p.page_number))

    @property
    def total_characters(self) -> int:
        return sum(page.character_count for page in self.pages)

    def is_digitally_readable(self, min_characters: int = 150) -> bool:
        """Verifica si el documento tiene suficiente texto extraíble sin requerir OCR."""
        return self.total_characters >= min_characters
