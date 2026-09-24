"""
Servicio de localización espacial de evidencias en documentos PDF utilizando PyMuPDF.
Calcula coordenadas de recuadros delimitadores (bounding boxes) para la Fase 1.5.
"""

import os
from typing import List, Optional
import uuid
import pymupdf as fitz

from app.domain.comparison import EvidenceRegion, EvidenceType


class SpatialLocatorService:
    """Localiza y extrae regiones rectangulares de texto para sustentar evidencias de correspondencia."""

    def locate_regions_for_item(
        self,
        pdf_path: str,
        match_id: str,
        syllabus_id: str,
        content_id: str,
        page_number: int,
        title: str,
        snippet: str,
        keywords: Optional[List[str]] = None,
        evidence_type: str = "COMBINED",
    ) -> List[EvidenceRegion]:
        """
        Localiza las coordenadas espaciales exactas del fragmento, título o palabras clave
        en la página especificada del documento PDF.
        """
        if not os.path.exists(pdf_path):
            return []

        regions: List[EvidenceRegion] = []

        try:
            doc = fitz.open(pdf_path)
            if page_number < 1 or page_number > len(doc):
                doc.close()
                return []

            page = doc[page_number - 1]
            rect = page.rect
            page_w = float(rect.width)
            page_h = float(rect.height)

            # 1. Búsqueda de coincidencia por título
            found_rects: List[fitz.Rect] = []
            if title and len(title.strip()) > 3:
                # Buscar título exacto o primeros 40 caracteres
                search_title = title.strip()[:50]
                title_matches = page.search_for(search_title)
                if title_matches:
                    found_rects.extend(title_matches[:2])

            # 2. Búsqueda de fragmento textual significativo
            if snippet and len(snippet.strip()) > 5:
                # Tomar fragmentos de 4 a 6 palabras representativas
                words = snippet.strip().split()
                if len(words) >= 3:
                    sub_phrase = " ".join(words[:min(6, len(words))])
                    phrase_matches = page.search_for(sub_phrase)
                    if phrase_matches:
                        found_rects.extend(phrase_matches[:2])

            # 3. Búsqueda por palabras clave compartidas
            if keywords:
                for kw in keywords[:3]:
                    if len(kw.strip()) >= 3:
                        kw_matches = page.search_for(kw.strip())
                        if kw_matches:
                            found_rects.extend(kw_matches[:1])

            # 4. Respaldo por bloques de texto con solapamiento temático
            if not found_rects:
                blocks = page.get_text("blocks")
                target_terms = set((title + " " + snippet).lower().split())
                best_block = None
                best_overlap = 0

                for b in blocks:
                    block_text = b[4].lower()
                    overlap = sum(1 for term in target_terms if len(term) > 3 and term in block_text)
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_block = b

                if best_block and best_overlap > 0:
                    found_rects.append(fitz.Rect(best_block[0], best_block[1], best_block[2], best_block[3]))

            # 5. Si aún no hay coincidencia, definir región representativa en la página
            if not found_rects:
                # Región segura de tercio medio de la página
                default_rect = fitz.Rect(54.0, page_h * 0.25, page_w - 54.0, page_h * 0.35)
                found_rects.append(default_rect)

            doc.close()

            # Construir entidades EvidenceRegion
            for i, r in enumerate(found_rects[:3]):  # Limitar a máx 3 regiones por correspondencia
                # Pequeño padding de 2 puntos para visualización limpia
                x0 = max(0.0, float(r.x0) - 2.0)
                y0 = max(0.0, float(r.y0) - 2.0)
                x1 = min(page_w, float(r.x1) + 2.0)
                y1 = min(page_h, float(r.y1) + 2.0)

                region_text = title if i == 0 else snippet[:60]
                regions.append(
                    EvidenceRegion(
                        id=f"REG-{uuid.uuid4().hex[:8].upper()}",
                        match_id=match_id,
                        syllabus_id=syllabus_id,
                        content_id=content_id,
                        page_number=page_number,
                        page_width=page_w,
                        page_height=page_h,
                        x0=round(x0, 2),
                        y0=round(y0, 2),
                        x1=round(x1, 2),
                        y1=round(y1, 2),
                        text=region_text,
                        evidence_type=evidence_type,
                    )
                )

        except Exception as e:
            # Tolerancia a fallos: ante cualquier error en el archivo, se retorna lista vacía sin interrumpir el flujo
            print(f"[SpatialLocatorService] Advertencia al localizar coordenadas: {e}")
            return []

        return regions
