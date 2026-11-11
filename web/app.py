"""FastAPI web app for the Chladni Visualizer: serves the front end in static/ and the JSON API under /api.

Run with `python run_web.py` (http://127.0.0.1:8102, local only). `scripts/build_static.py` exports every path in
STATIC_ENDPOINTS to JSON for the GitHub Pages site, so keep that list in step with the GET routes below.

Everything here comes from the desktop app's own modules: presets.py (pattern / frequency presets, amplitude_map),
pattern_generator.py (the pattern functions and their docstrings) and constants.py (physics and display constants).
"""
import inspect
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import constants  # noqa: E402
import pattern_generator  # noqa: E402
from presets import (  # noqa: E402
    DISPLAY_MODES, FREQUENCY_PRESETS, PATTERN_PRESETS, SIZE_DISTRIBUTIONS, amplitude_map, pattern_function,
)

STATIC = Path(__file__).resolve().parent / "static"
TITLE = "Chladni Visualizer"
SERVER_GRID = 48  # grid of the server-rendered patterns exported to the static site

app = FastAPI(title=TITLE)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def _doc(obj):
    return inspect.cleandoc(obj.__doc__ or "")


def _pattern(key, slug, name, method, mx, my):
    doc = _doc(pattern_function(method)).split("\n\n")
    return {"key": key, "slug": slug, "name": name, "method": method, "mode_x": mx, "mode_y": my,
            "summary": doc[0], "detail": " ".join(" ".join(doc[1:]).split())}


PATTERNS = {p[1]: _pattern(*p) for p in PATTERN_PRESETS}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info():
    """Project summary and counts for the home page."""
    return {"title": TITLE, "version": "1", "patterns": len(PATTERN_PRESETS),
            "frequency_presets": len(FREQUENCY_PRESETS), "max_particles": constants.MAX_PARTICLES,
            "grid_size": constants.DEFAULT_GRID_SIZE, "size_distributions": len(SIZE_DISTRIBUTIONS),
            "background": " ".join(_doc(pattern_generator).split("Physics background\n------------------\n")[-1].split())}


@app.get("/api/presets")
def presets():
    """Pattern presets (keys Q-O, with the generator docstrings), musical frequency presets (keys 1-0), options."""
    return {"patterns": list(PATTERNS.values()),
            "frequencies": [{"key": k, "frequency": f, "note": n} for k, f, n in FREQUENCY_PRESETS],
            "size_distributions": SIZE_DISTRIBUTIONS, "display_modes": DISPLAY_MODES}


@app.get("/api/defaults")
def defaults():
    """Physics and display constants from constants.py (colour tuples left out)."""
    return {k: getattr(constants, k) for k in dir(constants)
            if k.isupper() and isinstance(getattr(constants, k), (int, float))}


@app.get("/api/pattern/{slug}")
def pattern(slug: str, mode_x: int | None = Query(None, ge=0, le=40), mode_y: int | None = Query(None, ge=0, le=40),
            frequency: float = Query(constants.DEFAULT_FREQUENCY, gt=0, le=5000),
            grid: int = Query(SERVER_GRID, ge=2, le=200)):
    """Normalised amplitude map computed by the real Python generator (presets.amplitude_map), for cross-checking."""
    if slug not in PATTERNS:
        raise HTTPException(404, f"unknown pattern {slug!r}")
    p = PATTERNS[slug]
    mx = p["mode_x"] if mode_x is None else mode_x
    my = p["mode_y"] if mode_y is None else mode_y
    m = amplitude_map(pattern_function(p["method"]), grid, mx, my, frequency)
    return {"slug": slug, "method": p["method"], "mode_x": mx, "mode_y": my, "frequency": frequency, "grid": grid,
            "values": [round(float(v), 7) for v in m.ravel()], "source": "presets.amplitude_map (NumPy)"}


# GET paths (without the /api prefix) written to the static site as api/<path>.json.
STATIC_ENDPOINTS = ["/info", "/presets", "/defaults"] + [f"/pattern/{slug}" for slug in PATTERNS]
