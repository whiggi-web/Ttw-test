# TTW Universal Wrestler Pack, batch 2

Batch 2 only adds files. Nothing from Batch 1 is changed: `skeleton.json`, `loader.js`, `manifest.json`, `viewer.html`, `README.md`, the Batch 1 tools, wrestlers 01 and 02, and the 11 Batch 1 animations are byte-for-byte as delivered. Copy the Batch 2 files into the same `assets/ttw-wrestlers/` folder.

## What's new

| | |
|---|---|
| Wrestlers | `wrestler-03` to `wrestler-20`. The roster is now 20 (17 male, 3 female). |
| Animations | 47 new clips: 11 movement, 11 striking, 11 damage reactions, 14 falls and recovery. That's 58 in total. |
| `loader-ext.js` | Small add-on module (facing changes and pose-state helpers). |
| `manifest-batch2.json` | Full index: Batch 1 + Batch 2, plus everything still planned for Batches 3 and 4. |
| `viewer-batch2.html` | Roster Lab: any wrestler or all 20 at once, all 58 clips. |
| `tools/batch2/` | Generators for this batch. They import the Batch 1 templates without modifying them. |

Each wrestler is still 1 mesh, 1 material and 1 draw call, at 3,600 to 4,400 triangles. All 20 use the same skeleton and the same animation clips.

## Using Batch 2

```js
import { loadPack } from './assets/ttw-wrestlers/loader.js';
import './assets/ttw-wrestlers/loader-ext.js';            // once, after loader.js

const pack = await loadPack('./assets/ttw-wrestlers/manifest-batch2.json');
const w = pack.createWrestler('wrestler-13');
w.play('striking.roundhouse');
w.on('hit', (e) => combat.resolveHit(w, e.event));
```

Everything else works exactly as in Batch 1 (`play`, `on`, `update`, `getRootSpeed`, attachments, root motion modes).

Pointing at the Batch 1 `manifest.json` still loads only Batch 1, so existing code keeps working until you switch. When Batch 2 is approved you can rename `manifest-batch2.json` to `manifest.json`, or keep loading it by name.

## loader-ext.js

1. **Facing changes.** A few clips end facing a different way:
   - `movement.turn-180` (180)
   - `falls.roll-to-back` and `falls.roll-to-front` (180)
   - `falls.fall-left` (-90) and `falls.fall-right` (+90)

   Their `rootMotion` has `endRotationY`. When the next clip starts, the extension moves the wrestler by the hips' offset (as Batch 1 does) and also turns the wrestler's `object`, so the next clip lines up. If one of these clips is cut short, it turns the wrestler by however far the hips had actually turned.
2. **Pose states** from animation tags:
   - `getStartState(def)` and `getEndState(def)` read the state a clip starts from and ends in.
   - `animationsFrom(pack.animations, 'lying-back')` lists the clips that can start from a state.
   - `wrestler.currentState()` returns the state of the current clip, or `transition` while a one-shot clip is still playing.
   - States are `standing`, `lying-back`, `lying-front`, `kneeling`, `rope-lean` and `airborne-back`.

Without the extension, every clip still plays. The only thing lost is the facing change after those five clips.

## Roster

| ID | Name | | Look |
|---|---|---|---|
| 01 | Rex Calloway | M | red mohawk, goatee, red trunks, white boots, elbow pads (batch 1) |
| 02 | Nova Reyes | F | ponytail, teal singlet, full tights (batch 1) |
| 03 | Marcus Vane | M | bald, full beard, black tights, gold trim, armbands |
| 04 | Kenji Arata | M | topknot, white trunks, red kneepads and boots |
| 05 | Diego Fuego | M | red and gold mask, red tights, gold boots |
| 06 | Tank Okafor | M | buzz cut, moustache, blue fight shorts, heavier build |
| 07 | Silas Crowe | M | long black hair, white face paint, dark purple singlet |
| 08 | Jett Lennox | M | spiky blond hair, shades, neon green trunks |
| 09 | Ivy Hart | F | red bob, purple singlet, bare legs, purple boots |
| 10 | Bruno Kael | M | afro, goatee, orange tights, elbow pads |
| 11 | Hollis Grant | M | slicked grey hair, horseshoe moustache, brown trunks, tan boots |
| 12 | Ravi Sen | M | buzz cut, teal fight shorts, armbands |
| 13 | Axel Storm | M | long blond hair, beard, electric blue tights |
| 14 | Kai Moana | M | long dark hair, green trunks |
| 15 | Zeke Malone | M | blue mohawk, shades, black and blue tights |
| 16 | Luna Vega | F | two braids, face paint, black and silver bodysuit |
| 17 | Otis Brand | M | bald, moustache, red singlet, heavier build |
| 18 | Felix Dorn | M | slicked black hair, white and gold tights |
| 19 | Ox Barrow | M | buzz cut, full beard, olive fight shorts |
| 20 | Nico Strand | M | spiky red hair, goatee, yellow trunks, elbow pads |

Every wrestler is the same height. Build factors only vary a few percent, so contact points and paired moves line up on everyone.

## Animations

Every file has the Batch 1 fields (`id`, `name`, `category`, `duration`, `loop`, `skeleton`, `events`, `rootMotion`, `tags`, `tracks`) plus `"batch": 2`.

**Movement:**

| Animation | Duration | Movement |
|---|---|---|
| idle-fight | 1.0 s loop | on the spot |
| walk-cocky | 1.2 s loop | 1.2 m/s |
| walk-injured | 1.6 s loop | 0.8 m/s, limping, holding the ribs |
| sprint | 0.5 s loop | 6.5 m/s |
| backpedal | 1.0 s loop | 1.2 m/s backwards (+Z) |
| sidestep-left, sidestep-right | 0.8 s loop | 1.0 m/s along -X or +X |
| turn-180 | 0.7 s | ends facing backwards |
| stumble-forward | 0.95 s | 0.5 m |
| stumble-backward | 0.95 s | 0.45 m |
| stagger-move | 1.4 s loop | 0.7 m/s |

**Striking.** Each strike starts and ends in the guard and fires `hit` with the contact point, zone and reach:

| Animation | Hit at | Contact | Zone | Reach |
|---|---|---|---|---|
| jab | 0.15 s | left hand | head | 0.7 m |
| hook-right, hook-left | 0.32 s | right or left hand | head | 0.6 m |
| uppercut | 0.32 s | right hand | head | 0.5 m |
| body-punch | 0.28 s | right hand | body | 0.7 m |
| low-kick | 0.30 s | right shin | legs | 0.9 m |
| roundhouse | 0.42 s | right foot | head | 1.1 m |
| knee | 0.28 s | right knee | body | 0.5 m |
| elbow | 0.26 s | right elbow | head | 0.45 m |
| clothesline | 0.40 s | right forearm | head | 0.8 m |
| double-axe | 0.45 s | both hands | head | 0.6 m |

The clothesline charges forward using `speedCurve`.

**Damage reactions.** Each fires `hit_received` at 0 s. The ones that return to standing also fire `recover`.
- hit-front-body, hit-back-body, hit-left, hit-right
- hit-kick
- hit-clothesline: flips onto the back and ends lying there
- hit-chair
- stunned, dizzy: both loop
- knocked-back: driven 0.9 m back
- stumble-recover

**Falls and recovery:**
- Falls: fall-forward, fall-left, fall-right, fall-spear (driven 1.25 m back), fall-slam (starts held horizontal at waist height)
- Collapse to the knees: collapse-knees (ends kneeling)
- Lying loops: lie-back, lie-front, knockout
- Rolls: roll-to-back, roll-to-front
- Getting up: getup-front, getup-injured, quick-recovery (a kip-up)
- Events: `land` on impact, plus `jump` and `recover` where they apply

### How clips chain

| Ends in | Clips | Can be followed by |
|---|---|---|
| lying on the back | fall-backward (batch 1), fall-left, fall-right, fall-spear, fall-slam, hit-clothesline, roll-to-back | getup-back (batch 1), getup-injured, quick-recovery, roll-to-front, lie-back, knockout |
| face down | fall-forward, roll-to-front | getup-front, roll-to-back, lie-front |
| kneeling | collapse-knees | any standing clip (crossfade) |

"Lying on the back" always means the same pose and placement, so any clip in the first row can be followed by any clip in the last column.

## Viewer

Serve the folder and open `viewer-batch2.html`. You can:
- pick any wrestler, or show all 20 in a grid playing the same clip (a quick check that every clip works on every body)
- play, pause, scrub and change speed
- watch the event ticker
- toggle root motion, the skeleton and the attachment points
- pose any joint by hand

Clips that start lying down, kneeling or on the ropes jump to that pose first.

## Next batches

`manifest-batch2.json` lists the remaining 55 animations and the two props as `planned`, each with its batch number:
- **Batch 3:** ropes, aerial, taunts
- **Batch 4:** grappling paired moves (attacker and receiver files using `pairedMoveSchema`), weapons, and the folding chair and table props
