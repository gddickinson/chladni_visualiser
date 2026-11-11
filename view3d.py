"""
Chladni Visualizer - 3-D view (mixin for ChladniSimulator).

Perspective / top / N-S-E-W projections, the 3-D amplitude background
and depth-sorted 3-D particle drawing.  Split out of simulator.py
unchanged; it uses the simulator's camera, zoom and screen attributes.
"""

import math
from typing import Tuple

import numpy as np
import pygame

from constants import BLACK


class View3DMixin:
    """3-D projection and drawing methods used by ChladniSimulator."""

    def project_3d(self, x: float, y: float, z: float) -> Tuple[int, int, float]:
        """Project 3-D coordinates to 2-D screen with perspective."""
        cx = x - self.width / 2
        cy = y - self.height / 2
        effective_camera_height = self.camera_height / self.zoom_factor

        if self.camera_view == "top":
            screen_x = int(cx * self.zoom_factor + self.width / 2)
            screen_y = int(cy * self.zoom_factor + self.height / 2)
            depth = z
        elif self.camera_view == "north":
            screen_x = int(cx * self.zoom_factor + self.width / 2)
            screen_y = int((effective_camera_height - z - cy * 0.1) * self.zoom_factor + self.height / 2)
            depth = cy
        elif self.camera_view == "south":
            screen_x = int(-cx * self.zoom_factor + self.width / 2)
            screen_y = int((effective_camera_height - z + cy * 0.1) * self.zoom_factor + self.height / 2)
            depth = -cy
        elif self.camera_view == "east":
            screen_x = int(cy * self.zoom_factor + self.width / 2)
            screen_y = int((effective_camera_height - z - cx * 0.1) * self.zoom_factor + self.height / 2)
            depth = cx
        elif self.camera_view == "west":
            screen_x = int(-cy * self.zoom_factor + self.width / 2)
            screen_y = int((effective_camera_height - z + cx * 0.1) * self.zoom_factor + self.height / 2)
            depth = -cx
        else:  # perspective
            angle_rad = math.radians(self.camera_angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            new_y = cy * cos_a - z * sin_a
            new_z = cy * sin_a + z * cos_a + effective_camera_height
            if new_z > 1:
                perspective_scale = effective_camera_height / new_z * self.zoom_factor
                screen_x = int(cx * perspective_scale + self.width / 2)
                screen_y = int(new_y * perspective_scale + self.height / 2)
                depth = new_z
            else:
                screen_x = int(x)
                screen_y = int(y)
                depth = effective_camera_height
        return screen_x, screen_y, depth

    def draw_3d_background(self, pattern: np.ndarray):
        """Draw 3-D background grid for different view modes."""
        if self.camera_view == "top":
            for i in range(0, pattern.shape[0], 2):
                for j in range(0, pattern.shape[1], 2):
                    x = int((j / pattern.shape[1]) * self.width)
                    y = int((i / pattern.shape[0]) * self.height)
                    amplitude = pattern[i, j]
                    intensity = int(amplitude * 60 + 190)
                    intensity = max(190, min(255, intensity))
                    if amplitude < 0.3:
                        color = (intensity - 10, intensity - 5, intensity)
                    else:
                        color = (intensity, intensity - 20, intensity - 40)
                    screen_x, screen_y, _ = self.project_3d(x, y, 0)
                    if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                        rect_size = max(1, int(8 * self.zoom_factor))
                        pygame.draw.rect(self.screen, color,
                                         (screen_x, screen_y, rect_size, rect_size))
        else:
            grid_spacing = max(20, int(40 / self.zoom_factor))
            for i in range(0, self.width, grid_spacing):
                for j in range(0, self.height, grid_spacing):
                    grid_x = int((i / self.width) * pattern.shape[1])
                    grid_y = int((j / self.height) * pattern.shape[0])
                    grid_x = max(0, min(pattern.shape[1] - 1, grid_x))
                    grid_y = max(0, min(pattern.shape[0] - 1, grid_y))
                    amplitude = pattern[grid_y, grid_x]
                    height = amplitude * 50 * self.zoom_factor
                    x1, y1, z1 = self.project_3d(i, j, 0)
                    x2, y2, z2 = self.project_3d(i, j, height)
                    intensity = int(amplitude * 100 + 150)
                    intensity = max(150, min(255, intensity))
                    color = (intensity - 20, intensity - 10, intensity)
                    if (0 <= x1 < self.width and 0 <= y1 < self.height
                            and 0 <= x2 < self.width and 0 <= y2 < self.height):
                        if height > 2:
                            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2),
                                             max(1, int(2 * self.zoom_factor)))
                            pygame.draw.circle(self.screen, color, (x2, y2),
                                               max(1, int(3 * self.zoom_factor)))

    def _draw_particles_3d(self):
        particles_with_depth = []
        for p in self.particles:
            _, _, depth = self.project_3d(p.x, p.y, p.z)
            particles_with_depth.append((p, depth))
        particles_with_depth.sort(key=lambda item: item[1], reverse=True)

        for p, depth in particles_with_depth:
            screen_x, screen_y, z_dist = self.project_3d(p.x, p.y, p.z)
            if not (0 <= screen_x < self.width and 0 <= screen_y < self.height):
                continue
            depth_scale = self.camera_height / max(z_dist, 10)
            height_factor = 1 + p.z / 50
            size = int(p.size * depth_scale * height_factor)
            size = max(1, min(20, size))

            if p.settled and p.z < 5:
                shadow_offset = int(size * 0.3)
                pygame.draw.circle(self.screen, (100, 100, 100),
                                   (screen_x + shadow_offset, screen_y + shadow_offset), size)
                color = BLACK
            else:
                speed = math.sqrt(p.vx ** 2 + p.vy ** 2 + p.vz ** 2)
                height_intensity = min(255, int(p.z * 3 + 50))
                if speed > 50:
                    red = min(255, int(speed * 2 + height_intensity))
                    color = (red, height_intensity // 2, height_intensity // 3)
                else:
                    gray = max(30, min(150, int(height_intensity)))
                    color = (gray, gray, gray)

            if p.z > 20:
                glow = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*color, 40), (size * 2, size * 2), size * 2)
                self.screen.blit(glow, (screen_x - size * 2, screen_y - size * 2))
            pygame.draw.circle(self.screen, color, (screen_x, screen_y), size)
