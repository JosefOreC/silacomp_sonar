"""
Adaptador de extracción de texto y páginas para documentos PDF utilizando PyMuPDF.
Implementa el puerto ISyllabusExtractor.
"""

from datetime import datetime
import hashlib
import os
import shutil
import tempfile
from typing import List, Optional, Tuple
import pymupdf as fitz  # PyMuPDF

from app.domain.exceptions import InsufficientDigitalTextError, PdfCorruptedError, PdfValidationError
from app.domain.ports import IOCREngine, ISyllabusExtractor, OCRTextBlock
from app.domain.syllabus import Syllabus, SyllabusPage


class PyMuPdfExtractor(ISyllabusExtractor):
    """Adaptador de infraestructura que utiliza PyMuPDF para extraer texto digital estructurado con fallback de OCR."""

    def __init__(
        self,
        min_digital_characters: int = 150,
        max_file_size_bytes: int = 20 * 1024 * 1024,
        ocr_engine: Optional[IOCREngine] = None,
    ) -> None:
        self.min_digital_characters = min_digital_characters
        self.max_file_size_bytes = max_file_size_bytes
        self.ocr_engine = ocr_engine

    def _inject_ocr_layer(
        self,
        file_path: str,
        page_blocks: List[List[OCRTextBlock]],
    ) -> None:
        """Inyecta una capa de texto invisible (render_mode=3) en el PDF para permitir búsqueda espacial nativa."""
        doc = fitz.open(file_path)
        try:
            for page_idx, blocks in enumerate(page_blocks):
                if page_idx >= len(doc):
                    break
                page = doc[page_idx]
                for b in blocks:
                    h = b.y1 - b.y0
                    fontsize = max(8.0, min(h, 24.0))
                    # render_mode 3: texto no visible, pero indexable y seleccionable
                    page.insert_text(
                        (b.x0, max(b.y1 - 1.0, b.y0 + fontsize)),
                        b.text,
                        fontsize=fontsize,
                        render_mode=3,
                    )
            # Intentar guardar de forma incremental; si falla, guardar mediante archivo temporal
            try:
                doc.saveIncr()
            except Exception:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                    tmp_path = tmp_file.name
                doc.save(tmp_path)
                doc.close()
                shutil.move(tmp_path, file_path)
                return
        finally:
            if not doc.is_closed:
                doc.close()

    def extract_from_pdf(
        self,
        file_path: str,
        syllabus_id: str,
        filename: str,
        university: Optional[str] = None,
        course_name: Optional[str] = None,
        course_code: Optional[str] = None,
        enable_ocr: bool = True,
    ) -> Syllabus:
        """
        Lee el archivo PDF, valida su integridad y extrae el texto por página.
        Si el documento es escaneado y enable_ocr=True, ejecuta OCR neuronal con RapidOCR.
        """
        if not os.path.exists(file_path):
            raise PdfValidationError(f"El archivo especificado no existe: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise PdfValidationError("El archivo PDF está vacío (0 bytes).")

        if file_size > self.max_file_size_bytes:
            raise PdfValidationError(f"El archivo excede el tamaño máximo permitido ({self.max_file_size_bytes // (1024*1024)} MB).")

        # Calcular SHA-256 inicial
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
                cleaned_text = text.strip()
                char_count = len(cleaned_text)
                total_extracted_characters += char_count

                rect = page.rect
                pages.append(
                    SyllabusPage(
                        page_number=page_index + 1,
                        raw_text=cleaned_text,
                        character_count=char_count,
                        page_width=float(rect.width),
                        page_height=float(rect.height),
                        is_ocr=False,
                    )
                )
        finally:
            doc.close()

        is_scanned = False
        ocr_applied = False
        ocr_engine_name: Optional[str] = None

        # Si el texto digital nativo es insuficiente, evaluar fallback de OCR
        if total_extracted_characters < self.min_digital_characters:
            if self.ocr_engine is not None and enable_ocr:
                ocr_pages: List[SyllabusPage] = []
                all_page_blocks: List[List[OCRTextBlock]] = []
                total_ocr_characters = 0

                for page_idx in range(total_pages):
                    page_num = page_idx + 1
                    ocr_text, blocks, pw, ph = self.ocr_engine.extract_page_ocr(file_path, page_num)
                    cleaned_ocr_text = ocr_text.strip()
                    char_count = len(cleaned_ocr_text)
                    total_ocr_characters += char_count
                    all_page_blocks.append(blocks)

                    ocr_pages.append(
                        SyllabusPage(
                            page_number=page_num,
                            raw_text=cleaned_ocr_text,
                            character_count=char_count,
                            page_width=pw,
                            page_height=ph,
                            is_ocr=True,
                        )
                    )

                if total_ocr_characters >= self.min_digital_characters:
                    # Inyectar capa de texto invisible para soporte continuo del visor y búsqueda espacial
                    self._inject_ocr_layer(file_path, all_page_blocks)
                    pages = ocr_pages
                    is_scanned = True
                    ocr_applied = True
                    ocr_engine_name = type(self.ocr_engine).__name__
                    total_extracted_characters = total_ocr_characters
                else:
                    raise InsufficientDigitalTextError(
                        f"No se pudo extraer suficiente texto legible del documento escaneado ({total_ocr_characters} caracteres detectados con OCR). "
                        "El archivo parece ser un documento escaneado sin capa OCR suficiente o con páginas en blanco."
                    )
            else:
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
            is_scanned=is_scanned,
            ocr_applied=ocr_applied,
            ocr_engine_name=ocr_engine_name,
        )
