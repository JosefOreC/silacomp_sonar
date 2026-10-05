"""
Pruebas de integración de ciclo de vida de modelos ML y endpoints REST (Fase 2.0).
"""

from fastapi.testclient import TestClient
import pytest

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_list_models_returns_baseline_or_registered(client: TestClient) -> None:
    res = client.get("/api/models")
    assert res.status_code == 200
    models = res.json()
    assert len(models) >= 1
    assert any(m["is_active"] for m in models)


def test_train_model_and_activate_lifecycle(client: TestClient) -> None:
    # 1. Entrenar nuevo modelo supervisado
    res_train = client.post(
        "/api/models/train",
        json={
            "algorithm": "calibrated_logistic",
            "test_size": 0.25,
            "use_bootstrap": True,
            "auto_activate": False,
        },
    )
    assert res_train.status_code == 201
    model_data = res_train.json()
    version_id = model_data["version_id"]
    assert "metrics" in model_data
    assert model_data["metrics"]["accuracy"] > 0.60
    assert model_data["is_active"] is False

    # 2. Consultar evaluación del modelo
    res_eval = client.get(f"/api/models/{version_id}/evaluation")
    assert res_eval.status_code == 200
    eval_data = res_eval.json()
    assert eval_data["version_id"] == version_id
    assert "confusion_matrix" in eval_data["metrics"]

    # 3. Activar el modelo para producción
    res_act = client.post(f"/api/models/{version_id}/activate")
    assert res_act.status_code == 200

    # 4. Verificar que /active ahora retorna el modelo activado
    res_active = client.get("/api/models/active")
    assert res_active.status_code == 200
    active_data = res_active.json()
    assert active_data["version_id"] == version_id
    assert active_data["is_active"] is True


def test_dataset_export_csv_and_json(client: TestClient) -> None:
    # 1. Exportación JSON
    res_json = client.get("/api/dataset/export?format=json")
    assert res_json.status_code == 200
    assert isinstance(res_json.json(), list)

    # 2. Exportación CSV
    res_csv = client.get("/api/dataset/export?format=csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers.get("content-type", "")
    assert "semantic_sim" in res_csv.text
