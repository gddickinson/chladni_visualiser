#!/usr/bin/env python3
"""
Chladni Pattern Visualizer - Entry point.

Run this script to launch the interactive Chladni plate simulator.
Supports command-line arguments for initial configuration.
"""

import argparse

from constants import DEFAULT_HEIGHT, DEFAULT_NUM_PARTICLES, DEFAULT_WIDTH
from simulator import ChladniSimulator


def parse_args():
    parser = argparse.ArgumentParser(
        description="Interactive Chladni plate vibration pattern visualizer"
    )
    parser.add_argument(
        "--width", type=int, default=DEFAULT_WIDTH,
        help=f"Window width in pixels (default: {DEFAULT_WIDTH})"
    )
    parser.add_argument(
        "--height", type=int, default=DEFAULT_HEIGHT,
        help=f"Window height in pixels (default: {DEFAULT_HEIGHT})"
    )
    parser.add_argument(
        "--particles", type=int, default=DEFAULT_NUM_PARTICLES,
        help=f"Initial particle count (default: {DEFAULT_NUM_PARTICLES})"
    )
    parser.add_argument(
        "--mode", type=str, default="classic",
        choices=[
            "classic", "circular", "interference", "radial",
            "spiral", "diamond", "flower", "wave", "superposition",
        ],
        help="Initial pattern mode (default: classic)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    sim = ChladniSimulator(width=args.width, height=args.height)

    if args.particles != DEFAULT_NUM_PARTICLES:
        sim.num_particles = args.particles
        sim.init_particles()

    sim.run()


if __name__ == "__main__":
    main()
