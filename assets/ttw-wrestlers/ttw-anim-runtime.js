// TTW animation runtime (library v3). Additive: loader.js and loader-ext.js are not modified.
//
//   import { loadPack } from './assets/ttw-wrestlers/loader.js';
//   import './assets/ttw-wrestlers/loader-ext.js';
//   import { RootMotion, PairedPlayer, loadPaired } from './assets/ttw-wrestlers/ttw-anim-runtime.js';
//
// 1. Root motion that never drifts from the gameplay position
//    Clips with rootMotion.mode = "curve" describe the wrestler's travel as a curve [t, x, y, z, yawDeg] in the
//    wrestler's START frame (x right, y up, -z forward). Two policies:
//      "gameplay" (default): the root bone is held at the origin, so the mesh always sits exactly on
//                 wrestler.object. The game moves the authoritative position along the curve:
//                 RootMotion.targetAt(wrestler, t) / wrestler.rootMotion.target give the world position and yaw
//                 for any time, computed from the start transform and the JSON curve (deterministic, so the
//                 server and every client get the same answer). With autoRootMotion = true the runtime moves
//                 wrestler.object itself (single player, viewers).
//      "visual":  the root bone plays the travel (object stays put) and the travel is committed to the object
//                 when the next clip starts. For previews and replays only.
//    Nothing is ever accumulated silently: travel only comes from declared curves.
//
// 2. Deterministic playback: wrestler.seekAnimation(id, t) poses a wrestler at an exact time (late joiners,
//    rollback, scrubbing).
//
// 3. Paired moves: PairedPlayer drives an attacker and a defender on ONE shared clock from a paired/*.json
//    definition. Both start transforms come from one anchor, both clips are set to the same time every frame,
//    events are merged with their role, and both end positions are known in advance.

import * as THREE from 'three';
import { Wrestler } from './loader.js';

const DEG = Math.PI / 180;
const _q = new THREE.Quaternion();
const UP = new THREE.Vector3(0, 1, 0);

// ------------------------------------------------------------------ curve sampling (same Catmull-Rom as the clips)

export function sampleCurve(keys, t) {
  if (keys.length === 1 || t <= keys[0][0]) return keys[0].slice(1);
  const last = keys[keys.length - 1];
  if (t >= last[0]) return last.slice(1);
  let i = 0;
  while (i < keys.length - 2 && t > keys[i + 1][0]) i++;
  const k1 = keys[i], k2 = keys[i + 1];
  const u = (t - k1[0]) / ((k2[0] - k1[0]) || 1);
  const k0 = i > 0 ? keys[i - 1] : k1;
  const k3 = i + 2 < keys.length ? keys[i + 2] : k2;
  const out = [];
  for (let c = 1; c < k1.length; c++) {
    const p0 = k0[c], p1 = k1[c], p2 = k2[c], p3 = k3[c], u2 = u * u, u3 = u2 * u;
    out.push(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u2 + (-p0 + 3 * p1 - 3 * p2 + p3) * u3));
  }
  return out;
}

function yawOf(object) {
  const f = new THREE.Vector3(0, 0, -1).applyQuaternion(object.getWorldQuaternion(new THREE.Quaternion()));
  return Math.atan2(-f.x, -f.z);
}

// World position and yaw (radians) at time t for a curve that started at start = { position, yaw }
export function curveTarget(curve, start, t, scale = 1) {
  const [x, y, z, yawDeg] = sampleCurve(curve, t);
  const off = new THREE.Vector3(x * scale, y * scale, z * scale).applyAxisAngle(UP, start.yaw);
  return { position: start.position.clone().add(off), yaw: start.yaw + yawDeg * DEG };
}

// ------------------------------------------------------------------ Wrestler patch

export const RootMotion = {
  policy: 'gameplay',
  targetAt(wrestler, t) {
    const rm = wrestler.rootMotion;
    if (!rm) return null;
    return curveTarget(rm.def.rootMotion.curve, rm.start, t, wrestler.object.scale.y);
  },
};

if (!Wrestler.prototype.__ttwRuntime) {
  Object.defineProperty(Wrestler.prototype, '__ttwRuntime', { value: 3 });
  const basePlay = Wrestler.prototype.play;
  const baseUpdate = Wrestler.prototype.update;

  Wrestler.prototype.setRootMotionPolicy = function (policy) { this.rootMotionPolicy = policy; return this; };

  Wrestler.prototype._endCurve = function () {
    const rm = this.rootMotion;
    if (!rm) return;
    const policy = this.rootMotionPolicy || RootMotion.policy;
    if (policy === 'visual' || this.autoRootMotion) {
      // land the object exactly where the curve says (gameplay owns it otherwise)
      const a = this.actions[rm.id];
      const t = Math.min(a ? a.time : rm.def.duration, rm.def.duration);
      const tg = curveTarget(rm.def.rootMotion.curve, rm.start, t, this.object.scale.y);
      this._placeObject(tg);
    }
    this.rootMotion = null;
    this._zeroRoot();
  };

  Wrestler.prototype._placeObject = function (tg) {
    const o = this.object;
    if (o.parent) {
      const p = tg.position.clone(); o.parent.worldToLocal(p); o.position.copy(p);
      const pq = o.parent.getWorldQuaternion(new THREE.Quaternion()).invert();
      o.quaternion.setFromAxisAngle(UP, tg.yaw).premultiply(pq);
    } else {
      o.position.copy(tg.position); o.quaternion.setFromAxisAngle(UP, tg.yaw);
    }
    o.updateMatrixWorld(true);
  };

  Wrestler.prototype._zeroRoot = function () {
    const root = this.bones.root;
    root.position.copy(this.restPositions.root);
    root.quaternion.identity();
  };

  Wrestler.prototype.play = function (name, opts = {}) {
    const id = this.library.resolve(name);
    if (this.rootMotion) this._endCurve();
    const def = this.library.defs[id];
    const result = basePlay.call(this, name, opts);
    if (def.rootMotion?.mode === 'curve') {
      this.object.updateMatrixWorld(true);
      this.rootMotion = {
        id, def,
        start: { position: this.object.getWorldPosition(new THREE.Vector3()), yaw: yawOf(this.object) },
        target: null,
      };
      this._applyRootPolicy();
    }
    return result;
  };

  Wrestler.prototype._applyRootPolicy = function () {
    const rm = this.rootMotion;
    if (!rm) return;
    const a = this.actions[rm.id];
    const t = a ? a.time : 0;
    rm.time = t;
    rm.target = curveTarget(rm.def.rootMotion.curve, rm.start, t, this.object.scale.y);
    const policy = this.rootMotionPolicy || RootMotion.policy;
    if (policy === 'gameplay') {
      this._zeroRoot();
      if (this.autoRootMotion) this._placeObject(rm.target);
    }
  };

  Wrestler.prototype.update = function (dt) {
    baseUpdate.call(this, dt);
    if (this.rootMotion) {
      if (this.current !== this.rootMotion.id) { this._endCurve(); return; }
      this._applyRootPolicy();
    }
  };

  // Pose the wrestler at an exact time of a clip (no blending). Optional start transform for curve clips.
  Wrestler.prototype.seekAnimation = function (name, time, { start = null } = {}) {
    const id = this.library.resolve(name);
    if (this.current !== id) this.play(id, { fade: 0 });
    for (const [k, a] of Object.entries(this.actions)) if (k !== id) a.stop();
    const a = this.actions[id];
    a.enabled = true; a.paused = false; a.stopFading(); a.setEffectiveWeight(1); a.setEffectiveTimeScale(1);
    a.time = Math.max(0, Math.min(time, a.getClip().duration));
    if (start && this.rootMotion) this.rootMotion.start = { position: start.position.clone(), yaw: start.yaw };
    this._lastTime?.set(a, a.time);
    this.mixer.update(0);
    this._applyRootPolicy();
    return a;
  };
}

// ------------------------------------------------------------------ paired moves

export async function loadPaired(baseUrl, entries) {
  const out = {};
  await Promise.all(entries.filter((e) => e.status !== 'planned').map(async (e) => {
    const res = await fetch(baseUrl + e.file);
    if (res.ok) out[e.id] = await res.json();
  }));
  return out;
}

// Start transforms for both roles from one anchor (the attacker's position and yaw by default).
export function pairedStartTransforms(def, anchor) {
  const yaw = anchor.yaw;
  const off = new THREE.Vector3().fromArray(def.start.defenderOffset).applyAxisAngle(UP, yaw);
  const aoff = new THREE.Vector3().fromArray(def.start.attackerOffset || [0, 0, 0]).applyAxisAngle(UP, yaw);
  return {
    attacker: { position: anchor.position.clone().add(aoff), yaw: yaw + (def.start.attackerFacing || 0) * DEG },
    defender: { position: anchor.position.clone().add(off), yaw: yaw + def.start.defenderFacing * DEG },
  };
}

export class PairedPlayer {
  // def: paired JSON. attacker/defender: Wrestler instances whose libraries contain both animations.
  constructor(def, attacker, defender, { anchor = null, autoRootMotion = true } = {}) {
    this.def = def;
    this.attacker = attacker;
    this.defender = defender;
    this.time = 0;
    this.playing = false;
    this.listeners = new Map();
    this.anchor = anchor || { position: attacker.object.getWorldPosition(new THREE.Vector3()), yaw: yawOf(attacker.object) };
    this.starts = pairedStartTransforms(def, this.anchor);
    this.autoRootMotion = autoRootMotion;
  }

  on(name, fn) {
    if (!this.listeners.has(name)) this.listeners.set(name, new Set());
    this.listeners.get(name).add(fn);
    return () => this.listeners.get(name).delete(fn);
  }
  _emit(name, data) {
    for (const k of [name, '*']) for (const fn of this.listeners.get(k) || []) fn({ name, pair: this, ...data });
  }

  // Put both wrestlers on their start marks and pose them at t = 0. startTime lets late joiners catch up.
  start(startTime = 0) {
    for (const role of ['attacker', 'defender']) {
      const w = this[role];
      w.autoRootMotion = this.autoRootMotion;
      w._placeObject(this.starts[role]);
      w.play(this.def[role].animation, { fade: 0 });
      if (w.rootMotion) w.rootMotion.start = { position: this.starts[role].position.clone(), yaw: this.starts[role].yaw };
    }
    this.time = 0;
    this.playing = true;
    this._emit('start', { time: 0 });
    this.seek(startTime, true);
    return this;
  }

  // Both clips are set to the same time: they can never drift apart.
  seek(t, fire = false) {
    const prev = this.time;
    this.time = Math.max(0, Math.min(t, this.def.duration));
    for (const role of ['attacker', 'defender']) {
      const w = this[role];
      w.seekAnimation(this.def[role].animation, this.time, { start: this.starts[role] });
    }
    if (fire) for (const e of this.def.events) if (e.time > prev - 1e-9 && e.time <= this.time && !(prev === 0 && e.time === 0 && this._fired0)) this._emit(e.name, { role: e.role, time: e.time, event: e });
    this._fired0 = true;
  }

  update(dt) {
    if (!this.playing) return;
    const prev = this.time;
    const next = Math.min(this.def.duration, this.time + dt);
    this.seek(next);
    for (const e of this.def.events) if (e.time > prev && e.time <= next) this._emit(e.name, { role: e.role, time: e.time, event: e });
    if (next >= this.def.duration) { this.playing = false; this._emit('complete', { time: next }); }
  }

  // Where each wrestler ends up (world), known before the move plays: use for server-side validation.
  endTransforms() {
    const out = {};
    for (const role of ['attacker', 'defender']) {
      const def = this[role].library.defs[this.def[role].animation];
      out[role] = def.rootMotion?.mode === 'curve'
        ? curveTarget(def.rootMotion.curve, this.starts[role], def.duration)
        : { position: this.starts[role].position.clone(), yaw: this.starts[role].yaw };
    }
    return out;
  }
}

// ------------------------------------------------------------------ ropes giving way
// Library clips that cross or lean on the ropes carry ropeInteraction: per rope, keys [t, s, dx, dy, dz] in the clip's
// placement frame (s = contact point along the rope from the frame origin, d = how far the rope is pushed there).
// ropeContacts() turns that into world space for a wrestler that started the clip at `start` ({ position, yaw }).
// Bend the rope like a plucked string: zero at both posts, the full offset at the contact point. Purely visual.

function sampleRopeKeys(keys, t) {
  if (!keys.length || t < keys[0][0] - 1 / 60 || t > keys[keys.length - 1][0] + 1 / 60) return null;
  let i = 0;
  while (i < keys.length - 1 && keys[i + 1][0] < t) i++;
  const a = keys[i], b = keys[Math.min(i + 1, keys.length - 1)];
  if (t <= a[0]) return a.slice(1);
  if (b[0] - a[0] > 0.07) return t - a[0] < 1 / 60 ? a.slice(1) : null; // gap: no contact in between
  const u = (t - a[0]) / ((b[0] - a[0]) || 1);
  return a.slice(1).map((v, k) => v + (b[k + 1] - v) * u);
}

export function ropeContacts(def, t, start) {
  const ri = def.ropeInteraction;
  if (!ri || !def.placement?.frameStart) return [];
  const fs = def.placement.frameStart;
  const yawF = start.yaw - fs[3] * DEG;                       // frame -> world rotation
  const origin = start.position.clone().sub(new THREE.Vector3(fs[0], fs[1], fs[2]).applyAxisAngle(UP, yawF));
  const out = [];
  for (const r of ri.ropes) {
    const k = sampleRopeKeys(r.keys, t);
    if (!k) continue;
    const along = new THREE.Vector3(r.axis === 'x' ? 1 : 0, 0, r.axis === 'z' ? 1 : 0).applyAxisAngle(UP, yawF);
    out.push({
      rope: r.rope,
      direction: along,
      point: origin.clone().addScaledVector(along, k[0]),
      offset: new THREE.Vector3(k[1], k[2], k[3]).applyAxisAngle(UP, yawF),
    });
  }
  return out;
}

// Offset of a point on a straight rope (from `a` to `b`) when pushed by contacts (plucked-string shape).
export function ropeOffsetAt(a, b, u, contacts) {
  const L = a.distanceTo(b);
  const best = new THREE.Vector3();
  for (const c of contacts) {
    const uc = Math.max(0.05, Math.min(L - 0.05, c.point.clone().sub(a).dot(b.clone().sub(a).normalize())));
    const w = u <= uc ? u / uc : (L - u) / (L - uc);
    const v = c.offset.clone().multiplyScalar(Math.max(0, w));
    if (v.lengthSq() > best.lengthSq()) best.copy(v);
  }
  return best;
}
