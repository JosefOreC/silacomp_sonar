"""
Repositorio SQLite para persistencia y versionado de modelos de Machine Learning (Fase 2.0).
Implementa el puerto IModelVersionRepository.
"""

from datetime import datetime
import json
from typing import List, Optional

from app.domain.model_version import ModelVersion
from app.domain.ports import IModelVersionRepository
from app.infrastructure.persistence.database import DatabaseManager


class SqliteModelVersionRepository(IModelVersionRepository):
    """Gestión de versiones de algoritmos y modelos de aprendizaje supervisado sobre SQLite."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db = db_manager

    def save(self, model_version: ModelVersion) -> None:
        """Guarda o actualiza una versión de modelo registrada."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Si este modelo se marca como activo, desactivar los demás
            if model_version.is_active:
                cursor.execute("UPDATE model_versions SET is_active = 0;")

            cursor.execute(
                """
                INSERT INTO model_versions (
                    version_id, algorithm_name, description, parameters_json,
                    thresholds_json, metrics_json, is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(version_id) DO UPDATE SET
                    algorithm_name = excluded.algorithm_name,
                    description = excluded.description,
                    parameters_json = excluded.parameters_json,
                    thresholds_json = excluded.thresholds_json,
                    metrics_json = excluded.metrics_json,
                    is_active = excluded.is_active;
                """,
                (
                    model_version.version_id,
                    model_version.algorithm_name,
                    model_version.description,
                    json.dumps(model_version.parameters),
                    json.dumps(model_version.thresholds),
                    json.dumps(model_version.metrics),
                    1 if model_version.is_active else 0,
                    model_version.created_at.isoformat(),
                ),
            )
            conn.commit()

    def get_by_id(self, version_id: str) -> Optional[ModelVersion]:
        """Recupera una versión específica por su identificador."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM model_versions WHERE version_id = ?;", (version_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._map_row(row)

    def get_active_model(self) -> Optional[ModelVersion]:
        """Recupera la versión del modelo actualmente activo para producción."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM model_versions WHERE is_active = 1 ORDER BY created_at DESC LIMIT 1;")
            row = cursor.fetchone()
            if not row:
                return None
            return self._map_row(row)

    def set_active_model(self, version_id: str) -> bool:
        """Promueve un modelo candidato a activo y desactiva las versiones previas."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version_id FROM model_versions WHERE version_id = ?;", (version_id,))
            if not cursor.fetchone():
                return False

            cursor.execute("UPDATE model_versions SET is_active = 0;")
            cursor.execute("UPDATE model_versions SET is_active = 1 WHERE version_id = ?;", (version_id,))
            conn.commit()
            return True

    def list_all(self) -> List[ModelVersion]:
        """Lista todas las versiones de modelos registradas ordenadas cronológicamente."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM model_versions ORDER BY created_at DESC;")
            rows = cursor.fetchall()
            return [self._map_row(r) for r in rows]

    def _map_row(self, row: dict) -> ModelVersion:
        return ModelVersion(
            version_id=row["version_id"],
            algorithm_name=row["algorithm_name"],
            description=row["description"],
            parameters=json.loads(row["parameters_json"]) if row["parameters_json"] else {},
            thresholds=json.loads(row["thresholds_json"]) if row["thresholds_json"] else {},
            is_active=bool(row["is_active"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            metrics=json.loads(row["metrics_json"]) if row["metrics_json"] else {},
        )
