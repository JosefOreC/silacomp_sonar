"""
Caso de uso para el procesamiento, extracción y segmentación de un sílabo PDF.
"""

from typing import List, Optional
from app.domain.content import ContentItem
from app.domain.ports import ISegmentationService, ISyllabusExtractor, ISyllabusRepository
from app.domain.syllabus import Syllabus


class ProcessSyllabusUseCase:
    """Orquesta la extracción de páginas PDF, detección de estructura y segmentación temática."""

    def __init__(
        self,
        extractor: ISyllabusExtractor,
        segmenter: ISegmentationService,
        repository: Optional[ISyllabusRepository] = None,
    ) -> None:
        self.extractor = extractor
        self.segmenter = segmenter
        self.repository = repository

    def execute(
        self,
        file_path: str,
        syllabus_id: str,
        filename: str,
        university: Optional[str] = None,
        course_name: Optional[str] = None,
        course_code: Optional[str] = None,
        enable_ocr: bool = True,
    ) -> tuple[Syllabus, List[ContentItem]]:
        """
        Ejecuta el flujo completo de ingesta:
        1. Extracción con PyMuPDF (con soporte para OCR en Fase 2).
        2. Detección heurística de estructura y secciones.
        3. Segmentación en ítems temáticos discretos con normalización.
        4. Persistencia en repositorio si está configurado.
        """
        # Extracción y validación digital
        syllabus = self.extractor.extract_from_pdf(
            file_path=file_path,
            syllabus_id=syllabus_id,
            filename=filename,
            enable_ocr=enable_ocr,
        )
        if university:
            syllabus.university = university
        if course_name:
            syllabus.course_name = course_name
        if course_code:
            syllabus.course_code = course_code

        # Segmentación
        items = self.segmenter.segment(syllabus)

        # Persistir si existe repositorio
        if self.repository:
            self.repository.save(syllabus)

        return syllabus, items
