"""
Servicio de segmentación y detección de estructura académica para sílabos universitarios.
Implementa el puerto ISegmentationService tolerando variaciones entre universidades.
"""

from dataclasses import replace
import re
from typing import List, Optional, Tuple
from app.domain.content import ContentItem
from app.domain.ports import ISegmentationService
from app.domain.syllabus import SectionType, Syllabus, SyllabusPage, SyllabusSection
from app.infrastructure.nlp.normalizer import TextNormalizer


# Patrones de encabezados canónicos para detección de secciones
SECTION_PATTERNS = [
    (
        SectionType.GENERAL_DATA,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:datos?\s+generales?|informaci[oó]n\s+general|identificaci[oó]n)\b(?:\s*[:\-\–\—].*)?$", re.IGNORECASE),
    ),
    (
        SectionType.SUMILLA,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:sumilla|fundamentaci[oó]n|descripci[oó]n\s+general|introducci[oó]n)\b(?:\s*[:\-\–\—].*)?$", re.IGNORECASE),
    ),
    (
        SectionType.COMPETENCIES,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:competencias?(?:\s+del\s+curso|\s+gen[eé]ricas|\s+espec[ií]ficas)?|capacidades)\b(?:\s*[:\-\–\—].*)?$", re.IGNORECASE),
    ),
    (
        SectionType.LEARNING_OUTCOMES,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:resultados?\s+de\s+aprendizaje(?:\s+de\s+la\s+asignatura)?|logros?\s+de\s+aprendizaje|objetivos?\s+generales?)\b(?:\s*[:\-\–\—].*)?$", re.IGNORECASE),
    ),
    (
        SectionType.UNIT,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:unidad(?:\s+de\s+aprendizaje)?|cap[ií]tulo|m[oó]dulo|eje\s+tem[aá]tico)\s*(?:[I|V|X|0-9]+|\b(?:uno|dos|tres|cuatro|cinco|seis|siete|ocho|primera|segunda|tercera|cuarta|quinta)\b)(?:\s*[:\-\–\—].*)?$", re.IGNORECASE),
    ),
    (
        SectionType.METHODOLOGY,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:metodolog[ií]a|estrategias?\s+did[aá]cticas?|sistema\s+de\s+ense[ñn]anza)\b(?:\s*[:\-\–\—].*)?$", re.IGNORECASE),
    ),
    (
        SectionType.EVALUATION,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:sistema\s+de\s+evaluaci[oó]n|criterios?\s+de\s+evaluaci[oó]n|f[oó]rmula\s+de\s+calificaci[oó]n|evaluaci[oó]n)\s*$", re.IGNORECASE),
    ),
    (
        SectionType.BIBLIOGRAPHY,
        re.compile(r"^(?:[I|V|X|0-9]+\.?\s*)?(?:bibliograf[ií]a|referencias?(?:\s+bibliogr[aá]ficas?)?|fuentes\s+de\s+informaci[oó]n)\b(?:\s*[:\-\–\—].*)?$", re.IGNORECASE),
    ),
]

BOILERPLATE_PATTERNS = [
    re.compile(r"^(?:duraci[oó]n(?:\s+en\s+horas)?|\d+\s+horas?|ejes?\s+tem[aá]ticos?|organizaci[oó]n\s+de\s+los\s+aprendizajes|resultados?\s+de\s+aprendizaje\s+de\s+la\s+unidad)\b", re.IGNORECASE),
    re.compile(r"^(?:actividades?\s*(?:de\s+aprendizaje|formativas?)?|horas?\s*te[oó]ricas?|horas?\s*pr[aá]cticas?|semana\s*\d+\s*$|evaluaci[oó]n\s+de\s+entrada|instrumentos?\s+de\s+evaluaci[oó]n|porcentaje\s*%?|peso\s*%?|ponderaci[oó]n)\b", re.IGNORECASE),
    re.compile(r"^(?:conceptual|procedimental|actitudinal|saberes?\s+previos|evidencia\s+de\s+aprendizaje|r[uú]brica)\s*$", re.IGNORECASE),
]


class SyllabusSegmenter(ISegmentationService):
    """
    Detector heurístico de secciones y segmentador de contenidos temáticos.
    Diseñado para tolerar esquemas tabulares y listas no uniformes de diversas universidades.
    """

    def segment(self, syllabus: Syllabus) -> List[ContentItem]:
        """
        Analiza las páginas del sílabo, detecta secciones y descompone las unidades
        en una lista estructurada de ContentItem sin redundancias.
        """
        # Mapear texto continuo anotado con referencias de página
        page_spans = self._build_page_spans(syllabus.pages)
        full_text = "".join(span[0] for span in page_spans)

        # Detectar secciones canónicas en el texto
        raw_sections, section_spans = self._detect_sections(full_text, page_spans, syllabus.id)
        syllabus.sections = raw_sections

        # Segmentar contenidos a partir de las secciones
        items = self._extract_content_items(syllabus, raw_sections, full_text, page_spans, section_spans)

        # Si el sílabo no presentó encabezados tradicionales (estructura no canónica),
        # aplicar segmentación basada en párrafos temáticos para no dejar la comparación vacía.
        if not items:
            items = self._fallback_paragraph_segmentation(syllabus)

        # Deduplicar ítems redundantes dentro del mismo sílabo
        unique_items: List[ContentItem] = []
        seen_keys: set = set()
        order_idx = 1
        for it in items:
            norm_title = TextNormalizer.normalize_for_indexing(it.title)
            norm_snippet = TextNormalizer.normalize_for_indexing(it.text[:100])
            key = f"{norm_title}||{norm_snippet}"
            if key in seen_keys:
                continue
            seen_keys.add(key)
            if it.order != order_idx:
                it = replace(it, order=order_idx)
            unique_items.append(it)
            order_idx += 1

        return unique_items


    def _build_page_spans(self, pages: List[SyllabusPage]) -> List[Tuple[str, int]]:
        """Construye tuplas (texto_pagina, numero_pagina) ordenadas."""
        return [(p.raw_text + "\n", p.page_number) for p in sorted(pages, key=lambda x: x.page_number)]

    def _detect_sections(
        self, full_text: str, page_spans: List[Tuple[str, int]], syllabus_id: str
    ) -> Tuple[List[SyllabusSection], dict]:
        """Localiza posiciones de inicio de secciones y crea SyllabusSection con spans exactos."""
        raw_matches: List[Tuple[int, SectionType, str]] = []

        for line_match in re.finditer(r"^(.*?)$", full_text, re.MULTILINE):
            line = line_match.group(1).strip()
            if not line or len(line) > 75:
                continue

            for sec_type, pattern in SECTION_PATTERNS:
                if pattern.match(line):
                    raw_matches.append((line_match.start(), sec_type, line))
                    break

        raw_matches.sort(key=lambda x: x[0])

        # Filtrar secciones estructurales macro repetidas (evita falsas secciones dentro de tablas de evaluación)
        filtered_matches: List[Tuple[int, SectionType, str]] = []
        seen_macro_types: set = set()
        for start, sec_type, line in raw_matches:
            if sec_type in (SectionType.SUMILLA, SectionType.GENERAL_DATA, SectionType.METHODOLOGY, SectionType.EVALUATION, SectionType.BIBLIOGRAPHY):
                if sec_type in seen_macro_types:
                    continue
                seen_macro_types.add(sec_type)
            filtered_matches.append((start, sec_type, line))

        sections: List[SyllabusSection] = []
        section_spans: dict = {}
        for i, (start_char, sec_type, title) in enumerate(filtered_matches):
            end_char = filtered_matches[i + 1][0] if i + 1 < len(filtered_matches) else len(full_text)
            p_start = self._char_to_page(start_char, page_spans)
            p_end = self._char_to_page(end_char - 1, page_spans)

            sec_id = f"{syllabus_id}-SEC-{i+1:02d}"
            sections.append(
                SyllabusSection(
                    id=sec_id,
                    syllabus_id=syllabus_id,
                    title=title,
                    section_type=sec_type,
                    order=i + 1,
                    page_start=p_start,
                    page_end=max(p_start, p_end),
                )
            )
            section_spans[sec_id] = (start_char, end_char)

        return sections, section_spans

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
        section_spans: Optional[dict] = None,
    ) -> List[ContentItem]:
        """Extrae los contenidos individuales priorizando Unidades, Sumilla y Competencias."""
        items: List[ContentItem] = []
        item_counter = 1
        spans = section_spans or {}

        # Mapear secciones detectadas a sus textos
        unit_index = 1
        for sec in sections:
            sec_text = self._get_section_slice(sec, sections, full_text, spans)

            # Procesar Unidades de Aprendizaje (núcleo del contenido analítico)
            if sec.section_type == SectionType.UNIT:
                sub_items = self._split_unit_into_items(sec_text, sec, syllabus.id, item_counter, unit_index)
                for item in sub_items:
                    items.append(item)
                    item_counter += 1
                unit_index += 1

            # Procesar Sumilla (muy relevante para la vista general y correspondencia transversal)
            elif sec.section_type == SectionType.SUMILLA:
                clean_text = TextNormalizer.clean_display_text(sec_text)
                if len(clean_text) > 30:
                    items.append(
                        ContentItem(
                            id=f"{syllabus.id}-CONT-{item_counter:03d}",
                            syllabus_id=syllabus.id,
                            section_name="Sumilla",
                            title="Sumilla / Fundamentación General",
                            text=clean_text[:600],
                            normalized_text=TextNormalizer.normalize_for_indexing(clean_text[:600]),
                            page_start=sec.page_start,
                            page_end=sec.page_end,
                            order=item_counter,
                            unit_number=0,
                        )
                    )
                    item_counter += 1

            # Procesar Competencias y Resultados de Aprendizaje
            elif sec.section_type in (SectionType.COMPETENCIES, SectionType.LEARNING_OUTCOMES):
                comp_items_raw: List[str] = []
                current_comp: List[str] = []
                for raw_l in sec_text.splitlines():
                    l = raw_l.strip()
                    if not l or len(l) < 3:
                        continue
                    is_bullet = bool(re.match(r"^(?:[•●○■▪\*\-–—]|\d+[\.\)])\s*", l))
                    clean_l = re.sub(r"^(?:[•●○■▪\*\-–—]|\d+[\.\)])\s*", "", l).strip()
                    if is_bullet:
                        if current_comp:
                            comp_items_raw.append(" ".join(current_comp))
                        current_comp = [clean_l]
                    else:
                        if current_comp:
                            current_comp.append(clean_l)
                        elif len(clean_l) > 25:
                            current_comp = [clean_l]
                if current_comp:
                    comp_items_raw.append(" ".join(current_comp))

                for comp_text in comp_items_raw[:8]:  # Hasta 8 competencias clave
                    if any(pat.match(comp_text) for _, pat in SECTION_PATTERNS) or self._is_boilerplate_line(comp_text):
                        continue
                    clean_text = TextNormalizer.clean_display_text(comp_text)
                    if len(clean_text) < 25:
                        continue
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

    def _get_section_slice(
        self,
        target_sec: SyllabusSection,
        all_secs: List[SyllabusSection],
        full_text: str,
        section_spans: Optional[dict] = None,
    ) -> str:
        """Obtiene el texto entre el inicio de esta sección y el inicio de la siguiente con exactitud posicional."""
        if section_spans and target_sec.id in section_spans:
            start_pos, next_pos = section_spans[target_sec.id]
            return full_text[start_pos:next_pos]

        # Respaldo en caso de que section_spans no esté provisto
        pattern = re.escape(target_sec.title)
        match = re.search(pattern, full_text)
        if not match:
            return ""

        start_pos = match.end()
        next_pos = len(full_text)

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
        has_started_topics = False

        # Detectar líneas indicadoras de temas (Semana N, Viñeta, Números, o líneas breves) limpiando delimitadores
        topic_pattern = re.compile(
            r"^(?:semana\s*\d+|tema\s*\d+|\d+[\.\)]|[•●○■▪\*\-–—])\s*[:\-\.]?\s*(.*)",
            re.IGNORECASE,
        )

        for line in raw_lines:
            match = topic_pattern.match(line)
            if match:
                # Si ya teníamos un tema acumulado, guardarlo
                if has_started_topics and (current_buffer or current_title):
                    content_str = "\n".join(current_buffer).strip() or current_title
                    if len(content_str) > 8 and not self._is_boilerplate_line(content_str):
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

                has_started_topics = True
                matched_topic = match.group(1).strip()
                current_title = matched_topic
                current_buffer = [matched_topic] if matched_topic else []
            else:
                if not has_started_topics:
                    # Las líneas antes de la primera viñeta/tema son preámbulo administrativo de la unidad
                    # (ej. "Resultado de aprendizaje", "Al finalizar la unidad...", "Horas: 16")
                    continue
                # Filtrar encabezados tabulares o líneas de duración
                if len(line) > 5 and not self._is_boilerplate_line(line):
                    if not current_title:
                        current_title = line
                    current_buffer.append(line)

        # Último buffer pendiente
        if has_started_topics and (current_buffer or current_title):
            content_str = "\n".join(current_buffer).strip() or current_title
            if len(content_str) > 8 and not self._is_boilerplate_line(content_str):
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

        # Si no hubo viñetas reconocidas, dividir por párrafos mayores a 40 caracteres
        if not items:
            paragraphs = [p.strip() for p in unit_text.split("\n\n") if len(p.strip()) > 30 and not self._is_boilerplate_line(p)]
            for p in paragraphs:
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

    def _is_boilerplate_line(self, text: str) -> bool:
        """Determina si una línea es metadato administrativo/tabla (ej. horas, duración, ejes temáticos)."""
        first_line = text.strip().splitlines()[0] if text.strip() else ""
        return any(pat.search(first_line) for pat in BOILERPLATE_PATTERNS)

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

