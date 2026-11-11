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

## 2026-11-11 -- Bug fixes after review (branch `web-interface`, fast-forwarded to main)
- `main.py --mode` now selects the starting pattern and its preset modes (new `ChladniSimulator.set_pattern(slug)`,
  `pattern=` constructor argument; choices come from `presets.PATTERN_SLUGS`). `--particles` is clamped to 100-20,000.
- Shift + / Shift - (particle size range) only worked with the left Shift key; now either Shift (`event.mod`).
- README controls table described keys the code never had (arrows for mode numbers, T to cycle, R reset); replaced
  with the real bindings and `python main.py`. Documented (not changed): key 3 toggles 3D mode, so the D4 frequency
  preset bound to it is unreachable -- rebinding is George's call.
- `simulator.py` was over 500 lines: the 3-D view moved unchanged into `view3d.py` (`View3DMixin`).
- New `test_main.py` (headless SDL dummy driver): --mode for all 9 patterns, unknown mode rejected, particle clamp,
  right Shift, 3-D drawing for every camera view. Repo tests 66 passed; tests/test_web.py 21 passed; static and server
  smoke tests ok (server check on port 8112 because 8102 was held by another run_web.py from this repo, left running).
