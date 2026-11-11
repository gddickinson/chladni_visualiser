// Gallery (every preset pattern) and Mode table (a grid of (m, n) mode shapes for one family). Thumbnails show the
// normalised amplitude map with the nodal band bright, i.e. where the sand would collect.
import { route, app, esc, list } from './core.js';
import { amplitudeMap } from './chladni_engine.js';
import { loadSetup, drawMap, LOOKS, select, seg, fmtHz } from './ui.js';

const THUMB = 80; // grid of the thumbnails

function thumb(canvas, method, mx, my, f, base) {
  drawMap(canvas.getContext('2d'), amplitudeMap(method, THUMB, mx, my, f, 1, base), THUMB, LOOKS.nodal);
}

route('gallery', async () => {
  const { presets, consts: C } = await loadSetup();
  const f0 = C.DEFAULT_FREQUENCY;
  app().innerHTML = `<p class="kicker">Gallery</p><h1 class="glow">Nine pattern families</h1>
    <p class="lead">Each family is one static method of <code>PatternGenerator</code> in <code>pattern_generator.py</code>, shown at its
    preset mode numbers and ${fmtHz(f0)}. Bright lines are where the amplitude is close to zero: the nodal lines the sand finds.</p>
    <div class="grid gal">${list(presets.patterns, p => `
      <a class="card" href="#/plate?p=${p.slug}">
        <canvas width="320" height="320" data-slug="${p.slug}" role="img" aria-label="${esc(p.name)} nodal pattern, mode (${p.mode_x}, ${p.mode_y})"></canvas>
        <b>${esc(p.name)}</b><small>key ${p.key.toUpperCase()} · mode (${p.mode_x}, ${p.mode_y}) · ${esc(p.method)}</small>
        <span>${esc(p.summary)} ${esc(p.detail)}</span></a>`)}</div>`;
  const bySlug = Object.fromEntries(presets.patterns.map(p => [p.slug, p]));
  document.querySelectorAll('.gal canvas').forEach(c => { const p = bySlug[c.dataset.slug]; thumb(c, p.method, p.mode_x, p.mode_y, f0, f0); });
});

route('modes', async (args, q) => {
  const { presets, consts: C } = await loadSetup();
  const st = { slug: q.p || presets.patterns[0].slug, freq: C.DEFAULT_FREQUENCY, size: 5 };
  const host = app();
  host.innerHTML = `<p class="kicker">Mode table</p><h1 class="glow">Mode shapes (m, n)</h1>
    <p class="lead">Rows are mode y (n), columns mode x (m), for one pattern family at one frequency. Click a cell to shake sand on it.</p>
    <div class="row ctlrow"></div><div id="table" class="scroll"></div>`;
  const row = host.querySelector('.ctlrow');
  select(row, 'mpat', 'Pattern family', presets.patterns.map(p => [p.slug, p.name]), st.slug, v => { st.slug = v; draw(); });
  seg(row, 'Frequency', presets.frequencies.map(f => [f.frequency, f.note, `${f.frequency} Hz`]), st.freq, v => { st.freq = +v; draw(); });
  seg(row, 'Table size', [[4, '4×4'], [5, '5×5'], [6, '6×6']], st.size, v => { st.size = +v; draw(); });
  function draw() {
    const p = presets.patterns.find(x => x.slug === st.slug);
    const ns = Array.from({ length: st.size }, (_, i) => i + 1);
    document.getElementById('table').innerHTML = `<table class="modes"><caption class="small mute">${esc(p.name)} at ${fmtHz(st.freq)}</caption>
      <tr><th scope="col">n \\ m</th>${list(ns, m => `<th scope="col">${m}</th>`)}</tr>
      ${list(ns, n => `<tr><th scope="row">${n}</th>${list(ns, m => `<td><a href="#/plate?p=${p.slug}&mx=${m}&my=${n}&f=${st.freq}" aria-label="${esc(p.name)} mode (${m}, ${n})">
        <canvas width="120" height="120" data-m="${m}" data-n="${n}" role="img" aria-label="mode (${m}, ${n})"></canvas></a></td>`)}</tr>`)}</table>`;
    document.querySelectorAll('#table canvas').forEach(c => thumb(c, p.method, +c.dataset.m, +c.dataset.n, st.freq, C.DEFAULT_FREQUENCY));
  }
  draw();
});
