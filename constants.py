"""
Chladni Visualizer - Physics and display constants.

Extracted from the main simulator to eliminate magic numbers
and provide a single source of truth for tunable parameters.
"""

# Physics constants
VIBRATION_THRESHOLD = 0.1       # Amplitude above which particles are vibrated
FORCE_SCALE = 500               # Base force magnitude for vibrating particles
DAMPING_COEFFICIENT = 10        # Damping force multiplier in node regions
SETTLE_TIME = 0.5               # Seconds before a particle is considered settled
VELOCITY_DAMPING = 0.95         # Per-frame velocity damping factor
BOUNDARY_RESTITUTION = 0.3      # Velocity retention on boundary bounce

# Default simulation parameters
DEFAULT_WIDTH = 1400
DEFAULT_HEIGHT = 1000
DEFAULT_GRID_SIZE = 120
DEFAULT_NUM_PARTICLES = 2000
MIN_PARTICLES = 100
MAX_PARTICLES = 20000
DEFAULT_FREQUENCY = 440.0
DEFAULT_SPEED = 1.0
MIN_SPEED = 0.1
MAX_SPEED = 5.0

# Particle appearance
DEFAULT_PARTICLE_SIZE_MIN = 1.5
DEFAULT_PARTICLE_SIZE_MAX = 3.5

# 3D camera defaults
DEFAULT_CAMERA_ANGLE = 45
DEFAULT_CAMERA_HEIGHT = 200
DEFAULT_ZOOM = 1.0
MIN_ZOOM = 0.2
MAX_ZOOM = 5.0

# Colors
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRAY = (128, 128, 128)
BLUE = (50, 100, 200)
