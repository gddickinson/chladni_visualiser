# Session Log

## 2026-11-11 -- Web interface and static GitHub Pages site (branch `web-interface`)
- Added `presets.py` (Pygame-free): pattern presets, musical-note frequency presets, size distributions, display modes
  and `amplitude_map()`; `simulator.py` now builds its key maps and `calculate_pattern()` from it (behaviour unchanged,
  checked headless with SDL dummy driver).
- Added `web/` (FastAPI app + ES-module front end, shared web kit): Visualiser, Gallery, Mode table, Cross-check, About.
- `web/static/chladni_engine.js`: JS port of all nine `PatternGenerator` methods, `amplitude_map` and `Particle.update`.
  Node test checks 180 point values, 9 normalised maps and 3 particle trajectories (fixed random sequence) against the
  Python, plus constants and a settling check. `tests/test_web.py` verifies the embedded fixture is current.
- Note: at speed 1 the particle model concentrates sand slowly (about 21% -> 28% of grains on the nodal band after
  120 s simulated, Python and JS alike); the web page adds a time-lapse control and starts at 6,000 grains / speed 3.
- Static build, `scripts/screenshots.py` (static and against `run_web.py` on 8102) all ok; screenshots in `docs/img/`.
- Not ported: the desktop 3D view. `main.py --mode` is parsed but not applied by the desktop app (pre-existing).
