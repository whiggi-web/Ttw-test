# TTW Universal Wrestler Pack, batch 1

This batch has the universal skeleton, 2 of the 20 wrestlers, 11 core animations, the loader, a manifest and a test viewer. The other 18 wrestlers, the remaining animation categories and the chair and table props come in later batches. The manifest already lists all of them as `planned`, with the ids and file paths they will use.

Built for Three.js r160. Everything is JSON plus one ES module, with no textures, model files or animation libraries.

## What's in batch 1

| | |
|---|---|
| Skeleton | `ttw-humanoid`: 18 bones, 10 attachment points, joint limits. Same as the master wrestler. |
| Wrestlers | `wrestler-01` Rex Calloway (male): red mohawk, goatee, red trunks, white boots, elbow pads. `wrestler-02` Nova Reyes (female): dark ponytail, teal singlet, full tights, teal boots. |
| Cost per wrestler | 1 SkinnedMesh, 1 material, **1 draw call**, about 4,000 to 4,200 triangles |
| Animations | movement: idle, walk, run. striking: punch, kick. reactions: hit-front, hit-back. falls: fall-backward, getup-back. ropes: rope-lean, rope-rebound. |

## Folder

```
assets/ttw-wrestlers/
  skeleton.json            universal skeleton (never changes per wrestler)
  manifest.json            every wrestler, animation, prop and event, ready and planned
  loader.js                builds wrestlers, shared animation library, events, root motion
  viewer.html              test viewer (serve the folder; it fetches the JSON)
  roster/wrestler-XX.json  appearance only
  animations/<category>/<name>.json
  props/                   empty in batch 1
  tools/                   Python generators for the roster, animations and manifest
```

## Using it in TTW

```js
import { loadPack } from './assets/ttw-wrestlers/loader.js';

const pack = await loadPack('./assets/ttw-wrestlers/manifest.json');
const rex  = pack.createWrestler('wrestler-01');
const nova = pack.createWrestler('wrestler-02');
scene.add(rex.object, nova.object);

rex.play('movement.idle');           // the short name 'idle' also works
rex.on('hit', (e) => combat.resolveHit(rex, e.event));   // events report only; the game decides what happens
rex.on('finished', (e) => ai.onAnimationDone(rex, e.animation));

// game loop
rex.update(delta);
nova.update(delta);
```

`loadPack(url, { wrestlers: ['wrestler-01'], animations: [...] })` loads only what a scene needs. `createPack({ skeleton, wrestlers, animations })` takes JSON that's already bundled.

Several instances of the same wrestler share one geometry. Every wrestler shares the same `AnimationClip` objects.

### Wrestler API

| Member | Purpose |
|---|---|
| `object` | Group to add to the scene, move and rotate. Never rebuild geometry to move or animate. |
| `play(id, { fade, timeScale, restart, startTime })` | Crossfade to an animation. |
| `on(eventName, fn)` / `on('*', fn)` | Animation events. Returns an unsubscribe function. |
| `update(dt)` | Advance the mixer and fire the events crossed this frame. |
| `getRootSpeed()` | Forward speed in m/s that the current clip expects (see root motion). |
| `commitRootMotion()` | Apply a baked clip's travel now. Runs automatically on the next `play()`. |
| `autoRootMotion` | `false` by default. When `true`, the loader moves the wrestler itself (the viewer uses this). |
| `attachments` | Named transforms: `leftHandGrip`, `rightHandGrip`, `neckGrip`, `upperTorso`, `waist`, `leftShoulder`, `rightShoulder`, `propRightHand`, `propLeftHand`, `back`. |
| `attach(object3d, name)` | Parent a prop to an attachment point. |
| `getAttachmentWorld(name)` | World matrix, for grapple alignment and hit checks. |
| `setJointRotation`, `getJointRotation`, `resetPose`, `stop`, `setPaused`, `dispose` | Debug and control. |

`pack.animations.addMirrored('striking.kick', 'striking.kick-left')` builds a left-side version of any animation at runtime.

## Conventions

- Metres, Y up, **forward is -Z**, feet on Y=0, height 1.9 m.
- Every bone has an identity rest rotation, so `[0,0,0]` is the neutral pose on every wrestler.
- Animation rotations are degrees, Euler XYZ, local to the bone. Positions are offsets from rest.
- **Rope animations assume the ropes are behind the wrestler** (+Z), with the top rope about 1.25 m up and about 0.4 m behind the feet. That matches the arena's rope heights above the mat. Turn the wrestler to face away from the ropes before playing them.

## Root motion

Each animation states how it moves:

| Mode | Used by | What the game does |
|---|---|---|
| `none` | idle, punch, kick, rope-lean | Nothing. |
| `inPlace` | walk (1.5 m/s), run (4.0 m/s) | Move the wrestler forward at `speed` while it plays. |
| `speedCurve` | rope-rebound | Move forward at `getRootSpeed()`. It's 0 while sinking into the ropes, then ramps to 4 m/s. |
| `baked` | hit-front, hit-back, fall-backward, getup-back | Nothing. The hips travel inside the clip, and on the next `play()` the loader moves `object` by that distance (`endOffset`), so the next clip starts in the right spot. A baked clip cuts to the next one with no crossfade. |

## Chaining

- `falls.fall-backward` ends lying flat on the back. `falls.getup-back` starts from exactly that pose.
- `ropes.rope-lean` ends leaning on the ropes. `ropes.rope-rebound` starts from that pose and ends on the run cycle's first frame. Its `release` event names `movement.run` as the next clip.
- Clips tagged `starts-*` and `ends-*` in the manifest show which ones connect.

## Events

Each event has a time in seconds and optional fields. The loader emits them as the playhead crosses them, including on looping clips and at time 0.

| Event | In batch 1 |
|---|---|
| `hit` | punch at 0.30 s (`rightHandGrip`, head, 0.75 m reach). kick at 0.34 s (`rightFoot`, body, 1.0 m reach). |
| `hit_received` | hit-front and hit-back at 0.00 s |
| `recover` | hit-front and hit-back at 0.60 s. getup-back at 1.55 s. |
| `land` | fall-backward at 0.70 s |
| `rope_contact` | rope-lean at 0.30 s. rope-rebound at 0.00 s. |
| `rebound` | rope-rebound at 0.32 s |
| `release` | rope-rebound at 0.80 s, `next: movement.run` |
| `grab`, `jump`, `weapon_impact`, `table_break` | defined in the manifest, used in later batches |
| `finished` | emitted by the loader when any non-looping clip ends |

Animations never change health, collision or game state.

## Paired moves (next batches)

Two-character moves use two normal animation files with the same duration, `<move>.attacker.json` and `<move>.receiver.json`. A manifest entry describes the pairing:

```json
{
  "id": "grappling.body-slam", "duration": 1.6, "anchor": "attacker",
  "receiverOffset": { "position": [0, 0, -0.55], "rotationY": 180 },
  "contacts": [{ "time": 0.2, "attacker": "rightHandGrip", "receiver": "waist" }],
  "events": [{ "time": 0.2, "name": "grab" }, { "time": 1.15, "name": "land", "role": "receiver" }]
}
```

To play one:
1. Put the receiver at `receiverOffset` in the attacker's local frame.
2. Start both clips on the same frame.
3. `contacts` lists attachment pairs that should touch at a given time. Use them for debug checks with `getAttachmentWorld()`.

`manifest.pairedMoveSchema` has the full example.

## Adding wrestlers

Edit `ROSTER` in `tools/build-roster.py`, then run these from `assets/ttw-wrestlers`:

```
python tools/build-roster.py
python tools/build-manifest.py
```

Each wrestler picks a palette, build factors, outfit (`trunks` or `singlet`), hair, face and extras. Joints come from the skeleton and never move, so every animation keeps working. Animations come from `tools/build-animations.py` in the same way.

## Viewer

Serve the folder (for example `python -m http.server` in `assets/ttw-wrestlers`) and open `viewer.html`. You can:
- switch between Rex, Nova or both
- play any clip, pause, scrub the timeline and change speed
- reset the pose
- toggle root motion, a rope set, the skeleton and the attachment points
- pose any joint with sliders

An event ticker shows each event as it fires. Chained clips (getup, rope rebound) play their lead-in pose first.
