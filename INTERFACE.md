# Chladni Visualizer -- Interface Map

## Project Structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point with CLI argument parsing |
| `simulator.py` | `ChladniSimulator` class -- Pygame loop, rendering, input |
| `particle.py` | `Particle` class -- single sand grain physics |
| `pattern_generator.py` | `PatternGenerator` class -- static methods for each vibration mode |
| `constants.py` | All physics and display constants (no magic numbers) |
| `chladni_visualizer.py` | Original monolithic file (kept for reference) |
| `test_pattern_generator.py` | Tests for amplitude-map calculations |
| `test_particle.py` | Tests for particle physics |

## Key Classes

- **`Particle`** (`particle.py`): Represents a sand grain. Methods: `update()`, `_sample_amplitude()`, `_compute_forces()`, `_integrate()`, `_enforce_bounds()`.
- **`PatternGenerator`** (`pattern_generator.py`): Static methods for each pattern family: `classic_rectangular`, `circular_modes`, `interference_pattern`, `radial_symmetric`, `spiral_pattern`, `diamond_pattern`, `flower_pattern`, `wave_interference`, `complex_superposition`.
- **`ChladniSimulator`** (`simulator.py`): Owns the Pygame window, particle list, and main loop. Methods: `run()`, `handle_events()`, `calculate_pattern()`, `draw_*()`, `init_particles()`.

## Module Connections

```
main.py
  -> simulator.py (ChladniSimulator)
       -> particle.py (Particle)
       -> pattern_generator.py (PatternGenerator)
       -> constants.py (all tunable parameters)
```
