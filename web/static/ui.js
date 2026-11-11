// Shared page helpers: control layout, segmented buttons, readouts, and drawing amplitude maps / sand on canvases.
import { esc, api } from './core.js';
import { DEFAULTS } from './chladni_engine.js';

// Presets and constants from the Python code (presets.py, constants.py) via the API; the engine DEFAULTS fill gaps.
export async function loadSetup() {
  const [presets, defaults] = await Promise.all([api('/presets'), api('/defaults')]);
  return { presets, consts: { ...DEFAULTS, ...defaults } };
}

export function layout(host, intro = '') {
  host.insertAdjacentHTML('beforeend', `${intro ? `<p class="lead">${intro}</p>` : ''}<div class="sim"><div class="controls"></div><div class="view"></div></div>`);
  const sim = host.querySelector('.sim:last-of-type');
  return { controls: sim.querySelector('.controls'), view: sim.querySelector('.view') };
}

// Segmented buttons. Returns { set(value) } so keyboard shortcuts can move the highlight.
export function seg(host, label, options, value, cb) {
  const wrap = document.createElement('div');
  wrap.className = 'ctl';
  wrap.innerHTML = `<label>${esc(label)}</label><div class="seg" role="group" aria-label="${esc(label)}">${options.map(([v, l, t]) =>
    `<button type="button" data-v="${esc(v)}" ${t ? `title="${esc(t)}"` : ''} aria-pressed="${String(v) === String(value)}" class="${String(v) === String(value) ? 'on' : ''}">${esc(l)}</button>`).join('')}</div>`;
  host.appendChild(wrap);
  const set = v => wrap.querySelectorAll('button').forEach(b => {
    const on = b.dataset.v === String(v); b.classList.toggle('on', on); b.setAttribute('aria-pressed', on);
  });
  wrap.addEventListener('click', e => { const b = e.target.closest('button'); if (b) { set(b.dataset.v); cb(b.dataset.v); } });
  return { set };
}

export function select(host, id, label, options, value, cb) {
  const wrap = document.createElement('div');
  wrap.className = 'ctl';
  wrap.innerHTML = `<label for="${id}">${esc(label)}</label><select id="${id}">${options.map(([v, l]) =>
    `<option value="${esc(v)}" ${v === value ? 'selected' : ''}>${esc(l)}</option>`).join('')}</select>`;
  host.appendChild(wrap);
  const el = wrap.querySelector('select');
  el.addEventListener('change', () => cb(el.value));
  return el;
}

export function button(host, label, cb, alt = false) {
  const b = document.createElement('button');
  b.type = 'button'; b.textContent = label; if (alt) b.className = 'alt';
  b.addEventListener('click', cb);
  host.appendChild(b);
  return b;
}

export function readout(host) {
  const el = document.createElement('div');
  el.className = 'readout'; el.setAttribute('aria-live', 'off');
  host.appendChild(el);
  return rows => { el.innerHTML = rows.map(([k, v]) => `<div><span>${esc(k)}</span><b>${esc(v)}</b></div>`).join(''); };
}

// Set a slider's value and its label (core.slider only updates the label on user input).
export function setSlider(input, value, fmt = v => v) {
  input.value = value;
  const b = input.closest('.ctl')?.querySelector('label b');
  if (b) b.textContent = fmt(+input.value);
}

// Colour ramps for amplitude a in [0, 1] -> [r, g, b].
export const LOOKS = {
  // dark plate: vibrating regions glow violet-blue, nodal lines stay black for the sand to show
  neon: a => { const v = Math.pow(a, 0.9); return [10 + v * 48, 8 + v * 26, 20 + v * 96]; },
  // simulator.draw_pattern_background: intensity = clamp(a * 60 + 190, 190, 255), bluish below 0.3
  desktop: a => { const i = Math.max(190, Math.min(255, Math.trunc(a * 60 + 190))); return a < 0.3 ? [i - 10, i - 5, i] : [i, i, i]; },
  // nodal-line view for thumbnails: bright where the amplitude is near zero (where sand collects)
  nodal: a => { const v = Math.pow(1 - a, 9); return [12 + v * 243, 10 + v * 190, 22 + v * 70]; },
};

// Draw an n x n amplitude map to the whole canvas (bilinear smoothing by the browser).
export function drawMap(ctx, map, n, look = LOOKS.neon, smooth = true) {
  const img = new ImageData(n, n);
  for (let i = 0; i < n * n; i++) {
    const [r, g, b] = look(map[i]);
    img.data[i * 4] = r; img.data[i * 4 + 1] = g; img.data[i * 4 + 2] = b; img.data[i * 4 + 3] = 255;
  }
  const off = document.createElement('canvas');
  off.width = n; off.height = n;
  off.getContext('2d').putImageData(img, 0, 0);
  ctx.imageSmoothingEnabled = smooth;
  ctx.drawImage(off, 0, 0, ctx.canvas.width, ctx.canvas.height);
}

// Sand colours by state: settled, slow, fast (speed > 50 px/s), as simulator._draw_particles_2d distinguishes them.
const SAND = {
  neon: ['#ffe2a0', '#c8963a', '#ff6a8a'],
  desktop: ['rgb(30,30,30)', 'rgb(60,60,60)', 'rgb(110,55,36)'],
};

// Draw the grains of a Sand (engine coordinates width x height) scaled to the canvas.
export function drawSand(ctx, sand, look = 'neon', scaleSize = 1) {
  const sx = ctx.canvas.width / sand.width, sy = ctx.canvas.height / sand.height;
  const cols = SAND[look] || SAND.neon;
  const paths = [new Path2D(), new Path2D(), new Path2D()];
  const { x, y, vx, vy, size, settled } = sand;
  for (let i = 0; i < sand.n; i++) {
    const k = settled[i] ? 0 : (vx[i] * vx[i] + vy[i] * vy[i] > 2500 ? 2 : 1);
    const s = Math.max(1, size[i] * scaleSize * (settled[i] ? 1.3 : 1) * sx);
    paths[k].rect(x[i] * sx - s / 2, y[i] * sy - s / 2, s, s);
  }
  paths.forEach((p, k) => { ctx.fillStyle = cols[k]; ctx.fill(p); });
}

// Canvas inside a figure with an accessible name. Returns the 2D context.
export function figure(host, w, h, label, caption = '') {
  const fig = document.createElement('figure');
  fig.className = 'fig';
  fig.innerHTML = `<canvas width="${w}" height="${h}" role="img" aria-label="${esc(label)}"></canvas>${caption ? `<figcaption class="small mute">${esc(caption)}</figcaption>` : ''}`;
  host.appendChild(fig);
  return fig.querySelector('canvas').getContext('2d');
}

export const fmtHz = f => `${(+f).toFixed(1)} Hz`;
