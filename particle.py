"""
Chladni Visualizer - Particle module.

Contains the Particle class representing a single sand grain on the
Chladni plate.  Particles move in response to the vibration amplitude
map and settle in nodal regions.
"""

import random
import numpy as np

from constants import (
    VIBRATION_THRESHOLD,
    FORCE_SCALE,
    DAMPING_COEFFICIENT,
    SETTLE_TIME,
    VELOCITY_DAMPING,
    BOUNDARY_RESTITUTION,
)


class Particle:
    """A single sand particle on the vibrating plate."""

    def __init__(self, x: float, y: float, size: float = 2):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.z = 0.0
        self.vz = 0.0
        self.size = size
        self.settled = False
        self.settle_timer = 0.0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(
        self,
        dt: float,
        amplitude_map: np.ndarray,
        width: int,
        height: int,
        speed_multiplier: float = 1.0,
        mode_3d: bool = False,
    ):
        """Advance the particle by one time step."""
        local_amplitude = self._sample_amplitude(amplitude_map, width, height)
        fx, fy = self._compute_forces(local_amplitude, dt, speed_multiplier)
        self._integrate(fx, fy, dt, speed_multiplier)
        self._enforce_bounds(width, height)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sample_amplitude(
        self, amplitude_map: np.ndarray, width: int, height: int
    ) -> float:
        """Look up the vibration amplitude at the particle position."""
        grid_x = int((self.x / width) * amplitude_map.shape[1])
        grid_y = int((self.y / height) * amplitude_map.shape[0])
        grid_x = max(0, min(amplitude_map.shape[1] - 1, grid_x))
        grid_y = max(0, min(amplitude_map.shape[0] - 1, grid_y))
        return amplitude_map[grid_y, grid_x]

    def _compute_forces(
        self, local_amplitude: float, dt: float, speed_multiplier: float
    ) -> tuple:
        """Return (fx, fy) based on local vibration amplitude."""
        if local_amplitude > VIBRATION_THRESHOLD:
            force_magnitude = local_amplitude * FORCE_SCALE * speed_multiplier
            fx = (random.random() - 0.5) * force_magnitude
            fy = (random.random() - 0.5) * force_magnitude
            self.settled = False
            self.settle_timer = 0.0
        else:
            fx = -self.vx * DAMPING_COEFFICIENT * speed_multiplier
            fy = -self.vy * DAMPING_COEFFICIENT * speed_multiplier
            self.settle_timer += dt * speed_multiplier
            if self.settle_timer > SETTLE_TIME:
                self.settled = True
        return fx, fy

    def _integrate(
        self, fx: float, fy: float, dt: float, speed_multiplier: float
    ):
        """Apply forces and integrate velocity / position."""
        self.vx += fx * dt
        self.vy += fy * dt

        damping = VELOCITY_DAMPING ** speed_multiplier
        self.vx *= damping
        self.vy *= damping

        self.x += self.vx * dt * speed_multiplier
        self.y += self.vy * dt * speed_multiplier

    def _enforce_bounds(self, width: int, height: int):
        """Clamp position inside the plate and reflect velocity."""
        if self.x < 0:
            self.x = 0
            self.vx = abs(self.vx) * BOUNDARY_RESTITUTION
        elif self.x >= width:
            self.x = width - 1
            self.vx = -abs(self.vx) * BOUNDARY_RESTITUTION

        if self.y < 0:
            self.y = 0
            self.vy = abs(self.vy) * BOUNDARY_RESTITUTION
        elif self.y >= height:
            self.y = height - 1
            self.vy = -abs(self.vy) * BOUNDARY_RESTITUTION
