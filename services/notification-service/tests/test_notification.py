import importlib.util
from pathlib import Path
import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = SERVICE_ROOT / "app" / "main.py"

spec = importlib.util.spec_from_file_location("notification_main", MAIN_PY)
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)

app = m.app

@pytest.fixture()
def client():
    app.config.update({"TESTING": True})
    with app.test_client() as c:
        yield c

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "healthy"

def test_send(client):
    payload = {"channel":"email","to":"a@b.com","subject":"x","message":"hello"}
    r = client.post("/send", json=payload)
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "queued"
    assert data["channel"] == "email"

