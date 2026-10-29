"""Identidad de la aplicación y rutas locales configurables."""

import os
from pathlib import Path

APP_VERSION = "3.3.0"
APP_PHASE = 3
BACKEND_DIR = Path(__file__).resolve().parents[1]


def data_dir() -> Path:
    """Permite ejecutar pruebas o instancias con almacenamiento independiente."""
    return Path(os.environ.get("CONVCOMP_DATA_DIR", BACKEND_DIR / "data")).resolve()


def reports_dir() -> Path:
    return Path(os.environ.get("CONVCOMP_REPORTS_DIR", "data/reports")).resolve()
