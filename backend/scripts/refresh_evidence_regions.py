"""
Script de sincronización y actualización de regiones de evidencia espacial
para todas las comparaciones existentes en convcomp.db.
"""

import json
import os
import sqlite3
import sys

# Agregar backend al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.infrastructure.pdf.spatial_locator import SpatialLocatorService


def refresh_database_evidence_regions(db_path: str = "backend/data/convcomp.db") -> None:
    if not os.path.exists(db_path):
        print(f"Base de datos no encontrada en {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    locator = SpatialLocatorService()

    # Obtener todas las comparaciones y las rutas de sus archivos PDF
    cur.execute("""
        SELECT c.id, s1.file_path, s2.file_path, c.objective_syllabus_id, c.compared_syllabus_id
        FROM comparisons c
        JOIN syllabi s1 ON c.objective_syllabus_id = s1.id
        JOIN syllabi s2 ON c.compared_syllabus_id = s2.id
    """)
    comps = cur.fetchall()
    print(f"Procesando {len(comps)} comparaciones...")

    total_matches_updated = 0

    for comp_id, obj_pdf, cmp_pdf, obj_syl_id, cmp_syl_id in comps:
        cur.execute("""
            SELECT id, objective_item_id, compared_item_id,
                   objective_title, compared_title,
                   objective_page, compared_page,
                   objective_snippet, compared_snippet,
                   evidence_type, shared_keywords_json
            FROM content_matches
            WHERE comparison_id = ?
        """, (comp_id,))
        matches = cur.fetchall()

        for m in matches:
            (
                match_id, obj_item_id, cmp_item_id,
                obj_title, cmp_title,
                obj_page, cmp_page,
                obj_snippet, cmp_snippet,
                ev_type, shared_kw_json
            ) = m

            kw_list = json.loads(shared_kw_json) if shared_kw_json else []

            # Relocalizar objetivo
            obj_regs = []
            if obj_pdf and os.path.exists(obj_pdf):
                obj_regs = locator.locate_regions_for_item(
                    pdf_path=obj_pdf,
                    match_id=match_id,
                    syllabus_id=obj_syl_id,
                    content_id=obj_item_id,
                    page_number=obj_page,
                    title=obj_title,
                    snippet=obj_snippet,
                    keywords=kw_list,
                    evidence_type=ev_type,
                )

            # Relocalizar comparado
            cmp_regs = []
            if cmp_pdf and os.path.exists(cmp_pdf):
                cmp_regs = locator.locate_regions_for_item(
                    pdf_path=cmp_pdf,
                    match_id=match_id,
                    syllabus_id=cmp_syl_id,
                    content_id=cmp_item_id,
                    page_number=cmp_page,
                    title=cmp_title,
                    snippet=cmp_snippet,
                    keywords=kw_list,
                    evidence_type=ev_type,
                )

            actual_obj_page = obj_regs[0].page_number if obj_regs else obj_page
            actual_cmp_page = cmp_regs[0].page_number if cmp_regs else cmp_page

            serialized_regions = {
                "objective": [
                    {
                        "id": r.id,
                        "match_id": r.match_id,
                        "syllabus_id": r.syllabus_id,
                        "content_id": r.content_id,
                        "page_number": r.page_number,
                        "page_width": r.page_width,
                        "page_height": r.page_height,
                        "x0": r.x0,
                        "y0": r.y0,
                        "x1": r.x1,
                        "y1": r.y1,
                        "text": r.text,
                        "evidence_type": r.evidence_type,
                    }
                    for r in obj_regs
                ],
                "compared": [
                    {
                        "id": r.id,
                        "match_id": r.match_id,
                        "syllabus_id": r.syllabus_id,
                        "content_id": r.content_id,
                        "page_number": r.page_number,
                        "page_width": r.page_width,
                        "page_height": r.page_height,
                        "x0": r.x0,
                        "y0": r.y0,
                        "x1": r.x1,
                        "y1": r.y1,
                        "text": r.text,
                        "evidence_type": r.evidence_type,
                    }
                    for r in cmp_regs
                ],
            }

            cur.execute("""
                UPDATE content_matches
                SET evidence_regions_json = ?,
                    objective_page = ?,
                    compared_page = ?
                WHERE id = ?
            """, (json.dumps(serialized_regions), actual_obj_page, actual_cmp_page, match_id))
            total_matches_updated += 1

    conn.commit()
    conn.close()
    print(f"Actualización completada exitosamente. Total de correspondencias enriquecidas: {total_matches_updated}")


if __name__ == "__main__":
    refresh_database_evidence_regions()
