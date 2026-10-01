"""
Script de resincronización y actualización integral de sílabos y comparaciones en convcomp.db.
Re-segmenta documentos PDF existentes con el segmentador avanzado y re-ejecuta
las comparaciones previas aplicando el motor de afinidad temática multi-escala.
"""

import os
import sys
import sqlite3
import json

# Asegurar path de backend
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, backend_dir)

from app.infrastructure.pdf.extractor import PyMuPdfExtractor
from app.infrastructure.nlp.segmenter import SyllabusSegmenter
from app.infrastructure.nlp.vector_service import NlpVectorService
from app.infrastructure.pdf.spatial_locator import SpatialLocatorService
from app.application.compare_syllabi import CompareSyllabiUseCase
from app.domain.content import ContentItem

DB_PATH = os.path.join(backend_dir, "data", "convcomp.db")


def resync_all():
    print(f"Iniciando resincronización sobre BD: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print(f"Error: La base de datos no existe en {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    extractor = PyMuPdfExtractor()
    segmenter = SyllabusSegmenter()
    vector_service = NlpVectorService()
    locator = SpatialLocatorService()
    use_case = CompareSyllabiUseCase(vector_service, None, locator)

    # 1. Obtener todos los sílabos
    cursor.execute("SELECT id, course_name, university, course_code, file_path, filename FROM syllabi")
    syllabi_rows = cursor.fetchall()
    print(f"Total de sílabos registrados: {len(syllabi_rows)}")

    syllabi_items_map = {}

    for sid, cname, univ, ccode, fpath, fname in syllabi_rows:
        if not fpath or not os.path.exists(fpath):
            print(f"  [OMITIDO] Sílabo {sid} ({cname}) - Archivo no encontrado: {fpath}")
            continue

        print(f"  [RE-SEGMENTANDO] {sid} | {cname} ({univ})...")
        try:
            doc = extractor.extract_from_pdf(
                file_path=fpath,
                syllabus_id=sid,
                filename=fname or "syllabus.pdf",
                university=univ,
                course_name=cname,
                course_code=ccode,
            )
            items = segmenter.segment(doc)
            syllabi_items_map[sid] = (items, fpath)

            # Reemplazar content_items en base de datos
            cursor.execute("DELETE FROM content_items WHERE syllabus_id = ?", (sid,))
            for it in items:
                cursor.execute(
                    """
                    INSERT INTO content_items (id, syllabus_id, section_name, title, text, normalized_text, page_start, page_end, order_num, unit_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            print(f"    -> Guardados {len(items)} ítems limpios para {sid}")
        except Exception as e:
            print(f"    -> Error procesando {sid}: {e}")

    # 2. Re-ejecutar comparaciones existentes (priorizando activas de redes y ordenadas por created_at DESC)
    cursor.execute("""
        SELECT id, objective_syllabus_id, compared_syllabus_id 
        FROM comparisons 
        WHERE objective_syllabus_id = 'SYL-EA2CE0F95B' 
           OR compared_syllabus_id = 'SYL-E33C810E99'
           OR id IN ('COMP-5EBC9F1F68DF', 'COMP-B7809E5AA543', 'COMP-45542224779D')
        ORDER BY created_at DESC
    """)
    comp_rows = cursor.fetchall()
    print(f"\nComparaciones prioritarias a actualizar: {len(comp_rows)}")

    from app.infrastructure.persistence.sqlite_comparison_repository import SqliteComparisonRepository
    from app.infrastructure.persistence.database import DatabaseManager

    comp_repo = SqliteComparisonRepository(DatabaseManager(DB_PATH))

    for cid, obj_id, cmp_id in comp_rows:
        if obj_id not in syllabi_items_map or cmp_id not in syllabi_items_map:
            print(f"  [OMITIDO] Comparación {cid}: ítems no disponibles para {obj_id} o {cmp_id}")
            continue

        obj_items, obj_path = syllabi_items_map[obj_id]
        cmp_items, cmp_path = syllabi_items_map[cmp_id]

        print(f"  [RE-COMPARANDO] {cid}: {obj_id} vs {cmp_id}...")
        try:
            comp_res = use_case.execute(
                objective_syllabus_id=obj_id,
                compared_syllabus_id=cmp_id,
                objective_items=obj_items,
                compared_items=cmp_items,
                objective_pdf_path=obj_path,
                compared_pdf_path=cmp_path,
            )

            # Conservar el ID original de la comparación en BD
            from dataclasses import replace
            updated_matches = [replace(m, comparison_id=cid) for m in comp_res.matches]
            comp_res = replace(comp_res, id=cid, matches=updated_matches)

            # Guardar con el repositorio oficial
            comp_repo.save(comp_res)
            print(f"    -> Actualizado {cid}: Score={comp_res.global_score:.4f} | ObjCov={comp_res.objective_coverage}% | CmpCov={comp_res.compared_coverage}% | Matches={len(comp_res.matches)}")

        except Exception as e:
            print(f"    -> Error en comparación {cid}: {e}")
            import traceback
            traceback.print_exc()

    conn.close()
    print("\nResincronización completada con éxito.")


if __name__ == "__main__":
    resync_all()
