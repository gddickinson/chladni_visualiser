"""Compute reference numbers with the repo's Python code for web/static/chladni_engine.test.mjs.

The node test embeds this JSON between the FIXTURE markers; tests/test_web.py recomputes it and checks the embedded
copy still matches the Python (so the JS is always compared against the current pattern_generator.py / particle.py).

Run: python scripts/engine_fixture.py            (print JSON)
     python scripts/engine_fixture.py --write    (rewrite the block inside chladni_engine.test.mjs)
"""
import argparse
import json
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import constants  # noqa: E402
import particle as particle_mod  # noqa: E402
from presets import PATTERN_PRESETS, amplitude_map, pattern_function  # noqa: E402

TEST_FILE = ROOT / "web" / "static" / "chladni_engine.test.mjs"
POINTS = [(0.0, 0.0), (0.13, 0.71), (0.5, 0.5), (0.37, 0.92), (1.0, 0.25)]
MODES = [(3, 2, 1.0), (1, 1, 0.5), (5, 4, 1.337), (2, 7, 2.6)]
RANDS = [0.12, 0.93, 0.47, 0.05, 0.71, 0.33, 0.88, 0.21, 0.64, 0.99, 0.02, 0.56]


def field_cases():
    out = []
    for _key, _slug, _name, method, _mx, _my in PATTERN_PRESETS:
        f = pattern_function(method)
        for mx, my, ff in MODES:
            for x, y in POINTS:
                v = f(np.array([[x]]), np.array([[y]]), mx, my, ff)
                out.append([method, mx, my, ff, x, y, float(np.asarray(v).ravel()[0])])
    return out


def map_cases():
    out = []
    for _key, slug, _name, method, mx, my in PATTERN_PRESETS:
        m = amplitude_map(pattern_function(method), 24, mx, my, 523.3)
        out.append({"method": method, "n": 24, "mx": mx, "my": my, "freq": 523.3,
                    "sum": float(m.sum()), "row7": [float(v) for v in m[7]]})
    return out


def particle_cases():
    """Trajectories of Particle.update with a fixed random() sequence."""
    amp = amplitude_map(pattern_function("classic_rectangular"), 30, 3, 2, 440.0)
    cases = []
    for x0, y0, vx0, vy0, speed in [(700.0, 500.0, 0.0, 0.0, 1.0), (233.0, 512.0, 40.0, -15.0, 1.0),
                                    (5.0, 995.0, -300.0, 260.0, 2.5)]:
        seq = iter(RANDS * 20)
        particle_mod.random.random = lambda: next(seq)
        p = particle_mod.Particle(x0, y0)
        p.vx, p.vy = vx0, vy0
        traj = []
        for _ in range(12):
            p.update(0.016, amp, 1400, 1000, speed)
            traj.append([p.x, p.y, p.vx, p.vy, int(p.settled)])
        cases.append({"start": [x0, y0, vx0, vy0], "speed": speed, "traj": traj})
    particle_mod.random.random = random.random
    return {"map": {"method": "classic_rectangular", "n": 30, "mx": 3, "my": 2, "freq": 440.0},
            "rands": RANDS, "cases": cases}


def fixture():
    consts = {k: getattr(constants, k) for k in dir(constants) if k.isupper() and not isinstance(getattr(constants, k), tuple)}
    return {"fields": field_cases(), "maps": map_cases(), "particles": particle_cases(), "constants": consts}


def embedded():
    m = re.search(r"/\* FIXTURE-BEGIN \*/(.*)/\* FIXTURE-END \*/", TEST_FILE.read_text(), re.S)
    return json.loads(m.group(1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    text = json.dumps(fixture(), separators=(",", ":"))
    if not ap.parse_args().write:
        print(text)
        return
    src = TEST_FILE.read_text()
    src = re.sub(r"/\* FIXTURE-BEGIN \*/.*/\* FIXTURE-END \*/", lambda _: f"/* FIXTURE-BEGIN */{text}/* FIXTURE-END */", src, flags=re.S)
    TEST_FILE.write_text(src)
    print(f"wrote fixture ({len(text)} chars) into {TEST_FILE.name}")


if __name__ == "__main__":
    main()
