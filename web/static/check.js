// Cross-check: the JS engine's amplitude maps against grids computed by the Python generator (presets.amplitude_map,
// served by /api/pattern/<slug>). On the static site the Python grids were exported at build time (preset modes,
// 440 Hz); with the local server any mode numbers and frequency can be checked.
import { route, app, api, esc, list, isStatic, needsServer } from './core.js';
import { amplitudeMap } from './chladni_engine.js';
import { loadSetup, drawMap, LOOKS, button, fmtHz } from './ui.js';

function compare(py, method, base) {
  const js = amplitudeMap(method, py.grid, py.mode_x, py.mode_y, py.frequency, 1, base);
  let max = 0;
  py.values.forEach((v, i) => { max = Math.max(max, Math.abs(v - js[i])); });
  return { js, max };
}

function rowHtml(p, py, max) {
  const ok = max < 1e-6; // the server rounds to 7 decimals
  return `<tr><td><b>${esc(p.name)}</b><br><span class="small mute">${esc(p.method)}</span></td>
    <td class="mono">(${py.mode_x}, ${py.mode_y}) · ${fmtHz(py.frequency)} · ${py.grid}²</td>
    <td><canvas width="96" height="96" data-k="py" role="img" aria-label="Python grid"></canvas></td>
    <td><canvas width="96" height="96" data-k="js" role="img" aria-label="JavaScript grid"></canvas></td>
    <td class="mono ${ok ? 'ok' : 'err'}">${max.toExponential(2)} ${ok ? '✓' : '✗'}</td></tr>`;
}

route('check', async () => {
  const { presets, consts: C } = await loadSetup();
  const base = C.DEFAULT_FREQUENCY;
  const host = app();
  host.innerHTML = `<p class="kicker">Cross-check</p><h1 class="glow">Browser engine vs Python</h1>
    <p class="lead">Left: the normalised amplitude map computed by NumPy in <code>presets.amplitude_map</code> (the same function the
    desktop simulator calls every frame). Right: <code>chladni_engine.js</code> in this browser. The last column is the largest
    absolute difference over the grid (the server rounds to 7 decimals).</p>
    <div class="scroll"><table class="check"><thead><tr><th>Pattern</th><th>Mode · frequency · grid</th><th>Python</th><th>Browser</th><th>max |Δ|</th></tr></thead><tbody id="rows"></tbody></table></div>
    <h2>Any mode, any frequency</h2><div id="custom"></div>
    <p class="small mute">The node test <code>chladni_engine.test.mjs</code> also checks 180 point values, 9 maps and 3 particle
    trajectories against numbers from the Python code (run by <code>tests/test_web.py</code>).</p>`;
  const tbody = document.getElementById('rows');
  let worst = 0;
  for (const p of presets.patterns) {
    const py = await api(`/pattern/${p.slug}`);
    const { js, max } = compare(py, p.method, base);
    worst = Math.max(worst, max);
    tbody.insertAdjacentHTML('beforeend', rowHtml(p, py, max));
    const tr = tbody.lastElementChild;
    drawMap(tr.querySelector('[data-k=py]').getContext('2d'), Float64Array.from(py.values), py.grid, LOOKS.nodal, false);
    drawMap(tr.querySelector('[data-k=js]').getContext('2d'), js, py.grid, LOOKS.nodal, false);
  }
  tbody.insertAdjacentHTML('beforeend', `<tr><td colspan="4"><b>All ${presets.patterns.length} families</b></td><td class="mono ${worst < 1e-6 ? 'ok' : 'err'}">${worst.toExponential(2)}</td></tr>`);
  custom(document.getElementById('custom'), presets, base);
});

function custom(host, presets, base) {
  if (isStatic()) { host.innerHTML = needsServer('Checking other mode numbers and frequencies against Python'); return; }
  host.innerHTML = `<div class="row">
    <div><label for="cp">Pattern</label><select id="cp">${list(presets.patterns, p => `<option value="${p.slug}">${esc(p.name)}</option>`)}</select></div>
    <div><label for="cm">Mode x</label><input id="cm" type="number" min="0" max="40" value="5"></div>
    <div><label for="cn">Mode y</label><input id="cn" type="number" min="0" max="40" value="4"></div>
    <div><label for="cf">Frequency (Hz)</label><input id="cf" type="number" min="1" max="5000" step="0.1" value="587.3"></div>
    <div><label for="cg">Grid</label><input id="cg" type="number" min="2" max="200" value="120"></div></div>
    <p id="cout" class="mono" aria-live="polite"></p>`;
  const val = id => host.querySelector('#' + id).value;
  button(host.querySelector('.row'), 'Compare', async () => {
    const out = host.querySelector('#cout');
    try {
      const py = await api(`/pattern/${val('cp')}?mode_x=${+val('cm')}&mode_y=${+val('cn')}&frequency=${+val('cf')}&grid=${+val('cg')}`, { fresh: true });
      const p = presets.patterns.find(x => x.slug === py.slug);
      const { max } = compare(py, p.method, base);
      out.innerHTML = `${esc(p.name)} (${py.mode_x}, ${py.mode_y}) at ${fmtHz(py.frequency)}, ${py.grid}² grid: max |Δ| = <span class="${max < 1e-6 ? 'ok' : 'err'}">${max.toExponential(2)}</span>`;
    } catch (e) { out.innerHTML = `<span class="err">${esc(e.message)}</span>`; }
  });
}
