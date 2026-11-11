# Chladni Visualizer -- Interface Map

## Project Structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point with CLI argument parsing |
| `simulator.py` | `ChladniSimulator` class -- Pygame loop, rendering, input |
| `particle.py` | `Particle` class -- single sand grain physics |
| `pattern_generator.py` | `PatternGenerator` class -- static methods for each vibration mode |
| `presets.py` | Pygame-free presets: `PATTERN_PRESETS` (keys Q-O), `FREQUENCY_PRESETS` (keys 1-0), `SIZE_DISTRIBUTIONS`, `DISPLAY_MODES`, `pattern_function()`, `amplitude_map()` (body of `calculate_pattern`) |
| `constants.py` | All physics and display constants (no magic numbers) |
| `chladni_visualizer.py` | Original monolithic file (kept for reference) |
| `test_pattern_generator.py` | Tests for amplitude-map calculations |
| `test_particle.py` | Tests for particle physics |
| `run_web.py` | Starts the web app (uvicorn, http://127.0.0.1:8102) |
| `requirements-web.txt` | Pinned web/test dependencies |

## Web interface (`web/`)

| File | Purpose |
|------|---------|
| `web/app.py` | FastAPI app: `/api/info`, `/api/presets`, `/api/defaults`, `/api/pattern/{slug}` (NumPy grid via `presets.amplitude_map`); `STATIC_ENDPOINTS` |
| `web/static/index.html`, `style.css`, `core.js` | Shell, shared theme and router (web kit copies; `style.css`/`core.js` unchanged) |
| `web/static/style_app.css` | Sand-gold accent and page styles |
| `web/static/main.js` | Registers lazy pages, starts router |
| `web/static/static_api.js` | Answers `api()` from exported JSON on the static site |
| `web/static/chladni_engine.js` | JS port: `PATTERNS` (nine families), `amplitudeMap()`, `Sand` (Particle.update), `particleSize()`, `DEFAULTS` |
| `web/static/chladni_engine.test.mjs` | Node test vs Python numbers (FIXTURE block from `scripts/engine_fixture.py`) |
| `web/static/ui.js` | Shared controls, readout, `drawMap()`, `drawSand()`, colour looks, `loadSetup()` |
| `web/static/home.js` | `#/` hero with live plate, counts, cards |
| `web/static/plate.js` | `#/plate` the visualiser (controls + desktop key bindings) |
| `web/static/gallery.js` | `#/gallery` presets, `#/modes` mode table |
| `web/static/check.js` | `#/check` JS vs Python grids |
| `web/static/about.js` | `#/about` physics, controls, run instructions, credits |
| `scripts/build_static.py` | Exports the static site to `site/` |
| `scripts/screenshots.py` | Playwright smoke test and `docs/img/*.png` |
| `scripts/engine_fixture.py` | Computes the Python reference numbers for the node test (`--write`) |
| `tests/test_web.py` | API, static build, fixture-current and node engine tests |
| `.github/workflows/pages.yml` | Builds and publishes the static site on push to main |

## Key Classes

- **`Particle`** (`particle.py`): Represents a sand grain. Methods: `update()`, `_sample_amplitude()`, `_compute_forces()`, `_integrate()`, `_enforce_bounds()`.
- **`PatternGenerator`** (`pattern_generator.py`): Static methods for each pattern family: `classic_rectangular`, `circular_modes`, `interference_pattern`, `radial_symmetric`, `spiral_pattern`, `diamond_pattern`, `flower_pattern`, `wave_interference`, `complex_superposition`.
- **`ChladniSimulator`** (`simulator.py`): Owns the Pygame window, particle list, and main loop. Methods: `run()`, `handle_events()`, `calculate_pattern()`, `draw_*()`, `init_particles()`.

## Module Connections

```
main.py
  -> simulator.py (ChladniSimulator)
       -> particle.py (Particle)
       -> presets.py (presets, amplitude_map) -> pattern_generator.py (PatternGenerator)
       -> constants.py (all tunable parameters)

run_web.py -> web/app.py -> presets.py, pattern_generator.py, constants.py
web/static/main.js -> page modules -> ui.js, chladni_engine.js (JS port of pattern_generator.py + particle.py)
```
