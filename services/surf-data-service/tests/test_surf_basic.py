import importlib.util
from pathlib import Path
import pytest

# This file exists to avoid "fake tests" like `assert True`.
# It provides a minimal, REAL smoke test for the Surf Data service.
#
# NOTE: /forecast calls external APIs, so we MUST mock requests.get.

SERVICE_ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = SERVICE_ROOT / "app" / "main.py"

spec = importlib.util.spec_from_file_location("surf_data_main_basic", MAIN_PY)
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)

app = m.app

@pytest.fixture()
def client():
    app.config.update({"TESTING": True})
    with app.test_client() as c:
        yield c

def test_forecast_smoke_with_mocked_external_apis(client, monkeypatch):
    class FakeDateTime(m.datetime.datetime):
        @classmethod
        def utcnow(cls):
            return cls(2026, 2, 1, 12, 0, 0)

    monkeypatch.setattr(m.datetime, "datetime", FakeDateTime)
    now_str = FakeDateTime.utcnow().replace(minute=0, second=0, microsecond=0).isoformat()

    marine_json = {"hourly": {"time": [now_str], "wave_height": [1.5], "wave_period": [9], "wave_direction": [250]}}
    weather_json = {"hourly": {"time": [now_str], "temperature_2m": [17], "windspeed_10m": [12], "winddirection_10m": [80]}}

    class FakeResp:
        def __init__(self, payload):
            self._payload = payload
        def json(self):
            return self._payload

    def fake_get(url, params=None, timeout=None):
        if "marine-api.open-meteo.com" in url:
            return FakeResp(marine_json)
        if "api.open-meteo.com" in url:
            return FakeResp(weather_json)
        raise AssertionError("unexpected url: " + url)

    monkeypatch.setattr(m.requests, "get", fake_get)

    r = client.get("/forecast?spot=carcavelos")
    assert r.status_code == 200
    data = r.get_json()
    assert data["service"] == "surf-data-service"
    assert data["spot_key"] == "carcavelos"
    assert "waves" in data and "wind" in data and "temperature" in data
