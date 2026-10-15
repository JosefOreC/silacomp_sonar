"""Snapshots y experimentos inmutables de evaluación de comparaciones completas."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict
import hashlib
import json


@dataclass(frozen=True)
class EvaluationSnapshot:
    id: str
    name: str
    created_at: datetime
    content_hash: str
    payload: Dict[str, Any]


@dataclass(frozen=True)
class EvaluationExperiment:
    id: str
    snapshot_id: str
    created_at: datetime
    report: Dict[str, Any]


class EvaluationValidationError(ValueError):
    pass


def evaluation_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()
