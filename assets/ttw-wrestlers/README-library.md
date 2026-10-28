# TTW Wrestling Animation Library (library v3): Phases 1-4

This overlay adds a ring-aware animation library on top of the existing wrestler pack. It only adds files. `skeleton.json`, `loader.js`, `loader-ext.js`, `manifest.json`, `manifest-batch2.json`, the 20 wrestlers, the 58 batch clips and the props pack are byte-for-byte unchanged. Copy the contents of `assets/` over your existing `assets/` folder.

**What is in it**

| | |
|---|---|
| Clips | 228 new JSON animations. Phase 2 (ring): 50 ropes and apron, 31 turnbuckle, 6 ring-to-floor eliminations. Phase 3 (combat): 20 strikes, 15 reactions. Phase 4 (grappling): 19 lock-up and holds, 32 throws, 36 submissions, 17 ground, 2 lying hit reactions. Add the 58 batch clips and 5 props-pack chair clips, and the master manifest lists 291 working clips. |
| Paired moves | 53 two-person definitions in `paired/`. Phase 2 has 3: Irish whip, shove into the ropes, pull over the top rope. Phase 4 has 50: lock-up family, throws and slams, submissions with their hold loops, pins, pick-up and drag. |
| `manifest-master.json` | One index of everything. It covers batches 1-2, the props-pack clips, the new library clips, the paired moves and the planned ids for Phases 5-8 (`"status": "planned"`, no file yet). |
| `ttw-anim-runtime.js` | Additive runtime. It provides deterministic root-motion curves, `seekAnimation`, `PairedPlayer` and rope deformation helpers. |
| `viewer/index.html` | Animation Lab: browse, play, scrub and validate every clip in the ring, solo or as a pair. |
| `viewer/validate.js`, `tools/validate.mjs` | Library validator, for the browser and Node. |
| `viewer/ring-reference.json` | Ring dimensions the clips were authored against. They're the same numbers as the arena. |
| `CATALOGUE.md` | Every existing clip with its states, locations and root motion, then the planned list. |
| `tools/` | Generators (Python, numpy) and the manifest/catalogue builders. These are only needed to change or extend clips. |

## Using it in TTW

```js
import { loadPack } from './assets/ttw-wrestlers/loader.js';
import './assets/ttw-wrestlers/loader-ext.js';
import { RootMotion, PairedPlayer, ropeContacts } from './assets/ttw-wrestlers/ttw-anim-runtime.js';

const pack = await loadPack('./assets/ttw-wrestlers/manifest-master.json');
const w = pack.createWrestler('wrestler-07');
```

- `manifest-master.json` references the five chair clips as `../ttw-props/...`, so keep the props pack installed next to `ttw-wrestlers/`. Otherwise pass `loadPack(url, { animations: [...] })` with the ids you want.
- Importing the runtime patches `Wrestler.prototype`. Old clips behave exactly as before. Only clips with `rootMotion.mode: "curve"` use the new path.

## Root motion contract (library v3 clips)

Every new clip that travels declares it: `rootMotion.mode = "curve"` and `curve: [[t, x, y, z, yawDeg], ...]`. The curve is in the wrestler's **start frame**: x right, y up, -z forward, measured from where the clip started.

- **Gameplay owns the position.** In the default `"gameplay"` policy the root bone is held at zero, so the mesh always sits exactly on `wrestler.object`. Your movement code moves the object along the curve. `RootMotion.targetAt(wrestler, t)` gives the world position and yaw for any time, and it depends only on the start transform and the JSON. Server and clients compute the same answer, so it's deterministic.
- **Nothing is ever accumulated silently.** Travel only comes from declared curves, and `endOffset`, `endYaw` and `heightChange` tell you the end before the clip plays. Use that for validation on the server.
- `wrestler.autoRootMotion = true` lets the runtime move the object itself. That's fine for single player and the lab.
- `setRootMotionPolicy('visual')` plays the travel on the root bone instead (replays and previews). The object is updated when the clip ends.
- `heightChange` is non-zero for clips that change level: apron to floor is -1.16 m, floor to apron is +1.16 m, ring to top turnbuckle is +1.28 m. These match the arena: mat 1.2 m, floor 0.04 m, ropes 0.45, 0.85 and 1.25 m above the mat.
- `wrestler.seekAnimation(id, t, { start })` poses a wrestler at an exact time. Use it for late joiners, rollback and scrubbing.

## Placement: where a clip expects to be

Ring clips are authored in one of three frames and say so in `placement`:

| `placement.frame` | origin | used by |
|---|---|---|
| `rope` | middle of a rope line at mat height. x runs along the ropes, +z is into the ring, outside is z < 0 (apron edge at -0.6, floor at y -1.16) | ropes, apron, eliminations |
| `corner` | foot of a ring post. Ropes run along +x and +z, the ring is x > 0 and z > 0 | turnbuckle |
| `mat` | anywhere on open canvas | (Phase 3+) |

`placement.frameStart = [x, y, z, yawDeg]` is the clip's start in that frame. `placement.start` and `placement.end` are readable names such as `apron-facing-ring` or `perched`.

To start a rope clip at a given spot along any of the four rope sides:

```
frame origin = point on the rope line (mat height), frame yaw = yaw that faces into the ring
start position = origin + rotateY(frameYaw) * frameStart.xyz
start yaw      = frameYaw + frameStart.yaw
```

Corner clips work the same way from any of the four posts. The frame yaw is the one that maps +x and +z onto the two ropes leaving that post.

## Pose states and chaining

Every clip has `startState` and `endState`, plus `starts-*` and `ends-*` tags, so `loader-ext.js` `animationsFrom(state)` works on the new clips too. New states:

- `rope-hold`: facing the ropes, hands on the top rope
- `rope-lean`: the batch 1 state, reused exactly
- `rope-tangled`
- `rope-draped`: folded over the top rope
- `rope-hung`: chest on the middle rope, 619 position
- `rope-middle-perched`: on the middle rope, from the apron
- `apron-hold`
- `running`: the run cycle at a known phase
- `corner-hold`, `corner-climb-1`, `corner-climb-2`, `corner-top-out`
- `perched`: crouched on the top turnbuckle
- `perched-ready`: standing tall on the top turnbuckle
- `corner-seated`
- `corner-hanging`: tree of woe
- `corner-back`, `corner-slumped`
- `sitting`

Example chains:

- `ropes.whipped-into` (ends `rope-lean`) → `ropes.rebound-clothesline`
- `turnbuckle.climb-full` → `turnbuckle.prepare-jump` → `turnbuckle.jump-forward` or `turnbuckle.miss-aerial`
- `ropes.drape-over-top` → `ropes.hang-over-top` (loop) → `pair.pull-over-top-rope`

Each clip also has:

- `phases`: approach, contact, launch, traversal, flight, landing, recovery
- `interrupt.windows`: times you can cut away without a visible snap
- `startLocation` and `endLocation`: `ring`, `apron`, `floor`

## Events

The new clips use the agreed vocabulary: attack_start, hit, grab, grip_locked, lift_start, lift_complete, release, impact, land, rope_contact, rope_release, rebound, footstep, jump, apex, stun_start, recover and animation_complete. `animation_complete` is always the last event of a one-shot clip. Some events carry fields:

- `impact` has `surface` (mat, ropes, turnbuckle, floor)
- `land` has `zone` and `height` (the drop in metres)
- `hit` has `attachment`, `zone` and `reach`

Listen with `w.on('impact', fn)` as before.

## Paired moves (`paired/*.json`)

A paired move binds an attacker clip and a defender clip of equal length to **one clock**:

```js
const def = await (await fetch('assets/ttw-wrestlers/paired/irish-whip-ropes.json')).json();
const pp = new PairedPlayer(def, attackerWrestler, defenderWrestler, { anchor: { position, yaw } });
pp.on('*', (e) => game.onPairEvent(e.role, e.name, e));   // role: attacker | defender | both
pp.start(0);                 // or pp.start(elapsedSeconds) for a late joiner
// each frame: pp.update(dt)
const ends = pp.endTransforms(); // both final world positions, known before the move plays
```

| field | meaning |
|---|---|
| `attacker` / `defender` | `{ animation, startState, endState, startLocation, endLocation }` |
| `start` | `defenderOffset` and `defenderFacing` (degrees) in the attacker's start frame. The attacker is the anchor. |
| `end` | Each role's end offset and yaw, from its curve. |
| `contacts` | Time ranges where hands hold the opponent, with the attachments involved. |
| `events` | Merged timeline, each event with a `role`. |
| `phases`, `interruptible.windows` | As for single clips. Paired moves are mostly not interruptible. |
| `multiplayer` | `sync: "shared-clock"`. The server chooses the pair, the anchor and the start time, and clients only seek both clips to the same time. Both clips are deterministic, so they never drift apart. |
| `placement` | The attacker's placement, so the pair can be put in the ring the same way as a single clip. |

## Combat (Phase 3)

Strikes start and end in the batch fighting stance (`movement.idle-fight`). They're authored against an opponent standing square on, about 0.6 to 0.8 m away. Every `hit` event carries `zone` (head, body, legs), `attachment` (the striking body part) and `reach` (metres in front of the attacker), so combat can resolve the hit wherever the opponent actually is. `striking.back-elbow` has a negative reach (behind). `striking.leg-kick-combo` has two hits.

Running attacks (`striking.shoulder-block`, `striking.running-knee`) start from `running`, so they chain from the run cycle or any rebound clip. Ground strikes (`striking.stomp`, `striking.mount` → `striking.mounted-punches` loop → `striking.mount-off`, and `ground.elbow-drop`, `leg-drop`, `knee-drop`) mark their hits with `target: "ground"`. The lying opponent plays `reactions.lying-hit-back` or `reactions.lying-hit-front`.

Reactions are single-wrestler clips the game plays on `hit_received`, chosen by zone and strength:

- Head: `head-snap-left` and `head-snap-right`
- Body: `chop-sell`, `doubled-over`
- Big hits: `stagger-back-long`, `stagger-forward-long`, `spin-out-fall`, `flip-bump`, `superkick-drop`, `dropkick-fly-back`, `knee-buckle-fall`
- Loops: `bent-over-idle`, `kneeling-stunned`, `arm-hurt-loop`
- `reactions.hit-in-corner` plays from the `corner-back` state

`reactions.doubled-over` ends in **bent-over**, the set-up state for the powerbomb and fireman's carry.

## Grappling (Phase 4)

Grapples are paired moves. Each one chains from a set-up, and the next move starts exactly where the set-up ended: the paired JSON's start offset matches the set-up's end positions.

```
pair.lockup ─┬─ pair.shove-off
(both play   ├─ pair.side-headlock ──┬─ pair.headlock-takeover
 the same    │                       └─ pair.bulldog
 clip)       ├─ pair.front-facelock ─┬─ pair.vertical-suplex, pair.snap-suplex
             │                       ├─ pair.ddt
             │                       └─ pair.neckbreaker
             ├─ pair.wristlock, pair.hammerlock
             ├─ pair.hip-toss, pair.arm-drag
             └─ grappling.lockup-idle (loop), grappling.lockup-break
fighting stance ─┬─ pair.waistlock ─┬─ pair.belly-to-belly
                 │                  └─ pair.spinebuster
                 ├─ pair.body-slam, pair.chokeslam, pair.powerslam, pair.backbreaker
                 └─ (opponent's back turned) pair.rear-waistlock ─┬─ pair.german-suplex
                                                                  ├─ pair.sleeper-hold
                                                                  └─ pair.abdominal-stretch
opponent bent-over ─ pair.powerbomb, pair.fireman-carry
opponent lying-back ─ pair.figure-four, pair.sharpshooter, pair.boston-crab, pair.armbar,
                      pair.cover, pair.hook-leg-cover, pair.pick-up-opponent (→ bent-over), pair.drag-opponent
opponent lying-front ─ pair.camel-clutch, pair.crossface, pair.ankle-lock
opponent standing, back turned ─ pair.roll-up, pair.small-package
covering / pinned ─ pair.kick-out
```

**Submissions.** Each one has an apply pair (`pair.<name>`) and a looping hold pair (`pair.<name>-hold`). Both hold clips are loops with the same duration. Run the submission meter while the hold loops, then cut to a release or a getup.

**Pins.** `pair.cover` and `pair.hook-leg-cover` lock the cover at 0.7 s; start the referee count there. `pair.roll-up` and `pair.small-package` lock at 0.8 s. `pair.kick-out` breaks a cover.

The thrown wrestler always finishes in the library lying poses (`lying-back` or `lying-front`), so the batch getups (`falls.getup-back`, `falls.getup-front`) follow directly.

**Thrown bodies.** They're keyed by world orientation (where the head and the chest point) and converted to joint angles with continuity, so the body never spins the long way round between keys. The thrower's hands are pinned to points on the thrown body at every key.

## Ropes that give way (optional)

Real ropes get pushed and parted, so wrestlers in these clips overlap where the static rope would be. Every clip that touches a rope includes `ropeInteraction`. Per rope, keys `[t, s, dx, dy, dz]` give the contact point along the rope and how far the rope is pushed there. The largest push in the library is 0.18 m.

- `ropeContacts(def, t, start)` converts that to world space.
- `ropeOffsetAt(a, b, u, contacts)` bends a rope like a plucked string: zero at the posts, full offset at the contact point.

The lab does this, so you can see the effect. If your arena keeps static ropes you can ignore the field. The clips still read correctly, but expect some clipping through the ropes during crossings.

## Animation Lab

To run the Lab, serve the `assets/` folder over HTTP (for example `npx serve assets`) and open `ttw-wrestlers/viewer/index.html`.

The Lab includes:

- 20-wrestler select, category filter and search
- Play/pause, restart, loop, speed, a scrubbable timeline with event ticks and phase bands, and the duration
- Orbit and zoom, with front, side, rear, top and follow cameras
- Toggles for skeleton, mesh, root-motion path (with end marker), gameplay hitbox (turns red if the visual drifts from it), ring/ropes/turnbuckles and the visual root policy
- Two-person mode for paired moves, with a switch-roles button
- An inspector showing state, location, placement, root motion, events and interrupt windows
- A validation report listing missing assets

## Validation

```
node tools/validate.mjs            # from assets/ttw-wrestlers; writes tools/validation-report.json, exit code 1 on errors
```

It checks:

- Skeleton and bone names
- Key format and order
- Event names and times
- Root-motion declarations and curve end consistency
- Loop closure
- Joint ranges (elbows, knees)
- Paired definitions: matching durations, roles and offsets
- Duplicate motion, which catches renamed copies

Current result: 291 clips, 53 paired, 0 errors, 0 warnings.

## How the clips were checked

The generators author keys in ring coordinates with two-bone IK for hands and feet. Every clip is then sampled at 30 fps against the ring:

- Feet, knees, hands, elbows and head are checked against the mat, apron and floor.
- Limbs and torso are checked against all ropes.

An automatic repair pass inserts limb keys wherever interpolation would push a hand or foot through a surface. The per-clip results are in `tools/phase2/geometry-report.json`. Every clip was also rendered and reviewed in the lab.

**Known minor issues:**

- Elbows and hands dip 7-12 cm into the mat for a few frames in `ropes.enter-slide-under`, `ropes.enter-injured`, `submissions.sharpshooter-defender` and `submissions.boston-crab-defender`. The head does the same in `throws.hip-toss-defender` and `ground.pick-up-opponent-defender`. All of these happen while getting up or turning over.
- The automatic check covers floors and ropes. Body-to-body contact between the two wrestlers is reviewed visually, not computed, so brief limb overlaps can occur in fast throws.
- On the turnbuckle, hands and feet are placed on the ropes 0.33 m or more from the post, clear of the pads. The pads and posts themselves aren't part of the automatic check.
- Paired moves assume the wrestlers are about the same size, because hand contacts are authored on the shared skeleton. Wrestlers scaled very differently will show small gaps or overlaps at the hands.

## Regenerating

```
python tools/phase2/build-phase2.py      # Phase 2 clips + paired files (needs numpy)
python tools/phase3/build-phase3.py      # Phase 3
python tools/phase4/build-phase4.py      # Phase 4
python tools/build-master-manifest.py    # needs ../ttw-props/manifest.json
python tools/build-catalogue.py
node tools/validate.mjs
```
