import importlib.util
from pathlib import Path
import pytest

# This file exists to avoid "fake tests" like `assert True`.
# It provides a minimal, REAL smoke test for the Gateway service.

SERVICE_ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = SERVICE_ROOT / "app" / "main.py"

spec = importlib.util.spec_from_file_location("gateway_main_basic", MAIN_PY)
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)

app = m.app

@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "TEST")
    app.config.update({"TESTING": True})
    with app.test_client() as c:
        yield c

def test_health_smoke(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "gateway"
