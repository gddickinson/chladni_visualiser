"""
Smoke tests for the Particle class.
"""

import numpy as np

from particle import Particle


def _flat_amplitude_map(value=0.0, size=50):
    """Return a uniform amplitude map."""
    return np.full((size, size), value)


def test_particle_initial_state():
    p = Particle(100, 200, size=2.5)
    assert p.x == 100
    assert p.y == 200
    assert p.vx == 0.0
    assert p.vy == 0.0
    assert p.z == 0.0
    assert not p.settled


def test_particle_settles_in_node():
    """A particle in a zero-amplitude region should eventually settle."""
    amp = _flat_amplitude_map(0.0)
    p = Particle(250, 250)
    for _ in range(100):
        p.update(0.016, amp, 500, 500)
    assert p.settled


def test_particle_moves_in_vibration():
    """A particle in a high-amplitude region should be displaced."""
    amp = _flat_amplitude_map(1.0)
    p = Particle(250, 250)
    start_x, start_y = p.x, p.y
    for _ in range(10):
        p.update(0.016, amp, 500, 500)
    moved = abs(p.x - start_x) + abs(p.y - start_y)
    assert moved > 0


def test_particle_stays_in_bounds():
    """Particles must remain inside the plate boundaries."""
    amp = _flat_amplitude_map(1.0)
    p = Particle(0, 0)
    p.vx = -1000
    p.vy = -1000
    p.update(0.1, amp, 500, 500)
    assert 0 <= p.x < 500
    assert 0 <= p.y < 500


def test_3d_attributes_exist():
    """Particle should always have z / vz attributes (no hasattr needed)."""
    p = Particle(10, 20)
    assert hasattr(p, "z")
    assert hasattr(p, "vz")
