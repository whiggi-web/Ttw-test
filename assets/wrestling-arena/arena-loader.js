// Wrestling Arena loader for Three.js r160
// Builds the arena from arena.json + materials.json + parts/*.json
//
// Usage:
//   import * as THREE from 'three';
//   import { loadArena } from './arena-loader.js';
//   const arena = await loadArena('assets/wrestling-arena/arena.json');
//   scene.add(arena.group);
//   arena.applyEnvironment(scene);           // optional: background, fog, lights
//   arena.markers.ring_center                // THREE.Vector3
//   arena.paths.entrance_red                 // THREE.Vector3[]
//   arena.colliders                          // [{ id, tags, box: THREE.Box3 }]
//   arena.byId('stage_curtain')              // [Object3D]
//   arena.byTag('wall')                      // [Object3D] (each wall is its own object)
//   arena.setScreen('screen_main', { text: 'WHIGGI', sub: 'ENTERS' })
//
// If you already have the JSON in memory (bundled), call buildArena(def, materials, parts).

import * as THREE from 'three';

const DEG = Math.PI / 180;

export async function loadArena(url) {
  const base = url.slice(0, url.lastIndexOf('/') + 1);
  const def = await (await fetch(url)).json();
  const materials = await (await fetch(base + def.materials)).json();
  const parts = {};
  await Promise.all(def.parts.map(async (p) => {
    parts[p.id] = await (await fetch(base + p.file)).json();
  }));
  return buildArena(def, materials, parts);
}

export function buildArena(def, materialDefs, parts) {
  const root = new THREE.Group();
  root.name = def.name || 'arena';

  const matCache = {};
  const getMat = (name) => {
    const key = name || 'default';
    if (matCache[key]) return matCache[key];
    const m = materialDefs[key] || materialDefs.default || { color: '#888888' };
    const mat = new THREE.MeshStandardMaterial({
      color: m.color || '#888888',
      roughness: m.roughness ?? 0.8,
      metalness: m.metalness ?? 0,
    });
    if (m.emissive) {
      mat.emissive = new THREE.Color(m.emissive);
      mat.emissiveIntensity = m.emissiveIntensity ?? 1;
    }
    mat.name = key;
    matCache[key] = mat;
    return mat;
  };

  const index = new Map();       // id -> Object3D[]
  const tagIndex = new Map();    // tag -> Object3D[]
  const colliders = [];
  const markers = {};
  const screens = new Map();     // id -> { canvas, ctx, texture, def }

  const register = (obj, id, tags) => {
    obj.name = id;
    obj.userData.arenaId = id;
    obj.userData.tags = tags || [];
    if (!index.has(id)) index.set(id, []);
    index.get(id).push(obj);
    for (const t of tags || []) {
      if (!tagIndex.has(t)) tagIndex.set(t, []);
      tagIndex.get(t).push(obj);
    }
  };

  for (const p of def.parts) {
    const part = parts[p.id];
    if (!part) continue;
    const partGroup = new THREE.Group();
    partGroup.name = 'part_' + p.id;
    root.add(partGroup);

    for (const o of part.objects || []) {
      if (o.type === 'light') {
        buildLights(o, partGroup, register);
        continue;
      }
      const copies = mirrorScales(o.mirror);
      copies.forEach(({ scale, suffix }) => {
        const holder = new THREE.Group();
        holder.scale.copy(scale);
        // Walls get their own material instance so the game can fade one wall at a time
        const isWall = (o.tags || []).includes('wall');
        const matFor = isWall ? (n) => getMat(n).clone() : getMat;
        const built = buildObject(o, matFor, screens, suffix);
        if (!built) return;
        holder.add(built);
        partGroup.add(holder);
        const id = o.id + suffix;
        register(built, id, o.tags);
        built.userData.collide = !!o.collide;
      });
    }

    for (const [k, v] of Object.entries(part.markers || {})) {
      markers[k] = new THREE.Vector3(v[0], v[1], v[2]);
    }
  }

  root.updateMatrixWorld(true);

  // Colliders: one AABB per mesh instance for every object flagged collide
  for (const [id, objs] of index) {
    for (const obj of objs) {
      if (!obj.userData.collide) continue;
      obj.traverse((m) => {
        if (!m.isMesh || m.userData.noCollide) return;
        if (!m.geometry.boundingBox) m.geometry.computeBoundingBox();
        if (m.isInstancedMesh) {
          const im = new THREE.Matrix4();
          for (let i = 0; i < m.count; i++) {
            m.getMatrixAt(i, im);
            im.premultiply(m.matrixWorld);
            colliders.push({ id, tags: obj.userData.tags, box: m.geometry.boundingBox.clone().applyMatrix4(im) });
          }
        } else {
          colliders.push({ id, tags: obj.userData.tags, box: m.geometry.boundingBox.clone().applyMatrix4(m.matrixWorld) });
        }
      });
    }
  }

  const paths = {};
  for (const [name, list] of Object.entries(def.paths || {})) {
    paths[name] = list.filter((k) => markers[k]).map((k) => markers[k].clone());
  }

  const cameras = {};
  for (const [name, c] of Object.entries(def.cameras || {})) {
    cameras[name] = { position: new THREE.Vector3(...c.position), target: new THREE.Vector3(...c.target) };
  }

  const envLights = [];
  function applyEnvironment(scene) {
    const env = def.environment || {};
    if (env.background) scene.background = new THREE.Color(env.background);
    if (env.fog) scene.fog = new THREE.Fog(env.fog.color, env.fog.near, env.fog.far);
    if (env.hemisphere) {
      const h = new THREE.HemisphereLight(env.hemisphere.sky, env.hemisphere.ground, env.hemisphere.intensity);
      scene.add(h); envLights.push(h);
    }
    if (env.ambient) {
      const a = new THREE.AmbientLight(env.ambient.color, env.ambient.intensity);
      scene.add(a); envLights.push(a);
    }
    if (env.directional) {
      const d = new THREE.DirectionalLight(env.directional.color, env.directional.intensity);
      d.position.set(...env.directional.position);
      if (env.directional.castShadow) {
        d.castShadow = true;
        d.shadow.mapSize.set(2048, 2048);
        const s = d.shadow.camera;
        s.left = -45; s.right = 45; s.top = 45; s.bottom = -45; s.near = 1; s.far = 120;
        d.shadow.bias = -0.0005;
      }
      scene.add(d); scene.add(d.target); envLights.push(d);
    }
    return envLights;
  }

  function setScreen(id, content) {
    for (const [key, s] of screens) {
      if (key === id || key.startsWith(id + '_m')) {
        Object.assign(s.content, content);
        drawScreen(s);
      }
    }
  }

  return {
    group: root,
    markers,
    paths,
    cameras,
    colliders,
    screens,
    byId: (id) => index.get(id) || [],
    byTag: (tag) => tagIndex.get(tag) || [],
    applyEnvironment,
    setScreen,
    materials: matCache,
  };
}

// ---------- helpers ----------

function mirrorScales(mirror) {
  const out = [{ scale: new THREE.Vector3(1, 1, 1), suffix: '' }];
  if (!mirror) return out;
  if (mirror.includes('x')) out.push({ scale: new THREE.Vector3(-1, 1, 1), suffix: '_mx' });
  if (mirror.includes('z')) out.push({ scale: new THREE.Vector3(1, 1, -1), suffix: '_mz' });
  if (mirror.includes('x') && mirror.includes('z')) out.push({ scale: new THREE.Vector3(-1, 1, -1), suffix: '_mxz' });
  return out;
}

function offsetsFor(o) {
  if (o.grid) {
    const [nx, nz] = o.grid.counts;
    const [sx, sy, sz] = o.grid.step;
    const list = [];
    for (let i = 0; i < nx; i++) for (let j = 0; j < nz; j++) list.push(new THREE.Vector3(i * sx, 0, j * sz));
    return list;
  }
  if (o.array) {
    const list = [];
    const s = new THREE.Vector3(...o.array.step);
    for (let i = 0; i < o.array.count; i++) list.push(s.clone().multiplyScalar(i));
    return list;
  }
  return [new THREE.Vector3()];
}

function applyTransform(obj, o) {
  if (o.position) obj.position.set(...o.position);
  if (o.rotation) obj.rotation.set(o.rotation[0] * DEG, o.rotation[1] * DEG, o.rotation[2] * DEG);
}

function shadowFlags(mesh, o) {
  mesh.castShadow = o.castShadow !== false;
  mesh.receiveShadow = true;
}

function buildObject(o, getMat, screens, suffix) {
  switch (o.type) {
    case 'box':
    case 'cylinder':
      return buildPrimitive(o, getMat);
    case 'rope':
      return buildRope(o, getMat);
    case 'ramp':
      return buildRamp(o, getMat);
    case 'stairs':
      return buildStairs(o, getMat);
    case 'tiers':
      return buildTiers(o, getMat);
    case 'screen':
      return buildScreen(o, getMat, screens, suffix);
    default:
      console.warn('[arena] unknown object type', o.type, o.id);
      return null;
  }
}

function primitiveGeometry(o) {
  if (o.type === 'box') return new THREE.BoxGeometry(...o.size);
  const rt = o.radiusTop ?? o.radius ?? 0.5;
  const rb = o.radiusBottom ?? o.radius ?? 0.5;
  return new THREE.CylinderGeometry(rt, rb, o.height ?? 1, o.segments ?? 16);
}

function buildPrimitive(o, getMat) {
  const geo = primitiveGeometry(o);
  const mat = getMat(o.material);
  const offsets = offsetsFor(o);

  if (offsets.length === 1) {
    const mesh = new THREE.Mesh(geo, mat);
    applyTransform(mesh, o);
    shadowFlags(mesh, o);
    return mesh;
  }

  // Repeated objects become one InstancedMesh (one draw call)
  const inst = new THREE.InstancedMesh(geo, mat, offsets.length);
  const local = new THREE.Object3D();
  offsets.forEach((off, i) => {
    applyTransform(local, o);
    local.position.add(off);
    local.updateMatrix();
    inst.setMatrixAt(i, local.matrix);
  });
  inst.instanceMatrix.needsUpdate = true;
  inst.computeBoundingSphere();
  shadowFlags(inst, o);
  return inst;
}

function cylinderBetween(a, b, radius, mat) {
  const dir = new THREE.Vector3().subVectors(b, a);
  const len = dir.length();
  const geo = new THREE.CylinderGeometry(radius, radius, len, 8);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.copy(a).addScaledVector(dir, 0.5);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize());
  return mesh;
}

function buildRope(o, getMat) {
  const g = new THREE.Group();
  const a = new THREE.Vector3(...o.from);
  const b = new THREE.Vector3(...o.to);
  for (const off of offsetsFor(o)) {
    const m = cylinderBetween(a.clone().add(off), b.clone().add(off), o.radius ?? 0.03, getMat(o.material));
    shadowFlags(m, o);
    g.add(m);
  }
  return g;
}

function buildRamp(o, getMat) {
  const g = new THREE.Group();
  const a = new THREE.Vector3(...o.from);
  const b = new THREE.Vector3(...o.to);
  const dir = new THREE.Vector3().subVectors(b, a);
  const len = dir.length();
  const t = o.thickness ?? 0.2;
  const w = o.width ?? 3;

  // Orientation: local Z along the ramp, local Y the deck normal
  const zAxis = dir.clone().normalize();
  const xAxis = new THREE.Vector3(0, 1, 0).cross(zAxis).normalize();
  const yAxis = zAxis.clone().cross(xAxis).normalize();
  const basis = new THREE.Matrix4().makeBasis(xAxis, yAxis, zAxis);
  const quat = new THREE.Quaternion().setFromRotationMatrix(basis);
  const mid = a.clone().addScaledVector(dir, 0.5).addScaledVector(yAxis, -t / 2);

  const deck = new THREE.Mesh(new THREE.BoxGeometry(w, t, len), getMat(o.material));
  deck.position.copy(mid);
  deck.quaternion.copy(quat);
  shadowFlags(deck, o);
  g.add(deck);

  // Solid fill underneath so it reads as a raised walkway, not a floating plank
  const minY = Math.min(a.y, b.y);
  const maxY = Math.max(a.y, b.y);
  if (maxY - minY > 0.05 && (o.fill ?? true)) {
    const shape = new THREE.Shape();
    const horiz = Math.hypot(dir.x, dir.z);
    shape.moveTo(0, 0);
    shape.lineTo(horiz, 0);
    shape.lineTo(horiz, Math.max(b.y - t, 0));
    shape.lineTo(0, Math.max(a.y - t, 0));
    shape.closePath();
    const sg = new THREE.ExtrudeGeometry(shape, { depth: w * 0.98, bevelEnabled: false });
    sg.translate(0, 0, -w * 0.49);
    const side = new THREE.Mesh(sg, getMat(o.material));
    side.rotation.y = Math.atan2(-dir.z, dir.x);
    side.position.set(a.x, 0, a.z);
    shadowFlags(side, o);
    g.add(side);
  }

  if (o.edgeMaterial) {
    for (const s of [-1, 1]) {
      const edge = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.06, len), getMat(o.edgeMaterial));
      edge.position.copy(mid).addScaledVector(xAxis, s * (w / 2 - 0.04)).addScaledVector(yAxis, t / 2 + 0.03);
      edge.quaternion.copy(quat);
      edge.castShadow = false;
      edge.userData.noCollide = true;
      g.add(edge);
    }
  }
  return g;
}

function buildStairs(o, getMat) {
  // Local frame: origin at bottom front centre, climbing toward +Z
  const g = new THREE.Group();
  const mat = getMat(o.material);
  const n = o.steps ?? 3;
  const rise = o.rise ?? 0.3;
  const run = o.run ?? 0.3;
  const w = o.width ?? 1;
  for (let i = 0; i < n; i++) {
    const h = rise * (i + 1);
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, run), mat);
    m.position.set(0, h / 2, run * i + run / 2);
    shadowFlags(m, o);
    g.add(m);
  }
  applyTransform(g, o);
  return g;
}

function seededRandom(seed) {
  let s = seed >>> 0 || 1;
  return () => {
    s ^= s << 13; s ^= s >>> 17; s ^= s << 5;
    return ((s >>> 0) % 100000) / 100000;
  };
}

const CROWD_COLORS = ['#1b1d24', '#2b2f3a', '#5a1a1f', '#1a2d5a', '#3a3a3a', '#6b5a48', '#d8d8d8', '#8a1c22', '#1c4f8a', '#222222'];

function buildTiers(o, getMat) {
  // Local frame: rows run along X (length), stand rises toward +Z
  const g = new THREE.Group();
  const rows = o.rows ?? 15;
  const rise = o.rise ?? 0.45;
  const depth = o.depth ?? 0.85;
  const L = o.length ?? 20;
  const stepMat = getMat(o.material);

  // Stepped profile as one extruded shape (cheap: one mesh for all rows)
  const shape = new THREE.Shape();
  shape.moveTo(0, 0);
  for (let r = 0; r < rows; r++) {
    shape.lineTo(r * depth, (r + 1) * rise);
    shape.lineTo((r + 1) * depth, (r + 1) * rise);
  }
  shape.lineTo(rows * depth, 0);
  shape.closePath();
  const geo = new THREE.ExtrudeGeometry(shape, { depth: L, bevelEnabled: false });
  // shape x -> local Z (depth), shape y -> Y, extrude z -> local X (length)
  geo.rotateY(-Math.PI / 2);
  geo.translate(L / 2, 0, 0);
  const steps = new THREE.Mesh(geo, stepMat);
  shadowFlags(steps, { castShadow: false });
  g.add(steps);

  // Seats (instanced)
  const spacing = o.seatSpacing ?? 0.6;
  const perRow = Math.floor((L - 0.6) / spacing);
  const seatGeo = new THREE.BoxGeometry(spacing * 0.8, 0.45, 0.45);
  seatGeo.translate(0, 0.225, 0);
  const seats = new THREE.InstancedMesh(seatGeo, getMat(o.seatMaterial || 'seat'), rows * perRow);
  const tmp = new THREE.Object3D();
  let k = 0;
  const seatPositions = [];
  for (let r = 0; r < rows; r++) {
    for (let i = 0; i < perRow; i++) {
      const x = -L / 2 + 0.3 + spacing / 2 + i * spacing;
      const y = (r + 1) * rise;
      const z = r * depth + depth * 0.62;
      tmp.position.set(x, y, z);
      tmp.updateMatrix();
      seats.setMatrixAt(k++, tmp.matrix);
      seatPositions.push([x, y, z]);
    }
  }
  seats.instanceMatrix.needsUpdate = true;
  seats.computeBoundingSphere();
  seats.receiveShadow = true;
  seats.userData.noCollide = true;
  g.add(seats);

  // Crowd: simple seated blocks with a head, random fill, per-instance colour
  if (o.crowd && (o.crowd.density ?? 0) > 0) {
    const rnd = seededRandom(o.crowd.seed ?? 7);
    const colors = (o.crowd.colors || CROWD_COLORS).map((c) => new THREE.Color(c));
    const filled = seatPositions.filter(() => rnd() < o.crowd.density);
    const bodyGeo = new THREE.BoxGeometry(0.42, 0.62, 0.3);
    bodyGeo.translate(0, 0.45 + 0.31, -0.02);
    const headGeo = new THREE.BoxGeometry(0.2, 0.22, 0.2);
    headGeo.translate(0, 0.45 + 0.62 + 0.13, -0.02);
    const bodyMat = new THREE.MeshStandardMaterial({ roughness: 0.9 });
    const headMat = new THREE.MeshStandardMaterial({ roughness: 0.9 });
    const bodies = new THREE.InstancedMesh(bodyGeo, bodyMat, filled.length);
    const heads = new THREE.InstancedMesh(headGeo, headMat, filled.length);
    const skins = ['#e0b896', '#c08a64', '#8d5a3b', '#5a3a26', '#f0cfb0'].map((c) => new THREE.Color(c));
    filled.forEach((p, i) => {
      tmp.position.set(p[0] + (rnd() - 0.5) * 0.08, p[1], p[2]);
      tmp.rotation.set(0, (rnd() - 0.5) * 0.4, 0);
      tmp.scale.setScalar(0.9 + rnd() * 0.2);
      tmp.updateMatrix();
      bodies.setMatrixAt(i, tmp.matrix);
      heads.setMatrixAt(i, tmp.matrix);
      bodies.setColorAt(i, colors[Math.floor(rnd() * colors.length)]);
      heads.setColorAt(i, skins[Math.floor(rnd() * skins.length)]);
    });
    tmp.rotation.set(0, 0, 0); tmp.scale.setScalar(1);
    for (const im of [bodies, heads]) {
      im.instanceMatrix.needsUpdate = true;
      if (im.instanceColor) im.instanceColor.needsUpdate = true;
      im.computeBoundingSphere();
      im.name = 'crowd';
      im.userData.noCollide = true;
      g.add(im);
    }
    g.userData.crowd = { bodies, heads };
  }

  // LED ribbon along the front wall of the stand
  if (o.frontMaterial) {
    const rib = new THREE.Mesh(new THREE.BoxGeometry(L, 0.3, 0.04), getMat(o.frontMaterial));
    rib.position.set(0, rise * 0.55, -0.03);
    rib.userData.noCollide = true;
    g.add(rib);
  }

  applyTransform(g, o);
  return g;
}

function drawScreen(s) {
  const { canvas, ctx, content } = s;
  const W = canvas.width, H = canvas.height;
  const [c1, c2] = content.colors || ['#0a1a5c', '#c4161c'];
  const grad = ctx.createLinearGradient(0, 0, W, H);
  grad.addColorStop(0, c1);
  grad.addColorStop(1, c2);
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);
  // LED panel grid
  ctx.strokeStyle = 'rgba(0,0,0,0.25)';
  ctx.lineWidth = 2;
  const cell = Math.max(16, Math.round(W / 32));
  for (let x = 0; x < W; x += cell) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
  for (let y = 0; y < H; y += cell) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillStyle = '#ffffff';
  ctx.shadowColor = 'rgba(255,255,255,0.6)';
  ctx.shadowBlur = 24;
  if (content.text) {
    ctx.font = `900 ${Math.round(H * 0.26)}px Impact, "Arial Black", sans-serif`;
    ctx.fillText(content.text, W / 2, H * 0.45);
  }
  if (content.sub) {
    ctx.font = `700 ${Math.round(H * 0.11)}px "Arial Black", sans-serif`;
    ctx.fillText(content.sub, W / 2, H * 0.72);
  }
  ctx.shadowBlur = 0;
  s.texture.needsUpdate = true;
}

function buildScreen(o, getMat, screens, suffix) {
  const g = new THREE.Group();
  const [w, h] = o.size;
  const canvas = document.createElement('canvas');
  const res = 512 / Math.max(w, h);
  canvas.width = Math.max(64, Math.round(w * res));
  canvas.height = Math.max(64, Math.round(h * res));
  const ctx = canvas.getContext('2d');
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  const s = { canvas, ctx, texture, content: { ...(o.content || {}) } };
  drawScreen(s);
  screens.set(o.id + suffix, s);

  const panel = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: texture, toneMapped: false }));
  panel.position.z = 0.16;
  panel.name = 'screen_surface';
  // Mirrored copies get negative scale, so flip the surface back to keep text readable
  if (suffix.includes('x')) panel.scale.x = -1;
  g.add(panel);

  const frame = new THREE.Mesh(new THREE.BoxGeometry(w + 0.4, h + 0.4, 0.3), getMat(o.frameMaterial || 'screen_frame'));
  shadowFlags(frame, o);
  g.add(frame);
  applyTransform(g, o);
  return g;
}

function buildLights(o, parent, register) {
  const copies = mirrorScales(o.mirror);
  for (const { scale, suffix } of copies) {
    const pos = new THREE.Vector3(...o.position).multiply(scale);
    let light;
    if (o.light === 'spot') {
      light = new THREE.SpotLight(o.color || '#ffffff', o.intensity ?? 100, o.distance ?? 0, (o.angle ?? 30) * DEG, o.penumbra ?? 0.4, o.decay ?? 2);
      const tgt = new THREE.Vector3(...(o.target || [0, 0, 0])).multiply(scale);
      light.target.position.copy(tgt);
      parent.add(light.target);
    } else {
      light = new THREE.PointLight(o.color || '#ffffff', o.intensity ?? 100, o.distance ?? 0, o.decay ?? 2);
    }
    light.position.copy(pos);
    parent.add(light);
    register(light, o.id + suffix, o.tags);
  }
}
