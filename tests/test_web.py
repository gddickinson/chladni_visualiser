"""Web interface tests: every exported endpoint answers, the static build is complete, and the JS engine tests pass.

Run: python -m pytest -q tests/test_web.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.app import STATIC, STATIC_ENDPOINTS, app  # noqa: E402

client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200 and "static/main.js" in r.text


@pytest.mark.parametrize("path", STATIC_ENDPOINTS)
def test_endpoint(path):
    r = client.get("/api" + path)
    assert r.status_code == 200, r.text
    assert r.json() is not None


def test_static_build(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_static
    build_static.build(tmp_path / "site")
    assert (tmp_path / "site" / "index.html").read_text().count("APP_STATIC") == 1
    for path in STATIC_ENDPOINTS:
        assert (tmp_path / "site" / "api" / (path.strip("/") + ".json")).exists()


def test_static_assets_referenced_exist():
    html = (STATIC / "index.html").read_text()
    for name in ("style.css", "main.js"):
        assert f"static/{name}" in html and (STATIC / name).exists()


@pytest.mark.skipif(not shutil.which("node"), reason="node not installed")
def test_js_engine():
    tests = sorted(STATIC.glob("*.test.mjs"))
    for t in tests:
        r = subprocess.run(["node", str(t)], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr


# --- Chladni-specific API tests -------------------------------------------------------------------------------------
import numpy as np  # noqa: E402

import constants  # noqa: E402
from presets import FREQUENCY_PRESETS, PATTERN_PRESETS, amplitude_map, pattern_function  # noqa: E402


def test_presets_come_from_python():
    d = client.get("/api/presets").json()
    assert [(p["key"], p["method"], p["mode_x"], p["mode_y"]) for p in d["patterns"]] == \
        [(k, m, mx, my) for k, _s, _n, m, mx, my in PATTERN_PRESETS]
    assert [f["frequency"] for f in d["frequencies"]] == [f for _k, f, _n in FREQUENCY_PRESETS]
    assert all(p["summary"] for p in d["patterns"])


def test_defaults_are_constants():
    d = client.get("/api/defaults").json()
    assert d["FORCE_SCALE"] == constants.FORCE_SCALE and d["DEFAULT_FREQUENCY"] == constants.DEFAULT_FREQUENCY
    assert "WHITE" not in d


def test_pattern_grid_matches_generator():
    r = client.get("/api/pattern/flower?mode_x=5&mode_y=3&frequency=523.3&grid=40").json()
    ref = amplitude_map(pattern_function("flower_pattern"), 40, 5, 3, 523.3)
    assert np.allclose(np.array(r["values"]).reshape(40, 40), ref, atol=1e-6)
    assert client.get("/api/pattern/nope").status_code == 404
    assert client.get("/api/pattern/classic?grid=999").status_code == 422


def test_info_counts():
    d = client.get("/api/info").json()
    assert d["patterns"] == 9 and d["frequency_presets"] == 10 and "biharmonic" in d["background"]


def test_js_fixture_is_current():
    """The numbers embedded in chladni_engine.test.mjs still match the Python code."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import engine_fixture
    emb, now = engine_fixture.embedded(), engine_fixture.fixture()
    assert np.allclose([f[-1] for f in emb["fields"]], [f[-1] for f in now["fields"]], rtol=0, atol=1e-12)
    assert [f[:-1] for f in emb["fields"]] == [f[:-1] for f in now["fields"]]
    assert emb["particles"] == now["particles"] and emb["constants"] == now["constants"]
    assert np.allclose([m["sum"] for m in emb["maps"]], [m["sum"] for m in now["maps"]])
