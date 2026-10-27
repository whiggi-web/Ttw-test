// TTW loader extension, Batch 2. Additive: loader.js is not modified.
//
// Import once, anywhere after loader.js:
//   import { loadPack } from './assets/ttw-wrestlers/loader.js';
//   import './assets/ttw-wrestlers/loader-ext.js';
//
// Adds:
//  1. rootMotion.endRotationY for "baked" clips (turn-180, rolls, sideways falls). When the next clip starts,
//     the wrestler's object is moved by the hips offset (as in Batch 1) AND turned by endRotationY, so the next
//     clip starts in the right place facing the right way. If the clip is interrupted early, the hips' current
//     yaw is committed instead.
//  2. Pose-state helpers read from animation tags: getEndState(id), getStartState(id), currentState().
//     States: standing (default), lying-back, lying-front, kneeling, rope-lean, airborne-back.
//
// Without this module Batch 1 and Batch 2 clips still play; only the facing change after those few clips is lost.

import * as THREE from 'three';
import { Wrestler, AnimationLibrary } from './loader.js';

const RAD_PER_DEG = Math.PI / 180;

if (!Wrestler.prototype.__ttwExt) {
  Object.defineProperty(Wrestler.prototype, '__ttwExt', { value: 2 });

  const basePlay = Wrestler.prototype.play;
  const _q = new THREE.Quaternion();

  // Twist of a quaternion around the Y axis, in radians
  function yawTwist(q) {
    _q.set(0, q.y, 0, q.w);
    if (_q.lengthSq() < 1e-9) return 0;
    _q.normalize();
    return 2 * Math.atan2(_q.y, _q.w);
  }

  Wrestler.prototype.play = function (name, opts = {}) {
    const prevId = this.current;
    const rm = prevId && this.library.defs[prevId].rootMotion;
    if (rm && rm.mode === 'baked' && rm.endRotationY) {
      const action = this.actions[prevId];
      const finished = action.time >= action.getClip().duration - 1e-3;
      const yaw = finished ? rm.endRotationY * RAD_PER_DEG : yawTwist(this.bones.hips.quaternion);
      // 1) position, exactly as Batch 1 does it, in the old facing
      this.commitRootMotion();
      const hips = this.bones.hips;
      const rest = this.restPositions.hips;
      hips.position.x = rest.x;
      hips.position.z = rest.z; // so the Batch 1 play() finds nothing left to commit
      // 2) facing
      this.object.rotateY(yaw);
      this.object.updateMatrixWorld();
      opts = { ...opts, fade: 0 };
    }
    return basePlay.call(this, name, opts);
  };

  Wrestler.prototype.currentState = function () {
    if (!this.current) return 'standing';
    const def = this.library.defs[this.current];
    const action = this.actions[this.current];
    const done = action.time >= action.getClip().duration - 1e-3;
    return def.loop || done ? getEndState(def) : 'transition';
  };
}

const STATE_TAGS = ['lying-back', 'lying-front', 'kneeling', 'rope-lean', 'airborne-back'];

export function getEndState(def) {
  const t = (def.tags || []).find((x) => x.startsWith('ends-') && STATE_TAGS.includes(x.slice(5)));
  return t ? t.slice(5) : 'standing';
}

export function getStartState(def) {
  const t = (def.tags || []).find((x) => x.startsWith('starts-') && STATE_TAGS.includes(x.slice(7)));
  return t ? t.slice(7) : 'standing';
}

// All animation ids that can start from a given state, e.g. animationsFrom(pack.animations, 'lying-back')
export function animationsFrom(library, state) {
  return Object.values(library.defs).filter((d) => getStartState(d) === state).map((d) => d.id);
}

export { AnimationLibrary };
