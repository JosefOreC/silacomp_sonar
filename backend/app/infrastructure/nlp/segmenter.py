"""
Servicio de segmentación y detección de estructura académica para sílabos universitarios.
Implementa el puerto ISegmentationService tolerando variaciones entre universidades.
"""

import re
from typing import List, Optional, Tuple
from app.domain.content import ContentItem
from app.domain.ports import ISegmentationService
from app.domain.syllabus import SectionType, Syllabus, SyllabusPage, SyllabusSection
from app.infrastructure.nlp.normalizer import TextNormalizer


# Patrones de encabezados canónicos para detección de secciones
SECTION_PATTERNS = [
    (
        SectionType.SUMILLA,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:sumilla|fundamentaci[oó]n|descripci[oó]n(?: general)?|presentaci[oó]n)\b", re.IGNORECASE | re.MULTILINE),
    ),
    (
        SectionType.COMPETENCIES,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:competencias?(?: del curso| gen[eé]ricas| espec[ií]ficas)?|capacidades)\b", re.IGNORECASE | re.MULTILINE),
    ),
    (
        SectionType.LEARNING_OUTCOMES,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:resultados? de aprendizaje|logros? de aprendizaje|objetivos?(?: generales| espec[ií]ficos)?)\b", re.IGNORECASE | re.MULTILINE),
    ),
    (
        SectionType.UNIT,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:unidad(?: de aprendizaje)?|cap[ií]tulo|m[oó]dulo|eje tem[aá]tico)\s*(?:[I|V|X|0-9]+|\b[a-zA-Z]+)?\b", re.IGNORECASE | re.MULTILINE),
    ),
    (
        SectionType.METHODOLOGY,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:metodolog[ií]a|estrategias? did[aá]cticas?|sistema de ense[ñn]anza)\b", re.IGNORECASE | re.MULTILINE),
    ),
    (
        SectionType.EVALUATION,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:evaluaci[oó]n|sistema de evaluaci[oó]n|criterios? de evaluaci[oó]n|f[oó]rmula de calificaci[oó]n)\b", re.IGNORECASE | re.MULTILINE),
    ),
    (
        SectionType.BIBLIOGRAPHY,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:bibliograf[ií]a|referencias?(?: bibliogr[aá]ficas?)?|fuentes de informaci[oó]n)\b", re.IGNORECASE | re.MULTILINE),
    ),
    (
        SectionType.GENERAL_DATA,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:datos? generales?|informaci[oó]n general|identificaci[oó]n)\b", re.IGNORECASE | re.MULTILINE),
    ),
]


class SyllabusSegmenter(ISegmentationService):
    """
    Detector heurístico de secciones y segmentador de contenidos temáticos.
    Diseñado para tolerar esquemas tabulares y listas no uniformes de diversas universidades.
    """

    def segment(self, syllabus: Syllabus) -> List[ContentItem]:
        """
        Analiza las páginas del sílabo, detecta secciones y descompone las unidades
        en una lista estructurada de ContentItem.
        """
        # Mapear texto continuo anotado con referencias de página
        page_spans = self._build_page_spans(syllabus.pages)
        full_text = "".join(span[0] for span in page_spans)

        # Detectar secciones canónicas en el texto
        raw_sections = self._detect_sections(full_text, page_spans, syllabus.id)
        syllabus.sections = raw_sections

        # Segmentar contenidos a partir de las secciones
        items = self._extract_content_items(syllabus, raw_sections, full_text, page_spans)

        # Si el sílabo no presentó encabezados tradicionales (estructura no canónica),
        # aplicar segmentación basada en párrafos temáticos para no dejar la comparación vacía.
        if not items:
            items = self._fallback_paragraph_segmentation(syllabus)

        return items

    def _build_page_spans(self, pages: List[SyllabusPage]) -> List[Tuple[str, int]]:
        """Construye tuplas (texto_pagina, numero_pagina) ordenadas."""
        return [(p.raw_text + "\n", p.page_number) for p in sorted(pages, key=lambda x: x.page_number)]

    def _detect_sections(self, full_text: str, page_spans: List[Tuple[str, int]], syllabus_id: str) -> List[SyllabusSection]:
        """Localiza posiciones de inicio de secciones y crea SyllabusSection."""
        matches: List[Tuple[int, SectionType, str]] = []

        for line_match in re.finditer(r"^(.*?)$", full_text, re.MULTILINE):
            line = line_match.group(1).strip()
            if not line or len(line) > 80:
                continue

            for sec_type, pattern in SECTION_PATTERNS:
                if pattern.match(line):
                    matches.append((line_match.start(), sec_type, line))
                    break

        matches.sort(key=lambda x: x[0])

        sections: List[SyllabusSection] = []
        for i, (start_char, sec_type, title) in enumerate(matches):
            end_char = matches[i + 1][0] if i + 1 < len(matches) else len(full_text)
            p_start = self._char_to_page(start_char, page_spans)
            p_end = self._char_to_page(end_char - 1, page_spans)

            sections.append(
                SyllabusSection(
                    id=f"{syllabus_id}-SEC-{i+1:02d}",
                    syllabus_id=syllabus_id,
                    title=title,
                    section_type=sec_type,
                    order=i + 1,
                    page_start=p_start,
                    page_end=max(p_start, p_end),
                )
            )

        return sections

    def _char_to_page(self, char_idx: int, page_spans: List[Tuple[str, int]]) -> int:
        """Determina el número de página a partir de un índice de carácter absoluto."""
        current_offset = 0
        for text, page_num in page_spans:
            next_offset = current_offset + len(text)
            if current_offset <= char_idx < next_offset:
                return page_num
            current_offset = next_offset
        return page_spans[-1][1] if page_spans else 1

    def _extract_content_items(
        self,
        syllabus: Syllabus,
        sections: List[SyllabusSection],
        full_text: str,
        page_spans: List[Tuple[str, int]],
    ) -> List[ContentItem]:
        """Extrae los contenidos individuales priorizando Unidades, Sumilla y Competencias."""
        items: List[ContentItem] = []
        item_counter = 1

        # Mapear secciones detectadas a sus textos
        unit_index = 1
        for sec in sections:
            # Procesar Unidades de Aprendizaje (núcleo del contenido analítico)
            if sec.section_type == SectionType.UNIT:
                unit_text = self._get_section_slice(sec, sections, full_text)
                sub_items = self._split_unit_into_items(unit_text, sec, syllabus.id, item_counter, unit_index)
                for item in sub_items:
                    items.append(item)
                    item_counter += 1
                unit_index += 1

            # Procesar Sumilla (muy relevante para la vista general y correspondencia transversal)
            elif sec.section_type == SectionType.SUMILLA:
                sumilla_text = self._get_section_slice(sec, sections, full_text).strip()
                if len(sumilla_text) > 30:
                    clean_text = TextNormalizer.clean_display_text(sumilla_text)
                    items.append(
                        ContentItem(
                            id=f"{syllabus.id}-CONT-{item_counter:03d}",
                            syllabus_id=syllabus.id,
                            section_name="Sumilla",
                            title="Sumilla / Fundamentación General",
                            text=clean_text,
                            normalized_text=TextNormalizer.normalize_for_indexing(clean_text),
                            page_start=sec.page_start,
                            page_end=sec.page_end,
                            order=item_counter,
                            unit_number=0,
                        )
                    )
                    item_counter += 1

            # Procesar Competencias y Resultados de Aprendizaje
            elif sec.section_type in (SectionType.COMPETENCIES, SectionType.LEARNING_OUTCOMES):
                comp_text = self._get_section_slice(sec, sections, full_text).strip()
                comp_lines = [l.strip("-•* ").strip() for l in comp_text.splitlines() if len(l.strip()) > 25]
                for comp_line in comp_lines[:8]:  # Hasta 8 competencias clave
                    clean_text = TextNormalizer.clean_display_text(comp_line)
                    items.append(
                        ContentItem(
                            id=f"{syllabus.id}-CONT-{item_counter:03d}",
                            syllabus_id=syllabus.id,
                            section_name=sec.title[:40],
                            title=clean_text[:60] + ("..." if len(clean_text) > 60 else ""),
                            text=clean_text,
                            normalized_text=TextNormalizer.normalize_for_indexing(clean_text),
                            page_start=sec.page_start,
                            page_end=sec.page_end,
                            order=item_counter,
                            unit_number=None,
                        )
                    )
                    item_counter += 1

        return items

    def _get_section_slice(self, target_sec: SyllabusSection, all_secs: List[SyllabusSection], full_text: str) -> str:
        """Obtiene el texto entre el inicio de esta sección y el inicio de la siguiente."""
        # Búsqueda aproximada por título
        pattern = re.escape(target_sec.title)
        match = re.search(pattern, full_text)
        if not match:
            return ""

        start_pos = match.end()
        next_pos = len(full_text)

        # Buscar la siguiente sección
        curr_idx = all_secs.index(target_sec)
        if curr_idx + 1 < len(all_secs):
            next_sec = all_secs[curr_idx + 1]
            next_match = re.search(re.escape(next_sec.title), full_text[start_pos:])
            if next_match:
                next_pos = start_pos + next_match.start()

        return full_text[start_pos:next_pos]

    def _split_unit_into_items(
        self,
        unit_text: str,
        section: SyllabusSection,
        syllabus_id: str,
        start_order: int,
        unit_number: int,
    ) -> List[ContentItem]:
        """Descompone el texto de una unidad en tópicos individuales usando viñetas, semanas o saltos."""
        items: List[ContentItem] = []
        raw_lines = [l.strip() for l in unit_text.splitlines() if l.strip()]

        # Extraer tema de la unidad si existe en el título (ej. "UNIDAD II: NORMALIZACIÓN" -> "NORMALIZACIÓN")
        unit_theme = ""
        if ":" in section.title:
            unit_theme = section.title.split(":", 1)[1].strip()
        elif "-" in section.title:
            unit_theme = section.title.split("-", 1)[1].strip()

        current_title = ""
        current_buffer: List[str] = []
        order = start_order

        # Detectar líneas indicadoras de temas (Semana N, Viñeta, Números, o líneas breves) limpiando delimitadores
        topic_pattern = re.compile(r"^(?:semana\s*\d+|tema\s*\d+|\d+\.|\*|\-|•)\s*[:\-\.]?\s*(.*)", re.IGNORECASE)

        for line in raw_lines:
            match = topic_pattern.match(line)
            if match:
                # Si ya teníamos un tema acumulado, guardarlo
                if current_buffer or current_title:
                    content_str = "\n".join(current_buffer).strip() or current_title
                    if len(content_str) > 8:
                        final_title = f"{unit_theme} - {current_title}" if unit_theme and current_title and unit_theme.lower() not in current_title.lower() else (current_title or content_str[:50])
                        full_content = f"{unit_theme}. {content_str}" if unit_theme and unit_theme.lower() not in content_str.lower() else content_str
                        items.append(
                            ContentItem(
                                id=f"{syllabus_id}-CONT-{order:03d}",
                                syllabus_id=syllabus_id,
                                section_name=section.title[:50],
                                title=final_title.strip(" -:"),
                                text=full_content,
                                normalized_text=TextNormalizer.normalize_for_indexing(f"{final_title} {full_content}"),
                                page_start=section.page_start,
                                page_end=section.page_end,
                                order=order,
                                unit_number=unit_number,
                            )
                        )
                        order += 1
                current_title = match.group(1).strip()
                current_buffer = [current_title] if current_title else []
            else:
                if len(line) > 5:
                    current_buffer.append(line)

        # Último buffer pendiente
        if current_buffer or current_title:
            content_str = "\n".join(current_buffer).strip() or current_title
            if len(content_str) > 8:
                final_title = f"{unit_theme} - {current_title}" if unit_theme and current_title and unit_theme.lower() not in current_title.lower() else (current_title or content_str[:50])
                full_content = f"{unit_theme}. {content_str}" if unit_theme and unit_theme.lower() not in content_str.lower() else content_str
                items.append(
                    ContentItem(
                        id=f"{syllabus_id}-CONT-{order:03d}",
                        syllabus_id=syllabus_id,
                        section_name=section.title[:50],
                        title=final_title.strip(" -:"),
                        text=full_content,
                        normalized_text=TextNormalizer.normalize_for_indexing(f"{final_title} {full_content}"),
                        page_start=section.page_start,
                        page_end=section.page_end,
                        order=order,
                        unit_number=unit_number,
                    )
                )

        # Si no hubo viñetas, dividir por párrafos mayores a 40 caracteres
        if not items:
            paragraphs = [p.strip() for p in unit_text.split("\n\n") if len(p.strip()) > 30]
            for idx, p in enumerate(paragraphs):
                title = p.split("\n")[0][:60]
                items.append(
                    ContentItem(
                        id=f"{syllabus_id}-CONT-{order:03d}",
                        syllabus_id=syllabus_id,
                        section_name=section.title[:50],
                        title=title,
                        text=p,
                        normalized_text=TextNormalizer.normalize_for_indexing(p),
                        page_start=section.page_start,
                        page_end=section.page_end,
                        order=order,
                        unit_number=unit_number,
                    )
                )
                order += 1

        return items

    def _fallback_paragraph_segmentation(self, syllabus: Syllabus) -> List[ContentItem]:
        """Mecanismo de respaldo para sílabos sin títulos canónicos reconocibles."""
        items: List[ContentItem] = []
        order = 1

        for page in sorted(syllabus.pages, key=lambda x: x.page_number):
            paragraphs = [p.strip() for p in page.raw_text.split("\n\n") if len(p.strip()) > 40]
            for p in paragraphs:
                first_line = p.split("\n")[0].strip()
                title = first_line[:60] if len(first_line) > 10 else f"Contenido pág. {page.page_number}"
                items.append(
                    ContentItem(
                        id=f"{syllabus.id}-CONT-{order:03d}",
                        syllabus_id=syllabus.id,
                        section_name=f"Página {page.page_number}",
                        title=title,
                        text=p,
                        normalized_text=TextNormalizer.normalize_for_indexing(p),
                        page_start=page.page_number,
                        page_end=page.page_number,
                        order=order,
                        unit_number=None,
                    )
                )
                order += 1

        return items
