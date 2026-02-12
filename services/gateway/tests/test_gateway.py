import importlib.util
from pathlib import Path
import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = SERVICE_ROOT / "app" / "main.py"

import os
os.environ.setdefault('OTEL_DISABLED','1')

spec = importlib.util.spec_from_file_location("gateway_main", MAIN_PY)
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

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "gateway"

def test_api_report_calls_data_service(client, monkeypatch):
    class FakeResp:
        def json(self):
            return {"spot": "Carcavelos", "wind": {"speed_kmh": 10}}

    def fake_get(url, params=None, timeout=None):
        assert url.endswith("/forecast")
        assert params["spot"] == "carcavelos"
        return FakeResp()

    monkeypatch.setattr(m.requests, "get", fake_get)

    r = client.get("/api/report?spot=carcavelos")
    assert r.status_code == 200
    data = r.get_json()
    assert data["spot"] == "carcavelos"
    assert data["report"]["spot"] == "Carcavelos"

def test_send_daily_requires_token(client):
    r = client.post("/internal/send-daily")
    assert r.status_code == 401

def test_send_daily_sends_to_notification_service(client, monkeypatch):
    m.INTERNAL_TOKEN = "test-token"

    class FakeGetResp:
        def json(self):
            return {"spot": "Carcavelos", "utc_hour": "2026-01-01T00:00:00Z",
                    "wind": {"speed_kmh": 10, "direction_deg": 90},
                    "waves": {"height_m": 1.2, "period_s": 10, "direction_deg": 270},
                    "temperature": {"air_c": 18}}

    posted = []

    class FakePostResp:
        def __init__(self, payload):
            self._payload = payload
        def json(self):
            return {"status": "queued", "channel": self._payload["channel"], "to": self._payload["to"]}

    def fake_get(url, params=None, timeout=None):
        return FakeGetResp()

    def fake_post(url, json=None, timeout=None):
        posted.append(json)
        return FakePostResp(json)

    monkeypatch.setattr(m.requests, "get", fake_get)
    monkeypatch.setattr(m.requests, "post", fake_post)

    r = client.post("/internal/send-daily?spot=carcavelos", headers={"X-Internal-Token":"test-token"})
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "sent"
    assert data["count"] == 2
    assert len(posted) == 2

