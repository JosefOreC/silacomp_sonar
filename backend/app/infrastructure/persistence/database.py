"""
Gestor de base de datos SQLite para persistencia relacional local (Fase 1).
"""

import os
import sqlite3
from typing import Optional


DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data", "convcomp.db")


class DatabaseManager:
    """Administra conexiones y migraciones de esquema para SQLite."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = db_path or DEFAULT_DB_PATH
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self.init_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Retorna una conexión configurada con soporte para claves foráneas y filas tipo dict."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_schema(self) -> None:
        """Crea las tablas de persistencia si no existen."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Tabla de Sílabos
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS syllabi (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size_bytes INTEGER NOT NULL,
                sha256_hash TEXT NOT NULL,
                total_pages INTEGER NOT NULL,
                university TEXT,
                course_name TEXT,
                course_code TEXT,
                academic_term TEXT,
                created_at TEXT NOT NULL
            );
            """)

            # Páginas extraídas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS syllabus_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                syllabus_id TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                raw_text TEXT NOT NULL,
                character_count INTEGER NOT NULL,
                FOREIGN KEY (syllabus_id) REFERENCES syllabi(id) ON DELETE CASCADE,
                UNIQUE(syllabus_id, page_number)
            );
            """)

            # Secciones canónicas
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS syllabus_sections (
                id TEXT PRIMARY KEY,
                syllabus_id TEXT NOT NULL,
                title TEXT NOT NULL,
                section_type TEXT NOT NULL,
                order_num INTEGER NOT NULL,
                page_start INTEGER NOT NULL,
                page_end INTEGER NOT NULL,
                FOREIGN KEY (syllabus_id) REFERENCES syllabi(id) ON DELETE CASCADE
            );
            """)

            # Contenidos discretos segmentados
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_items (
                id TEXT PRIMARY KEY,
                syllabus_id TEXT NOT NULL,
                section_name TEXT NOT NULL,
                title TEXT NOT NULL,
                text TEXT NOT NULL,
                normalized_text TEXT NOT NULL,
                page_start INTEGER NOT NULL,
                page_end INTEGER NOT NULL,
                order_num INTEGER NOT NULL,
                unit_number INTEGER,
                FOREIGN KEY (syllabus_id) REFERENCES syllabi(id) ON DELETE CASCADE
            );
            """)

            # Comparaciones
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS comparisons (
                id TEXT PRIMARY KEY,
                objective_syllabus_id TEXT NOT NULL,
                compared_syllabus_id TEXT NOT NULL,
                global_score REAL NOT NULL,
                objective_coverage REAL NOT NULL,
                compared_coverage REAL NOT NULL,
                model_version TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (objective_syllabus_id) REFERENCES syllabi(id),
                FOREIGN KEY (compared_syllabus_id) REFERENCES syllabi(id)
            );
            """)

            # Correspondencias evaluadas (Predicciones IA)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_matches (
                id TEXT PRIMARY KEY,
                comparison_id TEXT NOT NULL,
                objective_item_id TEXT NOT NULL,
                compared_item_id TEXT NOT NULL,
                objective_title TEXT NOT NULL,
                compared_title TEXT NOT NULL,
                objective_section TEXT NOT NULL,
                compared_section TEXT NOT NULL,
                objective_page INTEGER NOT NULL,
                compared_page INTEGER NOT NULL,
                semantic_sim REAL NOT NULL,
                lexical_sim REAL NOT NULL,
                keyword_overlap REAL NOT NULL,
                structural_sim REAL NOT NULL,
                composite_score REAL NOT NULL,
                classification TEXT NOT NULL,
                evidence_type TEXT NOT NULL,
                shared_keywords_json TEXT NOT NULL,
                objective_snippet TEXT NOT NULL,
                compared_snippet TEXT NOT NULL,
                evidence_regions_json TEXT,
                FOREIGN KEY (comparison_id) REFERENCES comparisons(id) ON DELETE CASCADE
            );
            """)

            # Migraciones no destructivas para Fase 1.5
            try:
                cursor.execute("ALTER TABLE content_matches ADD COLUMN evidence_regions_json TEXT;")
            except sqlite3.OperationalError:
                pass


            # Contenidos no correspondidos (brechas en ambos sentidos)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS unmatched_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comparison_id TEXT NOT NULL,
                syllabus_role TEXT NOT NULL, -- 'OBJECTIVE' o 'COMPARED'
                item_id TEXT NOT NULL,
                syllabus_id TEXT NOT NULL,
                section_name TEXT NOT NULL,
                title TEXT NOT NULL,
                text_snippet TEXT NOT NULL,
                page INTEGER NOT NULL,
                best_candidate_id TEXT,
                best_candidate_title TEXT,
                best_score REAL,
                FOREIGN KEY (comparison_id) REFERENCES comparisons(id) ON DELETE CASCADE
            );
            """)

            # Revisiones Humanas (Inmutables, nunca sobrescriben la predicción IA)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id TEXT PRIMARY KEY,
                comparison_id TEXT NOT NULL,
                match_id TEXT,
                prediction_before TEXT,
                human_decision TEXT NOT NULL,
                correction_type TEXT NOT NULL,
                justification TEXT NOT NULL,
                reviewer_id TEXT NOT NULL,
                model_version TEXT NOT NULL,
                created_at TEXT NOT NULL,
                manual_obj_id TEXT,
                manual_cmp_id TEXT,
                FOREIGN KEY (comparison_id) REFERENCES comparisons(id) ON DELETE CASCADE
            );
            """)

            # Dataset Staging (para entrenamiento supervisado en Fase 2)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS dataset_examples (
                id TEXT PRIMARY KEY,
                review_id TEXT NOT NULL,
                objective_item_id TEXT NOT NULL,
                compared_item_id TEXT NOT NULL,
                objective_text TEXT NOT NULL,
                compared_text TEXT NOT NULL,
                features_json TEXT NOT NULL,
                prediction_label TEXT NOT NULL,
                ground_truth_label TEXT NOT NULL,
                model_version TEXT NOT NULL,
                source_university_obj TEXT,
                source_university_cmp TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
            );
            """)

            # Registro de Informes Formales Generados
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                report_id TEXT PRIMARY KEY,
                comparison_id TEXT NOT NULL,
                report_format TEXT NOT NULL,
                report_version TEXT NOT NULL,
                file_path TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                model_version TEXT NOT NULL,
                file_size_bytes INTEGER DEFAULT 0,
                FOREIGN KEY (comparison_id) REFERENCES comparisons(id) ON DELETE CASCADE
            );
            """)

            conn.commit()
