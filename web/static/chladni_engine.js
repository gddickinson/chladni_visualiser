// Chladni engine: a pure-JS port of pattern_generator.py (the nine PatternGenerator families), presets.amplitude_map
// (= ChladniSimulator.calculate_pattern) and particle.py (Particle.update: sample amplitude, forces, integrate, bounds).
// No DOM. Checked against numbers computed by the Python code in chladni_engine.test.mjs.

const { PI, cos, sin, sqrt, exp, atan2, trunc, abs } = Math;
const int = trunc; // Python int() on a float truncates toward zero

// Each function takes plate coordinates x, y in [0, plate_size] and returns the signed displacement, exactly as the
// matching PatternGenerator static method does element-wise.
export const PATTERNS = {
  classic_rectangular(x, y, mx, my, ff = 1) {
    const ex = mx * ff, ey = my * ff;
    const main = cos(ex * PI * x) * cos(ey * PI * y);
    const harmonic = cos(ex * PI * x * 0.5) * cos(ey * PI * y * 0.5) * 0.3;
    return main + harmonic * sin(ff * PI);
  },
  circular_modes(x, y, mr, mt, ff = 1) {
    const r = sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2) * 2;
    const theta = atan2(y - 0.5, x - 0.5);
    const er = mr * ff, et = mt + int(ff * 2);
    const radial = cos(er * PI * r) * exp(-r * (0.3 + 0.2 * ff));
    return radial * cos(et * theta);
  },
  interference_pattern(x, y, mx, my, ff = 1) {
    const s = ff;
    const p1 = cos(mx * s * PI * x) * cos(my * s * PI * y);
    const p2 = cos((mx + 1) * s * PI * y) * cos((my + 1) * s * PI * x);
    const p3 = cos(mx * s * PI * (x + y) + ff * PI * 0.5) * 0.4;
    return (p1 + p2 * 0.7 + p3) / 2.1;
  },
  radial_symmetric(x, y, mx, my, ff = 1) {
    const r = sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2);
    const fs = ff * 1.5;
    const inner = cos(mx * PI * r * fs * 4), outer = cos(my * PI * r * fs * 2);
    return inner * outer + cos(ff * PI * r * 8) * 0.3;
  },
  spiral_pattern(x, y, mx, my, ff = 1) {
    const r = sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2);
    const theta = atan2(y - 0.5, x - 0.5);
    const arms = my + int(ff);
    return cos(mx * PI * r * ff * 2 + arms * theta) * exp(-r * (1 + ff * 0.5));
  },
  diamond_pattern(x, y, mx, my, ff = 1) {
    const u = x + y, v = x - y, fs = ff * 1.2;
    const main = cos(mx * fs * PI * u) * cos(my * fs * PI * v);
    const rot = ff * PI * 0.25;
    const ur = u * cos(rot) - v * sin(rot), vr = u * sin(rot) + v * cos(rot);
    return main + cos(mx * fs * PI * ur * 0.7) * cos(my * fs * PI * vr * 0.7) * 0.4;
  },
  flower_pattern(x, y, mx, my, ff = 1) {
    const r = sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2);
    const theta = atan2(y - 0.5, x - 0.5);
    const petals = mx + int(ff * 2), radialFreq = my * ff;
    const petal = cos(petals * theta) ** 2;
    const radial = cos(radialFreq * PI * r * 3);
    const center = cos(ff * PI * r * 10) * exp(-r * 10) * 0.5;
    return (petal * radial + center) * exp(-r * (2 + ff));
  },
  wave_interference(x, y, mx, my, ff = 1) {
    const sources = [[0.3, 0.3], [0.7, 0.3], [0.5, 0.7]];
    let sum = 0;
    sources.forEach(([sx, sy], i) => {
      const r = sqrt((x - sx) ** 2 + (y - sy) ** 2);
      sum += cos(mx * ff * (i + 1) * PI * r + ff * PI * i * 0.5) / (r + 0.1);
    });
    return sum / sources.length;
  },
  complex_superposition(x, y, mx, my, ff = 1) {
    const fs = ff * 1.1;
    const p1 = cos(mx * fs * PI * x) * cos(my * fs * PI * y);
    const p2 = cos((mx + 2) * fs * PI * x) * cos(my * fs * PI * y) * (0.5 + 0.3 * sin(ff));
    const p3 = cos(mx * fs * PI * x) * cos((my + 1) * fs * PI * y) * (0.3 + 0.2 * cos(ff));
    const beat = cos(ff * PI * (x + y) * 2) * 0.2;
    return (p1 + p2 + p3 + beat) / 2.0;
  },
};

// Constants from constants.py (the web page replaces them with /api/defaults; the node test checks they agree).
export const DEFAULTS = {
  VIBRATION_THRESHOLD: 0.1, FORCE_SCALE: 500, DAMPING_COEFFICIENT: 10, SETTLE_TIME: 0.5, VELOCITY_DAMPING: 0.95,
  BOUNDARY_RESTITUTION: 0.3, DEFAULT_WIDTH: 1400, DEFAULT_HEIGHT: 1000, DEFAULT_GRID_SIZE: 120,
  DEFAULT_NUM_PARTICLES: 2000, MIN_PARTICLES: 100, MAX_PARTICLES: 20000, DEFAULT_FREQUENCY: 440.0, DEFAULT_SPEED: 1.0,
  MIN_SPEED: 0.1, MAX_SPEED: 5.0, DEFAULT_PARTICLE_SIZE_MIN: 1.5, DEFAULT_PARTICLE_SIZE_MAX: 3.5,
};

// presets.amplitude_map: |f| on an n x n grid (row = y, column = x), divided by (max + 1e-10). Returns Float32Array.
export function amplitudeMap(fn, n, mx, my, frequency, plateSize = 1, base = DEFAULTS.DEFAULT_FREQUENCY) {
  const f = typeof fn === 'string' ? PATTERNS[fn] : fn;
  const ff = frequency / base, out = new Float64Array(n * n), step = n > 1 ? plateSize / (n - 1) : 0;
  let max = 0;
  for (let i = 0; i < n; i++) {
    const y = i * step;
    for (let j = 0; j < n; j++) {
      const v = abs(f(j * step, y, mx, my, ff));
      out[i * n + j] = v;
      if (v > max) max = v;
    }
  }
  const k = 1 / (max + 1e-10);
  for (let i = 0; i < out.length; i++) out[i] *= k;
  return out;
}

// Particle size draw, as ChladniSimulator._random_particle_size. rand() is uniform in [0, 1).
export function particleSize(lo, hi, dist, rand) {
  if (dist === 'normal') {
    const u = 1 - rand(), v = rand();
    const g = sqrt(-2 * Math.log(u)) * cos(2 * PI * v); // Box-Muller (Python uses random.gauss)
    return Math.max(lo, Math.min(hi, (lo + hi) / 2 + g * (hi - lo) / 4));
  }
  if (dist === 'small') return lo + (hi - lo) * rand() ** 2;
  if (dist === 'large') return lo + (hi - lo) * (1 - rand() ** 2);
  return lo + (hi - lo) * rand();
}

// A set of sand grains in struct-of-arrays form (fast for 20,000 grains).
export class Sand {
  constructor(count, width, height, { sizeMin = DEFAULTS.DEFAULT_PARTICLE_SIZE_MIN, sizeMax = DEFAULTS.DEFAULT_PARTICLE_SIZE_MAX,
    dist = 'uniform', rand = Math.random, consts = DEFAULTS } = {}) {
    this.n = count; this.width = width; this.height = height; this.c = consts; this.rand = rand;
    this.x = new Float64Array(count); this.y = new Float64Array(count);
    this.vx = new Float64Array(count); this.vy = new Float64Array(count);
    this.size = new Float32Array(count); this.timer = new Float64Array(count); this.settled = new Uint8Array(count);
    // ChladniSimulator.init_particles: uniform in [50, width - 50] x [50, height - 50]
    for (let i = 0; i < count; i++) {
      this.x[i] = 50 + rand() * (width - 100);
      this.y[i] = 50 + rand() * (height - 100);
      this.size[i] = particleSize(sizeMin, sizeMax, dist, rand);
    }
  }

  // Particle.update for every grain. map is an n x n amplitude map (row-major, row = y).
  step(dt, map, n, speed = 1) {
    const { VIBRATION_THRESHOLD: thr, FORCE_SCALE: fsc, DAMPING_COEFFICIENT: dc, SETTLE_TIME: st,
      VELOCITY_DAMPING: vd, BOUNDARY_RESTITUTION: br } = this.c;
    const { x, y, vx, vy, timer, settled, width: W, height: H, rand } = this;
    const damping = vd ** speed;
    let nSettled = 0;
    for (let i = 0; i < this.n; i++) {
      // _sample_amplitude
      let gx = int((x[i] / W) * n), gy = int((y[i] / H) * n);
      gx = gx < 0 ? 0 : gx > n - 1 ? n - 1 : gx;
      gy = gy < 0 ? 0 : gy > n - 1 ? n - 1 : gy;
      const a = map[gy * n + gx];
      // _compute_forces
      let fx, fy;
      if (a > thr) {
        const fm = a * fsc * speed;
        fx = (rand() - 0.5) * fm;
        fy = (rand() - 0.5) * fm;
        settled[i] = 0; timer[i] = 0;
      } else {
        fx = -vx[i] * dc * speed;
        fy = -vy[i] * dc * speed;
        timer[i] += dt * speed;
        if (timer[i] > st) settled[i] = 1;
      }
      // _integrate
      vx[i] = (vx[i] + fx * dt) * damping;
      vy[i] = (vy[i] + fy * dt) * damping;
      x[i] += vx[i] * dt * speed;
      y[i] += vy[i] * dt * speed;
      // _enforce_bounds
      if (x[i] < 0) { x[i] = 0; vx[i] = abs(vx[i]) * br; } else if (x[i] >= W) { x[i] = W - 1; vx[i] = -abs(vx[i]) * br; }
      if (y[i] < 0) { y[i] = 0; vy[i] = abs(vy[i]) * br; } else if (y[i] >= H) { y[i] = H - 1; vy[i] = -abs(vy[i]) * br; }
      nSettled += settled[i];
    }
    return nSettled;
  }

  // Fraction of grains whose current position is within the nodal band (amplitude <= threshold).
  nodalFraction(map, n) {
    let k = 0;
    for (let i = 0; i < this.n; i++) {
      const gx = Math.min(n - 1, Math.max(0, int((this.x[i] / this.width) * n)));
      const gy = Math.min(n - 1, Math.max(0, int((this.y[i] / this.height) * n)));
      if (map[gy * n + gx] <= this.c.VIBRATION_THRESHOLD) k++;
    }
    return this.n ? k / this.n : 0;
  }
}
