# TTW animation catalogue

Generated from `manifest-master.json`. **291 clips exist as JSON files**, 53 paired moves, 113 entries are planned only (no file yet).

Columns: id, length in seconds (L = loop), pose state at start and end, where it starts and ends, root motion mode, origin.

## eliminations (6)

| id | name | s | states | location | root | from |
|---|---|---|---|---|---|---|
| `eliminations.apron-fall-back` | Fall backwards off the apron | 1.4 | standing → lying-back | apron → floor | curve | library v3, phase 2 |
| `eliminations.apron-fall-forward` | Fall forwards off the apron | 1.4 | standing → lying-front | apron → floor | curve | library v3, phase 2 |
| `eliminations.fall-through-ropes` | Stumble through the ropes to the floor | 1.8 | standing → lying-back | ring → floor | curve | library v3, phase 2 |
| `eliminations.knocked-through-ropes` | Knocked backwards through the ropes | 1.6 | standing → lying-back | ring → floor | curve | library v3, phase 2 |
| `eliminations.thrown-over-top` | Thrown over the top rope | 1.7 | standing → lying-front | ring → floor | curve | library v3, phase 2 |
| `eliminations.thrown-through-middle` | Thrown through the middle ropes | 1.5 | standing → lying-front | ring → floor | curve | library v3, phase 2 |

## falls (16)

| id | name | s | states | location | root | from |
|---|---|---|---|---|---|---|
| `falls.collapse-knees` | Collapse to knees | 1.2 | standing → standing | ring → ring | none | batch 2 |
| `falls.fall-backward` | Fall backwards | 1.8 | standing → standing | ring → ring | baked | batch 1 |
| `falls.fall-forward` | Fall forwards | 1.5 | standing → standing | ring → ring | baked | batch 2 |
| `falls.fall-left` | Fall sideways, left | 1.6 | standing → standing | ring → ring | baked | batch 2 |
| `falls.fall-right` | Fall sideways, right | 1.6 | standing → standing | ring → ring | baked | batch 2 |
| `falls.fall-slam` | Fall after body slam | 1.6 | standing → standing | ring → ring | none | batch 2 |
| `falls.fall-spear` | Fall after spear | 1.4 | standing → standing | ring → ring | baked | batch 2 |
| `falls.getup-back` | Get up from back | 2.0 | standing → standing | ring → ring | baked | batch 1 |
| `falls.getup-front` | Get up from stomach | 2.0 | standing → standing | ring → ring | baked | batch 2 |
| `falls.getup-injured` | Get up slowly, injured | 3.4 | standing → standing | ring → ring | baked | batch 2 |
| `falls.knockout` | Knockout idle | 4.0 L | standing → standing | ring → ring | none | batch 2 |
| `falls.lie-back` | Lie on back | 3.0 L | standing → standing | ring → ring | none | batch 2 |
| `falls.lie-front` | Lie face down | 3.0 L | standing → standing | ring → ring | none | batch 2 |
| `falls.quick-recovery` | Quick recovery | 1.1 | standing → standing | ring → ring | baked | batch 2 |
| `falls.roll-to-back` | Roll onto back | 1.1 | standing → standing | ring → ring | baked | batch 2 |
| `falls.roll-to-front` | Roll onto stomach | 1.1 | standing → standing | ring → ring | baked | batch 2 |

## grappling (19)

| id | name | s | states | location | root | from |
|---|---|---|---|---|---|---|
| `grappling.front-facelock-attacker` | Apply a front facelock | 0.85 | lockup → facelock-hold | ring → ring | curve | library v3, phase 4 |
| `grappling.front-facelock-defender` | Caught in a front facelock | 0.85 | lockup → facelocked | ring → ring | curve | library v3, phase 4 |
| `grappling.hammerlock-attacker` | Apply a hammerlock | 1.2 | lockup → hammerlock-hold | ring → ring | curve | library v3, phase 4 |
| `grappling.hammerlock-defender` | Caught in a hammerlock | 1.2 | lockup → hammerlocked | ring → ring | curve | library v3, phase 4 |
| `grappling.headlock-takeover-attacker` | Headlock takeover | 1.2 | headlock-hold → ground-headlock | ring → ring | curve | library v3, phase 4 |
| `grappling.headlock-takeover-defender` | Taken over by the headlock | 1.2 | headlocked → lying-back | ring → ring | curve | library v3, phase 4 |
| `grappling.lockup` | Collar-and-elbow lock-up | 1.0 | standing → lockup | ring → ring | curve | library v3, phase 4 |
| `grappling.lockup-break` | Break the lock-up | 0.8 | lockup → standing | ring → ring | curve | library v3, phase 4 |
| `grappling.lockup-idle` | Lock-up struggle (loop) | 2.0 L | lockup → lockup | ring → ring | curve | library v3, phase 4 |
| `grappling.rear-waistlock-attacker` | Rear waistlock | 1.0 | standing → rear-lock-hold | ring → ring | curve | library v3, phase 4 |
| `grappling.rear-waistlock-defender` | Grabbed from behind | 1.0 | standing → rear-locked | ring → ring | none | library v3, phase 4 |
| `grappling.shove-off-attacker` | Shove out of the lock-up | 1.1 | lockup → standing | ring → ring | curve | library v3, phase 4 |
| `grappling.shove-off-defender` | Shoved out of the lock-up | 1.1 | lockup → standing | ring → ring | curve | library v3, phase 4 |
| `grappling.side-headlock-attacker` | Apply a side headlock | 0.9 | lockup → headlock-hold | ring → ring | curve | library v3, phase 4 |
| `grappling.side-headlock-defender` | Caught in a side headlock | 0.9 | lockup → headlocked | ring → ring | none | library v3, phase 4 |
| `grappling.waistlock-attacker` | Shoot in for a body lock | 0.9 | standing → body-lock-hold | ring → ring | curve | library v3, phase 4 |
| `grappling.waistlock-defender` | Caught in a body lock | 0.9 | standing → body-locked | ring → ring | curve | library v3, phase 4 |
| `grappling.wristlock-attacker` | Apply a wristlock | 1.0 | lockup → wristlock-hold | ring → ring | curve | library v3, phase 4 |
| `grappling.wristlock-defender` | Caught in a wristlock | 1.0 | lockup → wristlocked | ring → ring | curve | library v3, phase 4 |

## ground (17)

| id | name | s | states | location | root | from |
|---|---|---|---|---|---|---|
| `ground.cover-attacker` | Cover | 1.3 | standing → covering | ring → ring | curve | library v3, phase 4 |
| `ground.cover-defender` | Cover (pinned) | 1.3 | lying-back → pinned | ring → ring | none | library v3, phase 4 |
| `ground.drag-opponent-attacker` | Drag a downed opponent | 2.4 | standing → standing | ring → ring | curve | library v3, phase 4 |
| `ground.drag-opponent-defender` | Dragged by the feet | 2.4 | lying-back → lying-back | ring → ring | curve | library v3, phase 4 |
| `ground.elbow-drop` | Elbow drop | 1.5 | standing → lying-back | ring → ring | curve | library v3, phase 4 |
| `ground.hook-leg-cover-attacker` | Hooked-leg cover | 1.3 | standing → covering | ring → ring | curve | library v3, phase 4 |
| `ground.hook-leg-cover-defender` | Hooked-leg cover (pinned) | 1.3 | lying-back → pinned | ring → ring | none | library v3, phase 4 |
| `ground.kick-out-attacker` | Thrown off the pin | 1.3 | covering → kneeling | ring → ring | curve | library v3, phase 4 |
| `ground.kick-out-defender` | Kick out of the pin | 1.3 | pinned → lying-back | ring → ring | none | library v3, phase 4 |
| `ground.knee-drop` | Knee drop | 1.4 | standing → standing | ring → ring | curve | library v3, phase 4 |
| `ground.leg-drop` | Leg drop | 1.5 | standing → sitting | ring → ring | curve | library v3, phase 4 |
| `ground.pick-up-opponent-attacker` | Pick up a downed opponent | 1.8 | standing → standing | ring → ring | curve | library v3, phase 4 |
| `ground.pick-up-opponent-defender` | Hauled to the feet | 1.8 | lying-back → bent-over | ring → ring | curve | library v3, phase 4 |
| `ground.roll-up-attacker` | Roll-up | 1.6 | standing → rolling-up | ring → ring | curve | library v3, phase 4 |
| `ground.roll-up-defender` | Roll-up (pinned) | 1.6 | standing → rolled-up | ring → ring | curve | library v3, phase 4 |
| `ground.small-package-attacker` | Small package | 1.6 | standing → rolling-up | ring → ring | curve | library v3, phase 4 |
| `ground.small-package-defender` | Small package (pinned) | 1.6 | standing → rolled-up | ring → ring | curve | library v3, phase 4 |

## movement (14)

| id | name | s | states | location | root | from |
|---|---|---|---|---|---|---|
| `movement.backpedal` | Backpedal | 1.0 L | standing → standing | ring → ring | inPlace | batch 2 |
| `movement.idle` | Idle | 2.4 L | standing → standing | ring → ring | none | batch 1 |
| `movement.idle-fight` | Idle, fighting stance | 1.0 L | standing → standing | ring → ring | none | batch 2 |
| `movement.run` | Run | 0.64 L | standing → standing | ring → ring | inPlace | batch 1 |
| `movement.sidestep-left` | Sidestep left | 0.8 L | standing → standing | ring → ring | inPlace | batch 2 |
| `movement.sidestep-right` | Sidestep right | 0.8 L | standing → standing | ring → ring | inPlace | batch 2 |
| `movement.sprint` | Sprint | 0.5 L | standing → standing | ring → ring | inPlace | batch 2 |
| `movement.stagger-move` | Stagger while moving | 1.4 L | standing → standing | ring → ring | inPlace | batch 2 |
| `movement.stumble-backward` | Stumble backward | 0.95 | standing → standing | ring → ring | baked | batch 2 |
| `movement.stumble-forward` | Stumble forward | 0.95 | standing → standing | ring → ring | baked | batch 2 |
| `movement.turn-180` | Turn around | 0.7 | standing → standing | ring → ring | baked | batch 2 |
| `movement.walk` | Walk | 1.0 L | standing → standing | ring → ring | inPlace | batch 1 |
| `movement.walk-cocky` | Walk, cocky | 1.2 L | standing → standing | ring → ring | inPlace | batch 2 |
| `movement.walk-injured` | Walk, injured | 1.6 L | standing → standing | ring → ring | inPlace | batch 2 |

## reactions (30)

| id | name | s | states | location | root | from |
|---|---|---|---|---|---|---|
| `reactions.arm-hurt-loop` | Hurt arm (loop) | 2.4 L | standing → standing | ring → ring | none | library v3, phase 3 |
| `reactions.bent-over-idle` | Bent over, winded (loop) | 2.4 L | bent-over → bent-over | ring → ring | curve | library v3, phase 3 |
| `reactions.chop-sell` | Sell a chest chop | 1.4 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `reactions.dizzy` | Dizzy | 1.6 L | standing → standing | ring → ring | none | batch 2 |
| `reactions.doubled-over` | Doubled over | 1.0 | standing → bent-over | ring → ring | curve | library v3, phase 3 |
| `reactions.dropkick-fly-back` | Blasted back by a dropkick | 1.4 | standing → lying-back | ring → ring | curve | library v3, phase 3 |
| `reactions.flip-bump` | Flip bump | 1.3 | standing → lying-front | ring → ring | curve | library v3, phase 3 |
| `reactions.head-snap-left` | Head snapped to the left | 1.05 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `reactions.head-snap-right` | Head snapped to the right | 1.05 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `reactions.hit-back` | Hit reaction, back | 0.75 | standing → standing | ring → ring | baked | batch 1 |
| `reactions.hit-back-body` | Hit from behind, body | 0.8 | standing → standing | ring → ring | baked | batch 2 |
| `reactions.hit-chair` | Hit by chair | 1.1 | standing → standing | ring → ring | baked | batch 2 |
| `reactions.hit-clothesline` | Hit by clothesline | 1.4 | standing → standing | ring → ring | baked | batch 2 |
| `reactions.hit-front` | Hit reaction, front | 0.75 | standing → standing | ring → ring | baked | batch 1 |
| `reactions.hit-front-body` | Hit from front, body | 0.8 | standing → standing | ring → ring | baked | batch 2 |
| `reactions.hit-in-corner` | Hit in the corner | 1.1 | corner-back → corner-back | ring → ring | curve | library v3, phase 3 |
| `reactions.hit-kick` | Hit by kick | 0.95 | standing → standing | ring → ring | baked | batch 2 |
| `reactions.hit-left` | Hit from left | 0.75 | standing → standing | ring → ring | baked | batch 2 |
| `reactions.hit-right` | Hit from right | 0.75 | standing → standing | ring → ring | baked | batch 2 |
| `reactions.knee-buckle-fall` | Knees buckle | 1.3 | standing → lying-front | ring → ring | curve | library v3, phase 3 |
| `reactions.kneeling-stunned` | Stunned on the knees (loop) | 2.4 L | kneeling → kneeling | ring → ring | none | library v3, phase 3 |
| `reactions.knocked-back` | Knocked backwards | 1.1 | standing → standing | ring → ring | baked | batch 2 |
| `reactions.lying-hit-back` | Hit while lying on the back | 1.0 | lying-back → lying-back | ring → ring | none | library v3, phase 4 |
| `reactions.lying-hit-front` | Hit while lying on the front | 1.0 | lying-front → lying-front | ring → ring | none | library v3, phase 4 |
| `reactions.spin-out-fall` | Spin out and fall | 1.5 | standing → lying-front | ring → ring | curve | library v3, phase 3 |
| `reactions.stagger-back-long` | Long stagger backwards | 1.6 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `reactions.stagger-forward-long` | Long stagger forwards | 1.6 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `reactions.stumble-recover` | Stumble and recover | 1.4 | standing → standing | ring → ring | baked | batch 2 |
| `reactions.stunned` | Stunned | 2.0 L | standing → standing | ring → ring | none | batch 2 |
| `reactions.superkick-drop` | Dropped by a superkick | 1.4 | standing → lying-back | ring → ring | curve | library v3, phase 3 |

## ropes (52)

| id | name | s | states | location | root | from |
|---|---|---|---|---|---|---|
| `ropes.apron-climb-up` | Climb onto the apron | 1.7 | standing → apron-hold | floor → apron | curve | library v3, phase 2 |
| `ropes.apron-drop-down` | Drop down from the apron | 1.5 | apron-hold → standing | apron → floor | curve | library v3, phase 2 |
| `ropes.apron-hang-on` | Hang on at the apron edge | 2.0 L | apron-teeter → apron-teeter | apron → apron | none | library v3, phase 2 |
| `ropes.apron-idle` | Apron idle | 2.4 L | apron-hold → apron-hold | apron → apron | none | library v3, phase 2 |
| `ropes.apron-shuffle-left` | Apron shuffle left | 1.0 L | apron-hold → apron-hold | apron → apron | none | library v3, phase 2 |
| `ropes.apron-shuffle-right` | Apron shuffle right | 1.0 L | apron-hold → apron-hold | apron → apron | none | library v3, phase 2 |
| `ropes.bounce-running` | Bounce off the ropes | 1.28 | running → running | ring → ring | curve | library v3, phase 2 |
| `ropes.climb-to-middle` | Climb onto the middle rope | 1.3 | apron-hold → rope-middle-perched | apron → apron | curve | library v3, phase 2 |
| `ropes.drape-over-top` | Fold over the top rope | 0.9 | standing → rope-draped | ring → ring | curve | library v3, phase 2 |
| `ropes.drape-recover` | Push off the top rope | 1.5 | rope-draped → standing | ring → ring | curve | library v3, phase 2 |
| `ropes.enter-between-ropes` | Enter between middle and top ropes | 2.0 | standing → standing | apron → ring | curve | library v3, phase 2 |
| `ropes.enter-climb-over-top` | Climb over the top rope | 2.95 | standing → standing | apron → ring | curve | library v3, phase 2 |
| `ropes.enter-dive-under` | Dive in under the bottom rope | 1.15 | standing → lying-front | floor → ring | curve | library v3, phase 2 |
| `ropes.enter-duck-top` | Duck under the top rope | 1.5 | standing → standing | apron → ring | curve | library v3, phase 2 |
| `ropes.enter-from-corner` | Enter at the corner | 2.1 | standing → standing | apron → ring | curve | library v3, phase 2 |
| `ropes.enter-injured` | Enter the ring injured | 5.4 | standing → standing | apron → ring | curve | library v3, phase 2 |
| `ropes.enter-jump-over-top` | Jump over the top rope | 1.4 | standing → standing | apron → ring | curve | library v3, phase 2 |
| `ropes.enter-over-bottom` | Enter over the bottom rope | 2.2 | standing → standing | apron → ring | curve | library v3, phase 2 |
| `ropes.enter-slide-under` | Slide in under the bottom rope | 2.7 | standing → standing | floor → ring | curve | library v3, phase 2 |
| `ropes.exit-between-ropes` | Exit between middle and top ropes | 2.0 | standing → standing | ring → apron | curve | library v3, phase 2 |
| `ropes.exit-climb-over-top` | Climb out over the top rope | 2.95 | standing → standing | ring → apron | curve | library v3, phase 2 |
| `ropes.exit-crawl-out` | Crawl out of the ring | 4.75 | standing → standing | ring → floor | curve | library v3, phase 2 |
| `ropes.exit-duck-through` | Duck out through the ropes | 1.5 | standing → standing | ring → apron | curve | library v3, phase 2 |
| `ropes.exit-jump-over-top` | Vault over the top rope to the floor | 1.5 | standing → standing | ring → floor | curve | library v3, phase 2 |
| `ropes.exit-roll-under` | Roll out under the bottom rope | 2.7 | standing → standing | ring → floor | curve | library v3, phase 2 |
| `ropes.exit-slide-under` | Slide out under the bottom rope | 1.95 | standing → standing | ring → floor | curve | library v3, phase 2 |
| `ropes.exit-under-middle` | Exit between bottom and middle ropes | 2.2 | standing → standing | ring → apron | curve | library v3, phase 2 |
| `ropes.get-tangled` | Get tangled in the ropes | 1.1 | rope-lean → rope-tangled | ring → ring | curve | library v3, phase 2 |
| `ropes.grab-hold` | Reach back and brace on the ropes | 0.7 | standing → rope-lean | ring → ring | curve | library v3, phase 2 |
| `ropes.grab-ropes` | Grab the ropes | 0.85 | standing → rope-hold | ring → ring | curve | library v3, phase 2 |
| `ropes.hang-between` | Slump between the ropes | 1.1 | standing → rope-hung | ring → ring | curve | library v3, phase 2 |
| `ropes.hang-over-top` | Draped over the top rope (loop) | 2.8 L | rope-draped → rope-draped | ring → ring | none | library v3, phase 2 |
| `ropes.hold-ropes` | Hold the ropes (loop) | 2.4 L | rope-hold → rope-hold | ring → ring | none | library v3, phase 2 |
| `ropes.hung-between-idle` | Hung between the ropes (loop) | 3.0 L | rope-hung → rope-hung | ring → ring | none | library v3, phase 2 |
| `ropes.hung-recover` | Climb out of the ropes | 1.6 | rope-hung → standing | ring → ring | curve | library v3, phase 2 |
| `ropes.irish-whip` | Irish whip | 1.4 | standing → standing | ring → ring | curve | library v3, phase 2 |
| `ropes.pull-over-top` | Pull opponent over the top rope | 1.4 | standing → standing | floor → floor | curve | library v3, phase 2 |
| `ropes.pulled-over-top` | Pulled over the top rope | 1.4 | rope-draped → lying-back | ring → floor | curve | library v3, phase 2 |
| `ropes.push-into-ropes` | Shove into the ropes | 1.0 | standing → standing | ring → ring | curve | library v3, phase 2 |
| `ropes.pushed-against` | Shoved into the ropes | 1.0 | standing → rope-lean | ring → ring | curve | library v3, phase 2 |
| `ropes.rebound-clothesline` | Rebound clothesline | 1.5 | rope-lean → standing | ring → ring | curve | library v3, phase 2 |
| `ropes.rebound-crossbody` | Rebound crossbody | 1.6 | rope-lean → lying-front | ring → ring | curve | library v3, phase 2 |
| `ropes.rebound-sprint` | Rebound into a sprint | 1.0 | rope-lean → running | ring → ring | curve | library v3, phase 2 |
| `ropes.rope-lean` | Rope lean | 0.7 | standing → standing | ring → ring | none | batch 1 |
| `ropes.rope-rebound` | Rope rebound | 0.8 | standing → standing | ring → ring | speedCurve | batch 1 |
| `ropes.run-into` | Run into the ropes | 0.95 | running → rope-lean | ring → ring | curve | library v3, phase 2 |
| `ropes.springboard-launch` | Springboard off the top rope | 1.4 | standing → standing | apron → ring | curve | library v3, phase 2 |
| `ropes.stretch` | Stretch on the ropes | 3.3 | standing → standing | ring → ring | curve | library v3, phase 2 |
| `ropes.tangled-escape` | Break free of the ropes | 1.4 | rope-tangled → standing | ring → ring | curve | library v3, phase 2 |
| `ropes.tangled-struggle` | Struggle in the ropes (loop) | 2.0 L | rope-tangled → rope-tangled | ring → ring | curve | library v3, phase 2 |
| `ropes.turn-from-ropes` | Turn away from the ropes | 1.05 | rope-hold → standing | ring → ring | curve | library v3, phase 2 |
| `ropes.whipped-into` | Whipped into the ropes | 1.4 | standing → rope-lean | ring → ring | curve | library v3, phase 2 |

## striking (33)

| id | name | s | states | location | root | from |
|---|---|---|---|---|---|---|
| `striking.back-elbow` | Back elbow | 0.9 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.big-boot` | Big boot | 1.3 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.body-punch` | Body punch | 0.7 | standing → standing | ring → ring | none | batch 2 |
| `striking.chop` | Knife-edge chop | 1.05 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.clothesline` | Clothesline | 1.0 | standing → standing | ring → ring | speedCurve | batch 2 |
| `striking.discus-clothesline` | Discus clothesline | 1.3 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.double-axe` | Double axe handle | 0.9 | standing → standing | ring → ring | none | batch 2 |
| `striking.dropkick` | Dropkick | 1.3 | standing → lying-back | ring → ring | curve | library v3, phase 3 |
| `striking.elbow` | Elbow strike | 0.7 | standing → standing | ring → ring | none | batch 2 |
| `striking.enzuigiri` | Enzuigiri | 1.4 | standing → sitting | ring → ring | curve | library v3, phase 3 |
| `striking.european-uppercut` | European uppercut | 0.9 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.forearm-smash` | Forearm smash | 0.9 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.headbutt` | Headbutt | 0.95 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.hook-left` | Hook punch, left | 0.75 | standing → standing | ring → ring | none | batch 2 |
| `striking.hook-right` | Hook punch, right | 0.75 | standing → standing | ring → ring | none | batch 2 |
| `striking.jab` | Jab | 0.45 | standing → standing | ring → ring | none | batch 2 |
| `striking.kick` | Kick | 0.9 | standing → standing | ring → ring | none | batch 1 |
| `striking.knee` | Knee strike | 0.7 | standing → standing | ring → ring | none | batch 2 |
| `striking.lariat` | Short-arm lariat | 1.25 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.leg-kick-combo` | Leg kick combination | 1.5 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.low-kick` | Low kick | 0.8 | standing → standing | ring → ring | none | batch 2 |
| `striking.mount` | Mount a downed opponent | 1.2 | standing → mounted | ring → ring | curve | library v3, phase 3 |
| `striking.mount-off` | Get off the mount | 1.1 | mounted → standing | ring → ring | curve | library v3, phase 3 |
| `striking.mounted-punches` | Mounted punches (loop) | 1.4 L | mounted → mounted | ring → ring | curve | library v3, phase 3 |
| `striking.punch` | Punch | 0.8 | standing → standing | ring → ring | none | batch 1 |
| `striking.roundhouse` | Roundhouse kick | 1.0 | standing → standing | ring → ring | none | batch 2 |
| `striking.running-knee` | Running knee | 1.25 | running → standing | ring → ring | curve | library v3, phase 3 |
| `striking.shoulder-block` | Running shoulder block | 1.4 | running → standing | ring → ring | curve | library v3, phase 3 |
| `striking.spinning-backfist` | Spinning backfist | 1.1 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.spinning-heel-kick` | Spinning heel kick | 1.2 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.stomp` | Stomp | 0.8 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.superkick` | Superkick | 1.1 | standing → standing | ring → ring | curve | library v3, phase 3 |
| `striking.uppercut` | Uppercut | 0.8 | standing → standing | ring → ring | none | batch 2 |

## submissions (36)

| id | name | s | states | location | root | from |
|---|---|---|---|---|---|---|
| `submissions.abdominal-stretch-attacker` | Apply an abdominal stretch | 1.6 | rear-lock-hold → abdominal-stretch-hold | ring → ring | curve | library v3, phase 4 |
| `submissions.abdominal-stretch-defender` | Caught in an abdominal stretch | 1.6 | rear-locked → abdominal-stretch-locked | ring → ring | none | library v3, phase 4 |
| `submissions.abdominal-stretch-hold-attacker` | Abdominal stretch: hold (loop) | 2.0 L | abdominal-stretch-hold → abdominal-stretch-hold | ring → ring | none | library v3, phase 4 |
| `submissions.abdominal-stretch-hold-defender` | Abdominal stretch: in the hold (loop) | 2.0 L | abdominal-stretch-locked → abdominal-stretch-locked | ring → ring | none | library v3, phase 4 |
| `submissions.ankle-lock-attacker` | Apply an ankle lock | 1.8 | standing → ankle-lock-hold | ring → ring | curve | library v3, phase 4 |
| `submissions.ankle-lock-defender` | Caught in an ankle lock | 1.8 | lying-front → ankle-lock-locked | ring → ring | none | library v3, phase 4 |
| `submissions.ankle-lock-hold-attacker` | Ankle lock: hold (loop) | 2.0 L | ankle-lock-hold → ankle-lock-hold | ring → ring | none | library v3, phase 4 |
| `submissions.ankle-lock-hold-defender` | Ankle lock: in the hold (loop) | 2.0 L | ankle-lock-locked → ankle-lock-locked | ring → ring | none | library v3, phase 4 |
| `submissions.armbar-attacker` | Apply a cross armbar | 2.0 | standing → armbar-hold | ring → ring | curve | library v3, phase 4 |
| `submissions.armbar-defender` | Caught in an armbar | 2.0 | lying-back → armbar-locked | ring → ring | none | library v3, phase 4 |
| `submissions.armbar-hold-attacker` | Cross armbar: hold (loop) | 2.0 L | armbar-hold → armbar-hold | ring → ring | none | library v3, phase 4 |
| `submissions.armbar-hold-defender` | Cross armbar: in the hold (loop) | 2.0 L | armbar-locked → armbar-locked | ring → ring | none | library v3, phase 4 |
| `submissions.boston-crab-attacker` | Apply the boston crab | 1.9 | standing → boston-crab-hold | ring → ring | curve | library v3, phase 4 |
| `submissions.boston-crab-defender` | Caught in the boston crab | 1.9 | lying-back → boston-crab-locked | ring → ring | curve | library v3, phase 4 |
| `submissions.boston-crab-hold-attacker` | Boston crab: hold (loop) | 2.4 L | boston-crab-hold → boston-crab-hold | ring → ring | none | library v3, phase 4 |
| `submissions.boston-crab-hold-defender` | Boston crab: in the hold (loop) | 2.4 L | boston-crab-locked → boston-crab-locked | ring → ring | none | library v3, phase 4 |
| `submissions.camel-clutch-attacker` | Apply a camel clutch | 2.0 | standing → camel-clutch-hold | ring → ring | curve | library v3, phase 4 |
| `submissions.camel-clutch-defender` | Caught in a camel clutch | 2.0 | lying-front → camel-clutch-locked | ring → ring | none | library v3, phase 4 |
| `submissions.camel-clutch-hold-attacker` | Camel clutch: hold (loop) | 2.0 L | camel-clutch-hold → camel-clutch-hold | ring → ring | none | library v3, phase 4 |
| `submissions.camel-clutch-hold-defender` | Camel clutch: in the hold (loop) | 2.0 L | camel-clutch-locked → camel-clutch-locked | ring → ring | none | library v3, phase 4 |
| `submissions.crossface-attacker` | Apply a crossface | 2.0 | standing → crossface-hold | ring → ring | curve | library v3, phase 4 |
| `submissions.crossface-defender` | Caught in a crossface | 2.0 | lying-front → crossface-locked | ring → ring | none | library v3, phase 4 |
| `submissions.crossface-hold-attacker` | Crossface: hold (loop) | 2.0 L | crossface-hold → crossface-hold | ring → ring | none | library v3, phase 4 |
| `submissions.crossface-hold-defender` | Crossface: in the hold (loop) | 2.0 L | crossface-locked → crossface-locked | ring → ring | none | library v3, phase 4 |
| `submissions.figure-four-attacker` | Apply a figure-four leglock | 2.4 | standing → figure-four-hold | ring → ring | curve | library v3, phase 4 |
| `submissions.figure-four-defender` | Caught in a figure-four | 2.4 | lying-back → figure-four-locked | ring → ring | none | library v3, phase 4 |
| `submissions.figure-four-hold-attacker` | Figure-four: hold (loop) | 2.4 L | figure-four-hold → figure-four-hold | ring → ring | none | library v3, phase 4 |
| `submissions.figure-four-hold-defender` | Figure-four: in the hold (loop) | 2.4 L | figure-four-locked → figure-four-locked | ring → ring | none | library v3, phase 4 |
| `submissions.sharpshooter-attacker` | Apply the sharpshooter | 1.9 | standing → sharpshooter-hold | ring → ring | curve | library v3, phase 4 |
| `submissions.sharpshooter-defender` | Caught in the sharpshooter | 1.9 | lying-back → sharpshooter-locked | ring → ring | curve | library v3, phase 4 |
| `submissions.sharpshooter-hold-attacker` | Sharpshooter: hold (loop) | 2.4 L | sharpshooter-hold → sharpshooter-hold | ring → ring | none | library v3, phase 4 |
| `submissions.sharpshooter-hold-defender` | Sharpshooter: in the hold (loop) | 2.4 L | sharpshooter-locked → sharpshooter-locked | ring → ring | none | library v3, phase 4 |
| `submissions.sleeper-hold-attacker` | Apply a sleeper hold | 2.0 | rear-lock-hold → sleeper-hold | ring → ring | curve | library v3, phase 4 |
| `submissions.sleeper-hold-defender` | Caught in a sleeper hold | 2.0 | rear-locked → sleeper-locked | ring → ring | none | library v3, phase 4 |
| `submissions.sleeper-hold-hold-attacker` | Sleeper hold: hold (loop) | 2.4 L | sleeper-hold → sleeper-hold | ring → ring | none | library v3, phase 4 |
| `submissions.sleeper-hold-hold-defender` | Sleeper hold: in the hold (loop) | 2.4 L | sleeper-locked → sleeper-locked | ring → ring | none | library v3, phase 4 |

## throws (32)

| id | name | s | states | location | root | from |
|---|---|---|---|---|---|---|
| `throws.arm-drag-attacker` | Arm drag | 1.2 | lockup → standing | ring → ring | curve | library v3, phase 4 |
| `throws.arm-drag-defender` | Arm-dragged | 1.2 | lockup → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.backbreaker-attacker` | Backbreaker | 2.3 | standing → standing | ring → ring | curve | library v3, phase 4 |
| `throws.backbreaker-defender` | Backbreakered | 2.3 | standing → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.belly-to-belly-attacker` | Belly-to-belly suplex | 1.6 | body-lock-hold → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.belly-to-belly-defender` | Belly-to-belly suplexed | 1.6 | body-locked → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.body-slam-attacker` | Body slam | 1.8 | standing → standing | ring → ring | curve | library v3, phase 4 |
| `throws.body-slam-defender` | Body slammed | 1.8 | standing → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.bulldog-attacker` | Bulldog | 1.4 | headlock-hold → sitting | ring → ring | curve | library v3, phase 4 |
| `throws.bulldog-defender` | Bulldogged | 1.4 | headlocked → lying-front | ring → ring | curve | library v3, phase 4 |
| `throws.chokeslam-attacker` | Chokeslam | 1.9 | standing → standing | ring → ring | curve | library v3, phase 4 |
| `throws.chokeslam-defender` | Chokeslammed | 1.9 | standing → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.ddt-attacker` | DDT | 1.5 | facelock-hold → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.ddt-defender` | Spiked with a DDT | 1.5 | facelocked → lying-front | ring → ring | curve | library v3, phase 4 |
| `throws.fireman-carry-attacker` | Fireman's carry slam | 2.6 | standing → standing | ring → ring | curve | library v3, phase 4 |
| `throws.fireman-carry-defender` | Fireman's carry slam (taken) | 2.6 | bent-over → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.german-suplex-attacker` | German suplex | 1.8 | rear-lock-hold → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.german-suplex-defender` | German suplexed | 1.8 | rear-locked → lying-front | ring → ring | curve | library v3, phase 4 |
| `throws.hip-toss-attacker` | Hip toss | 1.4 | lockup → standing | ring → ring | curve | library v3, phase 4 |
| `throws.hip-toss-defender` | Hip toss (taken) | 1.4 | lockup → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.neckbreaker-attacker` | Neckbreaker | 1.5 | facelock-hold → sitting | ring → ring | curve | library v3, phase 4 |
| `throws.neckbreaker-defender` | Neckbreakered | 1.5 | facelocked → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.powerbomb-attacker` | Powerbomb | 2.3 | standing → standing | ring → ring | curve | library v3, phase 4 |
| `throws.powerbomb-defender` | Powerbombed | 2.3 | bent-over → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.powerslam-attacker` | Scoop powerslam | 2.0 | standing → covering | ring → ring | curve | library v3, phase 4 |
| `throws.powerslam-defender` | Powerslammed | 2.0 | standing → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.snap-suplex-attacker` | Snap suplex | 1.5 | facelock-hold → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.snap-suplex-defender` | Snap suplex (taken) | 1.5 | facelocked → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.spinebuster-attacker` | Spinebuster | 1.7 | body-lock-hold → crouching | ring → ring | curve | library v3, phase 4 |
| `throws.spinebuster-defender` | Spinebustered | 1.7 | body-locked → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.vertical-suplex-attacker` | Vertical suplex | 2.4 | facelock-hold → lying-back | ring → ring | curve | library v3, phase 4 |
| `throws.vertical-suplex-defender` | Vertical suplex (taken) | 2.4 | facelocked → lying-back | ring → ring | curve | library v3, phase 4 |

## turnbuckle (31)

| id | name | s | states | location | root | from |
|---|---|---|---|---|---|---|
| `turnbuckle.approach-corner` | Walk to the corner | 1.9 | standing → standing | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.climb-bottom` | Climb onto the bottom rope | 0.85 | corner-hold → corner-climb-1 | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.climb-down` | Climb down from the top | 2.0 | perched → standing | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.climb-full` | Climb the turnbuckle | 2.3 | corner-hold → perched | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.climb-middle` | Climb onto the middle rope | 0.9 | corner-climb-1 → corner-climb-2 | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.climb-top` | Turn and climb to the top | 1.45 | corner-climb-2 → perched | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.climb-top-facing-out` | Stand on the top rope facing out | 1.4 | corner-climb-2 → corner-top-out | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.corner-back-idle` | Propped in the corner (loop) | 2.8 L | corner-back → corner-back | ring → ring | none | library v3, phase 2 |
| `turnbuckle.corner-slump` | Slump down in the corner | 1.4 | corner-back → corner-slumped | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.crouch-top` | Crouch back down on top | 0.9 | perched-ready → perched | ring → ring | none | library v3, phase 2 |
| `turnbuckle.fall` | Fall off the top | 1.5 | perched → lying-front | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.grab-corner` | Take hold of the corner | 0.8 | standing → corner-hold | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.hang-from-corner` | Slip into the tree of woe | 1.2 | corner-seated → corner-hanging | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.hanging-drop` | Drop out of the tree of woe | 1.3 | corner-hanging → lying-back | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.hanging-idle` | Hanging in the corner (loop) | 3.2 L | corner-hanging → corner-hanging | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.jump-backward` | Backflip off the top | 1.4 | corner-top-out → standing | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.jump-down` | Hop down into the ring | 1.05 | perched → standing | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.jump-forward` | Leap forward off the top | 1.35 | perched-ready → standing | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.jump-sideways` | Leap sideways off the top | 1.3 | perched-ready → standing | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.knocked-off-balance` | Knocked down onto the turnbuckle | 0.85 | perched-ready → corner-seated | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.land-awkward` | Land badly off the top | 2.1 | perched-ready → sitting | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.look-crowd` | Look round the crowd from the top | 3.0 | perched → perched | ring → ring | none | library v3, phase 2 |
| `turnbuckle.miss-aerial` | Miss a dive from the top | 2.0 | perched-ready → lying-front | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.perched-idle` | Perched on the top turnbuckle (loop) | 2.4 L | perched → perched | ring → ring | none | library v3, phase 2 |
| `turnbuckle.prepare-jump` | Rise up on the top turnbuckle | 1.0 | perched → perched-ready | ring → ring | none | library v3, phase 2 |
| `turnbuckle.pushed-off` | Shoved off the top to the floor | 1.4 | perched → lying-back | ring → floor | curve | library v3, phase 2 |
| `turnbuckle.recover-balance` | Wobble and steady on top | 1.3 | perched-ready → perched | ring → ring | none | library v3, phase 2 |
| `turnbuckle.seated-dazed` | Seated on the top turnbuckle (loop) | 2.8 L | corner-seated → corner-seated | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.taunt-top` | Pose on the top turnbuckle | 2.6 | perched → perched | ring → ring | none | library v3, phase 2 |
| `turnbuckle.thrown-off` | Thrown off the top | 1.3 | perched → lying-back | ring → ring | curve | library v3, phase 2 |
| `turnbuckle.whipped-into-corner` | Whipped into the corner | 1.6 | standing → corner-back | ring → ring | curve | library v3, phase 2 |

## weapons (5)

| id | name | s | states | location | root | from |
|---|---|---|---|---|---|---|
| `weapons.chair-drop` | Drop chair | 0.8 | standing → standing | ring → ring | none | props pack |
| `weapons.chair-hold` | Hold chair | 2.4 L | standing → standing | ring → ring | none | props pack |
| `weapons.chair-pickup` | Pick up chair | 1.3 | standing → standing | ring → ring | none | props pack |
| `weapons.chair-swing-horizontal` | Swing chair horizontally | 1.4 | standing → standing | ring → ring | none | props pack |
| `weapons.chair-swing-overhead` | Swing chair overhead | 1.5 | standing → standing | ring → ring | none | props pack |

## Paired moves (53)

| id | name | s | attacker | defender |
|---|---|---|---|---|
| `pair.irish-whip-ropes` | Irish whip into the ropes | 1.4 | `ropes.irish-whip` | `ropes.whipped-into` |
| `pair.push-against-ropes` | Shove into the ropes | 1.0 | `ropes.push-into-ropes` | `ropes.pushed-against` |
| `pair.pull-over-top-rope` | Pull over the top rope to the floor | 1.4 | `ropes.pull-over-top` | `ropes.pulled-over-top` |
| `pair.lockup` | Lock-up | 1.0 | `grappling.lockup` | `grappling.lockup` |
| `pair.shove-off` | Shove out of the lock-up | 1.1 | `grappling.shove-off-attacker` | `grappling.shove-off-defender` |
| `pair.side-headlock` | Side headlock | 0.9 | `grappling.side-headlock-attacker` | `grappling.side-headlock-defender` |
| `pair.headlock-takeover` | Headlock takeover | 1.2 | `grappling.headlock-takeover-attacker` | `grappling.headlock-takeover-defender` |
| `pair.wristlock` | Wristlock | 1.0 | `grappling.wristlock-attacker` | `grappling.wristlock-defender` |
| `pair.hammerlock` | Hammerlock | 1.2 | `grappling.hammerlock-attacker` | `grappling.hammerlock-defender` |
| `pair.front-facelock` | Front facelock | 0.85 | `grappling.front-facelock-attacker` | `grappling.front-facelock-defender` |
| `pair.waistlock` | Body lock | 0.9 | `grappling.waistlock-attacker` | `grappling.waistlock-defender` |
| `pair.rear-waistlock` | Rear waistlock | 1.0 | `grappling.rear-waistlock-attacker` | `grappling.rear-waistlock-defender` |
| `pair.body-slam` | Body slam | 1.8 | `throws.body-slam-attacker` | `throws.body-slam-defender` |
| `pair.vertical-suplex` | Vertical suplex | 2.4 | `throws.vertical-suplex-attacker` | `throws.vertical-suplex-defender` |
| `pair.snap-suplex` | Snap suplex | 1.5 | `throws.snap-suplex-attacker` | `throws.snap-suplex-defender` |
| `pair.ddt` | DDT | 1.5 | `throws.ddt-attacker` | `throws.ddt-defender` |
| `pair.neckbreaker` | Neckbreaker | 1.5 | `throws.neckbreaker-attacker` | `throws.neckbreaker-defender` |
| `pair.belly-to-belly` | Belly-to-belly suplex | 1.6 | `throws.belly-to-belly-attacker` | `throws.belly-to-belly-defender` |
| `pair.spinebuster` | Spinebuster | 1.7 | `throws.spinebuster-attacker` | `throws.spinebuster-defender` |
| `pair.german-suplex` | German suplex | 1.8 | `throws.german-suplex-attacker` | `throws.german-suplex-defender` |
| `pair.hip-toss` | Hip toss | 1.4 | `throws.hip-toss-attacker` | `throws.hip-toss-defender` |
| `pair.arm-drag` | Arm drag | 1.2 | `throws.arm-drag-attacker` | `throws.arm-drag-defender` |
| `pair.powerbomb` | Powerbomb | 2.3 | `throws.powerbomb-attacker` | `throws.powerbomb-defender` |
| `pair.chokeslam` | Chokeslam | 1.9 | `throws.chokeslam-attacker` | `throws.chokeslam-defender` |
| `pair.powerslam` | Scoop powerslam | 2.0 | `throws.powerslam-attacker` | `throws.powerslam-defender` |
| `pair.backbreaker` | Backbreaker | 2.3 | `throws.backbreaker-attacker` | `throws.backbreaker-defender` |
| `pair.fireman-carry` | Fireman's carry slam | 2.6 | `throws.fireman-carry-attacker` | `throws.fireman-carry-defender` |
| `pair.bulldog` | Bulldog | 1.4 | `throws.bulldog-attacker` | `throws.bulldog-defender` |
| `pair.figure-four` | Figure-four leglock | 2.4 | `submissions.figure-four-attacker` | `submissions.figure-four-defender` |
| `pair.figure-four-hold` | Figure-four (hold loop) | 2.4 | `submissions.figure-four-hold-attacker` | `submissions.figure-four-hold-defender` |
| `pair.sharpshooter` | Sharpshooter | 1.9 | `submissions.sharpshooter-attacker` | `submissions.sharpshooter-defender` |
| `pair.sharpshooter-hold` | Sharpshooter (hold loop) | 2.4 | `submissions.sharpshooter-hold-attacker` | `submissions.sharpshooter-hold-defender` |
| `pair.boston-crab` | Boston crab | 1.9 | `submissions.boston-crab-attacker` | `submissions.boston-crab-defender` |
| `pair.boston-crab-hold` | Boston crab (hold loop) | 2.4 | `submissions.boston-crab-hold-attacker` | `submissions.boston-crab-hold-defender` |
| `pair.armbar` | Cross armbar | 2.0 | `submissions.armbar-attacker` | `submissions.armbar-defender` |
| `pair.armbar-hold` | Cross armbar (hold loop) | 2.0 | `submissions.armbar-hold-attacker` | `submissions.armbar-hold-defender` |
| `pair.camel-clutch` | Camel clutch | 2.0 | `submissions.camel-clutch-attacker` | `submissions.camel-clutch-defender` |
| `pair.camel-clutch-hold` | Camel clutch (hold loop) | 2.0 | `submissions.camel-clutch-hold-attacker` | `submissions.camel-clutch-hold-defender` |
| `pair.crossface` | Crossface | 2.0 | `submissions.crossface-attacker` | `submissions.crossface-defender` |
| `pair.crossface-hold` | Crossface (hold loop) | 2.0 | `submissions.crossface-hold-attacker` | `submissions.crossface-hold-defender` |
| `pair.ankle-lock` | Ankle lock | 1.8 | `submissions.ankle-lock-attacker` | `submissions.ankle-lock-defender` |
| `pair.ankle-lock-hold` | Ankle lock (hold loop) | 2.0 | `submissions.ankle-lock-hold-attacker` | `submissions.ankle-lock-hold-defender` |
| `pair.sleeper-hold` | Sleeper hold | 2.0 | `submissions.sleeper-hold-attacker` | `submissions.sleeper-hold-defender` |
| `pair.sleeper-hold-hold` | Sleeper hold (hold loop) | 2.4 | `submissions.sleeper-hold-hold-attacker` | `submissions.sleeper-hold-hold-defender` |
| `pair.abdominal-stretch` | Abdominal stretch | 1.6 | `submissions.abdominal-stretch-attacker` | `submissions.abdominal-stretch-defender` |
| `pair.abdominal-stretch-hold` | Abdominal stretch (hold loop) | 2.0 | `submissions.abdominal-stretch-hold-attacker` | `submissions.abdominal-stretch-hold-defender` |
| `pair.cover` | Cover | 1.3 | `ground.cover-attacker` | `ground.cover-defender` |
| `pair.hook-leg-cover` | Hooked-leg cover | 1.3 | `ground.hook-leg-cover-attacker` | `ground.hook-leg-cover-defender` |
| `pair.kick-out` | Kick-out | 1.3 | `ground.kick-out-attacker` | `ground.kick-out-defender` |
| `pair.roll-up` | Roll-up | 1.6 | `ground.roll-up-attacker` | `ground.roll-up-defender` |
| `pair.small-package` | Small package | 1.6 | `ground.small-package-attacker` | `ground.small-package-defender` |
| `pair.pick-up-opponent` | Pick up a downed opponent | 1.8 | `ground.pick-up-opponent-attacker` | `ground.pick-up-opponent-defender` |
| `pair.drag-opponent` | Drag a downed opponent | 2.4 | `ground.drag-opponent-attacker` | `ground.drag-opponent-defender` |

## Old planned ids now covered by new clips

| planned id | covered by |
|---|---|
| `grappling.irish-whip` | `ropes.irish-whip` |
| `grappling.throw-to-ropes` | `ropes.push-into-ropes` |
| `ropes.run-into-ropes` | `ropes.run-into` |
| `ropes.turn-from-ropes` | `ropes.turn-from-ropes` |
| `ropes.rope-stretch` | `ropes.stretch` |
| `ropes.spring-forward` | `ropes.rebound-sprint` |
| `ropes.bounce-running` | `ropes.bounce-running` |
| `ropes.jump-over-top` | `ropes.enter-jump-over-top` |
| `ropes.climb-through` | `ropes.enter-duck-top` |
| `ropes.slide-under` | `ropes.enter-slide-under` |
| `ropes.enter-ring` | `ropes.enter-between-ropes` |
| `ropes.exit-ring` | `ropes.exit-between-ropes` |
| `ropes.tangled` | `ropes.get-tangled` |
| `aerial.top-rope-jump` | `turnbuckle.jump-forward` |
| `aerial.missed-dive` | `turnbuckle.miss-aerial` |

## Planned, not built yet (113)

Listed in the manifest with `"status": "planned"`. No JSON file exists for these.

- **aerial**: `aerial.body-splash`, `aerial.corkscrew-press`, `aerial.diving-attack`, `aerial.diving-crossbody`, `aerial.diving-elbow`, `aerial.diving-headbutt`, `aerial.diving-splash`, `aerial.elbow-drop`, `aerial.frog-splash`, `aerial.land-on-opponent`, `aerial.missile-dropkick`, `aerial.moonsault`, `aerial.plancha`, `aerial.running-jump`, `aerial.second-rope-elbow`, `aerial.springboard-crossbody`, `aerial.springboard-moonsault`, `aerial.standing-jump`, `aerial.suicide-dive`, `aerial.swan-dive`, `aerial.swanton-bomb`, `aerial.top-rope-legdrop`
- **eliminations**: `eliminations.battle-royal-toss`, `eliminations.feet-touch-floor`, `eliminations.hang-on-top-rope`, `eliminations.hold-on-apron`, `eliminations.pulled-off-apron`, `eliminations.save-on-ropes`, `eliminations.skin-the-cat`
- **environment**: `environment.climb-barricade`, `environment.entrance-pose-stage`, `environment.rammed-into-post`, `environment.ringside-brawl-idle`, `environment.sit-on-steps`, `environment.slam-on-announce-table`, `environment.thrown-into-barricade`, `environment.thrown-into-steps`, `environment.walk-ramp`
- **grappling**: `grappling.body-slam`, `grappling.break-grapple`, `grappling.ddt`, `grappling.front-facelock`, `grappling.grab`, `grappling.grapple-idle`, `grappling.hammerlock`, `grappling.headlock`, `grappling.headlock-takeover`, `grappling.push`, `grappling.rear-waistlock`, `grappling.shoulder-charge`, `grappling.shove-off`, `grappling.side-headlock`, `grappling.spear`, `grappling.suplex`, `grappling.waistlock`, `grappling.wristlock`
- **ground**: `ground.cover`, `ground.drag-opponent`, `ground.ground-stomp`, `ground.hook-leg-cover`, `ground.kick-out`, `ground.pick-up-opponent`, `ground.roll-up`, `ground.small-package`
- **recovery**: `recovery.catch-breath`, `recovery.getup-corner-assist`, `recovery.getup-ropes-assist`, `recovery.ref-check-respond`, `recovery.roll-to-knees`, `recovery.shake-off`
- **submissions**: `submissions.abdominal-stretch`, `submissions.ankle-lock`, `submissions.armbar`, `submissions.boston-crab`, `submissions.camel-clutch`, `submissions.crossface`, `submissions.figure-four`, `submissions.sharpshooter`, `submissions.sleeper-hold`
- **taunts**: `taunts.angry-challenge`, `taunts.beckon`, `taunts.chest-beat`, `taunts.cocky-laugh`, `taunts.crowd-hype`, `taunts.exhausted-celebration`, `taunts.flex`, `taunts.point`, `taunts.raise-arms`, `taunts.victory`
- **throws**: `throws.arm-drag`, `throws.backbreaker`, `throws.belly-to-belly`, `throws.body-slam`, `throws.bulldog`, `throws.chokeslam`, `throws.ddt`, `throws.fireman-carry`, `throws.german-suplex`, `throws.hip-toss`, `throws.neckbreaker`, `throws.powerbomb`, `throws.powerslam`, `throws.snap-suplex`, `throws.spinebuster`, `throws.vertical-suplex`
- **weapons**: `weapons.chair-hit-reaction`, `weapons.table-break-reaction`, `weapons.table-carry`, `weapons.table-fall-through`, `weapons.table-pickup`, `weapons.table-push`, `weapons.table-setup`, `weapons.table-slam`
