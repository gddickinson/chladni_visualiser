# Chladni Visualizer

See @INTERFACE.md for the project navigation map.

## Quick Start
```bash
pip install -r requirements.txt
python main.py
```

## Testing
```bash
python -m pytest test_pattern_generator.py test_particle.py test_main.py -v   # test_main needs pygame (headless)
python -m pytest -q tests/test_web.py      # web app + JS engine (needs node)
```

## Web
`python run_web.py` (port 8102). `web/static/chladni_engine.js` mirrors `pattern_generator.py` and `particle.py`:
change both together and rerun `python scripts/engine_fixture.py --write`.
