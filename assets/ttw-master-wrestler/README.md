# TTW Master Wrestler

The first TTW wrestler and the template for the other 19. Three.js r160, JSON only, no textures, no model files, no animation libraries.

- **1 SkinnedMesh, 1 geometry, 1 material, 1 draw call** per wrestler (colours are vertex colours)
- About **4,500 triangles**
- **18 bones**, **7 attachment points**
- 5 animations: idle, walk, run, punch, fall

## Files

| File | What it is |
|---|---|
| `wrestler.json` | Appearance only: palette, material settings, body parts and their skin weights. This is the file that changes per wrestler. |
| `skeleton.json` | The shared `ttw-humanoid` skeleton: bone hierarchy, rest offsets, attachment points, joint limits. Identical for every wrestler. |
| `animations/*.json` | Keyframe animations for the shared skeleton. Reusable on every wrestler. |
| `loader.js` | Builds the skinned mesh, skeleton, attachments and AnimationClips. ES module, imports `three`. |
| `preview.html` | Test viewer: orbit, zoom, skeleton overlay, attachment markers, play and pause clips, reset pose, per-joint rotation sliders. |

## Conventions

- Units are metres. Y is up. **Forward is local -Z**, so the character's right is +X.
- Feet sit on Y=0 in the neutral pose. Standing height is 1.9 m.
- **Every bone has an identity rest rotation.** The bind pose is the neutral reference pose (relaxed A-pose, arms 25 degrees out). So a bone rotation of `[0,0,0]` always means "neutral", on every wrestler.
- Rotations in JSON are **degrees, Euler order XYZ, local to the bone** (relative to the neutral pose).
- Positions in animation tracks are **offsets from the bone's rest position** (`positionMode: offsetFromRest`).

Handy rotation signs (character facing -Z):

| Joint | +X | +Y | +Z |
|---|---|---|---|
| upper legs, upper arms | swing forward | twist | right limb: out to the side. left limb: in toward body |
| lower legs | (knee bends with -X) | | |
| forearms | elbow bends with +X | | |
| feet | toes up | | |
| hips, spine, chest, neck, head | lean back (forward is -X) | turn to the character's left | lean to the character's left |

Mirroring a pose left to right: swap `left`/`right` bone names, keep X, negate Y and Z. For position offsets, negate X.

## Skeleton

```
root
└── hips
    ├── spine
    │   └── chest
    │       ├── neck
    │       │   └── head
    │       ├── leftUpperArm ── leftForearm ── leftHand
    │       └── rightUpperArm ── rightForearm ── rightHand
    ├── leftUpperLeg ── leftLowerLeg ── leftFoot
    └── rightUpperLeg ── rightLowerLeg ── rightFoot
```

`root` sits at the feet (origin). `hips` is the centre of mass bone and the one that carries vertical motion in the clips. No finger, toe, jaw or eye bones.

## Attachment points

Named `Object3D`s parented to bones, so they follow every animation. Find them with `wrestler.attachments.<name>` or `wrestler.object.getObjectByName(name)`.

| Name | Bone | Position |
|---|---|---|
| `leftHandGrip` | leftHand | centre of the left fist |
| `rightHandGrip` | rightHand | centre of the right fist |
| `neckGrip` | neck | middle of the neck |
| `upperTorso` | chest | front of the chest, sternum height |
| `waist` | hips | belt line, centre |
| `leftShoulder` | chest | top of the left shoulder |
| `rightShoulder` | chest | top of the right shoulder |

## Integrating into TTW

Copy the `ttw-master-wrestler` folder into the game's assets. Make sure the page has an import map for `three` pointing at r160 (or that your bundler resolves `three`).

```js
import * as THREE from 'three';
import { loadWrestler } from './assets/ttw-master-wrestler/loader.js';

const wrestler = await loadWrestler('./assets/ttw-master-wrestler/wrestler.json');
scene.add(wrestler.object);

// Place and turn the wrestler with wrestler.object. Never rebuild geometry to move or animate.
wrestler.object.position.set(2, 0, 0);
wrestler.object.rotation.y = Math.PI / 2;

wrestler.play('idle');                       // default 0.2 s crossfade
wrestler.play('walk', { fade: 0.25 });
wrestler.play('punch', { timeScale: 1.2 });

// game loop
wrestler.update(delta);
```

If the JSON is already bundled, skip the fetches: `buildWrestler(wrestlerJson, skeletonJson, { idle, walk, run, punch, fall })`.

### Wrestler API

| Member | Purpose |
|---|---|
| `object` | Group to add to the scene, move and rotate. Mixer root. |
| `mesh` | The SkinnedMesh (shadows on by default). |
| `bones` | `{ hips, chest, rightForearm, ... }` THREE.Bone lookup. |
| `attachments` | The seven named grip/anchor transforms. |
| `mixer`, `actions`, `clips` | Standard THREE.AnimationMixer, AnimationActions and AnimationClips. |
| `play(name, { fade, timeScale, restart })` | Start a clip, crossfading from the current one. |
| `stop()`, `setPaused(bool)`, `update(dt)` | Playback control. |
| `resetPose()` | Stop everything and return to the neutral pose. |
| `setJointRotation(bone, x, y, z)` | Pose a joint by hand in degrees. |
| `getAttachmentWorld(name)` | World matrix of an attachment point. |
| `addAnimation(name, json)` | Register another clip at runtime. |
| `dispose()` | Free GPU resources. |

### Locomotion

Walk and run are **in place**. Each file has `rootMotion.speed` in metres per second along local -Z (walk 1.5, run 4.0). Move `wrestler.object` at that speed while the clip plays and the feet stay planted. Scale `timeScale` and speed together if you change gait speed.

### Events

Clips can carry timed events, read from `clip.userData.events`:
- `punch`: `hit` at 0.30 s, on `rightHandGrip`
- `fall`: `impact` at 0.70 s

### Performance

- Each wrestler is one draw call. Twenty wrestlers on screen is twenty draw calls.
- Clips are built once and cached per skeleton, so every wrestler shares the same AnimationClip objects.
- The mesh uses a fixed bounding sphere (radius 2.4 m) so lifts and falls are never culled by mistake.
- On low-end phones, turn off `castShadow` on wrestlers outside the ring.

## Animation file format

```json
{
  "name": "walk",
  "duration": 1.0,
  "loop": true,
  "interpolation": "smooth",
  "sampleRate": 30,
  "rotationUnits": "degrees",
  "positionMode": "offsetFromRest",
  "rootMotion": { "mode": "inPlace", "speed": 1.5, "direction": [0, 0, -1] },
  "events": [],
  "tracks": {
    "rightUpperLeg": { "rotation": [[0, 26, 0, 0], [0.25, 2, 0, 0], [0.5, -20, 0, 0]] },
    "hips": { "position": [[0, 0, -0.035, 0], [0.25, 0, 0.012, 0]] }
  }
}
```

- Each key is `[time, x, y, z]`.
- `interpolation`: `smooth` (Catmull-Rom through the keys, resampled at `sampleRate`, wraps on looping clips), `linear` or `step`.
- Bones without a track hold the neutral pose, so every clip is a complete pose and can play on its own.
- `loop: false` clips hold their last frame (`clampWhenFinished`).

## Paired moves (planned, not implemented)

The rig is set up for synchronised attacker and receiver animations:

1. Both wrestlers share one skeleton, so a move is two clip files, for example `chokeslam.attacker.json` and `chokeslam.receiver.json`, with the same `duration`.
2. Pick a world-space **anchor** for the move (for example the attacker's position and facing at the start). Put both `wrestler.object`s on that anchor, each with its own fixed offset and facing stored in the move file.
3. Start both actions on the same frame. Because both clips use the same time base, they stay in sync.
4. Author the receiver's displacement (being lifted, thrown, dropped) as `root` and `hips` position and rotation tracks relative to its own start. The `root` bone is free for this, since normal locomotion moves `wrestler.object` instead.
5. Use the attachment points to author and verify contact. For example, during a chokeslam the receiver's `neckGrip` should sit on the attacker's `rightHandGrip`. `getAttachmentWorld()` gives you both for a debug check.

## Making the other 19 wrestlers

Keep `skeleton.json` and `animations/` exactly as they are. For each new wrestler, copy `wrestler.json` and change:
- `id` and `displayName`
- `palette` (skin, trunks, boots, hair, trim)
- part sizes (`r`, `rx`, `rz`, `radii`) for build: thicker arms, bigger gut, slimmer waist
- head parts: hair, beard and brow shapes, or swap the beard for a mask
- optional extra parts (kneepads, elbow pads, mask, tassels), each with a bone weight map

Do not move joints. Body shape changes go in the part sizes, so every animation and every paired move keeps working on every wrestler.

### Part types in `wrestler.json`

- `tube`: a skinned limb or torso through a list of points. Each point has a position, radius (`r`, or `rx` and `rz` for an oval), a colour and a skin weight map. Weights blend between points, which is what makes elbows, knees, shoulders and the waist bend smoothly.
- `ellipsoid`: a sphere with per-axis radii, bound to one weight map (muscles, head, hands, boots).
- `box`: boot soles and other flat details.
- `mirror: true` writes the part once for the right side and generates the left copy.
- Point positions can be `[x, y, z]`, `{ "joint": "rightForearm", "offset": [...] }` or `{ "between": ["rightForearm", "rightHand"], "t": 0.5 }`. `"rightHand:tail"` means the end of the hand bone.
