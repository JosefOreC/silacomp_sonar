"""Solicitudes idempotentes y resultados append-only de comparaciones por lote."""

from dataclasses import asdict
from datetime import datetime
import json
import sqlite3

from app.domain.comparison_batch import BatchResult, BatchSyllabus, ComparisonBatch
from app.infrastructure.persistence.database import DatabaseManager


class SqliteComparisonBatchRepository:
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def create(self, batch: ComparisonBatch) -> bool:
        payload = asdict(batch)
        payload["created_at"] = batch.created_at.isoformat()
        with self.db.get_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO comparison_batches VALUES (?, ?, ?) ON CONFLICT(id) DO NOTHING",
                (batch.id, batch.created_at.isoformat(), json.dumps(payload, ensure_ascii=False, allow_nan=False)),
            )
            return cursor.rowcount == 1

    @staticmethod
    def _batch(row: sqlite3.Row) -> ComparisonBatch:
        payload = json.loads(row["payload_json"])
        return ComparisonBatch(
            id=payload["id"], objective=BatchSyllabus(**payload["objective"]),
            candidates=tuple(BatchSyllabus(**candidate) for candidate in payload["candidates"]),
            model_version=payload["model_version"], weights=payload["weights"], thresholds=payload["thresholds"],
            created_at=datetime.fromisoformat(payload["created_at"]),
        )

    def get(self, batch_id: str) -> ComparisonBatch | None:
        with self.db.get_connection() as connection:
            row = connection.execute("SELECT * FROM comparison_batches WHERE id = ?", (batch_id,)).fetchone()
            return self._batch(row) if row else None

    def list_recent(self, limit: int) -> list[ComparisonBatch]:
        with self.db.get_connection() as connection:
            return [self._batch(row) for row in connection.execute(
                "SELECT * FROM comparison_batches ORDER BY created_at DESC, id LIMIT ?", (limit,),
            )]

    def add_result(self, batch_id: str, result: BatchResult) -> None:
        with self.db.get_connection() as connection:
            connection.execute("INSERT INTO comparison_batch_results VALUES (?, ?, ?)", (
                batch_id, result.compared_syllabus_id, json.dumps(asdict(result), ensure_ascii=False, allow_nan=False),
            ))

    def get_results(self, batch_id: str) -> tuple[BatchResult, ...]:
        with self.db.get_connection() as connection:
            return tuple(BatchResult(**json.loads(row["payload_json"])) for row in connection.execute(
                "SELECT payload_json FROM comparison_batch_results WHERE batch_id = ? ORDER BY compared_syllabus_id",
                (batch_id,),
            ))

    def complete(self, batch_id: str, completed_at: datetime) -> None:
        with self.db.get_connection() as connection:
            connection.execute(
                "INSERT INTO comparison_batch_completions VALUES (?, ?) ON CONFLICT(batch_id) DO NOTHING",
                (batch_id, completed_at.isoformat()),
            )

    def get_completion(self, batch_id: str) -> datetime | None:
        with self.db.get_connection() as connection:
            row = connection.execute(
                "SELECT completed_at FROM comparison_batch_completions WHERE batch_id = ?", (batch_id,),
            ).fetchone()
            return datetime.fromisoformat(row[0]) if row else None
