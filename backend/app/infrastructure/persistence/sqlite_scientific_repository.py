"""Persistencia append-only de conjuntos reservados y experimentos."""

from datetime import datetime
import json
import sqlite3
from typing import List, Optional

from app.domain.ports import IScientificEvaluationRepository
from app.domain.scientific_evaluation import EvaluationSnapshot, EvaluationExperiment, EvaluationValidationError
from app.infrastructure.persistence.database import DatabaseManager


class SqliteScientificRepository(IScientificEvaluationRepository):
    def __init__(self, db: DatabaseManager) -> None:
        self.db = db

    def save_snapshot(self, snapshot: EvaluationSnapshot) -> None:
        with self.db.get_connection() as conn:
            conn.execute("INSERT INTO evaluation_snapshots VALUES (?, ?, ?, ?, ?)",
                         (snapshot.id, snapshot.name, snapshot.created_at.isoformat(), snapshot.content_hash,
                          json.dumps(snapshot.payload, ensure_ascii=False, sort_keys=True, allow_nan=False)))

    @staticmethod
    def _snapshot(row: sqlite3.Row) -> EvaluationSnapshot:
        return EvaluationSnapshot(row["id"], row["name"], datetime.fromisoformat(row["created_at"]),
                                  row["content_hash"], json.loads(row["payload_json"]))

    def get_snapshot(self, snapshot_id: str) -> Optional[EvaluationSnapshot]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM evaluation_snapshots WHERE id = ?", (snapshot_id,)).fetchone()
            return self._snapshot(row) if row else None

    def list_snapshots(self) -> List[EvaluationSnapshot]:
        with self.db.get_connection() as conn:
            return [self._snapshot(row) for row in conn.execute("SELECT * FROM evaluation_snapshots ORDER BY created_at DESC, id")]

    def save_experiment(self, experiment: EvaluationExperiment) -> None:
        with self.db.get_connection() as conn:
            for evaluation in experiment.report["evaluations"].values():
                manifest = evaluation["manifest"]
                conn.execute("INSERT INTO evaluation_model_manifests VALUES (?, ?) ON CONFLICT(version_id) DO NOTHING",
                             (manifest["version_id"], manifest["manifest_hash"]))
                recorded = conn.execute("SELECT manifest_hash FROM evaluation_model_manifests WHERE version_id = ?",
                                        (manifest["version_id"],)).fetchone()[0]
                if recorded != manifest["manifest_hash"]:
                    raise EvaluationValidationError("La versión o su artefacto difiere de un experimento previo; registre otra versión.")
            conn.execute("INSERT INTO evaluation_experiments VALUES (?, ?, ?, ?)",
                         (experiment.id, experiment.snapshot_id, experiment.created_at.isoformat(),
                          json.dumps(experiment.report, ensure_ascii=False, sort_keys=True, allow_nan=False)))

    @staticmethod
    def _experiment(row: sqlite3.Row) -> EvaluationExperiment:
        return EvaluationExperiment(row["id"], row["snapshot_id"], datetime.fromisoformat(row["created_at"]),
                                    json.loads(row["report_json"]))

    def get_experiment(self, experiment_id: str) -> Optional[EvaluationExperiment]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM evaluation_experiments WHERE id = ?", (experiment_id,)).fetchone()
            return self._experiment(row) if row else None

    def list_experiments(self, limit: int = 20) -> List[EvaluationExperiment]:
        with self.db.get_connection() as conn:
            return [self._experiment(row) for row in conn.execute(
                "SELECT * FROM evaluation_experiments ORDER BY created_at DESC, id LIMIT ?", (limit,))]
