# Chladni Pattern Visualizer

An interactive real-time simulation of Chladni patterns using Pygame. Thousands of virtual particles settle into the nodal lines of vibrating plates, creating the beautiful geometric patterns first demonstrated by Ernst Chladni in the 18th century.

![Chladni Pattern Example](examples/chladni_example.png)

## Features

- **Real-time particle simulation** -- thousands of particles respond to vibration amplitude maps
- **Multiple pattern types**:
  - Classic rectangular plate modes
  - Circular plate modes (polar coordinates with Bessel function approximation)
  - Interference patterns from multiple wave sources
  - Radial symmetric patterns
- **Interactive controls**:
  - Adjust mode numbers (X/Y) with arrow keys
  - Change vibration frequency
  - Control simulation speed
  - Toggle 3D mode
  - Switch between pattern types
- **Visual customization** -- particles settle at nodal lines where vibration amplitude is minimal

## Requirements

- Python 3.7+
- pygame
- numpy

```bash
pip install pygame numpy
```

## Usage

```bash
python chladni_visualizer.py
```

### Controls

| Key | Action |
|-----|--------|
| Left/Right arrows | Change X mode number |
| Up/Down arrows | Change Y mode number |
| +/- | Adjust frequency |
| Space | Toggle simulation |
| R | Reset particles |
| T | Cycle pattern type |

## How It Works

The simulator creates an amplitude map for the selected Chladni mode pattern, then simulates particles that:
- Experience random forces in high-amplitude (vibrating) regions
- Settle via damping forces in low-amplitude (nodal) regions
- Naturally accumulate along the nodal lines, revealing the pattern

## Project Structure

```
chladni_visualizer/
├── chladni_visualizer.py   # Main application (Particle, PatternGenerator, ChladniSimulator)
├── examples/
│   └── chladni_example.png # Example output
└── README.md
```
