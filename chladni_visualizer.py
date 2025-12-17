import pygame
import numpy as np
import math
import random
import time
from typing import List, Tuple, Callable

class Particle:
    def __init__(self, x: float, y: float, size: float = 2):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.size = size
        self.settled = False
        self.settle_timer = 0.0

    def update(self, dt: float, amplitude_map: np.ndarray, width: int, height: int, speed_multiplier: float = 1.0, mode_3d: bool = False):
        # Safety check - ensure 3D attributes exist
        if mode_3d and not hasattr(self, 'z'):
            self.z = 0.0
            self.vz = 0.0

        # Convert position to grid coordinates
        grid_x = int((self.x / width) * amplitude_map.shape[1])
        grid_y = int((self.y / height) * amplitude_map.shape[0])

        # Clamp to valid indices
        grid_x = max(0, min(amplitude_map.shape[1] - 1, grid_x))
        grid_y = max(0, min(amplitude_map.shape[0] - 1, grid_y))

        # Get local amplitude (vibration strength)
        local_amplitude = amplitude_map[grid_y, grid_x]

        # Calculate forces
        if local_amplitude > 0.1:  # Strong vibration area
            # Add random motion to simulate vibration
            force_magnitude = local_amplitude * 500 * speed_multiplier
            force_x = (random.random() - 0.5) * force_magnitude
            force_y = (random.random() - 0.5) * force_magnitude
            self.settled = False
            self.settle_timer = 0.0
        else:  # Low vibration area (node) - particles settle here
            # Damping force
            force_x = -self.vx * 10 * speed_multiplier
            force_y = -self.vy * 10 * speed_multiplier

            # Small attractive force toward nearest node
            self.settle_timer += dt * speed_multiplier
            if self.settle_timer > 0.5:
                self.settled = True

        # Apply forces
        self.vx += force_x * dt
        self.vy += force_y * dt

        # Apply damping (adjusted by speed)
        damping = 0.95 ** speed_multiplier
        self.vx *= damping
        self.vy *= damping

        # Update position
        self.x += self.vx * dt * speed_multiplier
        self.y += self.vy * dt * speed_multiplier

        # Boundary conditions
        if self.x < 0:
            self.x = 0
            self.vx = abs(self.vx) * 0.3
        elif self.x >= width:
            self.x = width - 1
            self.vx = -abs(self.vx) * 0.3

        if self.y < 0:
            self.y = 0
            self.vy = abs(self.vy) * 0.3
        elif self.y >= height:
            self.y = height - 1
            self.vy = -abs(self.vy) * 0.3

class PatternGenerator:
    @staticmethod
    def classic_rectangular(x, y, mode_x, mode_y, freq_factor=1.0):
        """Classic rectangular Chladni pattern"""
        # Frequency affects the effective mode numbers and creates harmonics
        eff_mode_x = mode_x * freq_factor
        eff_mode_y = mode_y * freq_factor

        # Main pattern with frequency-dependent modulation
        main_pattern = np.cos(eff_mode_x * np.pi * x) * np.cos(eff_mode_y * np.pi * y)

        # Add frequency-dependent harmonic
        harmonic = np.cos(eff_mode_x * np.pi * x * 0.5) * np.cos(eff_mode_y * np.pi * y * 0.5) * 0.3

        return main_pattern + harmonic * np.sin(freq_factor * np.pi)

    @staticmethod
    def circular_modes(x, y, mode_r, mode_theta, freq_factor=1.0):
        """Circular plate patterns (polar coordinates)"""
        # Convert to polar coordinates
        r = np.sqrt((x - 0.5)**2 + (y - 0.5)**2) * 2
        theta = np.arctan2(y - 0.5, x - 0.5)

        # Frequency affects radial and angular components
        eff_mode_r = mode_r * freq_factor
        eff_mode_theta = mode_theta + int(freq_factor * 2)  # Discrete angular changes

        # Bessel function approximation with frequency scaling
        radial = np.cos(eff_mode_r * np.pi * r) * np.exp(-r * (0.3 + 0.2 * freq_factor))
        angular = np.cos(eff_mode_theta * theta)

        return radial * angular

    @staticmethod
    def interference_pattern(x, y, mode_x, mode_y, freq_factor=1.0):
        """Interference between multiple wave sources"""
        # Frequency creates different interference wavelengths
        scale = freq_factor
        pattern1 = np.cos(mode_x * scale * np.pi * x) * np.cos(mode_y * scale * np.pi * y)
        pattern2 = np.cos((mode_x + 1) * scale * np.pi * y) * np.cos((mode_y + 1) * scale * np.pi * x)

        # Phase shift based on frequency
        phase_shift = freq_factor * np.pi * 0.5
        pattern3 = np.cos(mode_x * scale * np.pi * (x + y) + phase_shift) * 0.4

        return (pattern1 + pattern2 * 0.7 + pattern3) / 2.1

    @staticmethod
    def radial_symmetric(x, y, mode_x, mode_y, freq_factor=1.0):
        """Radially symmetric patterns"""
        r = np.sqrt((x - 0.5)**2 + (y - 0.5)**2)

        # Frequency affects the radial wavelength and creates ripples
        freq_scale = freq_factor * 1.5
        inner_rings = np.cos(mode_x * np.pi * r * freq_scale * 4)
        outer_rings = np.cos(mode_y * np.pi * r * freq_scale * 2)

        # Add frequency-dependent beating pattern
        beat_pattern = np.cos(freq_factor * np.pi * r * 8) * 0.3

        return inner_rings * outer_rings + beat_pattern

    @staticmethod
    def spiral_pattern(x, y, mode_x, mode_y, freq_factor=1.0):
        """Spiral-like patterns"""
        r = np.sqrt((x - 0.5)**2 + (y - 0.5)**2)
        theta = np.arctan2(y - 0.5, x - 0.5)

        # Frequency affects spiral tightness and number of arms
        spiral_freq = freq_factor * 2
        arms = mode_y + int(freq_factor)

        spiral_pattern = np.cos(mode_x * np.pi * r * spiral_freq + arms * theta)
        decay = np.exp(-r * (1 + freq_factor * 0.5))

        return spiral_pattern * decay

    @staticmethod
    def diamond_pattern(x, y, mode_x, mode_y, freq_factor=1.0):
        """Diamond/rhombic patterns"""
        u = x + y
        v = x - y

        # Frequency creates different diamond sizes and orientations
        freq_scale = freq_factor * 1.2
        main_pattern = np.cos(mode_x * freq_scale * np.pi * u) * np.cos(mode_y * freq_scale * np.pi * v)

        # Add rotated component based on frequency
        rotation = freq_factor * np.pi * 0.25
        u_rot = u * np.cos(rotation) - v * np.sin(rotation)
        v_rot = u * np.sin(rotation) + v * np.cos(rotation)
        rotated = np.cos(mode_x * freq_scale * np.pi * u_rot * 0.7) * np.cos(mode_y * freq_scale * np.pi * v_rot * 0.7) * 0.4

        return main_pattern + rotated

    @staticmethod
    def flower_pattern(x, y, mode_x, mode_y, freq_factor=1.0):
        """Flower-like patterns with petals"""
        r = np.sqrt((x - 0.5)**2 + (y - 0.5)**2)
        theta = np.arctan2(y - 0.5, x - 0.5)

        # Frequency affects number of petals and radial frequency
        petals = mode_x + int(freq_factor * 2)  # More petals at higher frequencies
        radial_freq = mode_y * freq_factor

        petal_pattern = np.cos(petals * theta) ** 2
        radial_pattern = np.cos(radial_freq * np.pi * r * 3)

        # Add frequency-dependent center pattern
        center_pattern = np.cos(freq_factor * np.pi * r * 10) * np.exp(-r * 10) * 0.5

        decay = np.exp(-r * (2 + freq_factor))
        return (petal_pattern * radial_pattern + center_pattern) * decay

    @staticmethod
    def wave_interference(x, y, mode_x, mode_y, freq_factor=1.0):
        """Multiple point source interference"""
        sources = [(0.3, 0.3), (0.7, 0.3), (0.5, 0.7)]
        pattern = np.zeros_like(x)

        # Frequency affects wavelength of each source
        for i, (sx, sy) in enumerate(sources):
            r = np.sqrt((x - sx)**2 + (y - sy)**2)
            wave_freq = mode_x * freq_factor * (i + 1)

            # Different phase for each source based on frequency
            phase = freq_factor * np.pi * i * 0.5
            wave = np.cos(wave_freq * np.pi * r + phase) / (r + 0.1)
            pattern += wave

        return pattern / len(sources)

    @staticmethod
    def complex_superposition(x, y, mode_x, mode_y, freq_factor=1.0):
        """Superposition of multiple modes"""
        # Multiple patterns with frequency-dependent weights
        freq_scale = freq_factor * 1.1

        p1 = np.cos(mode_x * freq_scale * np.pi * x) * np.cos(mode_y * freq_scale * np.pi * y)
        p2 = np.cos((mode_x + 2) * freq_scale * np.pi * x) * np.cos(mode_y * freq_scale * np.pi * y) * (0.5 + 0.3 * np.sin(freq_factor))
        p3 = np.cos(mode_x * freq_scale * np.pi * x) * np.cos((mode_y + 1) * freq_scale * np.pi * y) * (0.3 + 0.2 * np.cos(freq_factor))

        # Add beating pattern
        beat = np.cos(freq_factor * np.pi * (x + y) * 2) * 0.2

        return (p1 + p2 + p3 + beat) / 2.0

class ChladniSimulator:
    def __init__(self, width: int = 800, height: int = 600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Advanced Chladni Pattern Visualizer")

        # Simulation parameters
        self.grid_size = 120
        self.particles: List[Particle] = []
        self.num_particles = 2000
        self.min_particles = 100
        self.max_particles = 20000  # Increased limit significantly

        # Display modes: 0=both, 1=particles only, 2=pattern only
        self.display_mode = 0
        self.display_modes = ["Both", "Particles Only", "Pattern Only"]

        # 3D visualization mode
        self.mode_3d = False
        self.camera_angle = 45  # Viewing angle in degrees
        self.camera_height = 200  # Camera height for perspective
        self.camera_view = "perspective"  # perspective, top, north, south, east, west
        self.camera_views = ["perspective", "top", "north", "south", "east", "west"]
        self.zoom_factor = 1.0  # Zoom multiplier
        self.min_zoom = 0.2
        self.max_zoom = 5.0

        # Particle appearance controls
        self.particle_size_min = 1.5
        self.particle_size_max = 3.5
        self.particle_size_distribution = "uniform"  # "uniform", "normal", "small", "large"

        # Speed control
        self.speed_multiplier = 1.0
        self.min_speed = 0.1
        self.max_speed = 5.0

        # Pattern parameters
        self.frequency = 440.0
        self.mode_x = 3
        self.mode_y = 2
        self.plate_size = 1.0
        self.current_pattern_func = PatternGenerator.classic_rectangular
        self.current_pattern_name = "Classic Rectangular"

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (30, 30, 30)
        self.GRAY = (128, 128, 128)
        self.BLUE = (50, 100, 200)

        # Initialize particles
        self.init_particles()

        # Pattern presets with different generators
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

        # Frequency presets
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

        # Clock for timing
        self.clock = pygame.time.Clock()

        self.print_instructions()

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
        """Initialize particles with specified count and size distribution"""
        self.particles = []

        for _ in range(self.num_particles):
            x = random.uniform(50, self.width - 50)
            y = random.uniform(50, self.height - 50)

            # Generate size based on distribution type
            if self.particle_size_distribution == "uniform":
                size = random.uniform(self.particle_size_min, self.particle_size_max)
            elif self.particle_size_distribution == "normal":
                mean_size = (self.particle_size_min + self.particle_size_max) / 2
                std_dev = (self.particle_size_max - self.particle_size_min) / 4
                size = max(self.particle_size_min, min(self.particle_size_max,
                          random.gauss(mean_size, std_dev)))
            elif self.particle_size_distribution == "small":
                # Bias toward smaller particles
                size = self.particle_size_min + (self.particle_size_max - self.particle_size_min) * (random.random() ** 2)
            elif self.particle_size_distribution == "large":
                # Bias toward larger particles
                size = self.particle_size_min + (self.particle_size_max - self.particle_size_min) * (1 - random.random() ** 2)
            else:
                size = random.uniform(self.particle_size_min, self.particle_size_max)

            self.particles.append(Particle(x, y, size))

    def calculate_pattern(self) -> np.ndarray:
        """Calculate the amplitude pattern using the current pattern generator"""
        # Create coordinate grids
        x = np.linspace(0, self.plate_size, self.grid_size)
        y = np.linspace(0, self.plate_size, self.grid_size)
        X, Y = np.meshgrid(x, y)

        # Calculate pattern using current generator
        freq_factor = self.frequency / 440.0
        pattern = self.current_pattern_func(X, Y, self.mode_x, self.mode_y, freq_factor)

        # Take absolute value and normalize
        pattern = np.abs(pattern)
        pattern = pattern / (np.max(pattern) + 1e-10)  # Avoid division by zero

        return pattern

    def draw_pattern_background(self, pattern: np.ndarray):
        """Draw a subtle background showing the vibration pattern"""
        for i in range(0, pattern.shape[0], 2):  # Skip every other for performance
            for j in range(0, pattern.shape[1], 2):
                x = int((j / pattern.shape[1]) * self.width)
                y = int((i / pattern.shape[0]) * self.height)

                # Convert amplitude to color intensity
                intensity = int(pattern[i, j] * 60 + 190)
                intensity = max(190, min(255, intensity))

                # Add slight blue tint for nodes (low vibration areas)
                if pattern[i, j] < 0.3:
                    color = (intensity - 10, intensity - 5, intensity)
                else:
                    color = (intensity, intensity, intensity)

                # Draw rectangle
                rect_size = max(2, self.width // pattern.shape[1] + 1)
                pygame.draw.rect(self.screen, color,
                               (x, y, rect_size, rect_size))

    def project_3d(self, x: float, y: float, z: float) -> Tuple[int, int, float]:
        """Project 3D coordinates to 2D screen coordinates with perspective and multiple view modes"""
        # Convert to centered coordinates
        cx = x - self.width / 2
        cy = y - self.height / 2

        # Apply zoom
        effective_camera_height = self.camera_height / self.zoom_factor

        if self.camera_view == "top":
            # Top-down view (orthographic projection)
            screen_x = int(cx * self.zoom_factor + self.width / 2)
            screen_y = int(cy * self.zoom_factor + self.height / 2)
            depth = z  # Use z for depth sorting

        elif self.camera_view == "north":
            # View from north (looking south) - show X-Z plane
            screen_x = int(cx * self.zoom_factor + self.width / 2)
            screen_y = int((effective_camera_height - z - cy * 0.1) * self.zoom_factor + self.height / 2)
            depth = cy  # Use Y for depth sorting

        elif self.camera_view == "south":
            # View from south (looking north) - show X-Z plane, flipped
            screen_x = int(-cx * self.zoom_factor + self.width / 2)
            screen_y = int((effective_camera_height - z + cy * 0.1) * self.zoom_factor + self.height / 2)
            depth = -cy  # Use negative Y for depth sorting

        elif self.camera_view == "east":
            # View from east (looking west) - show Y-Z plane
            screen_x = int(cy * self.zoom_factor + self.width / 2)
            screen_y = int((effective_camera_height - z - cx * 0.1) * self.zoom_factor + self.height / 2)
            depth = cx  # Use X for depth sorting

        elif self.camera_view == "west":
            # View from west (looking east) - show Y-Z plane, flipped
            screen_x = int(-cy * self.zoom_factor + self.width / 2)
            screen_y = int((effective_camera_height - z + cx * 0.1) * self.zoom_factor + self.height / 2)
            depth = -cx  # Use negative X for depth sorting

        else:  # perspective view
            # Apply rotation around X-axis (tilt the plate)
            angle_rad = math.radians(self.camera_angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Rotate coordinates
            new_y = cy * cos_a - z * sin_a
            new_z = cy * sin_a + z * cos_a + effective_camera_height

            # Perspective projection
            if new_z > 1:  # Avoid division by zero
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
        """Draw 3D perspective background grid for different view modes"""
        if self.camera_view == "top":
            # For top view, draw a simple intensity map
            for i in range(0, pattern.shape[0], 2):
                for j in range(0, pattern.shape[1], 2):
                    x = int((j / pattern.shape[1]) * self.width)
                    y = int((i / pattern.shape[0]) * self.height)

                    amplitude = pattern[i, j]
                    intensity = int(amplitude * 60 + 190)
                    intensity = max(190, min(255, intensity))

                    # Color nodes differently
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
            # For side views and perspective, draw height lines
            grid_spacing = max(20, int(40 / self.zoom_factor))

            for i in range(0, self.width, grid_spacing):
                for j in range(0, self.height, grid_spacing):
                    # Get pattern amplitude at this point
                    grid_x = int((i / self.width) * pattern.shape[1])
                    grid_y = int((j / self.height) * pattern.shape[0])
                    grid_x = max(0, min(pattern.shape[1] - 1, grid_x))
                    grid_y = max(0, min(pattern.shape[0] - 1, grid_y))

                    amplitude = pattern[grid_y, grid_x]
                    height = amplitude * 50 * self.zoom_factor  # Scale amplitude to height

                    # Project to screen coordinates
                    x1, y1, z1 = self.project_3d(i, j, 0)
                    x2, y2, z2 = self.project_3d(i, j, height)

                    # Color based on amplitude
                    intensity = int(amplitude * 100 + 150)
                    intensity = max(150, min(255, intensity))
                    color = (intensity - 20, intensity - 10, intensity)

                    # Draw vertical line to show height
                    if (0 <= x1 < self.width and 0 <= y1 < self.height and
                        0 <= x2 < self.width and 0 <= y2 < self.height):
                        if height > 2:
                            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2),
                                           max(1, int(2 * self.zoom_factor)))
                            # Draw small circle at top
                            pygame.draw.circle(self.screen, color, (x2, y2),
                                             max(1, int(3 * self.zoom_factor)))

    def update_particles(self, dt: float, pattern: np.ndarray):
        """Update all particles based on the current pattern"""
        for particle in self.particles:
            particle.update(dt, pattern, self.width, self.height, self.speed_multiplier, self.mode_3d)

    def draw_particles(self):
        """Draw all particles with enhanced visuals and 3D support"""
        if self.mode_3d:
            # Sort particles by depth for proper 3D rendering (back to front)
            particles_with_depth = []
            for particle in self.particles:
                # Safety check - ensure particle has z attribute
                if not hasattr(particle, 'z'):
                    particle.z = 0.0
                    particle.vz = 0.0

                _, _, depth = self.project_3d(particle.x, particle.y, particle.z)
                particles_with_depth.append((particle, depth))

            # Sort by depth (furthest first)
            particles_with_depth.sort(key=lambda x: x[1], reverse=True)

            # Draw particles in depth order
            for particle, depth in particles_with_depth:
                # Project to screen coordinates
                screen_x, screen_y, z_dist = self.project_3d(particle.x, particle.y, particle.z)

                # Skip if off-screen
                if not (0 <= screen_x < self.width and 0 <= screen_y < self.height):
                    continue

                # Calculate size based on depth and height
                depth_scale = self.camera_height / max(z_dist, 10)
                height_factor = 1 + particle.z / 50  # Particles get bigger when higher
                size = int(particle.size * depth_scale * height_factor)
                size = max(1, min(20, size))  # Clamp size

                # Color based on height and movement
                if particle.settled and particle.z < 5:
                    # Settled particles on ground
                    shadow_offset = int(size * 0.3)
                    shadow_color = (100, 100, 100)
                    pygame.draw.circle(self.screen, shadow_color,
                                     (screen_x + shadow_offset, screen_y + shadow_offset), size)
                    color = self.BLACK
                else:
                    # Flying particles - color based on height and speed
                    speed = math.sqrt(particle.vx**2 + particle.vy**2 + particle.vz**2)
                    height_intensity = min(255, int(particle.z * 3 + 50))

                    if speed > 50:  # Fast moving
                        red_component = min(255, int(speed * 2 + height_intensity))
                        color = (red_component, height_intensity // 2, height_intensity // 3)
                    else:
                        gray_level = max(30, min(150, int(height_intensity)))
                        color = (gray_level, gray_level, gray_level)

                # Draw particle with glow for high particles
                if particle.z > 20:
                    glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                    glow_color = (*color, 40)
                    pygame.draw.circle(glow_surface, glow_color, (size * 2, size * 2), size * 2)
                    self.screen.blit(glow_surface, (screen_x - size * 2, screen_y - size * 2))

                # Draw main particle
                pygame.draw.circle(self.screen, color, (screen_x, screen_y), size)
        else:
            # 2D mode - original rendering
            for particle in self.particles:
                # Vary particle appearance based on state
                if particle.settled:
                    color = self.BLACK
                    size = int(particle.size * 1.3)
                else:
                    speed = math.sqrt(particle.vx**2 + particle.vy**2)
                    if speed > 50:  # Fast moving particles
                        gray_level = max(60, min(120, int(speed * 1.5 + 60)))
                        color = (gray_level, gray_level // 2, gray_level // 3)  # Reddish tint
                    else:
                        gray_level = max(30, min(80, int(speed * 2 + 30)))
                        color = (gray_level, gray_level, gray_level)
                    size = int(particle.size)

                # Draw particle with slight glow effect for fast particles
                if not particle.settled and math.sqrt(particle.vx**2 + particle.vy**2) > 30:
                    # Draw larger, semi-transparent circle first
                    glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                    glow_color = (*color, 30)
                    pygame.draw.circle(glow_surface, glow_color, (size * 2, size * 2), size * 2)
                    self.screen.blit(glow_surface, (int(particle.x - size * 2), int(particle.y - size * 2)))

                # Draw main particle
                pygame.draw.circle(self.screen, color,
                                 (int(particle.x), int(particle.y)), size)

    def draw_ui(self):
        """Draw enhanced user interface"""
        font = pygame.font.Font(None, 36)
        font_small = pygame.font.Font(None, 24)

        # Main info panel background - larger for 3D info
        panel_width = 450
        panel_height = 260 if self.mode_3d else 180
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (255, 255, 255, 200), (0, 0, panel_width, panel_height))
        pygame.draw.rect(panel_surface, self.BLACK, (0, 0, panel_width, panel_height), 2)
        self.screen.blit(panel_surface, (10, 10))

        # Display current settings
        freq_text = font.render(f"Frequency: {self.frequency:.1f} Hz", True, self.BLACK)
        pattern_text = font_small.render(f"Pattern: {self.current_pattern_name}", True, self.BLACK)
        mode_text = font_small.render(f"Mode: ({self.mode_x}, {self.mode_y})", True, self.BLACK)
        speed_text = font.render(f"Speed: {self.speed_multiplier:.1f}x", True, self.BLUE)

        # Display and 3D settings
        mode_3d_text = font.render(f"3D Mode: {'ON' if self.mode_3d else 'OFF'}", True,
                                  (0, 150, 0) if self.mode_3d else self.BLACK)
        display_text = font_small.render(f"View: {self.display_modes[self.display_mode]}", True, self.BLACK)
        particles_text = font_small.render(f"Particles: {self.num_particles:,}", True, self.BLACK)
        size_text = font_small.render(f"Size: {self.particle_size_min:.1f}-{self.particle_size_max:.1f} ({self.particle_size_distribution})", True, self.BLACK)

        y_offset = 20
        self.screen.blit(freq_text, (20, y_offset))
        y_offset += 30
        self.screen.blit(pattern_text, (20, y_offset))
        y_offset += 20
        self.screen.blit(mode_text, (20, y_offset))
        y_offset += 25
        self.screen.blit(speed_text, (20, y_offset))
        y_offset += 30
        self.screen.blit(mode_3d_text, (20, y_offset))
        y_offset += 25
        self.screen.blit(display_text, (20, y_offset))
        y_offset += 20
        self.screen.blit(particles_text, (20, y_offset))
        y_offset += 20
        self.screen.blit(size_text, (20, y_offset))

        # 3D-specific info
        if self.mode_3d:
            y_offset += 25
            camera_view_text = font_small.render(f"Camera: {self.camera_view.title()}", True, (0, 100, 150))
            self.screen.blit(camera_view_text, (20, y_offset))

            y_offset += 20
            zoom_text = font_small.render(f"Zoom: {self.zoom_factor:.1f}x", True, (0, 100, 150))
            self.screen.blit(zoom_text, (20, y_offset))

            if self.camera_view == "perspective":
                y_offset += 20
                angle_text = font_small.render(f"Angle: {self.camera_angle}°", True, (0, 100, 150))
                self.screen.blit(angle_text, (20, y_offset))

        # Instructions panel
        instructions = [
            "Q-O: Patterns  |  1-0: Frequencies  |  3: Toggle 3D  |  C: Camera",
            "V: View mode  |  []: Particles  |  PgUp/Dn: Zoom",
            "←→: Camera angle  |  Shift+/-: Size  |  D: Distribution",
            "+/-: Speed  |  ↑↓: Fine speed  |  SPACE: Reset  |  ESC: Quit"
        ]

        inst_panel_height = len(instructions) * 25 + 20
        inst_surface = pygame.Surface((550, inst_panel_height), pygame.SRCALPHA)
        pygame.draw.rect(inst_surface, (255, 255, 255, 180), (0, 0, 550, inst_panel_height))
        pygame.draw.rect(inst_surface, self.BLACK, (0, 0, 550, inst_panel_height), 1)
        self.screen.blit(inst_surface, (10, self.height - inst_panel_height - 10))

        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, self.BLACK)
            self.screen.blit(text, (20, self.height - inst_panel_height + 10 + i * 25))

    def handle_events(self):
        """Handle pygame events with enhanced controls"""
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                elif event.key == pygame.K_SPACE:
                    self.init_particles()

                # 3D mode toggle
                elif event.key == pygame.K_3:
                    self.mode_3d = not self.mode_3d
                    # Reinitialize particles to ensure they have 3D attributes
                    self.init_particles()
                    print(f"3D Mode: {'ON' if self.mode_3d else 'OFF'}")
                    if self.mode_3d:
                        print("Use Left/Right arrows to adjust camera angle!")

                # 3D camera controls
                elif event.key == pygame.K_c and self.mode_3d:
                    # Cycle through camera views
                    current_idx = self.camera_views.index(self.camera_view)
                    self.camera_view = self.camera_views[(current_idx + 1) % len(self.camera_views)]
                    print(f"Camera view: {self.camera_view.title()}")

                elif event.key == pygame.K_LEFT and self.mode_3d and self.camera_view == "perspective":
                    self.camera_angle = max(10, self.camera_angle - 5)
                    print(f"Camera angle: {self.camera_angle}°")

                elif event.key == pygame.K_RIGHT and self.mode_3d and self.camera_view == "perspective":
                    self.camera_angle = min(80, self.camera_angle + 5)
                    print(f"Camera angle: {self.camera_angle}°")

                # Zoom controls
                elif event.key == pygame.K_PAGEUP and self.mode_3d:
                    self.zoom_factor = min(self.max_zoom, self.zoom_factor * 1.2)
                    print(f"Zoom: {self.zoom_factor:.1f}x")

                elif event.key == pygame.K_PAGEDOWN and self.mode_3d:
                    self.zoom_factor = max(self.min_zoom, self.zoom_factor / 1.2)
                    print(f"Zoom: {self.zoom_factor:.1f}x")

                # Display mode controls
                elif event.key == pygame.K_v:
                    self.display_mode = (self.display_mode + 1) % 3
                    print(f"Display mode: {self.display_modes[self.display_mode]}")

                # Particle count controls
                elif event.key == pygame.K_LEFTBRACKET:
                    decrement = 1000 if self.num_particles > 5000 else 250
                    self.num_particles = max(self.min_particles, self.num_particles - decrement)
                    self.init_particles()
                    print(f"Particle count: {self.num_particles:,}")

                elif event.key == pygame.K_RIGHTBRACKET:
                    increment = 1000 if self.num_particles > 5000 else 250
                    self.num_particles = min(self.max_particles, self.num_particles + increment)
                    self.init_particles()
                    print(f"Particle count: {self.num_particles:,}")

                # Particle size controls (with Shift)
                elif event.key in [pygame.K_PLUS, pygame.K_EQUALS] and keys[pygame.K_LSHIFT]:
                    self.particle_size_min = min(5.0, self.particle_size_min + 0.2)
                    self.particle_size_max = min(6.0, self.particle_size_max + 0.2)
                    self.init_particles()
                    print(f"Particle size range: {self.particle_size_min:.1f}-{self.particle_size_max:.1f}")

                elif event.key in [pygame.K_MINUS, pygame.K_UNDERSCORE] and keys[pygame.K_LSHIFT]:
                    self.particle_size_min = max(0.5, self.particle_size_min - 0.2)
                    self.particle_size_max = max(1.0, self.particle_size_max - 0.2)
                    self.init_particles()
                    print(f"Particle size range: {self.particle_size_min:.1f}-{self.particle_size_max:.1f}")

                # Particle distribution control
                elif event.key == pygame.K_d:
                    distributions = ["uniform", "normal", "small", "large"]
                    current_idx = distributions.index(self.particle_size_distribution)
                    self.particle_size_distribution = distributions[(current_idx + 1) % len(distributions)]
                    self.init_particles()
                    print(f"Particle distribution: {self.particle_size_distribution}")

                # Pattern selection
                elif event.key in self.pattern_presets:
                    name, func, mode_x, mode_y = self.pattern_presets[event.key]
                    self.current_pattern_name = name
                    self.current_pattern_func = func
                    self.mode_x = mode_x
                    self.mode_y = mode_y
                    print(f"Changed to pattern: {name} with modes ({mode_x}, {mode_y})")

                # Frequency selection
                elif event.key in self.frequency_presets:
                    self.frequency = self.frequency_presets[event.key]
                    print(f"Changed frequency to: {self.frequency:.1f} Hz")

                # Speed controls (without Shift)
                elif event.key in [pygame.K_PLUS, pygame.K_EQUALS] and not keys[pygame.K_LSHIFT]:
                    self.speed_multiplier = min(self.max_speed, self.speed_multiplier + 0.5)
                    print(f"Speed: {self.speed_multiplier:.1f}x")

                elif event.key in [pygame.K_MINUS, pygame.K_UNDERSCORE] and not keys[pygame.K_LSHIFT]:
                    self.speed_multiplier = max(self.min_speed, self.speed_multiplier - 0.5)
                    print(f"Speed: {self.speed_multiplier:.1f}x")

                # Fine speed controls (when not in 3D perspective mode)
                elif event.key == pygame.K_UP and (not self.mode_3d or self.camera_view != "perspective"):
                    self.speed_multiplier = min(self.max_speed, self.speed_multiplier + 0.1)
                    print(f"Speed: {self.speed_multiplier:.1f}x")

                elif event.key == pygame.K_DOWN and (not self.mode_3d or self.camera_view != "perspective"):
                    self.speed_multiplier = max(self.min_speed, self.speed_multiplier - 0.1)
                    print(f"Speed: {self.speed_multiplier:.1f}x")

        return True

    def run(self):
        """Main simulation loop"""
        running = True

        while running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds

            # Handle events
            running = self.handle_events()

            # Calculate current pattern
            pattern = self.calculate_pattern()

            # Update simulation (always update particles for physics)
            self.update_particles(dt, pattern)

            # Draw everything based on display mode
            self.screen.fill(self.WHITE)

            # Display mode: 0=both, 1=particles only, 2=pattern only
            if self.display_mode in [0, 2]:  # Show pattern
                if self.mode_3d:
                    self.draw_3d_background(pattern)
                else:
                    self.draw_pattern_background(pattern)

            if self.display_mode in [0, 1]:  # Show particles
                self.draw_particles()

            # Always show UI
            self.draw_ui()

            pygame.display.flip()

        pygame.quit()

def main():
    """Create and run the advanced Chladni pattern visualizer"""
    simulator = ChladniSimulator(width=1400, height=1000)  # Larger window for 3D and high particle counts
    simulator.run()

if __name__ == "__main__":
    main()
