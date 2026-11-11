// Home page: hero with a live sand plate, counts from the API, entry cards.
import { route, api, app, esc, list, animate, rng } from './core.js';
import { amplitudeMap, Sand } from './chladni_engine.js';
import { loadSetup, drawMap, drawSand, LOOKS } from './ui.js';

const DOORS = [
  ['#/plate', 'Visualiser', 'The full simulator: nine pattern families, mode numbers, frequency and musical-note presets, up to 20,000 grains, the desktop key bindings.'],
  ['#/gallery', 'Gallery', 'Every pattern family at its preset mode numbers, with the physics notes from the code. Click one to shake sand on it.'],
  ['#/modes', 'Mode table', 'A table of mode shapes (m, n) for any family, the way Chladni catalogued his figures.'],
  ['#/check', 'Cross-check', 'The browser engine against the Python generator: the same grids computed by NumPy on the server, compared value by value.'],
  ['#/about', 'About', 'What the model does (and does not do), how to run the desktop and web apps, credits.'],
];

route('home', async () => {
  const [info, { presets, consts: C }] = await Promise.all([api('/info'), loadSetup()]);
  app().innerHTML = `
  <section class="hero two heroplate">
    <div>
      <p class="kicker">Vibrating plates · nodal lines · sand</p>
      <h1 class="glow">Chladni Visualizer</h1>
      <p class="lead">Thousands of virtual grains settle into the nodal lines of a vibrating plate, revealing the geometric
      figures first demonstrated by Ernst Chladni in the 18th century. The simulation runs in your browser, ported from the
      Python/Pygame desktop app.</p>
      <a class="btn" href="#/plate">Open the visualiser</a><a class="btn alt" href="#/gallery">Browse the patterns</a>
    </div>
    <figure class="fig"><canvas id="hero" width="700" height="500" role="img" aria-label="Live simulation: sand settling on the nodal lines of a flower pattern"></canvas>
      <figcaption class="small mute" id="herocap"></figcaption></figure>
  </section>
  <div class="tiles">
    <div class="tile"><b>${info.patterns}</b><span>pattern families</span></div>
    <div class="tile"><b>${info.frequency_presets}</b><span>musical-note presets</span></div>
    <div class="tile"><b>${info.max_particles.toLocaleString('en')}</b><span>grains at most</span></div>
    <div class="tile"><b>${info.grid_size}²</b><span>amplitude grid</span></div>
  </div>
  <div class="grid wide">${list(DOORS, ([href, t, d]) => `<a class="card door" href="${href}"><b>${t}</b><span>${d}</span></a>`)}</div>
  <h2>Pattern families</h2>
  <p>${list(presets.patterns, p => `<a class="tag a" href="#/plate?p=${p.slug}">${esc(p.name)}</a>`)}</p>`;
  hero(presets, C);
});

// Small live plate: the flower preset at speed 5 with 4,000 grains, two physics steps per frame.
function hero(presets, C) {
  const ctx = document.getElementById('hero').getContext('2d');
  const p = presets.patterns.find(x => x.slug === 'flower') || presets.patterns[0];
  const n = 90, map = amplitudeMap(p.method, n, p.mode_x, p.mode_y, C.DEFAULT_FREQUENCY, 1, C.DEFAULT_FREQUENCY);
  const sand = new Sand(4000, C.DEFAULT_WIDTH, C.DEFAULT_HEIGHT, { rand: rng(7), consts: C });
  document.getElementById('herocap').textContent = `${p.name}, mode (${p.mode_x}, ${p.mode_y}) at ${C.DEFAULT_FREQUENCY} Hz, speed 5×`;
  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const draw = () => { drawMap(ctx, map, n, LOOKS.neon); drawSand(ctx, sand, 'neon', 1.4); };
  if (still) { for (let i = 0; i < 2400; i++) sand.step(1 / 60, map, n, 5); draw(); return; }
  animate(() => { sand.step(1 / 60, map, n, 5); sand.step(1 / 60, map, n, 5); draw(); });
}
