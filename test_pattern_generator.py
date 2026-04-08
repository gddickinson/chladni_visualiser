"""
Smoke tests for PatternGenerator amplitude-map calculations.

These verify basic mathematical properties that every valid Chladni
pattern should satisfy, without needing a Pygame display.
"""

import numpy as np
import pytest

from pattern_generator import PatternGenerator


# Helpers ---------------------------------------------------------------

def _make_grid(n=50):
    """Return (X, Y) meshgrid on [0, 1]."""
    t = np.linspace(0, 1, n)
    return np.meshgrid(t, t)


def _normalised_abs(pattern_func, mode_x=3, mode_y=2, freq=1.0, n=50):
    """Compute |pattern| normalised to [0, 1]."""
    X, Y = _make_grid(n)
    raw = pattern_func(X, Y, mode_x, mode_y, freq)
    out = np.abs(raw)
    mx = np.max(out)
    if mx > 0:
        out /= mx
    return out


# All pattern functions to test
ALL_PATTERNS = [
    PatternGenerator.classic_rectangular,
    PatternGenerator.circular_modes,
    PatternGenerator.interference_pattern,
    PatternGenerator.radial_symmetric,
    PatternGenerator.spiral_pattern,
    PatternGenerator.diamond_pattern,
    PatternGenerator.flower_pattern,
    PatternGenerator.wave_interference,
    PatternGenerator.complex_superposition,
]


# Tests -----------------------------------------------------------------

@pytest.mark.parametrize("func", ALL_PATTERNS)
def test_output_shape(func):
    """Pattern should return an array with the same shape as the input grid."""
    X, Y = _make_grid(40)
    result = func(X, Y, 3, 2, 1.0)
    assert result.shape == X.shape


@pytest.mark.parametrize("func", ALL_PATTERNS)
def test_no_nan_or_inf(func):
    """Pattern values should be finite for all grid points."""
    X, Y = _make_grid(40)
    result = func(X, Y, 3, 2, 1.0)
    assert np.all(np.isfinite(result))


@pytest.mark.parametrize("func", ALL_PATTERNS)
def test_normalised_range(func):
    """After abs + normalise, values should lie in [0, 1]."""
    normed = _normalised_abs(func)
    assert normed.min() >= 0.0
    assert normed.max() <= 1.0 + 1e-9


@pytest.mark.parametrize("func", ALL_PATTERNS)
def test_nodal_lines_exist(func):
    """Normalised pattern should contain regions near zero (nodal lines)."""
    normed = _normalised_abs(func, n=100)
    # At least 5% of points should be below 0.1 (near a node)
    frac_near_zero = np.mean(normed < 0.1)
    assert frac_near_zero > 0.01, (
        f"Expected some near-zero values, got fraction {frac_near_zero:.4f}"
    )


@pytest.mark.parametrize("func", ALL_PATTERNS)
def test_freq_changes_pattern(func):
    """Different freq_factors should produce different patterns."""
    X, Y = _make_grid(40)
    r1 = func(X, Y, 3, 2, 1.0)
    r2 = func(X, Y, 3, 2, 2.0)
    # They shouldn't be identical
    assert not np.allclose(r1, r2, atol=1e-6)


def test_classic_rectangular_symmetry():
    """Classic rectangular mode (m, n) should be symmetric under x<->y swap
    when mode_x == mode_y."""
    X, Y = _make_grid(60)
    r1 = PatternGenerator.classic_rectangular(X, Y, 3, 3, 1.0)
    r2 = PatternGenerator.classic_rectangular(Y, X, 3, 3, 1.0)
    np.testing.assert_allclose(r1, r2, atol=1e-10)


def test_radial_symmetric_is_radial():
    """Radial symmetric pattern should be unchanged under 90-degree rotation
    (approximately, since the grid is square)."""
    n = 60
    X, Y = _make_grid(n)
    r1 = PatternGenerator.radial_symmetric(X, Y, 3, 2, 1.0)
    # 90-deg rotation: (x,y) -> (y, 1-x) centred at 0.5
    r2 = PatternGenerator.radial_symmetric(Y, 1 - X, 3, 2, 1.0)
    np.testing.assert_allclose(r1, r2, atol=1e-10)
