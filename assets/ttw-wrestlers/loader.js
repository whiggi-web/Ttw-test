// TTW universal wrestler loader, Three.js r160
//
// One skeleton, one shared animation library, any number of wrestlers.
// Each wrestler is ONE SkinnedMesh (one geometry, one vertex-coloured material, one draw call).
//
//   import { loadPack } from './assets/ttw-wrestlers/loader.js';
//   const pack = await loadPack('./assets/ttw-wrestlers/manifest.json');
//   const rex  = pack.createWrestler('wrestler-01');
//   scene.add(rex.object);
//   rex.on('hit', (e) => engine.resolveStrike(rex, e));   // events never touch gameplay themselves
//   rex.play('striking.punch');
//   // every frame:
//   rex.update(delta);
//
// Animation ids are "<category>.<name>" (movement.walk). The short name ("walk") also works when it is unique.

import * as THREE from 'three';

const DEG = Math.PI / 180;

// ------------------------------------------------------------------ loading

export async function loadPack(manifestUrl, { wrestlers = null, animations = null } = {}) {
  const base = manifestUrl.slice(0, manifestUrl.lastIndexOf('/') + 1);
  const getJSON = async (file) => {
    const res = await fetch(base + file);
    if (!res.ok) throw new Error(`TTW: could not load ${base + file} (${res.status})`);
    return res.json();
  };
  const manifest = await (await fetch(manifestUrl)).json();
  const skeletonDef = await getJSON(manifest.skeleton);

  const wantW = manifest.wrestlers.filter((w) => w.status !== 'planned' && (!wrestlers || wrestlers.includes(w.id)));
  const wantA = manifest.animations.filter((a) => a.status !== 'planned' && (!animations || animations.includes(a.id)));
  const wrestlerDefs = {};
  const animationDefs = {};
  await Promise.all([
    ...wantW.map(async (w) => { wrestlerDefs[w.id] = await getJSON(w.file); }),
    ...wantA.map(async (a) => { animationDefs[a.id] = await getJSON(a.file); }),
  ]);
  return new WrestlerPack({ manifest, skeletonDef, wrestlerDefs, animationDefs });
}

// For bundled builds: pass the JSON objects directly.
export function createPack({ manifest = null, skeleton, wrestlers, animations }) {
  return new WrestlerPack({ manifest, skeletonDef: skeleton, wrestlerDefs: wrestlers, animationDefs: animations });
}

export class WrestlerPack {
  constructor({ manifest, skeletonDef, wrestlerDefs, animationDefs }) {
    this.manifest = manifest;
    this.skeletonDef = skeletonDef;
    this.wrestlerDefs = wrestlerDefs;
    this.animations = new AnimationLibrary(skeletonDef);
    for (const def of Object.values(animationDefs)) this.animations.add(def);
    this._geometryCache = new Map();
  }

  get wrestlerIds() { return Object.keys(this.wrestlerDefs); }

  // Geometry is built once per wrestler type and shared by every instance of that wrestler.
  createWrestler(id, options = {}) {
    const def = this.wrestlerDefs[id];
    if (!def) throw new Error(`TTW: unknown wrestler "${id}"`);
    if (def.skeletonId && def.skeletonId !== this.skeletonDef.id) {
      throw new Error(`TTW: ${id} expects skeleton ${def.skeletonId}, pack has ${this.skeletonDef.id}`);
    }
    const rig = buildSkeleton(this.skeletonDef);
    let geometry = this._geometryCache.get(id);
    if (!geometry) {
      geometry = buildGeometry(def, rig);
      this._geometryCache.set(id, geometry);
    }
    const m = def.material || {};
    const material = options.material || new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: m.roughness ?? 0.6,
      metalness: m.metalness ?? 0,
    });
    const mesh = new THREE.SkinnedMesh(geometry, material);
    mesh.name = 'body';
    mesh.castShadow = options.castShadow ?? true;
    mesh.receiveShadow = true;
    mesh.add(rig.root);
    mesh.updateMatrixWorld(true);
    mesh.bind(rig.skeleton);
    mesh.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, 0.9, 0), 2.4); // falls and lifts never get culled
    mesh.frustumCulled = options.frustumCulled ?? true;

    const object = new THREE.Group();
    object.name = id;
    object.userData.wrestlerId = id;
    object.add(mesh);
    return new Wrestler({ def, skeletonDef: this.skeletonDef, rig, mesh, object, library: this.animations, options });
  }
}

// ------------------------------------------------------------------ animation library (shared)

export class AnimationLibrary {
  constructor(skeletonDef) {
    this.skeletonDef = skeletonDef;
    this.defs = {};     // id -> JSON
    this.clips = {};    // id -> THREE.AnimationClip (shared by every wrestler)
    this.aliases = {};  // short name -> id (only when unique)
  }

  add(def) {
    if (def.skeleton && def.skeleton !== this.skeletonDef.id) {
      throw new Error(`TTW: animation ${def.id} targets skeleton ${def.skeleton}, not ${this.skeletonDef.id}`);
    }
    this.defs[def.id] = def;
    this.clips[def.id] = createClip(def, this.skeletonDef);
    const short = def.id.split('.').pop();
    this.aliases[short] = short in this.aliases && this.aliases[short] !== def.id ? null : def.id;
    return this.clips[def.id];
  }

  resolve(name) {
    if (this.defs[name]) return name;
    const id = this.aliases[name];
    if (!id) throw new Error(`TTW: unknown or ambiguous animation "${name}"`);
    return id;
  }

  // Build a left/right mirrored copy of an animation (e.g. hook-left from hook-right).
  addMirrored(sourceId, newId, newName) {
    const src = this.defs[this.resolve(sourceId)];
    const def = mirrorAnimationDef(src, newId, newName);
    this.add(def);
    return def;
  }

  byCategory() {
    const out = {};
    for (const d of Object.values(this.defs)) (out[d.category] ||= []).push(d.id);
    return out;
  }
}

export function mirrorAnimationDef(src, newId, newName) {
  const swap = (n) => n.startsWith('left') ? 'right' + n.slice(4) : n.startsWith('right') ? 'left' + n.slice(5) : n;
  const tracks = {};
  for (const [bone, tr] of Object.entries(src.tracks)) {
    const t = {};
    if (tr.rotation) t.rotation = tr.rotation.map(([time, x, y, z]) => [time, x, -y, -z]);
    if (tr.position) t.position = tr.position.map(([time, x, y, z]) => [time, -x, y, z]);
    tracks[swap(bone)] = t;
  }
  const swapAny = (s) => s.replace(/left|right|Left|Right/, (m) => ({ left: 'right', right: 'left', Left: 'Right', Right: 'Left' })[m]);
  const events = (src.events || []).map((e) => {
    const c = { ...e };
    if (c.attachment) c.attachment = swapAny(c.attachment);
    if (c.bone) c.bone = swapAny(c.bone);
    return c;
  });
  return { ...src, id: newId, name: newName || newId, tracks, events, mirroredFrom: src.id };
}

// ------------------------------------------------------------------ wrestler runtime

export class Wrestler {
  constructor({ def, skeletonDef, rig, mesh, object, library, options = {} }) {
    this.id = def.id;
    this.def = def;
    this.skeletonDef = skeletonDef;
    this.library = library;
    this.object = object;
    this.mesh = mesh;
    this.skeleton = rig.skeleton;
    this.bones = rig.bones;
    this.attachments = rig.attachments;
    this.restPositions = rig.restPositions;
    this.mixer = new THREE.AnimationMixer(object);
    this.actions = {};
    this.current = null;
    this.paused = false;
    this.autoRootMotion = options.autoRootMotion ?? false; // let the game move the wrestler unless asked
    this._listeners = new Map();
    this._lastTime = new Map();
    this._tmpV = new THREE.Vector3();
    this._finished = [];

    // 'finished' is queued so it is emitted after the clip's own timed events for that frame
    this.mixer.addEventListener('finished', (e) => this._finished.push(e.action.getClip().name));
  }

  // ---- events: hit, grab, release, rope_contact, rebound, jump, land, recover, weapon_impact, table_break ...
  on(name, fn) {
    if (!this._listeners.has(name)) this._listeners.set(name, new Set());
    this._listeners.get(name).add(fn);
    return () => this._listeners.get(name).delete(fn);
  }
  _emit(name, data) {
    const payload = { wrestler: this, name, ...data };
    for (const key of [name, '*']) {
      const set = this._listeners.get(key);
      if (set) for (const fn of set) fn(payload);
    }
  }

  action(id) {
    id = this.library.resolve(id);
    if (!this.actions[id]) {
      const def = this.library.defs[id];
      const a = this.mixer.clipAction(this.library.clips[id]);
      a.setLoop(def.loop ? THREE.LoopRepeat : THREE.LoopOnce, Infinity);
      a.clampWhenFinished = def.clampWhenFinished ?? !def.loop;
      this.actions[id] = a;
    }
    return this.actions[id];
  }

  play(name, { fade = 0.2, timeScale = 1, restart = true, startTime = 0 } = {}) {
    const id = this.library.resolve(name);
    const next = this.action(id);
    const prevId = this.current;
    const prev = prevId && this.actions[prevId];
    if (prev === next && !restart) return next;

    // Baked root motion: move the object by the distance the hips travelled, then start the next clip clean.
    if (prevId && this.library.defs[prevId].rootMotion?.mode === 'baked') {
      if (this.commitRootMotion()) fade = 0;
    }

    next.reset();
    next.time = startTime;
    next.enabled = true;
    next.setEffectiveTimeScale(timeScale);
    next.setEffectiveWeight(1);
    next.play();
    if (prev && prev !== next && fade > 0) prev.crossFadeTo(next, fade, false);
    else if (prev && prev !== next) prev.stop();
    this._lastTime.set(next, startTime - 1e-6);
    this.current = id;
    this.paused = false;
    if (fade === 0) this.mixer.update(0);
    return next;
  }

  // Move the wrestler's object by the hips' current XZ offset from rest, in the object's own frame.
  // Returns true when it moved. Called automatically when leaving a clip with rootMotion.mode "baked".
  commitRootMotion() {
    const hips = this.bones.hips;
    const rest = this.restPositions.hips;
    const off = this._tmpV.set(hips.position.x - rest.x, 0, hips.position.z - rest.z);
    if (off.lengthSq() < 1e-6) return false;
    off.applyQuaternion(this.object.quaternion).multiply(this.object.scale);
    this.object.position.add(off);
    this.object.updateMatrixWorld();
    return true;
  }

  stop() {
    this.mixer.stopAllAction();
    this.current = null;
  }

  setPaused(paused) { this.paused = paused; }

  // Forward speed (m/s along the wrestler's facing) that the current clip expects the game to apply.
  getRootSpeed() {
    if (!this.current) return 0;
    const def = this.library.defs[this.current];
    const rm = def.rootMotion || {};
    const a = this.actions[this.current];
    if (rm.mode === 'inPlace') return (rm.speed || 0) * a.getEffectiveTimeScale();
    if (rm.mode === 'speedCurve') {
      const k = rm.speedCurve;
      const t = a.time;
      if (t <= k[0][0]) return k[0][1];
      for (let i = 0; i < k.length - 1; i++) {
        if (t <= k[i + 1][0]) {
          const u = (t - k[i][0]) / (k[i + 1][0] - k[i][0]);
          return (k[i][1] + (k[i + 1][1] - k[i][1]) * u) * a.getEffectiveTimeScale();
        }
      }
      return k[k.length - 1][1];
    }
    return 0;
  }

  update(dt) {
    if (this.paused) return;
    this.mixer.update(dt);
    if (this.autoRootMotion) {
      const speed = this.getRootSpeed();
      if (speed) this.object.translateZ(-speed * dt);
    }
    this._fireEvents();
    while (this._finished.length) this._emit('finished', { animation: this._finished.shift() });
  }

  _fireEvents() {
    for (const [id, action] of Object.entries(this.actions)) {
      if (!action.isRunning() && !(action === this.actions[this.current])) continue;
      if (action.getEffectiveWeight() < 0.5) { this._lastTime.set(action, action.time); continue; }
      const def = this.library.defs[id];
      const evs = def.events;
      const prev = this._lastTime.get(action) ?? action.time;
      const now = action.time;
      if (evs && evs.length && now !== prev) {
        const wrapped = now < prev; // looped
        for (const e of evs) {
          const fire = wrapped ? (e.time > prev || e.time <= now) : (e.time > prev && e.time <= now);
          if (fire) this._emit(e.name, { animation: id, time: e.time, event: e });
        }
      }
      this._lastTime.set(action, now);
    }
  }

  resetPose() {
    this.stop();
    for (const [name, bone] of Object.entries(this.bones)) {
      bone.position.copy(this.restPositions[name]);
      bone.quaternion.identity();
      bone.scale.set(1, 1, 1);
    }
  }

  setJointRotation(boneName, x = 0, y = 0, z = 0) {
    const b = this.bones[boneName];
    if (b) b.quaternion.setFromEuler(new THREE.Euler(x * DEG, y * DEG, z * DEG, 'XYZ'));
  }

  getJointRotation(boneName) {
    const e = new THREE.Euler().setFromQuaternion(this.bones[boneName].quaternion, 'XYZ');
    return [e.x / DEG, e.y / DEG, e.z / DEG];
  }

  getAttachmentWorld(name, target = new THREE.Matrix4()) {
    const a = this.attachments[name];
    if (!a) return null;
    a.updateWorldMatrix(true, false);
    return target.copy(a.matrixWorld);
  }

  // Parent a prop (chair, title belt) to a hand or any attachment point.
  attach(object3d, attachmentName = 'propRightHand') {
    const a = this.attachments[attachmentName];
    if (!a) throw new Error(`TTW: no attachment "${attachmentName}"`);
    a.add(object3d);
    return object3d;
  }

  dispose() {
    this.stop();
    this.mesh.material.dispose(); // geometry is shared per wrestler type; the pack owns it
    this.skeleton.dispose();
  }
}

// ------------------------------------------------------------------ skeleton

function buildSkeleton(skelDef) {
  const bones = {};
  const restPositions = {};
  const worldRest = {};
  const tails = {};
  const list = [];
  let root = null;

  for (const b of skelDef.bones) {
    const bone = new THREE.Bone();
    bone.name = b.name;
    bone.position.fromArray(b.position);
    restPositions[b.name] = bone.position.clone();
    bones[b.name] = bone;
    list.push(bone);
    if (b.parent) {
      if (!bones[b.parent]) throw new Error(`TTW skeleton: parent "${b.parent}" must be listed before "${b.name}"`);
      bones[b.parent].add(bone);
      worldRest[b.name] = worldRest[b.parent].clone().add(bone.position);
    } else {
      root = bone;
      worldRest[b.name] = bone.position.clone();
    }
    if (b.tail) tails[b.name] = worldRest[b.name].clone().add(new THREE.Vector3().fromArray(b.tail));
  }

  const attachments = {};
  for (const a of skelDef.attachments || []) {
    const o = new THREE.Object3D();
    o.name = a.name;
    o.position.fromArray(a.position || [0, 0, 0]);
    const r = a.rotation || [0, 0, 0];
    o.rotation.set(r[0] * DEG, r[1] * DEG, r[2] * DEG, 'XYZ');
    o.userData.attachment = true;
    bones[a.bone].add(o);
    attachments[a.name] = o;
  }

  const boneIndex = {};
  list.forEach((b, i) => { boneIndex[b.name] = i; });

  return { root, bones, list, boneIndex, restPositions, worldRest, tails, attachments, skeleton: new THREE.Skeleton(list) };
}

// ------------------------------------------------------------------ geometry

function swapSide(name) {
  if (name.startsWith('left')) return 'right' + name.slice(4);
  if (name.startsWith('right')) return 'left' + name.slice(5);
  return name;
}

function mirrorValue(v) {
  if (Array.isArray(v)) return [-v[0], v[1], v[2]];
  return v;
}

function mirrorAt(at) {
  if (Array.isArray(at)) return mirrorValue(at);
  const out = { ...at };
  if (at.joint) out.joint = at.joint.split(':').map(swapSide).join(':');
  if (at.between) out.between = at.between.map((n) => n.split(':').map(swapSide).join(':'));
  if (at.offset) out.offset = mirrorValue(at.offset);
  return out;
}

function mirrorWeights(w) {
  const out = {};
  for (const [k, v] of Object.entries(w || {})) out[swapSide(k)] = v;
  return out;
}

function mirrorPart(p) {
  const q = JSON.parse(JSON.stringify(p));
  q.name = (p.name || p.type) + '_L';
  delete q.mirror;
  if (q.at) q.at = mirrorAt(q.at);
  if (q.w) q.w = mirrorWeights(q.w);
  if (q.rotation) q.rotation = [q.rotation[0], -q.rotation[1], -q.rotation[2]];
  if (q.points) q.points = q.points.map((pt) => ({ ...pt, at: mirrorAt(pt.at), w: mirrorWeights(pt.w) }));
  q.flip = true; // mirrored geometry needs its winding reversed
  return q;
}

function resolvePoint(at, rig) {
  const v = new THREE.Vector3();
  const jointPos = (ref) => {
    const [name, tail] = ref.split(':');
    const p = tail === 'tail' ? rig.tails[name] : rig.worldRest[name];
    if (!p) throw new Error(`TTW wrestler: unknown joint "${ref}"`);
    return p;
  };
  if (Array.isArray(at)) return v.fromArray(at);
  if (at.joint) v.copy(jointPos(at.joint));
  else if (at.between) v.lerpVectors(jointPos(at.between[0]), jointPos(at.between[1]), at.t ?? 0.5);
  if (at.offset) v.add(new THREE.Vector3().fromArray(at.offset));
  return v;
}

class GeoBuilder {
  constructor(rig, palette) {
    this.rig = rig;
    this.palette = palette;
    this.pos = []; this.nor = []; this.col = []; this.si = []; this.sw = []; this.idx = [];
    this.colorCache = {};
  }
  color(name) {
    if (!this.colorCache[name]) {
      const hex = this.palette[name] ?? name ?? '#ff00ff';
      this.colorCache[name] = new THREE.Color(hex); // converted to linear by ColorManagement
    }
    return this.colorCache[name];
  }
  weights(w) {
    const entries = Object.entries(w || {}).filter(([, v]) => v > 0).sort((a, b) => b[1] - a[1]).slice(0, 4);
    const sum = entries.reduce((s, [, v]) => s + v, 0) || 1;
    const idx = [0, 0, 0, 0], wt = [0, 0, 0, 0];
    entries.forEach(([name, v], i) => {
      const bi = this.rig.boneIndex[name];
      if (bi === undefined) throw new Error(`TTW wrestler: unknown bone "${name}" in weights`);
      idx[i] = bi; wt[i] = v / sum;
    });
    return { idx, wt };
  }
  vertex(p, n, c, sk) {
    this.pos.push(p.x, p.y, p.z);
    this.nor.push(n.x, n.y, n.z);
    this.col.push(c.r, c.g, c.b);
    this.si.push(...sk.idx);
    this.sw.push(...sk.wt);
    return this.pos.length / 3 - 1;
  }
  tri(a, b, c, flip) {
    if (flip) this.idx.push(a, c, b); else this.idx.push(a, b, c);
  }
  // Append an indexed BufferGeometry transformed by matrix, with one weight set and colour
  addGeometry(geo, matrix, color, sk, flip) {
    const normalMatrix = new THREE.Matrix3().getNormalMatrix(matrix);
    const p = geo.attributes.position, n = geo.attributes.normal;
    const base = this.pos.length / 3;
    const v = new THREE.Vector3(), nn = new THREE.Vector3();
    for (let i = 0; i < p.count; i++) {
      v.fromBufferAttribute(p, i).applyMatrix4(matrix);
      nn.fromBufferAttribute(n, i).applyMatrix3(normalMatrix).normalize();
      this.vertex(v, nn, color, sk);
    }
    const index = geo.index ? geo.index.array : [...Array(p.count).keys()];
    for (let i = 0; i < index.length; i += 3) this.tri(base + index[i], base + index[i + 1], base + index[i + 2], flip);
  }
  build() {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(this.pos, 3));
    g.setAttribute('normal', new THREE.Float32BufferAttribute(this.nor, 3));
    g.setAttribute('color', new THREE.Float32BufferAttribute(this.col, 3));
    g.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(this.si, 4));
    g.setAttribute('skinWeight', new THREE.Float32BufferAttribute(this.sw, 4));
    g.setIndex(this.idx);
    g.computeBoundingBox();
    return g;
  }
}

function buildGeometry(def, rig) {
  const gb = new GeoBuilder(rig, def.palette || {});
  const parts = [];
  for (const p of def.parts || []) {
    parts.push(p);
    if (p.mirror) parts.push(mirrorPart(p));
  }
  for (const p of parts) {
    if (p.type === 'tube') addTube(gb, p, rig);
    else if (p.type === 'ellipsoid') addEllipsoid(gb, p, rig);
    else if (p.type === 'box') addBox(gb, p, rig);
    else console.warn('TTW wrestler: unknown part type', p.type);
  }
  const geo = gb.build();
  geo.userData.triangles = gb.idx.length / 3;
  return geo;
}

function partMatrix(p, rig) {
  const m = new THREE.Matrix4();
  const r = p.rotation || [0, 0, 0];
  const q = new THREE.Quaternion().setFromEuler(new THREE.Euler(r[0] * DEG, r[1] * DEG, r[2] * DEG, 'XYZ'));
  const scale = p.radii ? new THREE.Vector3().fromArray(p.radii) : new THREE.Vector3(1, 1, 1);
  m.compose(resolvePoint(p.at, rig), q, scale);
  return m;
}

function addEllipsoid(gb, p, rig) {
  const [ws, hs] = p.segments || [10, 8];
  const geo = new THREE.SphereGeometry(1, ws, hs);
  // mirrored parts: negative-free, since mirroring is done on position/rotation, winding stays valid
  gb.addGeometry(geo, partMatrix(p, rig), gb.color(p.color), gb.weights(p.w), false);
  geo.dispose();
}

function addBox(gb, p, rig) {
  const geo = new THREE.BoxGeometry(...p.size);
  const m = partMatrix({ ...p, radii: null }, rig);
  gb.addGeometry(geo, m, gb.color(p.color), gb.weights(p.w), false);
  geo.dispose();
}

function addTube(gb, p, rig) {
  const radial = p.radial || 10;
  const pts = p.points.map((pt) => ({
    c: resolvePoint(pt.at, rig),
    rx: pt.rx ?? pt.r ?? 0.1,
    rz: pt.rz ?? pt.r ?? 0.1,
    w: pt.w || {},
    color: pt.color,
    steps: pt.steps ?? 2,
  }));

  // Tangent at each control point (central difference) so duplicated boundary rings match exactly
  const tangents = pts.map((pt, i) => {
    const a = pts[Math.max(0, i - 1)].c, b = pts[Math.min(pts.length - 1, i + 1)].c;
    return new THREE.Vector3().subVectors(b, a).normalize();
  });

  const lerpW = (wa, wb, t) => {
    const out = {};
    for (const [k, v] of Object.entries(wa)) out[k] = (out[k] || 0) + v * (1 - t);
    for (const [k, v] of Object.entries(wb)) out[k] = (out[k] || 0) + v * t;
    return out;
  };

  const ringFrame = (t) => {
    // front = character forward (-Z) made perpendicular to the tube direction
    const front = new THREE.Vector3(0, 0, -1);
    if (Math.abs(front.dot(t)) > 0.95) front.set(0, 1, 0);
    front.addScaledVector(t, -front.dot(t)).normalize();
    const side = new THREE.Vector3().crossVectors(front, t).normalize();
    return { front, side };
  };

  const rings = []; // { verts: [index], center, sk, color }
  const makeRing = (c, t, rx, rz, w, color) => {
    const { front, side } = ringFrame(t);
    const sk = gb.weights(w);
    const col = gb.color(color);
    const verts = [];
    for (let j = 0; j < radial; j++) {
      const a = (j / radial) * Math.PI * 2;
      const ca = Math.cos(a), sa = Math.sin(a);
      const pos = c.clone().addScaledVector(side, ca * rx).addScaledVector(front, sa * rz);
      // ellipse normal
      const n = new THREE.Vector3().addScaledVector(side, ca / rx).addScaledVector(front, sa / rz).normalize();
      verts.push(gb.vertex(pos, n, col, sk));
    }
    return { verts, c: c.clone(), t: t.clone(), sk, col };
  };

  // Winding: rings advance along t; side x front points along -t or +t depending on frame, so test once
  const { front: f0, side: s0 } = ringFrame(tangents[0]);
  const ccw = new THREE.Vector3().crossVectors(s0, f0).dot(tangents[0]) > 0;
  const flip = ccw ? false : true;

  const segRings = [];
  for (let k = 0; k < pts.length - 1; k++) {
    const A = pts[k], B = pts[k + 1];
    const seg = [];
    for (let s = 0; s <= A.steps; s++) {
      const u = s / A.steps;
      const c = new THREE.Vector3().lerpVectors(A.c, B.c, u);
      const t = new THREE.Vector3().lerpVectors(tangents[k], tangents[k + 1], u).normalize();
      seg.push(makeRing(c, t, THREE.MathUtils.lerp(A.rx, B.rx, u), THREE.MathUtils.lerp(A.rz, B.rz, u), lerpW(A.w, B.w, u), A.color));
    }
    segRings.push(seg);
    for (let s = 0; s < seg.length - 1; s++) {
      const r0 = seg[s].verts, r1 = seg[s + 1].verts;
      for (let j = 0; j < radial; j++) {
        const j1 = (j + 1) % radial;
        gb.tri(r0[j], r0[j1], r1[j1], flip);
        gb.tri(r0[j], r1[j1], r1[j], flip);
      }
    }
    rings.push(...seg);
  }

  const caps = p.caps || [false, false];
  const cap = (ring, atStart) => {
    const n = ring.t.clone().multiplyScalar(atStart ? -1 : 1);
    const center = gb.vertex(ring.c, n, ring.col, ring.sk);
    // flat cap vertices share position but need the cap normal
    const capVerts = ring.verts.map((vi) => {
      const p = new THREE.Vector3(gb.pos[vi * 3], gb.pos[vi * 3 + 1], gb.pos[vi * 3 + 2]);
      return gb.vertex(p, n, ring.col, ring.sk);
    });
    for (let j = 0; j < radial; j++) {
      const j1 = (j + 1) % radial;
      if (atStart) gb.tri(center, capVerts[j1], capVerts[j], flip);
      else gb.tri(center, capVerts[j], capVerts[j1], flip);
    }
  };
  if (caps[0]) cap(rings[0], true);
  if (caps[1]) cap(rings[rings.length - 1], false);
}


// ------------------------------------------------------------------ animation

// Build a THREE.AnimationClip from TTW keyframe JSON (called once per animation by AnimationLibrary). Every bone in the skeleton gets a track,
// so clips fully define the pose and can be played, blended or swapped independently.
export function createClip(animDef, skeletonDef) {
  const name = animDef.id || animDef.name;

  const duration = animDef.duration;
  const fps = animDef.sampleRate || 30;
  const smooth = (animDef.interpolation || 'smooth') === 'smooth';
  const stepped = animDef.interpolation === 'step';
  const loop = !!animDef.loop;
  const tracks = [];
  const rest = {};
  for (const b of skeletonDef.bones) rest[b.name] = b.position;

  const sampleTimes = [];
  const n = Math.max(1, Math.round(duration * fps));
  for (let i = 0; i <= n; i++) sampleTimes.push((i / n) * duration);

  for (const b of skeletonDef.bones) {
    const def = (animDef.tracks || {})[b.name] || {};

    // rotation
    const rotKeys = def.rotation || [[0, 0, 0, 0]];
    const times = smooth ? sampleTimes : rotKeys.map((k) => k[0]);
    const quats = [];
    const q = new THREE.Quaternion(), prev = new THREE.Quaternion();
    times.forEach((t, i) => {
      const [x, y, z] = smooth ? sampleCurve(rotKeys, t, duration, loop) : rotKeys[i].slice(1);
      q.setFromEuler(new THREE.Euler(x * DEG, y * DEG, z * DEG, 'XYZ'));
      if (i > 0 && q.dot(prev) < 0) q.set(-q.x, -q.y, -q.z, -q.w); // keep shortest path
      prev.copy(q);
      quats.push(q.x, q.y, q.z, q.w);
    });
    const qt = new THREE.QuaternionKeyframeTrack(`${b.name}.quaternion`, times, quats);
    if (stepped) qt.setInterpolation(THREE.InterpolateDiscrete);
    tracks.push(qt);

    // position (offset from rest, only for bones that declare it)
    if (def.position) {
      const pk = def.position;
      const ptimes = smooth ? sampleTimes : pk.map((k) => k[0]);
      const vals = [];
      ptimes.forEach((t, i) => {
        const [x, y, z] = smooth ? sampleCurve(pk, t, duration, loop) : pk[i].slice(1);
        vals.push(rest[b.name][0] + x, rest[b.name][1] + y, rest[b.name][2] + z);
      });
      const vt = new THREE.VectorKeyframeTrack(`${b.name}.position`, ptimes, vals);
      if (stepped) vt.setInterpolation(THREE.InterpolateDiscrete);
      tracks.push(vt);
    } else {
      tracks.push(new THREE.VectorKeyframeTrack(`${b.name}.position`, [0], rest[b.name].slice()));
    }
  }

  const clip = new THREE.AnimationClip(name, duration, tracks);
  clip.userData = {
    id: animDef.id,
    displayName: animDef.name,
    category: animDef.category,
    loop,
    rootMotion: animDef.rootMotion || null,
    events: animDef.events || [],
    clampWhenFinished: animDef.clampWhenFinished ?? !loop,
  };
  return clip;
}

// Catmull-Rom through the keys (values only), wrapping for looping clips
function sampleCurve(keys, t, duration, loop) {
  if (keys.length === 1) return keys[0].slice(1);
  let i = 0;
  while (i < keys.length - 2 && t > keys[i + 1][0]) i++;
  const k1 = keys[i], k2 = keys[i + 1];
  const span = k2[0] - k1[0] || 1;
  const u = Math.min(1, Math.max(0, (t - k1[0]) / span));
  const last = keys.length - 1;
  const k0 = i > 0 ? keys[i - 1] : (loop ? keys[last - 1] : k1);
  const k3 = i + 2 <= last ? keys[i + 2] : (loop ? keys[1] : k2);
  const out = [];
  for (let c = 1; c <= 3; c++) {
    const p0 = k0[c], p1 = k1[c], p2 = k2[c], p3 = k3[c];
    const u2 = u * u, u3 = u2 * u;
    out.push(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u2 + (-p0 + 3 * p1 - 3 * p2 + p3) * u3));
  }
  return out;
}
