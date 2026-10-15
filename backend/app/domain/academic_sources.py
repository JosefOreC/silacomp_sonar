"""Identidades académicas compartidas por partición, reserva y trazabilidad."""

import hashlib
import json
import unicodedata
from typing import List, Tuple

from app.domain.review import DatasetExample


def normalize_source(value: str) -> str:
    return " ".join("".join(c for c in unicodedata.normalize("NFKD", value.casefold())
                            if not unicodedata.combining(c)).split())


def academic_source_tokens(example: DatasetExample) -> List[Tuple[str, ...]]:
    tokens = []
    for university, course, syllabus, item in (
        (example.source_university_obj, example.source_course_obj, example.source_syllabus_obj, example.objective_item_id),
        (example.source_university_cmp, example.source_course_cmp, example.source_syllabus_cmp, example.compared_item_id),
    ):
        if university and course:
            tokens.append(("academic", normalize_source(university), normalize_source(course)))
        else:
            tokens.append(("unknown_provenance",))
        if syllabus:
            tokens.append(("syllabus", syllabus))
        if item and item != "UNKNOWN":
            tokens.append(("item", item))
    if example.objective_text.strip() and example.compared_text.strip():
        pair = sorted((normalize_source(example.objective_text), normalize_source(example.compared_text)))
        tokens.append(("text_pair", hashlib.sha256(json.dumps(pair).encode()).hexdigest()))
    for digest in (example.source_syllabus_hash_obj, example.source_syllabus_hash_cmp):
        if digest:
            tokens.append(("document_hash", digest))
    return tokens


def connected_source_group_count(examples: List[DatasetExample]) -> int:
    groups = []
    for example in examples:
        tokens = set(academic_source_tokens(example))
        remaining = []
        for group in groups:
            if tokens & group:
                tokens.update(group)
            else:
                remaining.append(group)
        # Revisitar grupos que puedan conectarse transitivamente tras una unión posterior.
        while any(tokens & group for group in remaining):
            kept = []
            for group in remaining:
                if tokens & group:
                    tokens.update(group)
                else:
                    kept.append(group)
            remaining = kept
        groups = remaining + [tokens]
    return len(groups)
