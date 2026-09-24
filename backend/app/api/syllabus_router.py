"""
Router de API para gestión, carga y extracción de Sílabos.
"""

import os
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.deps import (
    get_syllabus_extractor,
    get_syllabus_repository,
    get_syllabus_segmenter,
)
from app.api.schemas import ContentItemResponse, SyllabusResponse
from app.application.process_syllabus import ProcessSyllabusUseCase
from app.domain.exceptions import InsufficientDigitalTextError, PdfCorruptedError, PdfValidationError
from app.infrastructure.nlp.segmenter import SyllabusSegmenter
from app.infrastructure.pdf.extractor import PyMuPdfExtractor
from app.infrastructure.persistence.sqlite_syllabus_repository import SqliteSyllabusRepository

router = APIRouter(prefix="/syllabi", tags=["Sílabos"])


@router.post("/upload", response_model=SyllabusResponse, status_code=status.HTTP_201_CREATED)
async def upload_syllabus(
    file: UploadFile = File(...),
    university: Optional[str] = Form(None),
    course_name: Optional[str] = Form(None),
    course_code: Optional[str] = Form(None),
    extractor: PyMuPdfExtractor = Depends(get_syllabus_extractor),
    segmenter: SyllabusSegmenter = Depends(get_syllabus_segmenter),
    repo: SqliteSyllabusRepository = Depends(get_syllabus_repository),
) -> SyllabusResponse:
    """
    Recibe un documento de sílabo en formato PDF, valida su legibilidad digital,
    extrae el texto conservando trazabilidad de páginas y segmenta sus contenidos.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se admiten documentos en formato PDF (.pdf).",
        )

    # Directorio de subida seguro
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    syllabus_id = f"SYL-{uuid.uuid4().hex[:10].upper()}"
    saved_filename = f"{syllabus_id}_{file.filename}"
    file_path = os.path.join(upload_dir, saved_filename)

    try:
        content_bytes = await file.read()
        if len(content_bytes) == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo subido está vacío (0 bytes).")

        with open(file_path, "wb") as f:
            f.write(content_bytes)

        use_case = ProcessSyllabusUseCase(extractor=extractor, segmenter=segmenter, repository=repo)
        syllabus, items = use_case.execute(
            file_path=file_path,
            syllabus_id=syllabus_id,
            filename=file.filename,
            university=university,
            course_name=course_name,
            course_code=course_code,
        )

        # Persistir los ítems segmentados
        repo.save_content_items(items)

        return SyllabusResponse(
            id=syllabus.id,
            filename=syllabus.filename,
            total_pages=syllabus.total_pages,
            file_size_bytes=syllabus.file_size_bytes,
            sha256_hash=syllabus.sha256_hash,
            university=syllabus.university,
            course_name=syllabus.course_name,
            course_code=syllabus.course_code,
            total_characters=syllabus.total_characters,
            created_at=syllabus.created_at,
        )

    except InsufficientDigitalTextError as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except (PdfValidationError, PdfCorruptedError) as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error inesperado al procesar PDF: {e}")


@router.get("", response_model=List[SyllabusResponse])
def list_syllabi(repo: SqliteSyllabusRepository = Depends(get_syllabus_repository)) -> List[SyllabusResponse]:
    """Lista todos los sílabos cargados en el sistema."""
    syllabi = repo.list_all()
    return [
        SyllabusResponse(
            id=s.id,
            filename=s.filename,
            total_pages=s.total_pages,
            file_size_bytes=s.file_size_bytes,
            sha256_hash=s.sha256_hash,
            university=s.university,
            course_name=s.course_name,
            course_code=s.course_code,
            total_characters=s.total_characters,
            created_at=s.created_at,
        )
        for s in syllabi
    ]


@router.get("/{syllabus_id}", response_model=SyllabusResponse)
def get_syllabus(syllabus_id: str, repo: SqliteSyllabusRepository = Depends(get_syllabus_repository)) -> SyllabusResponse:
    """Obtiene los detalles de un sílabo por ID."""
    s = repo.get_by_id(syllabus_id)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sílabo no encontrado.")
    return SyllabusResponse(
        id=s.id,
        filename=s.filename,
        total_pages=s.total_pages,
        file_size_bytes=s.file_size_bytes,
        sha256_hash=s.sha256_hash,
        university=s.university,
        course_name=s.course_name,
        course_code=s.course_code,
        total_characters=s.total_characters,
        created_at=s.created_at,
    )


@router.get("/{syllabus_id}/items", response_model=List[ContentItemResponse])
def get_syllabus_items(syllabus_id: str, repo: SqliteSyllabusRepository = Depends(get_syllabus_repository)) -> List[ContentItemResponse]:
    """Obtiene los contenidos temáticos segmentados de un sílabo."""
    s = repo.get_by_id(syllabus_id)
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sílabo no encontrado.")
    items = repo.get_content_items(syllabus_id)
    return [
        ContentItemResponse(
            id=it.id,
            syllabus_id=it.syllabus_id,
            section_name=it.section_name,
            title=it.title,
            text=it.text,
            page_start=it.page_start,
            page_end=it.page_end,
            order=it.order,
            unit_number=it.unit_number,
        )
        for it in items
    ]
