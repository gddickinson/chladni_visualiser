"""
Tests for the command-line entry point: --mode selects the starting
pattern and --particles the grain count.  Runs Pygame headless (SDL
dummy video/audio drivers); skipped when Pygame is not installed.
"""

import os

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
pygame = pytest.importorskip("pygame")

import main  # noqa: E402
from pattern_generator import PatternGenerator  # noqa: E402
from presets import PATTERN_PRESETS, PATTERN_SLUGS  # noqa: E402


def _sim(*argv):
    return main.build_simulator(main.parse_args(["--width", "300", "--height", "200", *argv]))


def test_default_mode_is_classic():
    sim = _sim()
    assert sim.current_pattern_func is PatternGenerator.classic_rectangular
    assert (sim.mode_x, sim.mode_y) == (3, 2)


@pytest.mark.parametrize("preset", PATTERN_PRESETS, ids=PATTERN_SLUGS)
def test_mode_selects_pattern(preset):
    _key, slug, name, method, mx, my = preset
    sim = _sim("--mode", slug)
    assert sim.current_pattern_name == name
    assert sim.current_pattern_func is getattr(PatternGenerator, method)
    assert (sim.mode_x, sim.mode_y) == (mx, my)


def test_unknown_mode_rejected():
    with pytest.raises(SystemExit):
        main.parse_args(["--mode", "triangle"])


def test_particles_clamped():
    assert len(_sim("--particles", "300").particles) == 300
    assert len(_sim("--particles", "5").particles) == 100  # MIN_PARTICLES


def test_right_shift_changes_size_range():
    sim = _sim()
    before = sim.particle_size_max
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_EQUALS, mod=pygame.KMOD_RSHIFT))
    sim.handle_events()
    assert sim.particle_size_max > before and sim.speed_multiplier == 1.0


def test_3d_view_draws_every_camera():
    """3-D drawing (view3d.View3DMixin) runs for every camera view."""
    sim = _sim("--mode", "spiral", "--particles", "200")
    sim.mode_3d = True
    pattern = sim.calculate_pattern()
    for view in sim.camera_views:
        sim.camera_view = view
        sim.update_particles(0.016, pattern)
        sim.draw_3d_background(pattern)
        sim.draw_particles()
        assert isinstance(sim.project_3d(10, 20, 5)[0], int)
    sim.draw_ui()
