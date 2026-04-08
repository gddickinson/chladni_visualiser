# Chladni Pattern Visualizer -- Roadmap

## Current State
A single-file Pygame application (`chladni_visualizer.py`) simulating Chladni plate vibration patterns with real-time particle physics. Contains three classes (`Particle`, `PatternGenerator`, `ChladniSimulator`) in one file. Supports rectangular, circular, interference, and radial pattern modes with interactive keyboard controls. Clean implementation with type hints. No tests, no dependency management.

## Short-term Improvements
- [x] Add `requirements.txt` (pygame, numpy)
- [x] Split `chladni_visualizer.py` into `particle.py`, `pattern_generator.py`, `simulator.py`, and `main.py`
- [x] Add docstrings to `PatternGenerator` methods explaining the physics of each mode
- [x] Handle edge cases: particles escaping bounds, zero-frequency modes
- [x] Add command-line arguments for initial mode, particle count, and window size
- [x] Write tests for `PatternGenerator` amplitude map calculations against known solutions

## Feature Enhancements
- [ ] Add screenshot/recording capability (save current pattern as PNG or GIF)
- [ ] Implement color themes (sand on black, white on blue, custom palettes)
- [ ] Add real Bessel function modes using `scipy.special` instead of approximation
- [ ] Show mode number labels and frequency on screen as an overlay HUD
- [ ] Add mouse interaction -- tap plate to add particles at cursor position
- [ ] Implement plate boundary shape options (square, circle, triangle, guitar-shaped)
- [ ] Add audio synthesis matching the displayed vibration frequency

## Long-term Vision
- [ ] Port to a web-based version using WebGL/Canvas for broader accessibility
- [ ] Add 3D visualization using OpenGL (height = amplitude, particles settle in valleys)
- [ ] Implement real finite element plate vibration solver for arbitrary geometries
- [ ] Support user-defined plate shapes via SVG/image mask import
- [ ] Create educational mode with step-by-step physics explanations

## Technical Debt
- [x] `Particle.update()` method is long (~60 lines) -- break into sub-methods (force calculation, integration, settling)
- [x] 3D mode attributes added dynamically via `hasattr` check -- use proper initialization
- [x] Magic numbers for physics constants (damping, force scale) -- extract to named constants or config
- [x] No `.gitignore` for screenshots or build artifacts
- [x] Single-file structure will not scale if features are added -- split before enhancing
