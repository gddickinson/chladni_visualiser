// About: what the model is (from the code's own docstrings and constants), the desktop controls, how to run, credits.
import { route, app, api, esc, list } from './core.js';
import { loadSetup } from './ui.js';

const DESKTOP_KEYS = [ // simulator.print_instructions
  ['Q W E R T Y U I O', 'Pattern presets'], ['1 to 0', 'Frequencies / musical notes'], ['V', 'Cycle view: both, particles, pattern'],
  ['3', 'Toggle 3D mode'], ['C', 'Cycle camera views (perspective, top, N/S/E/W)'], ['Left / Right', 'Perspective camera angle'],
  ['Page Up / Down', 'Zoom'], ['[ ]', 'Fewer / more particles (up to 20,000)'], ['Shift + - / Shift + =', 'Particle size range'],
  ['D', 'Cycle particle size distribution'], ['+ / -', 'Speed'], ['Up / Down', 'Fine speed adjustment'], ['Space', 'Reset particles'], ['Esc', 'Quit'],
];

route('about', async () => {
  const [info, { presets, consts: C }] = await Promise.all([api('/info'), loadSetup()]);
  app().innerHTML = `<p class="kicker">About</p><h1 class="glow">How the visualiser works</h1>
  <p class="lead">An interactive simulation of Chladni patterns: virtual particles settle into the nodal lines of vibrating plates,
  the geometric patterns first demonstrated by Ernst Chladni in the 18th century. This site is the web version of the
  Python/Pygame <a href="https://github.com/gddickinson/chladni_visualiser">Chladni Visualizer</a>.</p>

  <h2>The plate</h2>
  <p>${esc(info.background)}</p>
  <p>Each pattern family is a function f(x, y; m, n, φ) of the plate coordinates x, y ∈ [0, 1], the two mode numbers and the
  frequency factor φ (the chosen frequency divided by ${C.DEFAULT_FREQUENCY} Hz). The simulator samples it on a
  ${C.DEFAULT_GRID_SIZE} × ${C.DEFAULT_GRID_SIZE} grid and normalises:</p>
  <p><span class="eq">A(x, y) = |f(x, y)| / (max |f| + 10⁻¹⁰)</span></p>
  <p>For example the classic rectangular mode is</p>
  <p><span class="eq">f = cos(mφπx)·cos(nφπy) + 0.3·cos(mφπx/2)·cos(nφπy/2)·sin(φπ)</span></p>
  <div class="scroll"><table><tr><th>Family</th><th>Key</th><th>Preset (m, n)</th><th>What the code does</th></tr>
  ${list(presets.patterns, p => `<tr><td><a href="#/plate?p=${p.slug}">${esc(p.name)}</a></td><td class="mono">${p.key.toUpperCase()}</td>
    <td class="mono">(${p.mode_x}, ${p.mode_y})</td><td>${esc(p.summary)} ${esc(p.detail)}</td></tr>`)}</table></div>

  <h2>The sand</h2>
  <p>Each grain (<code>particle.py</code>) looks up the amplitude A at its position every frame and then:</p>
  <ul>
    <li>if <b>A &gt; ${C.VIBRATION_THRESHOLD}</b>, it gets a random kick in x and y, each uniform in ±½ · A · ${C.FORCE_SCALE} · speed, and is marked as moving;</li>
    <li>otherwise a damping force −v · ${C.DAMPING_COEFFICIENT} · speed slows it, and after ${C.SETTLE_TIME} s in a quiet region it counts as settled;</li>
    <li>velocity is integrated, multiplied by ${C.VELOCITY_DAMPING}<sup>speed</sup> each step, and the position advanced;</li>
    <li>at the plate edge it is clamped and bounces back with ${C.BOUNDARY_RESTITUTION} of its speed.</li>
  </ul>
  <p>Grains therefore random-walk out of the vibrating regions and stop where the plate is nearly still, so the sand accumulates along
  the nodal lines. At speed 1 this takes minutes of simulated time; the web visualiser adds a time-lapse control (several physics steps
  per drawn frame; the desktop app draws every step) and starts with 6,000 grains at speed 3× (desktop: 2,000 at 1×).</p>
  <p class="callout">The patterns are simplified analytic approximations that capture the visual character of each mode family; they
  are not solutions of the biharmonic plate equation, and the circular modes use an exponentially decaying cosine in place of Bessel functions.</p>

  <h2>What the web version covers</h2>
  <p><code>chladni_engine.js</code> is a line-by-line port of all nine <code>PatternGenerator</code> methods, the amplitude map and the
  <code>Particle</code> update, plus the pattern and musical-note presets, the four grain-size distributions and the three view modes.
  It is tested against numbers computed by the Python code (see <a href="#/check">Cross-check</a>). The desktop app's 3D view
  (camera views, zoom, perspective) and the particle-size range keys are not ported; mode-number sliders and the free frequency slider are web additions.</p>

  <h2>Run it yourself</h2>
  <h3>Desktop app (Pygame)</h3>
  <pre>pip install -r requirements.txt
python main.py</pre>
  <div class="scroll"><table><tr><th>Key</th><th>Action</th></tr>${list(DESKTOP_KEYS, ([k, a]) => `<tr><td class="mono">${esc(k)}</td><td>${esc(a)}</td></tr>`)}</table></div>
  <h3>Web app (this site, with the Python API)</h3>
  <pre>pip install -r requirements-web.txt
python run_web.py          # http://127.0.0.1:8102</pre>
  <p>The local app serves presets and constants from <code>presets.py</code> and <code>constants.py</code>, and computes pattern grids
  with the real NumPy generator for the cross-check. The static GitHub Pages site is built by <code>scripts/build_static.py</code>.</p>

  <h2>Credits</h2>
  <p>Chladni Visualizer by George Dickinson, MIT licence. Built with AI assistance from <a href="https://claude.com/">Claude (Anthropic)</a>.</p>`;
});
