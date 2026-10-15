"""API exclusiva de pruebas de navegador: almacenamiento efímero y NLP controlado.

No se debe importar desde producción. Las variables se fijan antes de app.main,
que inicializa el esquema al importarse. No hay endpoints de preparación/reset.
"""

import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="convcomp-browser-") as temporary:
        os.environ["CONVCOMP_DATA_DIR"] = str(Path(temporary) / "data")
        os.environ["CONVCOMP_REPORTS_DIR"] = str(Path(temporary) / "reports")
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"

        from fastapi.testclient import TestClient
        import uvicorn

        from app.api.deps import get_vector_service
        from app.main import app
        from tests.integration.test_ground_truth_endpoints import seed_comparison
        from tests.integration.test_scientific_evaluation_endpoints import (
            ControlledVectors, annotate_complete, register_candidate,
        )

        app.dependency_overrides[get_vector_service] = lambda: ControlledVectors()
        with TestClient(app) as client:
            for group in (1, 2):
                annotate_complete(client, group)
            seed_comparison(3, size=2)
            register_candidate()
        uvicorn.run(app, host="127.0.0.1", port=18765, log_level="warning")


if __name__ == "__main__":
    main()
