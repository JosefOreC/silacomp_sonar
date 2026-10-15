"""Lotes y cierres independientes de las predicciones y revisiones originales."""

from dataclasses import asdict
from datetime import datetime
import json
from typing import List, Optional

from app.domain.active_learning import AnnotationCase, AnnotationCoverage, PriorityReason
from app.domain.annotation_batch import AnnotationBatch, AnnotationBatchCompletion
from app.domain.ports import IAnnotationBatchRepository
from app.infrastructure.persistence.database import DatabaseManager


class SqliteAnnotationBatchRepository(IAnnotationBatchRepository):
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def save(self, batch: AnnotationBatch) -> None:
        data = asdict(batch)
        data["created_at"] = batch.created_at.isoformat()
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO annotation_batches VALUES (?, ?, ?)",
                         (batch.id, json.dumps(data), data["created_at"]))

    @staticmethod
    def _decode(snapshot: str) -> AnnotationBatch:
        data = json.loads(snapshot)
        return AnnotationBatch(
            id=data["id"], reviewer_id=data["reviewer_id"], comparison_id=data["comparison_id"],
            strategy_version=data["strategy_version"], created_at=datetime.fromisoformat(data["created_at"]),
            reference_thresholds=data["reference_thresholds"],
            cases=[AnnotationCase(**{**case, "reason": PriorityReason(case["reason"]) if case["reason"] else None})
                   for case in data["cases"]],
            coverage_before=AnnotationCoverage(**data["coverage_before"]),
            scope_before=AnnotationCoverage(**data["scope_before"]),
        )

    def get_by_id(self, batch_id: str) -> Optional[AnnotationBatch]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT snapshot_json FROM annotation_batches WHERE id = ?", (batch_id,)).fetchone()
            return self._decode(row[0]) if row else None

    def list_recent(self, limit: int = 20) -> List[AnnotationBatch]:
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT snapshot_json FROM annotation_batches ORDER BY created_at DESC, id LIMIT ?", (limit,))
            return [self._decode(row[0]) for row in rows]

    def get_completion(self, batch_id: str) -> Optional[AnnotationBatchCompletion]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT snapshot_json FROM annotation_batch_completions WHERE batch_id = ?", (batch_id,)).fetchone()
            if not row:
                return None
            data = json.loads(row[0])
            return AnnotationBatchCompletion(data["batch_id"], datetime.fromisoformat(data["completed_at"]),
                                             AnnotationCoverage(**data["coverage_after"]), AnnotationCoverage(**data["scope_after"]))

    def complete(self, completion: AnnotationBatchCompletion) -> None:
        data = asdict(completion)
        data["completed_at"] = completion.completed_at.isoformat()
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO annotation_batch_completions VALUES (?, ?) ON CONFLICT(batch_id) DO NOTHING",
                         (completion.batch_id, json.dumps(data)))
