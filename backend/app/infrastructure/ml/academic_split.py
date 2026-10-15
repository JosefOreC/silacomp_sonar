"""Particiones reproducibles que mantienen juntas las fuentes académicas relacionadas."""

from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.model_selection import GroupShuffleSplit, train_test_split

from app.domain.review import DatasetExample
from app.domain.academic_sources import academic_source_tokens


def is_synthetic(example: DatasetExample) -> bool:
    return example.model_version == "bootstrap-calibration-001" and example.id.startswith("BOOT-")


def academic_groups(examples: List[DatasetExample]) -> np.ndarray:
    """Componentes conectados: compartir una fuente en cualquier rol impide cruzar particiones."""
    parents = list(range(len(examples)))
    owners: Dict[Tuple[str, ...], int] = {}

    def root(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    for index, example in enumerate(examples):
        if is_synthetic(example):
            continue
        tokens = academic_source_tokens(example)
        for token in tokens:
            if token in owners:
                parents[root(index)] = root(owners[token])
            else:
                owners[token] = index

    return np.array([root(i) for i in range(len(examples))])


def split_examples(
    examples: List[DatasetExample], y: np.ndarray, test_size: float, random_state: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """El bootstrap solo entra al entrenamiento cuando existen observaciones reales."""
    synthetic = np.array([i for i, ex in enumerate(examples) if is_synthetic(ex)], dtype=int)
    real = np.array([i for i, ex in enumerate(examples) if not is_synthetic(ex)], dtype=int)
    groups = academic_groups(examples)
    if not len(real):
        _, counts = np.unique(y, return_counts=True)
        train, test = train_test_split(
            np.arange(len(examples)), test_size=test_size, random_state=random_state,
            stratify=y if counts.min() >= 2 else None,
        )
        return train, test, groups, {"strategy": "synthetic_stratified", "evaluation_scope": "synthetic",
                                     "eligible_for_auto_activation": False}

    if any(not all(value and value.strip() for value in (
        examples[i].source_university_obj, examples[i].source_course_obj,
        examples[i].source_university_cmp, examples[i].source_course_cmp,
    )) for i in real):
        raise ValueError("No se pueden certificar grupos académicos independientes: complete universidad y asignatura de ambos sílabos en las revisiones reales.")

    if len(np.unique(groups[real])) < 2:
        raise ValueError("Se requieren al menos dos grupos académicos independientes con universidad y asignatura para evaluar sin filtración de datos.")
    # Buscar una partición por grupos que conserve las clases reales en ambos conjuntos.
    classes = set(y[real])
    if len(classes) < 2:
        raise ValueError("La evaluación real requiere al menos dos clases revisadas por humanos.")
    candidates = GroupShuffleSplit(n_splits=128, test_size=test_size, random_state=random_state)
    valid = []
    for train_rel, test_rel in candidates.split(real, y[real], groups[real]):
        train, test = real[train_rel], real[test_rel]
        if set(y[train]) == classes and set(y[test]) == classes:
            valid.append((abs(len(test) / len(real) - test_size), train, test))
    if not valid:
        raise ValueError("No es posible separar grupos académicos conservando las clases en entrenamiento y evaluación. Añada revisiones de más asignaturas y universidades.")
    _, train, test = min(valid, key=lambda candidate: candidate[0])
    train_groups = sorted(int(g) for g in np.unique(groups[train]))
    test_groups = sorted(int(g) for g in np.unique(groups[test]))
    return np.concatenate((train, synthetic)), test, groups, {
        "strategy": "academic_connected_groups", "evaluation_scope": "human_reviews",
        "train_groups": train_groups, "test_groups": test_groups,
        "synthetic_train_count": len(synthetic), "synthetic_test_count": 0,
        "train_example_ids": [examples[i].id for i in train],
        "test_example_ids": [examples[i].id for i in test],
        "eligible_for_auto_activation": True,
    }
