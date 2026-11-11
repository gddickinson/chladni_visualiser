"""Web interface for the Chladni Visualizer.

Contents:
    app.py      FastAPI app: front end from static/, JSON API under /api (presets, defaults, Python-computed patterns),
                STATIC_ENDPOINTS exported by scripts/build_static.py for the GitHub Pages site.
    static/     ES-module front end (no build step); chladni_engine.js is the JS port of pattern_generator.py and
                particle.py used by every page, checked by chladni_engine.test.mjs.
"""
