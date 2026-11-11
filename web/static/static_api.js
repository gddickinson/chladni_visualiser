// Static-site data layer: answers api() calls from the JSON files exported by scripts/build_static.py.
// /pattern/<slug> exists only at the preset modes and the default 440 Hz (computed by the Python generator at build
// time); other parameters need the local Python server.
const files = new Map();
async function file(rel) {
  if (!files.has(rel)) files.set(rel, fetch('api/' + rel + '.json').then(r => { if (!r.ok) throw new Error(`${r.status} ${rel}`); return r.json(); }));
  return files.get(rel);
}

export async function staticApi(path) {
  const [p, qs] = path.split('?');
  const clean = p.replace(/^\/+/, '');
  if (clean.startsWith('pattern/') && qs) throw new Error('Custom server-rendered patterns need the local app (Python server).');
  return file(clean);
}
