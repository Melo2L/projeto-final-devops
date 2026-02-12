import importlib.util
from pathlib import Path
import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
MAIN_PY = SERVICE_ROOT / "app" / "main.py"

spec = importlib.util.spec_from_file_location("scheduler_main", MAIN_PY)
m = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(m)

def test_run_once_posts_to_gateway(monkeypatch):
    called = {"count": 0}

    class FakeResp:
        status_code = 200
        text = "ok"

    def fake_post(url, headers=None, timeout=None):
        called["count"] += 1
        assert "/internal/send-daily" in url
        assert headers.get("X-Internal-Token") == m.INTERNAL_TOKEN
        return FakeResp()

    monkeypatch.setattr(m.requests, "post", fake_post)

    m.run_once()
    assert called["count"] == 1

