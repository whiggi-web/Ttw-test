// TTW Animation Lab. Runs from assets/ttw-wrestlers/viewer/ (serve the assets folder) or as a bundled page.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const LIBS = window.TTW_LAB_LIBS || null;
const WL = LIBS ? LIBS.wrestler : await import('../loader.js');
if (!LIBS) { try { await import('../loader-ext.js'); } catch (e) { console.warn('loader-ext.js not found', e); } }
const RT = LIBS ? LIBS.runtime : await import('../ttw-anim-runtime.js');
const V = LIBS ? LIBS.validate : await import('./validate.js');

const $ = (id) => document.getElementById(id);
const DEG = Math.PI / 180;
const missing = [];

// ------------------------------------------------------------------ data
async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${res.status} ${url}`);
  return res.json();
}

let DATA;
if (window.TTW_LAB_DATA) DATA = window.TTW_LAB_DATA;
else {
  let manifest, base = '../';
  for (const f of ['manifest-master.json', 'manifest-batch2.json', 'manifest.json']) {
    try { manifest = await fetchJSON(base + f); manifest.__file = f; break; } catch (e) { /* try next */ }
  }
  const skeleton = await fetchJSON(base + manifest.skeleton);
  const ring = await fetchJSON('./ring-reference.json');
  const wrestlers = {}, animations = {}, paired = {};
  await Promise.all([
    ...manifest.wrestlers.filter((w) => !w.status || w.status === 'ready').map(async (w) => {
      try { wrestlers[w.id] = await fetchJSON(base + w.file); } catch (e) { missing.push(`wrestler ${w.id}: ${w.file}`); }
    }),
    ...manifest.animations.filter((a) => !a.status || a.status === 'ready').map(async (a) => {
      try { animations[a.id] = await fetchJSON(base + a.file); } catch (e) { missing.push(`animation ${a.id}: ${a.file}`); }
    }),
    ...(manifest.paired || []).filter((p) => !p.status || p.status === 'ready').map(async (p) => {
      try { paired[p.id] = await fetchJSON(base + p.file); } catch (e) { missing.push(`paired ${p.id}: ${p.file}`); }
    }),
  ]);
  DATA = { manifest, skeleton, ring, wrestlers, animations, paired };
}
const { manifest, skeleton, ring, wrestlers: WDEFS, animations: ADEFS, paired: PDEFS } = DATA;

const pack = WL.createPack({ skeleton, wrestlers: WDEFS, animations: {} });
for (const def of Object.values(ADEFS)) {
  try { pack.animations.add(def); } catch (e) { missing.push(`animation ${def.id}: ${e.message}`); }
}
const LIB = pack.animations;

// ------------------------------------------------------------------ scene
const view = $('view');
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
view.prepend(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color('#0b0c10');
const camera = new THREE.PerspectiveCamera(40, 1, 0.05, 200);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.minDistance = 0.8;
controls.maxDistance = 30;
scene.add(new THREE.HemisphereLight('#d0dcff', '#2a2218', 1.1));
const key = new THREE.DirectionalLight('#fff3e4', 2.4);
key.position.set(4, 9, -5);
key.castShadow = true;
key.shadow.mapSize.set(2048, 2048);
Object.assign(key.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7, near: 1, far: 30 });
scene.add(key, key.target);
const rim = new THREE.DirectionalLight('#7fc4ff', 0.9);
rim.position.set(-5, 4, 6);
scene.add(rim);

// ring reference geometry, built from ring-reference.json (same numbers as the arena)
const ringGroup = new THREE.Group();
const ROPES = [];
scene.add(ringGroup);
(function buildRing() {
  const M = ring.matHeight, RL = ring.ropeLine, AE = ring.apronEdge, F = ring.floorHeight;
  const floor = new THREE.Mesh(new THREE.BoxGeometry(18, 0.04, 18), new THREE.MeshStandardMaterial({ color: '#1c1f28', roughness: 1 }));
  floor.position.y = F - 0.02; floor.receiveShadow = true; scene.add(floor);
  const grid = new THREE.GridHelper(18, 36, '#39404f', '#262b36'); grid.position.y = F + 0.002; scene.add(grid);
  const apron = new THREE.Mesh(new THREE.BoxGeometry(AE * 2, M - F - 0.1, AE * 2), new THREE.MeshStandardMaterial({ color: '#15161c', roughness: 0.9 }));
  apron.position.y = F + (M - F - 0.1) / 2; apron.receiveShadow = true; ringGroup.add(apron);
  const mat = new THREE.Mesh(new THREE.BoxGeometry(AE * 2, 0.1, AE * 2), new THREE.MeshStandardMaterial({ color: '#dfe3ea', roughness: 0.95 }));
  mat.position.y = M - 0.05; mat.receiveShadow = true; ringGroup.add(mat);
  const edge = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(RL * 2, 0.001, RL * 2)), new THREE.LineBasicMaterial({ color: '#9aa3b5' }));
  edge.position.y = M + 0.002; ringGroup.add(edge);
  const ropeMat = new THREE.MeshStandardMaterial({ color: '#d0242c', roughness: 0.6 });
  ring.ropeHeights.forEach((h, li) => {
    for (const [ax, sgn] of [['x', 1], ['x', -1], ['z', 1], ['z', -1]]) {
      const rope = new THREE.Mesh(new THREE.CylinderGeometry(ring.ropeRadius, ring.ropeRadius, RL * 2, 8, 70), ropeMat);
      rope.castShadow = true;
      if (ax === 'x') { rope.rotation.z = Math.PI / 2; rope.position.set(0, h, sgn * RL); }
      else { rope.rotation.x = Math.PI / 2; rope.position.set(sgn * RL, h, 0); }
      ringGroup.add(rope);
      rope.updateMatrixWorld(true);
      const pos = rope.geometry.attributes.position;
      ROPES.push({ mesh: rope, level: ['bottom', 'middle', 'top'][li], axis: ax, base: pos.array.slice(), len: RL * 2,
        a: rope.localToWorld(new THREE.Vector3(0, -RL, 0)), b: rope.localToWorld(new THREE.Vector3(0, RL, 0)), bent: false });
    }
  });
  const postMat = new THREE.MeshStandardMaterial({ color: '#a3acb6', metalness: 0.7, roughness: 0.35 });
  const padMat = new THREE.MeshStandardMaterial({ color: '#e6e6e6', roughness: 0.7 });
  const tb = ring.turnbuckle;
  for (const x of [-1, 1]) for (const z of [-1, 1]) {
    const post = new THREE.Mesh(new THREE.CylinderGeometry(ring.post.radius, ring.post.radius, ring.post.top - F, 12), postMat);
    post.position.set(x * ring.post.position, F + (ring.post.top - F) / 2, z * ring.post.position); post.castShadow = true; ringGroup.add(post);
    const pad = new THREE.Mesh(new THREE.BoxGeometry(tb.padSize, tb.padTop - tb.padBottom, tb.padSize), padMat);
    pad.position.set(x * tb.padCenter, (tb.padTop + tb.padBottom) / 2, z * tb.padCenter); pad.rotation.y = Math.PI / 4; ringGroup.add(pad);
  }
})();
$('showRing').onchange = (e) => (ringGroup.visible = e.target.checked);

// ------------------------------------------------------------------ placement: frame coords -> world
const FRAMES = {
  rope: { origin: new THREE.Vector3(0, ring.matHeight, -ring.ropeLine) },     // south ropes, ring towards +Z
  corner: { origin: new THREE.Vector3(-ring.ropeLine, ring.matHeight, -ring.ropeLine) }, // south-west post
  mat: { origin: new THREE.Vector3(0, ring.matHeight, 0) },                               // ring centre
};
const LEGACY = { 'ropes.rope-lean': ['rope', [0, 0, 0.42, 180]], 'ropes.rope-rebound': ['rope', [0, 0, 0.42, 180]] };
function startOf(def) {
  let frame = def.placement?.frame, fs = def.placement?.frameStart;
  if (!frame && LEGACY[def.id]) [frame, fs] = LEGACY[def.id];
  if (!frame || !FRAMES[frame] || !fs) return { position: new THREE.Vector3(0, ring.matHeight, 0.6), yaw: 0 };
  const o = FRAMES[frame].origin;
  return { position: new THREE.Vector3(o.x + fs[0], o.y + fs[1], o.z + fs[2]), yaw: fs[3] * DEG };
}

// ------------------------------------------------------------------ wrestlers
const actors = {};
function makeActor(slot, id) {
  if (actors[slot]) { scene.remove(actors[slot].w.object, actors[slot].skel, actors[slot].hit); }
  const w = pack.createWrestler(id);
  w.autoRootMotion = true;
  scene.add(w.object);
  const skel = new THREE.SkeletonHelper(w.object); skel.material.depthTest = false; skel.visible = $('showSkel').checked; scene.add(skel);
  const hit = new THREE.Mesh(new THREE.CapsuleGeometry(0.3, 1.25, 4, 12), new THREE.MeshBasicMaterial({ color: '#4fd18b', wireframe: true, transparent: true, opacity: 0.35 }));
  hit.visible = $('showHit').checked; scene.add(hit);
  w.on('*', (e) => { if (e.name !== 'finished') tick(`${slot === 'A' ? '' : 'B '}${e.name}${e.time !== undefined ? ' @' + e.time.toFixed(2) : ''}`, ''); });
  actors[slot] = { w, skel, hit };
  return actors[slot];
}

// ------------------------------------------------------------------ UI: wrestlers
const wIds = Object.keys(WDEFS).sort();
for (const sel of [$('wA'), $('wB')]) for (const id of wIds) {
  const o = document.createElement('option'); o.value = id; o.textContent = `${id.slice(-2)}  ${WDEFS[id].displayName}`; sel.appendChild(o);
}
$('wA').value = wIds.includes('wrestler-01') ? 'wrestler-01' : wIds[0];
$('wB').value = wIds.includes('wrestler-13') ? 'wrestler-13' : wIds[Math.min(1, wIds.length - 1)];

// ------------------------------------------------------------------ UI: library list
let mode = 'single';
let current = null;      // animation id or paired id
const cats = [...new Set(Object.values(ADEFS).map((d) => d.category))].sort();
function fillCats() {
  const c = $('cat'); c.innerHTML = '';
  const opts = mode === 'pair' ? ['all paired'] : ['all', ...cats];
  for (const k of opts) { const o = document.createElement('option'); o.value = k; o.textContent = k; c.appendChild(o); }
}
function entries() {
  if (mode === 'pair') return Object.values(PDEFS).map((p) => ({ id: p.id, name: p.name, category: p.category, duration: p.duration, isPair: true, tags: p.tags || [] }));
  return Object.values(ADEFS).map((d) => ({ id: d.id, name: d.name, category: d.category, duration: d.duration, isNew: d.libraryVersion >= 3, tags: d.tags || [], loop: d.loop }));
}
function renderList() {
  const q = $('search').value.trim().toLowerCase();
  const cat = $('cat').value;
  const list = $('list'); list.innerHTML = '';
  const items = entries().filter((e) => (cat === 'all' || cat === 'all paired' || e.category === cat) &&
    (!q || e.id.toLowerCase().includes(q) || e.name.toLowerCase().includes(q) || e.tags.some((t) => t.includes(q))))
    .sort((a, b) => a.id.localeCompare(b.id));
  for (const e of items) {
    const d = document.createElement('div');
    d.className = 'item'; d.setAttribute('role', 'option'); d.setAttribute('aria-selected', String(e.id === current)); d.id = 'item-' + e.id.replace(/\W/g, '-');
    d.innerHTML = `<span class="n"></span><span class="d"></span><span class="m"></span>`;
    d.querySelector('.n').textContent = e.name;
    d.querySelector('.d').textContent = `${e.duration.toFixed(2)}s${e.loop ? ' loop' : ''}`;
    d.querySelector('.m').textContent = e.id;
    if (e.isNew) { const c = document.createElement('span'); c.className = 'chip new'; c.textContent = 'v3'; d.querySelector('.d').append(' ', c); }
    if (e.isPair) { const c = document.createElement('span'); c.className = 'chip pair'; c.textContent = 'pair'; d.querySelector('.d').append(' ', c); }
    d.onclick = () => select(e.id);
    list.appendChild(d);
  }
  if (!items.length) list.textContent = 'No matches';
}
$('search').oninput = renderList;
$('cat').onchange = renderList;

// ------------------------------------------------------------------ playback
let playing = true, pair = null, startA = null;
const rootLines = new THREE.Group(); scene.add(rootLines);
function drawCurve(def, start, color) {
  if (def.rootMotion?.mode !== 'curve') return;
  const pts = [];
  for (let t = 0; t <= def.duration + 1e-6; t += 1 / 30) pts.push(RT.curveTarget(def.rootMotion.curve, start, t).position.clone().add(new THREE.Vector3(0, 0.01, 0)));
  const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color, depthTest: false }));
  line.renderOrder = 30; rootLines.add(line);
  const end = RT.curveTarget(def.rootMotion.curve, start, def.duration);
  const m = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.18, 10), new THREE.MeshBasicMaterial({ color, depthTest: false }));
  m.position.copy(end.position).add(new THREE.Vector3(0, 0.1, 0)); m.rotation.set(-Math.PI / 2, 0, 0); m.rotation.z = -end.yaw; m.renderOrder = 31;
  rootLines.add(m);
}
function clearCurves() { rootLines.clear(); }
$('showRoot').onchange = (e) => (rootLines.visible = e.target.checked);

function placeActor(a, start) {
  a.w.stop();
  a.w.rootMotion = null;
  a.w._zeroRoot?.();
  a.w._placeObject ? a.w._placeObject(start) : (a.w.object.position.copy(start.position), a.w.object.rotation.set(0, start.yaw, 0));
}

function select(id) {
  current = id;
  clearCurves();
  tickerEl.innerHTML = '';
  if (mode === 'single') {
    const def = ADEFS[id];
    const a = actors.A || makeActor('A', $('wA').value);
    if (actors.B) actors.B.w.object.visible = actors.B.hit.visible = actors.B.skel.visible = false;
    startA = startOf(def);
    placeActor(a, startA);
    a.w.setRootMotionPolicy($('visualPolicy').checked ? 'visual' : 'gameplay');
    a.w.play(id, { fade: 0 });
    if (a.w.rootMotion) a.w.rootMotion.start = { position: startA.position.clone(), yaw: startA.yaw };
    drawCurve(def, startA, '#ffc84a');
    buildTrack(def.duration, def.events || [], def.phases || []);
    inspect(def);
    framCam(startA, def);
  } else {
    const def = PDEFS[id];
    const a = actors.A || makeActor('A', $('wA').value);
    const b = actors.B || makeActor('B', $('wB').value);
    b.w.object.visible = true; b.hit.visible = $('showHit').checked; b.skel.visible = $('showSkel').checked;
    const anchor = startOf(def);
    pair = new RT.PairedPlayer(def, a.w, b.w, { anchor });
    pair.on('*', (e) => { if (!['start'].includes(e.name)) tick(`${e.role || ''} ${e.name}${e.time !== undefined ? ' @' + e.time.toFixed(2) : ''}`, e.role === 'attacker' ? 'a' : e.role === 'defender' ? 'd' : ''); });
    pair.start(0);
    drawCurve(ADEFS[def.attacker.animation], pair.starts.attacker, '#ff4d4d');
    drawCurve(ADEFS[def.defender.animation], pair.starts.defender, '#6aa8ff');
    buildTrack(def.duration, def.events || [], def.phases || []);
    inspectPair(def);
    framCam(anchor, def);
  }
  playing = true; $('play').textContent = 'Pause';
  for (const el of document.querySelectorAll('.item')) el.setAttribute('aria-selected', String(el.id === 'item-' + id.replace(/\W/g, '-')));
  $('curId').textContent = id;
}

function restart() { if (current) select(current); }
$('restart').onclick = restart;
$('play').onclick = () => { playing = !playing; $('play').textContent = playing ? 'Pause' : 'Play'; };
$('speed').oninput = () => ($('speedOut').textContent = Number($('speed').value).toFixed(2));
$('visualPolicy').onchange = restart;
for (const k of ['single', 'pair']) $('mode-' + k).onclick = () => {
  mode = k; for (const j of ['single', 'pair']) $('mode-' + j).setAttribute('aria-pressed', String(j === k));
  pair = null; current = null; fillCats(); renderList();
  const first = entries().sort((a, b) => a.id.localeCompare(b.id))[0]; if (first) select(first.id);
};
$('wA').onchange = () => { makeActor('A', $('wA').value); restart(); };
$('wB').onchange = () => { makeActor('B', $('wB').value); restart(); };
$('swap').onclick = () => { const a = $('wA').value; $('wA').value = $('wB').value; $('wB').value = a; makeActor('A', $('wA').value); makeActor('B', $('wB').value); restart(); };
$('showSkel').onchange = (e) => { for (const a of Object.values(actors)) a.skel.visible = e.target.checked && a.w.object.visible; };
$('showHit').onchange = (e) => { for (const a of Object.values(actors)) a.hit.visible = e.target.checked && a.w.object.visible; };
$('showMesh').onchange = (e) => { for (const a of Object.values(actors)) a.w.mesh.material.visible = e.target.checked; };

function duration() { return mode === 'pair' ? (pair ? pair.def.duration : 0) : (current ? ADEFS[current].duration : 0); }
function curTime() {
  if (mode === 'pair') return pair ? pair.time : 0;
  const w = actors.A?.w; if (!w || !w.current) return 0;
  return w.actions[w.current].time;
}
function seek(t) {
  playing = false; $('play').textContent = 'Play';
  if (mode === 'pair' && pair) pair.seek(t);
  else if (actors.A && current) actors.A.w.seekAnimation(current, t, { start: startA });
}

// ------------------------------------------------------------------ timeline
const track = $('track'), head = $('head');
const PHASE_COL = { approach: '#59607a', contact: '#ffc84a', launch: '#ff9a3c', traversal: '#6aa8ff', flight: '#9b7bff', landing: '#ff4d4d', recovery: '#4fd18b', hold: '#8b92a3' };
function buildTrack(dur, events, phases) {
  for (const el of [...track.querySelectorAll('.tick, .phase')]) el.remove();
  for (const p of phases) {
    const d = document.createElement('div'); d.className = 'phase';
    d.style.left = `${(p.start / dur) * 100}%`; d.style.width = `${((p.end - p.start) / dur) * 100}%`; d.style.background = PHASE_COL[p.name] || '#59607a';
    d.title = p.name; track.appendChild(d);
  }
  const shown = events.filter((e) => e.name !== 'animation_complete' && e.name !== 'footstep');
  shown.forEach((e, i) => {
    const d = document.createElement('div'); d.className = 'tick' + (e.role === 'attacker' ? ' a' : e.role === 'defender' ? ' d' : '');
    d.style.left = `calc(${(e.time / dur) * 100}% - 1px)`;
    const s = document.createElement('span'); s.textContent = e.name; s.style.top = `${4 + (i % 2) * 10}px`; d.appendChild(s);
    d.title = `${e.name} @ ${e.time}s${e.role ? ' (' + e.role + ')' : ''}`; track.appendChild(d);
  });
}
function trackTime(ev) { const r = track.getBoundingClientRect(); return Math.max(0, Math.min(1, (ev.clientX - r.left) / r.width)) * duration(); }
let dragging = false;
track.addEventListener('pointerdown', (e) => { dragging = true; track.setPointerCapture(e.pointerId); seek(trackTime(e)); });
track.addEventListener('pointermove', (e) => { if (dragging) seek(trackTime(e)); });
track.addEventListener('pointerup', () => (dragging = false));
track.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight') seek(curTime() + 1 / 30); if (e.key === 'ArrowLeft') seek(curTime() - 1 / 30); });

// ------------------------------------------------------------------ inspector + ticker
const tickerEl = $('ticker');
function tick(text, cls) {
  const d = document.createElement('div'); d.className = 'ev ' + cls; d.textContent = text;
  tickerEl.prepend(d); while (tickerEl.children.length > 8) tickerEl.lastChild.remove();
}
function kv(pairs) {
  const el = $('inspect'); el.innerHTML = '';
  for (const [k, v] of pairs) { const a = document.createElement('span'); a.textContent = k; const b = document.createElement('span'); b.textContent = v; el.append(a, b); }
}
function inspect(d) {
  const rm = d.rootMotion || { mode: 'none' };
  kv([
    ['id', d.id], ['name', d.name], ['category', d.category], ['duration', `${d.duration}s${d.loop ? ' (loop)' : ''}`],
    ['state', `${d.startState || 'standing'} -> ${d.endState || 'standing'}`],
    ['location', `${d.startLocation || 'ring'} -> ${d.endLocation || 'ring'}`],
    ['placement', d.placement ? `${d.placement.start} -> ${d.placement.end}` : 'anywhere'],
    ['root motion', rm.mode + (rm.endOffset ? `  end [${rm.endOffset.map((v) => v.toFixed(2)).join(', ')}]` : '') + (rm.endYaw ? `  yaw ${rm.endYaw}` : '') + (rm.heightChange ? `  height ${rm.heightChange}` : '')],
    ['events', (d.events || []).filter((e) => e.name !== 'footstep').map((e) => `${e.name}@${e.time}`).join(', ') || 'none'],
    ['interrupt', d.interrupt ? d.interrupt.windows.map((w) => `${w[0]}-${w[1]}s`).join(', ') : 'any time'],
    ['tags', (d.tags || []).join(', ')],
  ]);
}
function inspectPair(p) {
  kv([
    ['id', p.id], ['name', p.name], ['category', p.category], ['duration', p.duration + 's'],
    ['attacker', `${p.attacker.animation}  ${p.attacker.startState} -> ${p.attacker.endState}`],
    ['defender', `${p.defender.animation}  ${p.defender.startState} -> ${p.defender.endState}`],
    ['start', `defender at [${p.start.defenderOffset.join(', ')}], facing ${p.start.defenderFacing} deg`],
    ['events', p.events.map((e) => `${e.role[0]}:${e.name}@${e.time}`).join(', ')],
    ['interrupt', p.interruptible ? p.interruptible.windows.map((w) => `${w[0]}-${w[1]}s`).join(', ') : 'no'],
    ['sync', p.multiplayer ? p.multiplayer.sync : ''],
  ]);
}

// ------------------------------------------------------------------ validation
function runValidation() {
  const entriesM = manifest.animations;
  const rep = V.validateLibrary({ skeleton, entries: entriesM, animations: ADEFS, paired: PDEFS });
  const el = $('report'); el.innerHTML = '';
  const line = (cls, text) => { const d = document.createElement('div'); d.className = cls; d.textContent = text; el.appendChild(d); };
  line(rep.ok ? 'ok' : 'e', `${manifest.__file || 'bundled manifest'}: ${rep.stats.animations} animations, ${rep.stats.paired} paired, ${rep.stats.planned} planned`);
  line(rep.errors.length ? 'e' : 'ok', `${rep.errors.length} errors, ${rep.warnings.length} warnings`);
  for (const m of missing) line('e', 'missing: ' + m);
  for (const e of rep.errors.slice(0, 60)) line('e', `${e.id}: ${e.msg}`);
  for (const w of rep.warnings.slice(0, 80)) line('w', `${w.id}: ${w.msg}`);
  return rep;
}
$('runValidate').onclick = runValidation;

// ------------------------------------------------------------------ cameras
let camMode = 'follow';
function framCam(start, def) {
  const fwd = new THREE.Vector3(-Math.sin(start.yaw), 0, -Math.cos(start.yaw));
  const right = new THREE.Vector3(Math.cos(start.yaw), 0, -Math.sin(start.yaw));
  const c = start.position.clone().add(new THREE.Vector3(0, 0.9, 0));
  const end = def.rootMotion?.mode === 'curve' ? RT.curveTarget(def.rootMotion.curve, start, def.duration).position : start.position;
  c.lerp(end.clone().add(new THREE.Vector3(0, 0.9, 0)), 0.5);
  const dist = 4.2;
  const pos = { front: c.clone().addScaledVector(fwd, dist).add(new THREE.Vector3(0, 0.4, 0)),
                side: c.clone().addScaledVector(right, dist).add(new THREE.Vector3(0, 0.4, 0)),
                rear: c.clone().addScaledVector(fwd, -dist).add(new THREE.Vector3(0, 0.6, 0)),
                top: c.clone().add(new THREE.Vector3(0.01, 7, 0.01)),
                follow: c.clone().addScaledVector(right, dist * 0.8).addScaledVector(fwd, dist * 0.6).add(new THREE.Vector3(0, 1.0, 0)) };
  camera.position.copy(pos[camMode] || pos.follow);
  controls.target.copy(c);
}
for (const b of document.querySelectorAll('[data-cam]')) b.onclick = () => {
  camMode = b.dataset.cam; for (const x of document.querySelectorAll('[data-cam]')) x.setAttribute('aria-pressed', String(x === b));
  if (current) framCam(mode === 'pair' ? startOf(PDEFS[current]) : startA, mode === 'pair' ? PDEFS[current] : ADEFS[current]);
};

// ------------------------------------------------------------------ loop
function resize() {
  const r = view.getBoundingClientRect();
  renderer.setSize(r.width, r.height, false);
  camera.aspect = r.width / Math.max(1, r.height); camera.updateProjectionMatrix();
}
new ResizeObserver(resize).observe(view);
resize();

const _v = new THREE.Vector3();
function step(dt) {
  if (mode === 'pair' && pair) {
    pair.update(dt);
    if (!pair.playing && $('loop').checked) restart();
  } else if (actors.A && current) {
    const w = actors.A.w;
    w.update(dt);
    const def = ADEFS[current];
    const a = w.actions[w.current];
    if (!def.loop && a && a.time >= def.duration - 1e-4 && $('loop').checked) restart();
    if (def.loop && (def.rootMotion?.mode === 'inPlace' || def.rootMotion?.mode === 'speedCurve') && w.object.position.distanceTo(startA.position) > 3) restart();
  }
}
function updateHud() {
  const lines = [];
  for (const [slot, a] of Object.entries(actors)) {
    if (!a.w.object.visible) continue;
    a.w.object.updateMatrixWorld(true);
    const op = a.w.object.getWorldPosition(new THREE.Vector3());
    const hips = a.w.bones.hips.getWorldPosition(_v);
    const drift = Math.hypot(hips.x - op.x, hips.z - op.z);
    a.hit.position.copy(op).add(new THREE.Vector3(0, 0.93, 0));
    const lying = /lying|airborne/.test((ADEFS[a.w.current]?.endState) || '') || hips.y - op.y < 0.6;
    const bad = drift > (lying ? 0.6 : 0.35);
    a.hit.material.color.set(bad ? '#ff4d4d' : '#4fd18b');
    const def = ADEFS[a.w.current];
    lines.push(`${slot === 'A' ? (mode === 'pair' ? 'attacker' : 'wrestler') : 'defender'} <b>${a.w.def.displayName}</b>  ${a.w.current || ''}  state ${def?.startState || '-'} -> ${def?.endState || '-'}  position ${op.x.toFixed(2)}, ${op.y.toFixed(2)}, ${op.z.toFixed(2)}  hips-to-hitbox ${drift.toFixed(2)} m${bad ? ' <span class="warn">visual off hitbox</span>' : ''}`);
  }
  if (missing.length) lines.push(`<span class="warn">${missing.length} missing assets (see Validation)</span>`);
  $('hud').innerHTML = lines.map((l) => `<div>${l}</div>`).join('');
  const t = curTime(), d = duration();
  $('time').textContent = `${t.toFixed(2)} / ${d.toFixed(2)} s`;
  head.style.left = d ? `${(t / d) * 100}%` : '0';
}

// ropes give way: bend each rope like a plucked string around the contacts reported by the clips (purely visual)
const _inv = new THREE.Quaternion(), _o = new THREE.Vector3();
function bendRopes() {
  const contacts = [];
  const add = (def, start, t) => { if (def && start) contacts.push(...RT.ropeContacts(def, t, start)); };
  if (mode === 'pair' && pair) {
    add(ADEFS[pair.def.attacker.animation], pair.starts.attacker, pair.time);
    add(ADEFS[pair.def.defender.animation], pair.starts.defender, pair.time);
  } else if (current && actors.A) add(ADEFS[current], startA, curTime());
  for (const r of ROPES) {
    const mine = contacts.filter((c) => c.rope === r.level && Math.abs(c.direction.dot(r.b.clone().sub(r.a).normalize())) > 0.9 &&
      c.point.distanceTo(closestOnLine(r.a, r.b, c.point)) < 0.5);
    const pos = r.mesh.geometry.attributes.position;
    if (!mine.length) { if (r.bent) { pos.array.set(r.base); pos.needsUpdate = true; r.bent = false; } continue; }
    _inv.copy(r.mesh.quaternion).invert();
    for (let i = 0; i < pos.count; i++) {
      const y = r.base[i * 3 + 1];
      const off = RT.ropeOffsetAt(r.a, r.b, y + r.len / 2, mine).applyQuaternion(_inv);
      pos.array[i * 3] = r.base[i * 3] + off.x; pos.array[i * 3 + 1] = y + off.y; pos.array[i * 3 + 2] = r.base[i * 3 + 2] + off.z;
    }
    pos.needsUpdate = true; r.mesh.geometry.computeBoundingSphere(); r.bent = true;
  }
}
function closestOnLine(a, b, p) { const d = b.clone().sub(a).normalize(); return a.clone().addScaledVector(d, p.clone().sub(a).dot(d)); }

const clock = new THREE.Clock();
let frame = 0;
function loop() {
  const dt = Math.min(clock.getDelta(), 0.05) * Number($('speed').value);
  if (playing) step(dt);
  if (camMode === 'follow' && actors.A && playing) {
    const h = actors.A.w.bones.hips.getWorldPosition(_v);
    controls.target.lerp(h, 0.08);
  }
  for (const a of Object.values(actors)) a.skel.visible = $('showSkel').checked && a.w.object.visible;
  bendRopes();
  if (++frame % 3 === 0) updateHud();
  controls.update();
  renderer.render(scene, camera);
  if (!window.__paused) requestAnimationFrame(loop);
}

// start
fillCats();
renderList();
runValidation();
makeActor('A', $('wA').value);
const firstId = ADEFS['ropes.enter-between-ropes'] ? 'ropes.enter-between-ropes' : Object.keys(ADEFS).sort()[0];
select(firstId);
loop();

window.__lab = {
  select, seek, restart, runValidation, scene, camera, controls, renderer, actors, LIB, RT, DATA,
  setMode: (m) => $('mode-' + m).click(),
  setCam: (m) => document.querySelector(`[data-cam="${m}"]`).click(),
  render(pos, target) { if (pos) camera.position.set(...pos); if (target) controls.target.set(...target); controls.update(); bendRopes(); updateHud(); renderer.render(scene, camera); },
  step(dt, n = 1) { for (let i = 0; i < n; i++) step(dt); updateHud(); },
};
window.__ready = true;
