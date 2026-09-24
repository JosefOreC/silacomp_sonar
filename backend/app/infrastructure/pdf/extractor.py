"""
Adaptador de extracción de texto y páginas para documentos PDF utilizando PyMuPDF.
Implementa el puerto ISyllabusExtractor.
"""

from datetime import datetime
import hashlib
import os
from typing import List, Optional
import pymupdf as fitz  # PyMuPDF

from app.domain.exceptions import InsufficientDigitalTextError, PdfCorruptedError, PdfValidationError
from app.domain.ports import ISyllabusExtractor
from app.domain.syllabus import Syllabus, SyllabusPage


class PyMuPdfExtractor(ISyllabusExtractor):
    """Adaptador de infraestructura que utiliza PyMuPDF para extraer texto digital estructurado."""

    def __init__(self, min_digital_characters: int = 150, max_file_size_bytes: int = 20 * 1024 * 1024) -> None:
        self.min_digital_characters = min_digital_characters
        self.max_file_size_bytes = max_file_size_bytes

    def extract_from_pdf(
        self,
        file_path: str,
        syllabus_id: str,
        filename: str,
        university: Optional[str] = None,
        course_name: Optional[str] = None,
        course_code: Optional[str] = None,
    ) -> Syllabus:
        """
        Lee el archivo PDF, valida su integridad y extrae el texto por página.
        Lanza InsufficientDigitalTextError si el documento no tiene capa de texto digital.
        """
        if not os.path.exists(file_path):
            raise PdfValidationError(f"El archivo especificado no existe: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise PdfValidationError("El archivo PDF está vacío (0 bytes).")

        if file_size > self.max_file_size_bytes:
            raise PdfValidationError(f"El archivo excede el tamaño máximo permitido ({self.max_file_size_bytes // (1024*1024)} MB).")

        # Calcular SHA-256
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)
        sha256_hash = hasher.hexdigest()

        # Abrir con PyMuPDF
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise PdfCorruptedError(f"No fue posible abrir el archivo PDF. Archivo corrupto o protegido: {e}") from e

        total_pages = len(doc)
        if total_pages == 0:
            doc.close()
            raise PdfValidationError("El documento PDF no contiene páginas.")

        pages: List[SyllabusPage] = []
        total_extracted_characters = 0

        try:
            for page_index in range(total_pages):
                page = doc[page_index]
                text = page.get_text("text") or ""
                # Limpiar texto de página
                cleaned_text = text.strip()
                char_count = len(cleaned_text)
                total_extracted_characters += char_count

                pages.append(
                    SyllabusPage(
                        page_number=page_index + 1,
                        raw_text=cleaned_text,
                        character_count=char_count,
                    )
                )
        finally:
            doc.close()

        # Validar si el texto digital es suficiente
        if total_extracted_characters < self.min_digital_characters:
            raise InsufficientDigitalTextError(
                f"No se pudo extraer suficiente texto digital del documento ({total_extracted_characters} caracteres detectados). "
                "El archivo parece ser un documento escaneado sin capa OCR. "
                "El soporte para OCR estará disponible en la Fase 2."
            )

        return Syllabus(
            id=syllabus_id,
            filename=filename,
            file_path=file_path,
            file_size_bytes=file_size,
            sha256_hash=sha256_hash,
            total_pages=total_pages,
            created_at=datetime.now(),
            university=university,
            course_name=course_name,
            course_code=course_code,
            pages=pages,
        )
