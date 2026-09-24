"""
Entidades de dominio para Contenidos de Aprendizaje e Ítems Temáticos.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ContentItem:
    """
    Representa una unidad atómica o desagregada de contenido temático dentro de un sílabo.
    Permite comparar temas puntuales y mantener trazabilidad con la página física.
    """
    id: str  # Ej: OBJ-CONT-001 o CMP-CONT-014
    syllabus_id: str
    section_name: str  # Ej: "Unidad I: Álgebra Relacional"
    title: str  # Ej: "Operadores relacionales y proyecciones"
    text: str  # Texto descriptivo original del contenido
    normalized_text: str  # Texto normalizado para cómputo léxico
    page_start: int
    page_end: int
    order: int
    unit_number: Optional[int] = None

    def __post_init__(self) -> None:
        if not self.title.strip() and not self.text.strip():
            raise ValueError("Un ContentItem no puede tener título y texto vacíos simultáneamente.")
        if self.page_start < 1 or self.page_end < self.page_start:
            raise ValueError("Rango de páginas inválido para el ContentItem.")

    @property
    def display_label(self) -> str:
        """Etiqueta legible para vistas e informes."""
        if self.title:
            return f"[{self.section_name}] {self.title}"
        return f"[{self.section_name}] {self.text[:60]}..."
