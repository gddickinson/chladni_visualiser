// Visualiser: the desktop simulator in the browser. Sand (particle.py physics, ported in chladni_engine.js) is shaken
// off the vibrating regions of the selected pattern and collects on its nodal lines.
// Keys as in the desktop app: Q-O patterns, 1-0 notes, V view, D size distribution, Space reset, +/- speed, [ ] grains.
import { route, app, esc, slider, animate, rng } from './core.js';
import { amplitudeMap, Sand } from './chladni_engine.js';
import { loadSetup, layout, seg, select, button, readout, setSlider, drawMap, drawSand, LOOKS, fmtHz } from './ui.js';

const VIEW_W = 1400, VIEW_H = 1000; // canvas pixels; the engine uses the desktop window size from /api/defaults

route('plate', async (args, q) => {
  const { presets, consts: C } = await loadSetup();
  const bySlug = Object.fromEntries(presets.patterns.map(p => [p.slug, p]));
  const start = bySlug[q.p] || presets.patterns[0];
  const W = C.DEFAULT_WIDTH, H = C.DEFAULT_HEIGHT, GRID = C.DEFAULT_GRID_SIZE;
  const st = {
    slug: start.slug, mx: q.mx != null ? +q.mx : start.mode_x, my: q.my != null ? +q.my : start.mode_y,
    freq: q.f != null ? +q.f : C.DEFAULT_FREQUENCY, speed: 3, laps: 6, count: 6000, // web start-up: more grains, faster (desktop: 2,000 grains at 1×)
    dist: presets.size_distributions[0], view: 0, look: 'neon', running: true, simTime: 0,
  };

  const host = app();
  host.innerHTML = `<p class="kicker">Visualiser</p><h1 class="glow">Sand on a vibrating plate</h1>`;
  const { controls, view } = layout(host, 'Choose a pattern family, its mode numbers and a driving frequency. Grains in vibrating regions get random kicks; in near-still regions they are damped and settle, so the sand draws the nodal lines.');
  const ctx = (() => {
    const c = document.createElement('canvas');
    c.width = VIEW_W; c.height = VIEW_H; c.id = 'plate'; c.tabIndex = 0;
    c.setAttribute('role', 'img');
    view.appendChild(c);
    view.insertAdjacentHTML('beforeend', `<p class="small mute keys">Keys: <kbd>Q</kbd>-<kbd>O</kbd> pattern · <kbd>1</kbd>-<kbd>0</kbd> note ·
      <kbd>V</kbd> view · <kbd>D</kbd> grain sizes · <kbd>Space</kbd> new sand · <kbd>+</kbd>/<kbd>-</kbd> speed · <kbd>[</kbd>/<kbd>]</kbd> grains · <kbd>P</kbd> pause</p>
      <div class="panel" id="pdoc"></div>`);
    return c.getContext('2d');
  })();

  // --- controls -------------------------------------------------------------
  const patSel = select(controls, 'pat', 'Pattern family', presets.patterns.map(p => [p.slug, `${p.name} (${p.key.toUpperCase()})`]), st.slug, v => setPattern(v));
  const mxIn = slider(controls, { id: 'mx', label: 'Mode x (m)', min: 0, max: 16, value: st.mx }, v => { st.mx = v; remap(); });
  const myIn = slider(controls, { id: 'my', label: 'Mode y (n)', min: 0, max: 16, value: st.my }, v => { st.my = v; remap(); });
  const fIn = slider(controls, { id: 'f', label: 'Frequency', min: 55, max: 1760, step: 0.1, value: st.freq, fmt: v => v.toFixed(1), unit: ' Hz' },
    v => { st.freq = v; notes.set(''); remap(); });
  const notes = seg(controls, 'Notes (keys 1-0)', presets.frequencies.map(f => [f.frequency, f.note, `${f.frequency} Hz (key ${f.key})`]), st.freq,
    v => setFreq(+v));
  const spIn = slider(controls, { id: 'sp', label: 'Speed', min: C.MIN_SPEED, max: C.MAX_SPEED, step: 0.1, value: st.speed, fmt: v => v.toFixed(1), unit: '×' },
    v => { st.speed = v; });
  slider(controls, { id: 'laps', label: 'Time-lapse (physics steps per frame)', min: 1, max: 20, value: st.laps }, v => { st.laps = v; });
  const nIn = slider(controls, { id: 'n', label: 'Grains', min: C.MIN_PARTICLES, max: C.MAX_PARTICLES, step: 100, value: st.count, fmt: v => v.toLocaleString('en') },
    v => { st.count = v; resetLater(); });
  const distSeg = seg(controls, 'Grain sizes (D)', presets.size_distributions.map(d => [d, d]), st.dist, v => { st.dist = v; reset(); });
  const viewSeg = seg(controls, 'View (V)', presets.display_modes.map((m, i) => [i, m.replace(' Only', '')]), st.view, v => { st.view = +v; });
  seg(controls, 'Look', [['neon', 'Neon'], ['desktop', 'Desktop']], st.look, v => { st.look = v; });
  const runBtn = button(controls, 'Pause', () => toggleRun());
  button(controls, 'New sand', () => reset(), true);
  const show = readout(controls);

  // --- state changes ----------------------------------------------------------
  let map = null, sand = null, seed = 1, resetTimer = 0;
  function remap() {
    const p = bySlug[st.slug];
    map = amplitudeMap(p.method, GRID, st.mx, st.my, st.freq, 1, C.DEFAULT_FREQUENCY);
    ctx.canvas.setAttribute('aria-label', `${p.name}, mode (${st.mx}, ${st.my}) at ${fmtHz(st.freq)}: sand pattern on the plate`);
  }
  function reset() {
    sand = new Sand(st.count, W, H, { sizeMin: C.DEFAULT_PARTICLE_SIZE_MIN, sizeMax: C.DEFAULT_PARTICLE_SIZE_MAX, dist: st.dist, rand: rng(seed++), consts: C });
    st.simTime = 0;
  }
  function resetLater() { clearTimeout(resetTimer); resetTimer = setTimeout(reset, 150); }
  function setPattern(slug) {
    const p = bySlug[slug];
    Object.assign(st, { slug, mx: p.mode_x, my: p.mode_y });
    patSel.value = slug; setSlider(mxIn, st.mx); setSlider(myIn, st.my);
    document.getElementById('pdoc').innerHTML = `<h3>${esc(p.name)} <span class="mute">· PatternGenerator.${esc(p.method)}</span></h3>
      <p><b>${esc(p.summary)}</b> ${esc(p.detail)}</p>`;
    remap();
  }
  function setFreq(f) { st.freq = f; setSlider(fIn, f, v => v.toFixed(1)); notes.set(f); remap(); }
  function setSpeed(v) { st.speed = Math.round(Math.min(C.MAX_SPEED, Math.max(C.MIN_SPEED, v)) * 10) / 10; setSlider(spIn, st.speed, x => x.toFixed(1)); }
  function setCount(v) { st.count = Math.min(C.MAX_PARTICLES, Math.max(C.MIN_PARTICLES, v)); setSlider(nIn, st.count, x => x.toLocaleString('en')); reset(); }
  function toggleRun() { st.running = !st.running; runBtn.textContent = st.running ? 'Pause' : 'Run'; }

  // desktop key bindings (simulator.handle_events), ignored while typing in a field
  const keyFor = Object.fromEntries(presets.patterns.map(p => [p.key, p.slug]));
  const noteFor = Object.fromEntries(presets.frequencies.map(f => [f.key, f.frequency]));
  function onKey(e) {
    if (e.ctrlKey || e.metaKey || e.altKey || /^(SELECT|TEXTAREA)$/.test(e.target.tagName) || (e.target.type && e.target.type !== 'range' && e.target.tagName === 'INPUT')) return;
    const k = e.key.toLowerCase();
    if (keyFor[k]) setPattern(keyFor[k]);
    else if (k in noteFor) setFreq(noteFor[k]);
    else if (k === 'v') { st.view = (st.view + 1) % 3; viewSeg.set(st.view); }
    else if (k === 'd') { const d = presets.size_distributions; st.dist = d[(d.indexOf(st.dist) + 1) % d.length]; distSeg.set(st.dist); reset(); }
    else if (k === ' ') { reset(); }
    else if (k === 'p') toggleRun();
    else if (k === '+' || k === '=') setSpeed(st.speed + 0.5);
    else if (k === '-' || k === '_') setSpeed(st.speed - 0.5);
    else if (k === '[') setCount(st.count - (st.count > 5000 ? 1000 : 250));
    else if (k === ']') setCount(st.count + (st.count > 5000 ? 1000 : 250));
    else return;
    e.preventDefault();
  }
  document.addEventListener('keydown', onKey);

  setPattern(st.slug); setFreq(st.freq); reset();

  // --- loop -------------------------------------------------------------------
  let frames = 0, settled = 0;
  const stop = animate(() => {
    if (st.running) {
      for (let i = 0; i < st.laps; i++) settled = sand.step(1 / 60, map, GRID, st.speed);
      st.simTime += st.laps / 60;
    }
    const look = st.look;
    if (st.view !== 1) drawMap(ctx, map, GRID, LOOKS[look]);
    else { ctx.fillStyle = look === 'desktop' ? '#fff' : '#07060d'; ctx.fillRect(0, 0, VIEW_W, VIEW_H); }
    if (st.view !== 2) drawSand(ctx, sand, look, 1.6);
    if (frames++ % 10 === 0) {
      show([['pattern', bySlug[st.slug].name], ['mode (m, n)', `(${st.mx}, ${st.my})`], ['frequency', fmtHz(st.freq)],
        ['freq factor', (st.freq / C.DEFAULT_FREQUENCY).toFixed(3)], ['grains', sand.n.toLocaleString('en')],
        ['settled', `${(100 * settled / sand.n).toFixed(0)}%`], ['on nodal band', `${(100 * sand.nodalFraction(map, GRID)).toFixed(0)}%`],
        ['simulated time', `${st.simTime.toFixed(1)} s`]]);
    }
  });
  // the router stops the animation on leaving; the key handler goes with it
  window.addEventListener('hashchange', () => { document.removeEventListener('keydown', onKey); stop(); }, { once: true });
});
