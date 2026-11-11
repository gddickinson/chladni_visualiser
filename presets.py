"""
Chladni Visualizer - Presets and amplitude-map helper (no Pygame).

Single source of truth for the pattern presets (keys Q-O), the musical
frequency presets (keys 1-0), the particle-size distributions and the
display modes.  ``simulator.py`` maps these onto Pygame key codes; the
web API (``web/app.py``) serves them as JSON.  ``amplitude_map`` is the
pure-NumPy body of ``ChladniSimulator.calculate_pattern``.
"""

import numpy as np

from constants import DEFAULT_FREQUENCY
from pattern_generator import PatternGenerator

# (key, slug, display name, PatternGenerator method, mode_x, mode_y)
# The slugs match the choices of main.py --mode.
PATTERN_PRESETS = [
    ("q", "classic", "Classic Rectangular", "classic_rectangular", 3, 2),
    ("w", "circular", "Circular Modes", "circular_modes", 2, 3),
    ("e", "interference", "Interference", "interference_pattern", 4, 3),
    ("r", "radial", "Radial Symmetric", "radial_symmetric", 3, 2),
    ("t", "spiral", "Spiral Pattern", "spiral_pattern", 4, 6),
    ("y", "diamond", "Diamond Pattern", "diamond_pattern", 4, 3),
    ("u", "flower", "Flower Pattern", "flower_pattern", 8, 2),
    ("i", "wave", "Wave Interference", "wave_interference", 5, 3),
    ("o", "superposition", "Complex Superposition", "complex_superposition", 3, 4),
]

PATTERN_SLUGS = [slug for _key, slug, *_rest in PATTERN_PRESETS]

# (key, frequency in Hz, musical note)
FREQUENCY_PRESETS = [
    ("1", 220.0, "A3"),
    ("2", 261.6, "C4"),
    ("3", 293.7, "D4"),
    ("4", 329.6, "E4"),
    ("5", 349.2, "F4"),
    ("6", 392.0, "G4"),
    ("7", 440.0, "A4"),
    ("8", 493.9, "B4"),
    ("9", 523.3, "C5"),
    ("0", 587.3, "D5"),
]

SIZE_DISTRIBUTIONS = ["uniform", "normal", "small", "large"]
DISPLAY_MODES = ["Both", "Particles Only", "Pattern Only"]


def pattern_function(method_name: str):
    """Return the PatternGenerator static method called *method_name*."""
    return getattr(PatternGenerator, method_name)


def amplitude_map(func, grid_size, mode_x, mode_y, frequency, plate_size=1.0):
    """|pattern| on a grid_size x grid_size grid over the plate, normalised to [0, 1].

    Rows are y, columns are x (np.meshgrid order).  freq_factor is
    frequency / DEFAULT_FREQUENCY (440 Hz).
    """
    x = np.linspace(0, plate_size, grid_size)
    y = np.linspace(0, plate_size, grid_size)
    X, Y = np.meshgrid(x, y)
    freq_factor = frequency / DEFAULT_FREQUENCY
    pattern = np.abs(func(X, Y, mode_x, mode_y, freq_factor))
    return pattern / (np.max(pattern) + 1e-10)
