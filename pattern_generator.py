"""
Chladni Visualizer - Pattern generator module.

Each static method computes a 2-D amplitude map for one family of
Chladni-plate vibration patterns.  The *mode_x* / *mode_y* integers
select a particular standing-wave mode, and *freq_factor* (ratio of
the chosen frequency to 440 Hz) allows continuous interpolation
between modes.

Physics background
------------------
A real Chladni plate vibrates in modes determined by its boundary
conditions.  For a rectangular plate with free edges the displacement
is a product of cosines in x and y.  For a circular plate the modes
involve Bessel functions of the first kind and angular harmonics.
The functions here use simplified analytic approximations that
capture the visual character of each mode family without solving the
full biharmonic plate equation.
"""

import numpy as np


class PatternGenerator:
    """Library of Chladni-plate vibration pattern functions."""

    @staticmethod
    def classic_rectangular(x, y, mode_x, mode_y, freq_factor=1.0):
        """Classic rectangular Chladni pattern.

        Uses the product of cosines that arise from the free-edge
        boundary condition on a rectangular plate.  A half-frequency
        harmonic is mixed in to add visual richness.
        """
        eff_mode_x = mode_x * freq_factor
        eff_mode_y = mode_y * freq_factor

        main_pattern = (
            np.cos(eff_mode_x * np.pi * x) * np.cos(eff_mode_y * np.pi * y)
        )
        harmonic = (
            np.cos(eff_mode_x * np.pi * x * 0.5)
            * np.cos(eff_mode_y * np.pi * y * 0.5)
            * 0.3
        )
        return main_pattern + harmonic * np.sin(freq_factor * np.pi)

    @staticmethod
    def circular_modes(x, y, mode_r, mode_theta, freq_factor=1.0):
        """Circular plate patterns (polar coordinates).

        Converts to polar coordinates and applies a Bessel-function
        *approximation* (exponentially decaying cosine) multiplied by
        an angular harmonic cos(m * theta).
        """
        r = np.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2) * 2
        theta = np.arctan2(y - 0.5, x - 0.5)

        eff_mode_r = mode_r * freq_factor
        eff_mode_theta = mode_theta + int(freq_factor * 2)

        radial = np.cos(eff_mode_r * np.pi * r) * np.exp(
            -r * (0.3 + 0.2 * freq_factor)
        )
        angular = np.cos(eff_mode_theta * theta)
        return radial * angular

    @staticmethod
    def interference_pattern(x, y, mode_x, mode_y, freq_factor=1.0):
        """Interference between multiple wave sources.

        Superimposes three standing waves at slightly different mode
        numbers and a frequency-dependent phase shift, producing a
        moiré-like interference texture.
        """
        scale = freq_factor
        pattern1 = (
            np.cos(mode_x * scale * np.pi * x)
            * np.cos(mode_y * scale * np.pi * y)
        )
        pattern2 = (
            np.cos((mode_x + 1) * scale * np.pi * y)
            * np.cos((mode_y + 1) * scale * np.pi * x)
        )
        phase_shift = freq_factor * np.pi * 0.5
        pattern3 = (
            np.cos(mode_x * scale * np.pi * (x + y) + phase_shift) * 0.4
        )
        return (pattern1 + pattern2 * 0.7 + pattern3) / 2.1

    @staticmethod
    def radial_symmetric(x, y, mode_x, mode_y, freq_factor=1.0):
        """Radially symmetric patterns.

        Two sets of concentric rings (inner and outer) are multiplied
        together, with an additional beating cosine to enrich the
        pattern at higher frequencies.
        """
        r = np.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2)
        freq_scale = freq_factor * 1.5
        inner_rings = np.cos(mode_x * np.pi * r * freq_scale * 4)
        outer_rings = np.cos(mode_y * np.pi * r * freq_scale * 2)
        beat_pattern = np.cos(freq_factor * np.pi * r * 8) * 0.3
        return inner_rings * outer_rings + beat_pattern

    @staticmethod
    def spiral_pattern(x, y, mode_x, mode_y, freq_factor=1.0):
        """Spiral-like patterns.

        An Archimedean spiral whose arm count and tightness depend on
        the mode numbers and frequency, with Gaussian radial decay.
        """
        r = np.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2)
        theta = np.arctan2(y - 0.5, x - 0.5)
        spiral_freq = freq_factor * 2
        arms = mode_y + int(freq_factor)
        spiral = np.cos(mode_x * np.pi * r * spiral_freq + arms * theta)
        decay = np.exp(-r * (1 + freq_factor * 0.5))
        return spiral * decay

    @staticmethod
    def diamond_pattern(x, y, mode_x, mode_y, freq_factor=1.0):
        """Diamond / rhombic patterns.

        Rotates to 45-degree coordinates (u = x+y, v = x-y) so the
        nodal lines form diamond shapes, with a frequency-dependent
        secondary rotation for additional complexity.
        """
        u = x + y
        v = x - y
        freq_scale = freq_factor * 1.2
        main_pattern = (
            np.cos(mode_x * freq_scale * np.pi * u)
            * np.cos(mode_y * freq_scale * np.pi * v)
        )
        rotation = freq_factor * np.pi * 0.25
        u_rot = u * np.cos(rotation) - v * np.sin(rotation)
        v_rot = u * np.sin(rotation) + v * np.cos(rotation)
        rotated = (
            np.cos(mode_x * freq_scale * np.pi * u_rot * 0.7)
            * np.cos(mode_y * freq_scale * np.pi * v_rot * 0.7)
            * 0.4
        )
        return main_pattern + rotated

    @staticmethod
    def flower_pattern(x, y, mode_x, mode_y, freq_factor=1.0):
        """Flower-like patterns with petals.

        Combines angular cos^2 petals with radial oscillations and an
        exponential envelope, plus a Gaussian centre bloom at higher
        frequencies.
        """
        r = np.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2)
        theta = np.arctan2(y - 0.5, x - 0.5)
        petals = mode_x + int(freq_factor * 2)
        radial_freq = mode_y * freq_factor
        petal_pattern = np.cos(petals * theta) ** 2
        radial_pattern = np.cos(radial_freq * np.pi * r * 3)
        center_pattern = (
            np.cos(freq_factor * np.pi * r * 10) * np.exp(-r * 10) * 0.5
        )
        decay = np.exp(-r * (2 + freq_factor))
        return (petal_pattern * radial_pattern + center_pattern) * decay

    @staticmethod
    def wave_interference(x, y, mode_x, mode_y, freq_factor=1.0):
        """Multiple point-source interference.

        Three fixed point sources each emit spherical waves whose
        frequency and phase depend on *mode_x* and *freq_factor*.
        The 1/r decay gives a natural fall-off away from each source.
        """
        sources = [(0.3, 0.3), (0.7, 0.3), (0.5, 0.7)]
        pattern = np.zeros_like(x)
        for i, (sx, sy) in enumerate(sources):
            r = np.sqrt((x - sx) ** 2 + (y - sy) ** 2)
            wave_freq = mode_x * freq_factor * (i + 1)
            phase = freq_factor * np.pi * i * 0.5
            wave = np.cos(wave_freq * np.pi * r + phase) / (r + 0.1)
            pattern += wave
        return pattern / len(sources)

    @staticmethod
    def complex_superposition(x, y, mode_x, mode_y, freq_factor=1.0):
        """Superposition of multiple modes.

        Adds three rectangular modes with frequency-dependent weights
        plus a diagonal beating term, approximating the response of a
        plate driven at a frequency that excites several modes at once.
        """
        freq_scale = freq_factor * 1.1
        p1 = (
            np.cos(mode_x * freq_scale * np.pi * x)
            * np.cos(mode_y * freq_scale * np.pi * y)
        )
        p2 = (
            np.cos((mode_x + 2) * freq_scale * np.pi * x)
            * np.cos(mode_y * freq_scale * np.pi * y)
            * (0.5 + 0.3 * np.sin(freq_factor))
        )
        p3 = (
            np.cos(mode_x * freq_scale * np.pi * x)
            * np.cos((mode_y + 1) * freq_scale * np.pi * y)
            * (0.3 + 0.2 * np.cos(freq_factor))
        )
        beat = np.cos(freq_factor * np.pi * (x + y) * 2) * 0.2
        return (p1 + p2 + p3 + beat) / 2.0
