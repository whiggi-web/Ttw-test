// TTW animation library validator. Pure JavaScript (no Three.js), runs in Node and in the browser.
//
//   import { validateLibrary } from './validate.js';
//   const report = validateLibrary({ skeleton, entries, animations, paired });
//   report.errors / report.warnings / report.stats
//
// entries:    manifest entries [{ id, file, category, status }]
// animations: { id: animationJson } for every entry that loaded (missing ones are reported)
// paired:     { id: pairedJson }

export const REQUIRED_BONES = [
  'root', 'hips', 'spine', 'chest', 'neck', 'head',
  'leftUpperArm', 'leftForearm', 'leftHand', 'rightUpperArm', 'rightForearm', 'rightHand',
  'leftUpperLeg', 'leftLowerLeg', 'leftFoot', 'rightUpperLeg', 'rightLowerLeg', 'rightFoot',
];

export const EVENT_VOCABULARY = [
  // library standard
  'attack_start', 'hit', 'grab', 'grip_locked', 'lift_start', 'lift_complete', 'release', 'impact', 'land',
  'rope_contact', 'rope_release', 'rebound', 'footstep', 'jump', 'apex', 'stun_start', 'recover', 'animation_complete',
  // earlier batches and props (still valid)
  'hit_received', 'weapon_impact', 'table_break', 'swing',
];

export const ROOT_MOTION_MODES = ['none', 'inPlace', 'speedCurve', 'baked', 'curve'];

const finite = (v) => typeof v === 'number' && Number.isFinite(v);

export function validateSkeleton(skeleton) {
  const errors = [], warnings = [];
  if (!skeleton || !Array.isArray(skeleton.bones)) return { errors: ['skeleton.json has no bones array'], warnings };
  const names = new Set();
  const world = {};
  for (const b of skeleton.bones) {
    if (names.has(b.name)) errors.push(`duplicate bone "${b.name}"`);
    if (b.parent && !names.has(b.parent)) errors.push(`bone "${b.name}" listed before its parent "${b.parent}"`);
    names.add(b.name);
    if (!Array.isArray(b.position) || b.position.length !== 3 || !b.position.every(finite)) errors.push(`bone "${b.name}" has an invalid position`);
    const p = b.parent ? world[b.parent] : [0, 0, 0];
    world[b.name] = [p[0] + b.position[0], p[1] + b.position[1], p[2] + b.position[2]];
  }
  for (const n of REQUIRED_BONES) if (!names.has(n)) errors.push(`missing required bone "${n}"`);
  for (const n of names) if (!REQUIRED_BONES.includes(n)) warnings.push(`extra bone "${n}" (not part of the TTW skeleton)`);
  const root = skeleton.bones.find((b) => !b.parent);
  if (!root || root.name !== 'root') errors.push('the top bone must be "root"');
  for (const a of skeleton.attachments || []) if (!names.has(a.bone)) errors.push(`attachment "${a.name}" uses unknown bone "${a.bone}"`);
  for (const f of ['leftFoot', 'rightFoot']) {
    if (world[f] && (world[f][1] < 0.04 || world[f][1] > 0.16)) warnings.push(`${f} joint is at y=${world[f][1].toFixed(3)}; feet should rest on y=0`);
  }
  if (skeleton.forward && skeleton.forward !== '-z') errors.push('forward axis must be -z');
  return { errors, warnings, world };
}

function checkKeys(keys, width, duration, where, out) {
  if (!Array.isArray(keys) || !keys.length) { out.errors.push(`${where}: no keys`); return; }
  let prev = -Infinity;
  for (const k of keys) {
    if (!Array.isArray(k) || k.length !== width || !k.every(finite)) { out.errors.push(`${where}: key ${JSON.stringify(k)} is not ${width} numbers`); return; }
    if (k[0] < prev - 1e-9) { out.errors.push(`${where}: key times are not in order`); return; }
    if (k[0] < -1e-6 || k[0] > duration + 1e-3) out.errors.push(`${where}: key at ${k[0]}s is outside 0..${duration}s`);
    prev = k[0];
  }
  if (Math.abs(keys[0][0]) > 1e-6) out.warnings.push(`${where}: first key is at ${keys[0][0]}s, not 0`);
  if (Math.abs(keys[keys.length - 1][0] - duration) > 1e-3) out.warnings.push(`${where}: last key is at ${keys[keys.length - 1][0]}s, clip is ${duration}s`);
}

export function validateAnimation(def, skeleton, entry = null) {
  const out = { errors: [], warnings: [] };
  const id = def && def.id;
  if (!def || typeof def !== 'object') { out.errors.push('not a JSON object'); return out; }
  for (const f of ['id', 'name', 'category', 'duration', 'loop', 'tracks']) if (def[f] === undefined) out.errors.push(`missing "${f}"`);
  if (!finite(def.duration) || def.duration <= 0) out.errors.push('duration must be a positive number');
  if (entry && entry.id !== def.id) out.errors.push(`manifest id "${entry.id}" does not match file id "${def.id}"`);
  if (id && def.category && !id.startsWith(def.category + '.')) out.warnings.push(`id "${id}" does not start with its category "${def.category}."`);
  if (def.skeleton && skeleton.id && def.skeleton !== skeleton.id) out.errors.push(`made for skeleton "${def.skeleton}", library skeleton is "${skeleton.id}"`);
  const bones = new Set(skeleton.bones.map((b) => b.name));
  const tracks = def.tracks || {};
  let keyCount = 0;
  for (const [bone, tr] of Object.entries(tracks)) {
    if (!bones.has(bone)) { out.errors.push(`track for unknown bone "${bone}"`); continue; }
    for (const ch of Object.keys(tr)) if (!['rotation', 'position'].includes(ch)) out.errors.push(`${bone}: unknown channel "${ch}"`);
    if (tr.rotation) { checkKeys(tr.rotation, 4, def.duration, `${bone}.rotation`, out); keyCount += tr.rotation.length; }
    if (tr.position) { checkKeys(tr.position, 4, def.duration, `${bone}.position`, out); keyCount += tr.position.length; }
  }
  if (!Object.keys(tracks).length) out.errors.push('no tracks: empty placeholder');
  else if (keyCount < 4) out.warnings.push('very few keys');
  // events
  for (const e of def.events || []) {
    if (!finite(e.time) || e.time < -1e-6 || e.time > def.duration + 1e-6) out.errors.push(`event "${e.name}" at ${e.time}s is outside the clip`);
    if (!EVENT_VOCABULARY.includes(e.name)) out.warnings.push(`event "${e.name}" is not in the standard vocabulary`);
  }
  // root motion: anything that moves the root bone must be declared
  const rm = def.rootMotion || { mode: 'none' };
  if (!ROOT_MOTION_MODES.includes(rm.mode)) out.errors.push(`unknown rootMotion.mode "${rm.mode}"`);
  if (tracks.root && rm.mode !== 'curve') out.errors.push('animates the root bone but rootMotion.mode is not "curve" (undeclared world movement)');
  if (rm.mode === 'curve') {
    if (!Array.isArray(rm.curve)) out.errors.push('rootMotion.curve missing');
    else {
      checkKeys(rm.curve, 5, def.duration, 'rootMotion.curve', out);
      const last = rm.curve[rm.curve.length - 1];
      if (rm.endOffset && last && Math.hypot(last[1] - rm.endOffset[0], last[2] - rm.endOffset[1], last[3] - rm.endOffset[2]) > 1e-3) out.errors.push('rootMotion.endOffset does not match the end of the curve');
      if (rm.endYaw !== undefined && last && Math.abs(last[4] - rm.endYaw) > 1e-3) out.errors.push('rootMotion.endYaw does not match the end of the curve');
    }
  }
  if (rm.mode === 'baked' && !rm.endOffset) out.warnings.push('baked root motion without endOffset');
  if (['none', 'inPlace'].includes(rm.mode) && tracks.hips && tracks.hips.position) {
    const last = tracks.hips.position[tracks.hips.position.length - 1];
    if (Math.hypot(last[1], last[3]) > 0.25) out.warnings.push(`hips end ${Math.hypot(last[1], last[3]).toFixed(2)} m from the origin with rootMotion "${rm.mode}"`);
  }
  // loops should close
  if (def.loop) {
    for (const [bone, tr] of Object.entries(tracks)) for (const ch of ['rotation', 'position']) {
      const k = tr[ch]; if (!k || k.length < 2) continue;
      const a = k[0], b = k[k.length - 1];
      if (Math.abs(a[1] - b[1]) + Math.abs(a[2] - b[2]) + Math.abs(a[3] - b[3]) > 0.5) out.warnings.push(`loop does not close on ${bone}.${ch}`);
    }
  }
  // joint sanity (degrees)
  const range = { Forearm: [0, [-20, 165]], LowerLeg: [0, [-160, 12]] };
  for (const [bone, tr] of Object.entries(tracks)) {
    for (const [suffix, [axis, [lo, hi]]] of Object.entries(range)) {
      if (!bone.endsWith(suffix) || !tr.rotation) continue;
      for (const k of tr.rotation) if (k[1 + axis] < lo || k[1 + axis] > hi) { out.warnings.push(`${bone} bends to ${k[1 + axis].toFixed(0)} deg at ${k[0]}s (outside ${lo}..${hi})`); break; }
    }
  }
  return out;
}

export function validatePaired(pair, animations) {
  const out = { errors: [], warnings: [] };
  for (const f of ['id', 'name', 'category', 'duration', 'attacker', 'defender', 'start', 'events', 'end']) if (pair[f] === undefined) out.errors.push(`missing "${f}"`);
  for (const role of ['attacker', 'defender']) {
    const r = pair[role];
    if (!r) continue;
    const a = animations[r.animation];
    if (!a) { out.errors.push(`${role} animation "${r.animation}" not found`); continue; }
    if (Math.abs(a.duration - pair.duration) > 1e-3) out.errors.push(`${role} animation lasts ${a.duration}s, pair lasts ${pair.duration}s`);
    if (!r.startState || !r.endState) out.warnings.push(`${role} has no start/end state`);
  }
  for (const e of pair.events || []) {
    if (e.time < 0 || e.time > pair.duration + 1e-6) out.errors.push(`event "${e.name}" outside the pair duration`);
    if (!['attacker', 'defender', 'both'].includes(e.role)) out.errors.push(`event "${e.name}" has role "${e.role}"`);
  }
  if (pair.start && !Array.isArray(pair.start.defenderOffset)) out.errors.push('start.defenderOffset missing');
  if (!pair.multiplayer) out.warnings.push('no multiplayer block');
  return out;
}

function trackSignature(def) {
  // rounded, order-independent fingerprint of the motion, to catch renamed copies
  const parts = [];
  for (const bone of Object.keys(def.tracks || {}).sort()) {
    for (const ch of ['rotation', 'position']) {
      const k = def.tracks[bone][ch]; if (!k) continue;
      parts.push(bone + ch + k.map((x) => x.map((v) => Math.round(v * 10) / 10).join(',')).join(';'));
    }
  }
  return parts.join('|');
}

export function validateLibrary({ skeleton, entries = [], animations = {}, paired = {} }) {
  const report = { errors: [], warnings: [], stats: { animations: 0, planned: 0, missing: 0, paired: 0, byCategory: {}, events: {} } };
  const sk = validateSkeleton(skeleton);
  sk.errors.forEach((m) => report.errors.push({ id: 'skeleton', msg: m }));
  sk.warnings.forEach((m) => report.warnings.push({ id: 'skeleton', msg: m }));
  const seen = new Set();
  const sigs = new Map();
  for (const e of entries) {
    if (e.status && e.status !== 'ready') { if (e.status === 'planned') report.stats.planned++; else report.stats.superseded = (report.stats.superseded || 0) + 1; continue; }
    if (seen.has(e.id)) report.errors.push({ id: e.id, msg: 'duplicate id in manifest' });
    seen.add(e.id);
    const def = animations[e.id];
    if (!def) { report.stats.missing++; report.errors.push({ id: e.id, msg: `file missing or unreadable: ${e.file}` }); continue; }
    const r = validateAnimation(def, skeleton, e);
    r.errors.forEach((m) => report.errors.push({ id: e.id, msg: m }));
    r.warnings.forEach((m) => report.warnings.push({ id: e.id, msg: m }));
    report.stats.animations++;
    report.stats.byCategory[def.category] = (report.stats.byCategory[def.category] || 0) + 1;
    for (const ev of def.events || []) report.stats.events[ev.name] = (report.stats.events[ev.name] || 0) + 1;
    const sig = trackSignature(def);
    if (sigs.has(sig)) report.warnings.push({ id: e.id, msg: `same motion as ${sigs.get(sig)}` });
    else sigs.set(sig, e.id);
  }
  for (const [id, p] of Object.entries(paired)) {
    const r = validatePaired(p, animations);
    r.errors.forEach((m) => report.errors.push({ id, msg: m }));
    r.warnings.forEach((m) => report.warnings.push({ id, msg: m }));
    report.stats.paired++;
  }
  report.ok = report.errors.length === 0;
  return report;
}
