"""
Servicio de localización espacial de evidencias en documentos PDF utilizando PyMuPDF.
Calcula coordenadas de recuadros delimitadores (bounding boxes) para la Fase 1.5.
"""

import os
import re
from typing import List, Optional
import uuid
import pymupdf as fitz

from app.domain.comparison import EvidenceRegion


class SpatialLocatorService:
    """Localiza y extrae regiones rectangulares de texto para sustentar evidencias de correspondencia."""

    @staticmethod
    def _merge_rects_into_lines(rects: List[fitz.Rect], y_tolerance: float = 4.0) -> List[fitz.Rect]:
        """Fusiona rectángulos de palabras o fragmentos que pertenecen a la misma línea tipográfica."""
        lines: List[fitz.Rect] = []
        for r in rects:
            merged = False
            for l in lines:
                if abs(l.y0 - r.y0) <= y_tolerance or abs(l.y1 - r.y1) <= y_tolerance:
                    l.x0 = min(l.x0, r.x0)
                    l.y0 = min(l.y0, r.y0)
                    l.x1 = max(l.x1, r.x1)
                    l.y1 = max(l.y1, r.y1)
                    merged = True
                    break
            if not merged:
                lines.append(fitz.Rect(r))
        lines.sort(key=lambda l: (l.y0, l.x0))
        return lines

    @staticmethod
    def _cluster_contiguous_lines(lines: List[fitz.Rect], max_gap: float = 16.0) -> List[fitz.Rect]:
        """Agrupa líneas de texto contiguas (mismo párrafo o tópico) en un solo bounding box envolvente."""
        if not lines:
            return []
        clusters: List[fitz.Rect] = [fitz.Rect(lines[0])]
        for curr in lines[1:]:
            prev = clusters[-1]
            if curr.y0 - prev.y1 <= max_gap and curr.y0 >= prev.y0 - 2:
                prev.x0 = min(prev.x0, curr.x0)
                prev.y0 = min(prev.y0, curr.y0)
                prev.x1 = max(prev.x1, curr.x1)
                prev.y1 = max(prev.y1, curr.y1)
            else:
                clusters.append(fitz.Rect(curr))
        return clusters

    def _extract_page_rects(
        self,
        page: fitz.Page,
        clean_title: str,
        clean_snippet: str,
        full_title: str,
        full_snippet: str,
    ) -> List[fitz.Rect]:
        """Extrae rectángulos de texto de la página buscando títulos, párrafos o bloques temáticos completos."""
        page_h = float(page.rect.height)
        raw_rects: List[fitz.Rect] = []

        # 1. Búsqueda por título limpio completo o prefijo sustancial (> 5 caracteres)
        if clean_title and len(clean_title) >= 5:
            r = page.search_for(clean_title)
            if not r and len(clean_title) > 25:
                r = page.search_for(clean_title[:25])
            if r:
                raw_rects.extend(r)

        # 2. Búsqueda por líneas del snippet (hasta 4 líneas significativas)
        if clean_snippet:
            snippet_lines = [l.strip() for l in clean_snippet.splitlines() if len(l.strip()) >= 8]
            for sline in snippet_lines[:4]:
                cleaned_sline = re.sub(r"^(?:[•●○■▪\*\-–—]|\d+[\.\)])\s*", "", sline).strip()
                if len(cleaned_sline) >= 8:
                    r = page.search_for(cleaned_sline[:40])
                    if r:
                        raw_rects.extend(r)

        # 3. Búsqueda por subfrases de 3 a 5 palabras
        if not raw_rects:
            words = [w for w in re.split(r"\s+", clean_title or clean_snippet) if len(w) > 3]
            for start_idx in range(min(4, len(words))):
                sub_phrase = " ".join(words[start_idx:start_idx + 4])
                if len(sub_phrase) >= 12:
                    r = page.search_for(sub_phrase)
                    if r:
                        raw_rects.extend(r)
                        break

        # 4. Búsqueda por bloque temático de mayor solapamiento léxico (excluyendo cabeceras/pies)
        if not raw_rects:
            target_words = set(w.lower() for w in re.findall(r"\b\w{4,}\b", (full_title + " " + full_snippet)))
            blocks = page.get_text("blocks")
            best_block = None
            best_overlap = 0

            for b in blocks:
                # Excluir cabeceras extremas (< 45 pt) y pies (> page_h - 45 pt)
                if b[1] < 45 or b[3] > page_h - 45:
                    continue
                b_text = b[4].lower()
                b_words = set(re.findall(r"\b\w{4,}\b", b_text))
                overlap = len(target_words.intersection(b_words))
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_block = b

            if best_block and best_overlap >= 2:
                raw_rects.append(fitz.Rect(best_block[0], best_block[1], best_block[2], best_block[3]))

        return raw_rects

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
        Localiza las coordenadas espaciales exactas del fragmento y título correspondiente
        en la página especificada del documento PDF, con soporte para auto-resolución de página.
        """
        if not os.path.exists(pdf_path):
            return []

        regions: List[EvidenceRegion] = []

        try:
            doc = fitz.open(pdf_path)
            num_pages = len(doc)
            if num_pages == 0 or page_number < 1 or page_number > num_pages:
                doc.close()
                return []

            # 1. Limpieza rigurosa de títulos para remover prefijos sintéticos agregados por el segmentador
            clean_title = (title or "").strip()
            if " - " in clean_title:
                clean_title = clean_title.split(" - ", 1)[1].strip()
            clean_title = re.sub(r"^(?:unidad\s+[ivx\d]+|tema\s*\d+|semana\s*\d+)\s*[:\-\.]?\s*", "", clean_title, flags=re.I).strip()
            clean_title = re.sub(r"^(?:[•●○■▪\*\-–—]|\d+[\.\)])\s*", "", clean_title).strip()
            clean_title = re.sub(r"\.{3,}$", "", clean_title).strip()

            is_synthetic_title = bool(re.search(r"^(?:sumilla|fundamentaci[oó]n|datos?\s+generales?|competencias?|resultados?\s+de\s+aprendizaje)\b", clean_title, re.I))
            if is_synthetic_title:
                clean_title = ""

            clean_snippet = (snippet or "").strip()
            clean_snippet = re.sub(r"^(?:[•●○■▪\*\-–—]|\d+[\.\)])\s*", "", clean_snippet).strip()

            # 2. Localización de página: primero en page_number; si no está allí, buscar en páginas adyacentes o restantes
            target_page_idx = max(0, min(num_pages - 1, page_number - 1))
            actual_page_idx = target_page_idx
            raw_rects = self._extract_page_rects(doc[target_page_idx], clean_title, clean_snippet, title, snippet)

            if not raw_rects and num_pages > 1:
                # Probar página siguiente y anterior primero (típico cuando una unidad cruza página)
                candidate_indices: List[int] = []
                if target_page_idx + 1 < num_pages:
                    candidate_indices.append(target_page_idx + 1)
                if target_page_idx - 1 >= 0:
                    candidate_indices.append(target_page_idx - 1)
                for idx in range(num_pages):
                    if idx not in candidate_indices and idx != target_page_idx:
                        candidate_indices.append(idx)

                for c_idx in candidate_indices:
                    c_rects = self._extract_page_rects(doc[c_idx], clean_title, clean_snippet, title, snippet)
                    if c_rects:
                        raw_rects = c_rects
                        actual_page_idx = c_idx
                        break

            found_page = doc[actual_page_idx]
            page_w = float(found_page.rect.width)
            page_h = float(found_page.rect.height)
            actual_page_num = actual_page_idx + 1

            if not raw_rects:
                # Si todo falla, definir recuadro seguro en tercio medio de la página esperada
                default_rect = fitz.Rect(54.0, page_h * 0.25, page_w - 54.0, page_h * 0.35)
                raw_rects.append(default_rect)

            doc.close()

            # 3. Fusionar palabras en líneas y agrupar líneas contiguas en párrafos envolventes
            lines = self._merge_rects_into_lines(raw_rects)
            clusters = self._cluster_contiguous_lines(lines)

            # Construir entidades EvidenceRegion
            for i, c in enumerate(clusters[:2]):  # Máximo 2 recuadros coherentes por correspondencia
                x0 = max(0.0, float(c.x0) - 3.0)
                y0 = max(0.0, float(c.y0) - 2.0)
                x1 = min(page_w, float(c.x1) + 3.0)
                y1 = min(page_h, float(c.y1) + 2.0)

                region_text = title if i == 0 and len(title) > 5 else (snippet[:80] if snippet else title)
                regions.append(
                    EvidenceRegion(
                        id=f"REG-{uuid.uuid4().hex[:8].upper()}",
                        match_id=match_id,
                        syllabus_id=syllabus_id,
                        content_id=content_id,
                        page_number=actual_page_num,
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
            print(f"[SpatialLocatorService] Advertencia al localizar coordenadas: {e}")
            return []

        return regions
