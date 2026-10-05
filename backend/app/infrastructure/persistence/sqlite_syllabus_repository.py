"""
Repositorio SQLite para Sílabos, Páginas y Contenidos.
Implementa el puerto ISyllabusRepository.
"""

from datetime import datetime
from typing import List, Optional
from app.domain.content import ContentItem
from app.domain.ports import ISyllabusRepository
from app.domain.syllabus import SectionType, Syllabus, SyllabusPage, SyllabusSection
from app.infrastructure.persistence.database import DatabaseManager


class SqliteSyllabusRepository(ISyllabusRepository):
    """Implementación de persistencia para sílabos y páginas sobre SQLite."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def save(self, syllabus: Syllabus) -> None:
        """Guarda o actualiza un sílabo, sus páginas y secciones de forma transaccional."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO syllabi (
                    id, filename, file_path, file_size_bytes, sha256_hash,
                    total_pages, university, course_name, course_code,
                    academic_term, created_at, is_scanned, ocr_applied, ocr_engine_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    filename = excluded.filename,
                    university = excluded.university,
                    course_name = excluded.course_name,
                    course_code = excluded.course_code,
                    academic_term = excluded.academic_term,
                    is_scanned = excluded.is_scanned,
                    ocr_applied = excluded.ocr_applied,
                    ocr_engine_name = excluded.ocr_engine_name;
                """,
                (
                    syllabus.id,
                    syllabus.filename,
                    syllabus.file_path,
                    syllabus.file_size_bytes,
                    syllabus.sha256_hash,
                    syllabus.total_pages,
                    syllabus.university,
                    syllabus.course_name,
                    syllabus.course_code,
                    syllabus.academic_term,
                    syllabus.created_at.isoformat(),
                    1 if syllabus.is_scanned else 0,
                    1 if syllabus.ocr_applied else 0,
                    syllabus.ocr_engine_name,
                ),
            )

            # Guardar páginas
            if syllabus.pages:
                cursor.execute("DELETE FROM syllabus_pages WHERE syllabus_id = ?;", (syllabus.id,))
                for page in syllabus.pages:
                    cursor.execute(
                        """
                        INSERT INTO syllabus_pages (syllabus_id, page_number, raw_text, character_count)
                        VALUES (?, ?, ?, ?);
                        """,
                        (syllabus.id, page.page_number, page.raw_text, page.character_count),
                    )

            # Guardar secciones
            if syllabus.sections:
                cursor.execute("DELETE FROM syllabus_sections WHERE syllabus_id = ?;", (syllabus.id,))
                for sec in syllabus.sections:
                    cursor.execute(
                        """
                        INSERT INTO syllabus_sections (id, syllabus_id, title, section_type, order_num, page_start, page_end)
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                        """,
                        (sec.id, sec.syllabus_id, sec.title, sec.section_type.value, sec.order, sec.page_start, sec.page_end),
                    )

            conn.commit()

    def get_by_id(self, syllabus_id: str) -> Optional[Syllabus]:
        """Recupera un sílabo completo por ID con sus páginas y secciones."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM syllabi WHERE id = ?;", (syllabus_id,))
            row = cursor.fetchone()
            if not row:
                return None

            cursor.execute("SELECT * FROM syllabus_pages WHERE syllabus_id = ? ORDER BY page_number ASC;", (syllabus_id,))
            page_rows = cursor.fetchall()
            pages = [
                SyllabusPage(
                    page_number=p["page_number"],
                    raw_text=p["raw_text"],
                    character_count=p["character_count"],
                )
                for p in page_rows
            ]

            cursor.execute("SELECT * FROM syllabus_sections WHERE syllabus_id = ? ORDER BY order_num ASC;", (syllabus_id,))
            sec_rows = cursor.fetchall()
            sections = [
                SyllabusSection(
                    id=s["id"],
                    syllabus_id=s["syllabus_id"],
                    title=s["title"],
                    section_type=SectionType(s["section_type"]),
                    order=s["order_num"],
                    page_start=s["page_start"],
                    page_end=s["page_end"],
                )
                for s in sec_rows
            ]

            return Syllabus(
                id=row["id"],
                filename=row["filename"],
                file_path=row["file_path"],
                file_size_bytes=row["file_size_bytes"],
                sha256_hash=row["sha256_hash"],
                total_pages=row["total_pages"],
                created_at=datetime.fromisoformat(row["created_at"]),
                university=row["university"],
                course_name=row["course_name"],
                course_code=row["course_code"],
                academic_term=row["academic_term"],
                pages=pages,
                sections=sections,
                is_scanned=bool(row["is_scanned"]) if "is_scanned" in row.keys() else False,
                ocr_applied=bool(row["ocr_applied"]) if "ocr_applied" in row.keys() else False,
                ocr_engine_name=row["ocr_engine_name"] if "ocr_engine_name" in row.keys() else None,
            )

    def list_all(self) -> List[Syllabus]:
        """Retorna la lista de todos los sílabos registrados."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM syllabi ORDER BY created_at DESC;")
            rows = cursor.fetchall()
            return [
                Syllabus(
                    id=r["id"],
                    filename=r["filename"],
                    file_path=r["file_path"],
                    file_size_bytes=r["file_size_bytes"],
                    sha256_hash=r["sha256_hash"],
                    total_pages=r["total_pages"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                    university=r["university"],
                    course_name=r["course_name"],
                    course_code=r["course_code"],
                    academic_term=r["academic_term"],
                    is_scanned=bool(r["is_scanned"]) if "is_scanned" in r.keys() else False,
                    ocr_applied=bool(r["ocr_applied"]) if "ocr_applied" in r.keys() else False,
                    ocr_engine_name=r["ocr_engine_name"] if "ocr_engine_name" in r.keys() else None,
                )
                for r in rows
            ]

    def save_content_items(self, items: List[ContentItem]) -> None:
        """Persiste los ítems de contenido temáticos segmentados de un sílabo."""
        if not items:
            return
        syllabus_id = items[0].syllabus_id
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM content_items WHERE syllabus_id = ?;", (syllabus_id,))
            for it in items:
                cursor.execute(
                    """
                    INSERT INTO content_items (
                        id, syllabus_id, section_name, title, text,
                        normalized_text, page_start, page_end, order_num, unit_number
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        it.id,
                        it.syllabus_id,
                        it.section_name,
                        it.title,
                        it.text,
                        it.normalized_text,
                        it.page_start,
                        it.page_end,
                        it.order,
                        it.unit_number,
                    ),
                )
            conn.commit()

    def get_content_items(self, syllabus_id: str) -> List[ContentItem]:
        """Obtiene los ítems de contenido temáticos de un sílabo ordenados."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM content_items WHERE syllabus_id = ? ORDER BY order_num ASC;", (syllabus_id,))
            rows = cursor.fetchall()
            return [
                ContentItem(
                    id=r["id"],
                    syllabus_id=r["syllabus_id"],
                    section_name=r["section_name"],
                    title=r["title"],
                    text=r["text"],
                    normalized_text=r["normalized_text"],
                    page_start=r["page_start"],
                    page_end=r["page_end"],
                    order=r["order_num"],
                    unit_number=r["unit_number"],
                )
                for r in rows
            ]
