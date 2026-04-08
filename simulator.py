"""
Chladni Visualizer - Simulator module.

Contains the ChladniSimulator class that owns the Pygame window,
manages the particle system, renders both 2-D and 3-D views, and
processes user input.
"""

import math
import random
from typing import List, Tuple

import numpy as np
import pygame

from constants import (
    BLACK,
    BLUE,
    DEFAULT_CAMERA_ANGLE,
    DEFAULT_CAMERA_HEIGHT,
    DEFAULT_FREQUENCY,
    DEFAULT_GRID_SIZE,
    DEFAULT_HEIGHT,
    DEFAULT_NUM_PARTICLES,
    DEFAULT_PARTICLE_SIZE_MAX,
    DEFAULT_PARTICLE_SIZE_MIN,
    DEFAULT_SPEED,
    DEFAULT_WIDTH,
    DEFAULT_ZOOM,
    MAX_PARTICLES,
    MAX_SPEED,
    MAX_ZOOM,
    MIN_PARTICLES,
    MIN_SPEED,
    MIN_ZOOM,
    WHITE,
)
from particle import Particle
from pattern_generator import PatternGenerator


class ChladniSimulator:
    """Main simulation driver: rendering, input, and game loop."""

    def __init__(self, width: int = DEFAULT_WIDTH, height: int = DEFAULT_HEIGHT):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Advanced Chladni Pattern Visualizer")

        # Simulation parameters
        self.grid_size = DEFAULT_GRID_SIZE
        self.particles: List[Particle] = []
        self.num_particles = DEFAULT_NUM_PARTICLES
        self.min_particles = MIN_PARTICLES
        self.max_particles = MAX_PARTICLES

        # Display modes: 0=both, 1=particles only, 2=pattern only
        self.display_mode = 0
        self.display_modes = ["Both", "Particles Only", "Pattern Only"]

        # 3D visualization mode
        self.mode_3d = False
        self.camera_angle = DEFAULT_CAMERA_ANGLE
        self.camera_height = DEFAULT_CAMERA_HEIGHT
        self.camera_view = "perspective"
        self.camera_views = ["perspective", "top", "north", "south", "east", "west"]
        self.zoom_factor = DEFAULT_ZOOM
        self.min_zoom = MIN_ZOOM
        self.max_zoom = MAX_ZOOM

        # Particle appearance controls
        self.particle_size_min = DEFAULT_PARTICLE_SIZE_MIN
        self.particle_size_max = DEFAULT_PARTICLE_SIZE_MAX
        self.particle_size_distribution = "uniform"

        # Speed control
        self.speed_multiplier = DEFAULT_SPEED
        self.min_speed = MIN_SPEED
        self.max_speed = MAX_SPEED

        # Pattern parameters
        self.frequency = DEFAULT_FREQUENCY
        self.mode_x = 3
        self.mode_y = 2
        self.plate_size = 1.0
        self.current_pattern_func = PatternGenerator.classic_rectangular
        self.current_pattern_name = "Classic Rectangular"

        # Initialize particles
        self.init_particles()

        # Pattern presets
        self.pattern_presets = {
            pygame.K_q: ("Classic Rectangular", PatternGenerator.classic_rectangular, 3, 2),
            pygame.K_w: ("Circular Modes", PatternGenerator.circular_modes, 2, 3),
            pygame.K_e: ("Interference", PatternGenerator.interference_pattern, 4, 3),
            pygame.K_r: ("Radial Symmetric", PatternGenerator.radial_symmetric, 3, 2),
            pygame.K_t: ("Spiral Pattern", PatternGenerator.spiral_pattern, 4, 6),
            pygame.K_y: ("Diamond Pattern", PatternGenerator.diamond_pattern, 4, 3),
            pygame.K_u: ("Flower Pattern", PatternGenerator.flower_pattern, 8, 2),
            pygame.K_i: ("Wave Interference", PatternGenerator.wave_interference, 5, 3),
            pygame.K_o: ("Complex Superposition", PatternGenerator.complex_superposition, 3, 4),
        }

        # Frequency presets (musical notes)
        self.frequency_presets = {
            pygame.K_1: 220.0,   # A3
            pygame.K_2: 261.6,   # C4
            pygame.K_3: 293.7,   # D4
            pygame.K_4: 329.6,   # E4
            pygame.K_5: 349.2,   # F4
            pygame.K_6: 392.0,   # G4
            pygame.K_7: 440.0,   # A4
            pygame.K_8: 493.9,   # B4
            pygame.K_9: 523.3,   # C5
            pygame.K_0: 587.3,   # D5
        }

        self.clock = pygame.time.Clock()
        self.print_instructions()

    # ------------------------------------------------------------------
    # Initialization helpers
    # ------------------------------------------------------------------

    def print_instructions(self):
        print("=== Advanced Chladni Pattern Visualizer ===")
        print("\nPattern Controls:")
        print("Q - Classic Rectangular    W - Circular Modes")
        print("E - Interference          R - Radial Symmetric")
        print("T - Spiral Pattern        Y - Diamond Pattern")
        print("U - Flower Pattern        I - Wave Interference")
        print("O - Complex Superposition")
        print("\nFrequency Controls:")
        print("1-0 - Different frequencies/musical notes")
        print("\nDisplay Controls:")
        print("V - Cycle view modes (Both/Particles/Pattern)")
        print("3 - Toggle 3D mode")
        print("C - Cycle camera views (Perspective/Top/N/S/E/W)")
        print("Left/Right Arrow - Adjust perspective camera angle")
        print("Page Up/Down - Zoom in/out")
        print("[ ] - Decrease/Increase particle count (up to 20,000!)")
        print("Shift + - / Shift + = - Particle size range")
        print("D - Cycle particle size distribution")
        print("\nSpeed Controls:")
        print("+ or = - Increase speed    - or _ - Decrease speed")
        print("Arrow Up/Down - Fine speed adjustment")
        print("\nOther Controls:")
        print("SPACE - Reset particles    ESC - Quit")

    def init_particles(self):
        """Initialize particles with the current count and size distribution."""
        self.particles = []
        for _ in range(self.num_particles):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)
            size = self._random_particle_size()
            self.particles.append(Particle(x, y, size))

    def _random_particle_size(self) -> float:
        lo, hi = self.particle_size_min, self.particle_size_max
        dist = self.particle_size_distribution
        if dist == "normal":
            mean = (lo + hi) / 2
            std = (hi - lo) / 4
            return max(lo, min(hi, random.gauss(mean, std)))
        if dist == "small":
            return lo + (hi - lo) * (random.random() ** 2)
        if dist == "large":
            return lo + (hi - lo) * (1 - random.random() ** 2)
        # "uniform" or fallback
        return random.uniform(lo, hi)

    # ------------------------------------------------------------------
    # Pattern calculation
    # ------------------------------------------------------------------

    def calculate_pattern(self) -> np.ndarray:
        """Calculate the amplitude pattern using the current generator."""
        x = np.linspace(0, self.plate_size, self.grid_size)
        y = np.linspace(0, self.plate_size, self.grid_size)
        X, Y = np.meshgrid(x, y)

        freq_factor = self.frequency / DEFAULT_FREQUENCY
        pattern = self.current_pattern_func(X, Y, self.mode_x, self.mode_y, freq_factor)

        pattern = np.abs(pattern)
        pattern = pattern / (np.max(pattern) + 1e-10)
        return pattern

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def draw_pattern_background(self, pattern: np.ndarray):
        """Draw a subtle 2-D background showing the vibration pattern."""
        for i in range(0, pattern.shape[0], 2):
            for j in range(0, pattern.shape[1], 2):
                x = int((j / pattern.shape[1]) * self.width)
                y = int((i / pattern.shape[0]) * self.height)
                intensity = int(pattern[i, j] * 60 + 190)
                intensity = max(190, min(255, intensity))
                if pattern[i, j] < 0.3:
                    color = (intensity - 10, intensity - 5, intensity)
                else:
                    color = (intensity, intensity, intensity)
                rect_size = max(2, self.width // pattern.shape[1] + 1)
                pygame.draw.rect(self.screen, color, (x, y, rect_size, rect_size))

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

    # ------------------------------------------------------------------
    # Particle rendering
    # ------------------------------------------------------------------

    def update_particles(self, dt: float, pattern: np.ndarray):
        for particle in self.particles:
            particle.update(dt, pattern, self.width, self.height,
                            self.speed_multiplier, self.mode_3d)

    def draw_particles(self):
        if self.mode_3d:
            self._draw_particles_3d()
        else:
            self._draw_particles_2d()

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

    def _draw_particles_2d(self):
        for p in self.particles:
            if p.settled:
                color = BLACK
                size = int(p.size * 1.3)
            else:
                speed = math.sqrt(p.vx ** 2 + p.vy ** 2)
                if speed > 50:
                    gray = max(60, min(120, int(speed * 1.5 + 60)))
                    color = (gray, gray // 2, gray // 3)
                else:
                    gray = max(30, min(80, int(speed * 2 + 30)))
                    color = (gray, gray, gray)
                size = int(p.size)

            if not p.settled and math.sqrt(p.vx ** 2 + p.vy ** 2) > 30:
                glow = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*color, 30), (size * 2, size * 2), size * 2)
                self.screen.blit(glow, (int(p.x - size * 2), int(p.y - size * 2)))
            pygame.draw.circle(self.screen, color, (int(p.x), int(p.y)), size)

    # ------------------------------------------------------------------
    # UI overlay
    # ------------------------------------------------------------------

    def draw_ui(self):
        font = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)

        panel_width = 450
        panel_height = 260 if self.mode_3d else 180
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (255, 255, 255, 200), (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel_surface, BLACK, (0, 0, panel_width, panel_height), 2)
        self.screen.blit(panel_surface, (10, 10))

        y_off = 20
        for text_str, fnt, col in [
            (f"Frequency: {self.frequency:.1f} Hz", font, BLACK),
            (f"Pattern: {self.current_pattern_name}", font_small, BLACK),
            (f"Mode: ({self.mode_x}, {self.mode_y})", font_small, BLACK),
            (f"Speed: {self.speed_multiplier:.1f}x", font, BLUE),
            (f"3D Mode: {'ON' if self.mode_3d else 'OFF'}", font,
             (0, 150, 0) if self.mode_3d else BLACK),
            (f"View: {self.display_modes[self.display_mode]}", font_small, BLACK),
            (f"Particles: {self.num_particles:,}", font_small, BLACK),
            (f"Size: {self.particle_size_min:.1f}-{self.particle_size_max:.1f}"
             f" ({self.particle_size_distribution})", font_small, BLACK),
        ]:
            surf = fnt.render(text_str, True, col)
            self.screen.blit(surf, (20, y_off))
            y_off += 30 if fnt == font else 20

        if self.mode_3d:
            y_off += 5
            cam_text = font_small.render(f"Camera: {self.camera_view.title()}", True, (0, 100, 150))
            self.screen.blit(cam_text, (20, y_off))
            y_off += 20
            zoom_text = font_small.render(f"Zoom: {self.zoom_factor:.1f}x", True, (0, 100, 150))
            self.screen.blit(zoom_text, (20, y_off))
            if self.camera_view == "perspective":
                y_off += 20
                angle_text = font_small.render(f"Angle: {self.camera_angle}", True, (0, 100, 150))
                self.screen.blit(angle_text, (20, y_off))

        instructions = [
            "Q-O: Patterns  |  1-0: Frequencies  |  3: Toggle 3D  |  C: Camera",
            "V: View mode  |  []: Particles  |  PgUp/Dn: Zoom",
            "<->: Camera angle  |  Shift+/-: Size  |  D: Distribution",
            "+/-: Speed  |  Up/Dn: Fine speed  |  SPACE: Reset  |  ESC: Quit",
        ]
        inst_h = len(instructions) * 25 + 20
        inst_surf = pygame.Surface((550, inst_h), pygame.SRCALPHA)
        pygame.draw.rect(inst_surf, (255, 255, 255, 180), (0, 0, 550, inst_h))
        pygame.draw.rect(inst_surf, BLACK, (0, 0, 550, inst_h), 1)
        self.screen.blit(inst_surf, (10, self.height - inst_h - 10))
        for i, line in enumerate(instructions):
            t = font_small.render(line, True, BLACK)
            self.screen.blit(t, (20, self.height - inst_h + 10 + i * 25))

    # ------------------------------------------------------------------
    # Event handling
    # ------------------------------------------------------------------

    def handle_events(self) -> bool:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type != pygame.KEYDOWN:
                continue

            key = event.key

            if key == pygame.K_ESCAPE:
                return False
            elif key == pygame.K_SPACE:
                self.init_particles()
            elif key == pygame.K_3:
                self.mode_3d = not self.mode_3d
                self.init_particles()
                print(f"3D Mode: {'ON' if self.mode_3d else 'OFF'}")
            elif key == pygame.K_c and self.mode_3d:
                idx = self.camera_views.index(self.camera_view)
                self.camera_view = self.camera_views[(idx + 1) % len(self.camera_views)]
                print(f"Camera view: {self.camera_view.title()}")
            elif key == pygame.K_LEFT and self.mode_3d and self.camera_view == "perspective":
                self.camera_angle = max(10, self.camera_angle - 5)
            elif key == pygame.K_RIGHT and self.mode_3d and self.camera_view == "perspective":
                self.camera_angle = min(80, self.camera_angle + 5)
            elif key == pygame.K_PAGEUP and self.mode_3d:
                self.zoom_factor = min(self.max_zoom, self.zoom_factor * 1.2)
            elif key == pygame.K_PAGEDOWN and self.mode_3d:
                self.zoom_factor = max(self.min_zoom, self.zoom_factor / 1.2)
            elif key == pygame.K_v:
                self.display_mode = (self.display_mode + 1) % 3
            elif key == pygame.K_LEFTBRACKET:
                dec = 1000 if self.num_particles > 5000 else 250
                self.num_particles = max(self.min_particles, self.num_particles - dec)
                self.init_particles()
            elif key == pygame.K_RIGHTBRACKET:
                inc = 1000 if self.num_particles > 5000 else 250
                self.num_particles = min(self.max_particles, self.num_particles + inc)
                self.init_particles()
            elif key in (pygame.K_PLUS, pygame.K_EQUALS) and keys[pygame.K_LSHIFT]:
                self.particle_size_min = min(5.0, self.particle_size_min + 0.2)
                self.particle_size_max = min(6.0, self.particle_size_max + 0.2)
                self.init_particles()
            elif key in (pygame.K_MINUS, pygame.K_UNDERSCORE) and keys[pygame.K_LSHIFT]:
                self.particle_size_min = max(0.5, self.particle_size_min - 0.2)
                self.particle_size_max = max(1.0, self.particle_size_max - 0.2)
                self.init_particles()
            elif key == pygame.K_d:
                dists = ["uniform", "normal", "small", "large"]
                idx = dists.index(self.particle_size_distribution)
                self.particle_size_distribution = dists[(idx + 1) % len(dists)]
                self.init_particles()
            elif key in self.pattern_presets:
                name, func, mx, my = self.pattern_presets[key]
                self.current_pattern_name = name
                self.current_pattern_func = func
                self.mode_x = mx
                self.mode_y = my
            elif key in self.frequency_presets:
                self.frequency = self.frequency_presets[key]
            elif key in (pygame.K_PLUS, pygame.K_EQUALS) and not keys[pygame.K_LSHIFT]:
                self.speed_multiplier = min(self.max_speed, self.speed_multiplier + 0.5)
            elif key in (pygame.K_MINUS, pygame.K_UNDERSCORE) and not keys[pygame.K_LSHIFT]:
                self.speed_multiplier = max(self.min_speed, self.speed_multiplier - 0.5)
            elif key == pygame.K_UP and (not self.mode_3d or self.camera_view != "perspective"):
                self.speed_multiplier = min(self.max_speed, self.speed_multiplier + 0.1)
            elif key == pygame.K_DOWN and (not self.mode_3d or self.camera_view != "perspective"):
                self.speed_multiplier = max(self.min_speed, self.speed_multiplier - 0.1)

        return True

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            running = self.handle_events()
            pattern = self.calculate_pattern()
            self.update_particles(dt, pattern)
            self.screen.fill(WHITE)

            if self.display_mode in (0, 2):
                if self.mode_3d:
                    self.draw_3d_background(pattern)
                else:
                    self.draw_pattern_background(pattern)

            if self.display_mode in (0, 1):
                self.draw_particles()

            self.draw_ui()
            pygame.display.flip()

        pygame.quit()
