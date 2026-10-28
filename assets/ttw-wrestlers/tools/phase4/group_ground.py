"""Phase 4, ground work: pinning (cover, hooked cover, kick-out, roll-up, small package), ground strikes (elbow
drop, leg drop, knee drop, with lying hit reactions), picking a downed opponent up and dragging them.

Pair frame: attacker at the origin facing -z. A defender lying across in front of the attacker: frame [0, 0, -0.9, 90]
(on the back, head to the attacker's right, +x)."""
from common import *
from pairs import *
from throws_lib import *

D_SIDE = A.Frame('mat', [0, 0, -0.9, 90])
D_LB = A.Frame('mat', [0, 0, -1.3, 180])
UP, DOWN = [0, 1, 0], [0, -1, 0]
PX, NX, PZ, NZ = [1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]
KNEELS = {'hips': {'p': [0, -0.515, 0.04]}, 'rightUpperLeg': r(10, 0, 4), 'leftUpperLeg': r(10, 0, -4), 'rightLowerLeg': r(-100), 'leftLowerLeg': r(-100),
          'rightFoot': r(-55), 'leftFoot': r(-55)}

def osc(ph, a): return a * math.sin(ph * 2 * math.pi)


def build(L, PR):
    P = PR.p

    # ================================================================ cover and hooked cover
    def cover(name, title, hook):
        d_id, a_id = f'ground.{name}-defender', f'ground.{name}-attacker'
        def d_k(t, k=0.0, wr=0.0):
            parts = [{'hips': {'p': [0, -0.83, 0], 'r': [90, 0, wr * 4]}, 'neck': r(10 + wr * 10)}]
            if hook: parts.append({'leftUpperLeg': r(70 * k, 0, -10), 'leftLowerLeg': r(-90 * k)})
            return K(t, [0, 0, -0.9], 90, A.LIE_BACK, *parts)
        keys = [d_k(0), d_k(0.45, 0.4), d_k(0.7, 1.0), d_k(1.3, 1.0, 0.4)]
        L.clip(d_id, f'{title} (pinned)', 1.3, keys, D_SIDE,
               events=[ev(0.6, 'grab', attachment='chest'), ev(0.7, 'grip_locked')],
               desc=f'Defender: on the back, pinned by the attacker lying across the chest{", the near leg hooked up" if hook else ""}.',
               tags=['pin', 'defender', name], start_state='lying-back', end_state='pinned', placement='center', interrupt={'windows': []})
        chest = lambda t, lx: P(d_id, t, 'chest', (lx, 0.12, 0))
        knee = lambda t: P(d_id, t, 'leftLowerLeg', (0, 0, 0))
        COV = {'hips': {'p': [0, -0.66, 0], 'r': [-75, 0, 0]}, 'spine': r(-8), 'neck': r(30),
               'rightUpperLeg': r(40, 0, 25), 'leftUpperLeg': r(15, 0, -20), 'rightLowerLeg': r(-80), 'leftLowerLeg': r(-50), 'rightFoot': r(-50), 'leftFoot': r(-50)}
        keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
        keys.append(K(0.35, [0.25, 0, -0.35], 0, A.STANCE, body(hy=-0.3, lean=-25), feet=stand_feet([0.25, 0, -0.35], 0, width=0.18)))
        rh = knee(0.7) if hook else chest(0.7, -0.1)
        keys.append(K(0.7, [0.28, 0, -0.45], 0, COV, lhand=chest(0.7, 0.12), rhand=rh))
        rh = knee(1.3) if hook else chest(1.3, -0.1)
        keys.append(K(1.3, [0.28, 0, -0.45], 0, COV, {'hips': {'p': [0, -0.68, 0], 'r': [-78, 0, 0]}}, lhand=chest(1.3, 0.12), rhand=rh))
        L.clip(a_id, title, 1.3, keys, AT,
               events=[ev(0.35, 'footstep'), ev(0.6, 'grab', attachment='leftHandGrip'), ev(0.7, 'grip_locked')],
               desc=f'Attacker: drop across the downed opponent\'s chest for the pin{" and hook the near leg up" if hook else ""}. Ends covering (start the referee count here).',
               tags=['pin', 'attacker', name], end_state='covering', placement='center')
        PR.move(f'pair.{name}', title, 'ground', a_id, d_id,
                [ev2(0.6, 'grab', 'both'), ev2(0.7, 'grip_locked', 'both'), ev2(1.3, 'animation_complete', 'both')],
                f'Defender on the back across in front of the attacker: {title.lower()}. Run the count from 0.7 s.',
                contacts=[{'from': 0.6, 'to': 1.3, 'attacker': 'chest+propLeftHand', 'defender': 'chest'}], tags=['pin'])
        return COV
    COV = cover('cover', 'Cover', False)
    cover('hook-leg-cover', 'Hooked-leg cover', True)

    # ---------------------------------------------------------------- kick-out (from the cover)
    d_id, a_id = 'ground.kick-out-defender', 'ground.kick-out-attacker'
    B = Body(90)
    keys = [B.pose(0, [0, 0, -0.9], 90, A.LIE_BACK)]
    keys.append(B.pose(0.25, [0, 0, -0.9], 90, A.LIE_BACK, {'hips': {'p': [0, -0.8, 0], 'r': [80, 0, 0]}, 'rightUpperLeg': r(40), 'leftUpperLeg': r(40), 'rightLowerLeg': r(-60), 'leftLowerLeg': r(-60)}))
    keys.append(B.pose(0.42, [0, 0, -0.9], 90, A.LIE_BACK, {'hips': {'p': [0, -0.72, 0], 'r': [80, 0, -25]}, 'spine': r(-10), 'neck': r(30), 'rightUpperArm': r(60, 0, 30)}))      # shoulder up
    keys.append(B.pose(0.8, [0, 0, -0.9], 90, A.LIE_BACK, {'neck': r(20)}))
    keys.append(B.pose(1.3, [0, 0, -0.9], 90, A.LIE_BACK))
    L.clip(d_id, 'Kick out of the pin', 1.3, keys, D_SIDE,
           events=[ev(0.42, 'release'), ev(0.42, 'recover', note='shoulder up before three')],
           desc='Defender: pinned, bridges and jerks a shoulder off the mat, throwing the attacker off. Stays lying on the back.',
           tags=['pin', 'defender', 'kick-out'], start_state='pinned', end_state='lying-back', placement='center', interrupt={'windows': []})
    KNEELB = A.merge(KNEELS, {'spine': r(-10), 'neck': r(10)})
    keys = [K(0, [0.28, 0, -0.45], 0, COV)]
    keys.append(K(0.42, [0.28, 0.18, -0.35], 0, COV, {'hips': {'p': [0, -0.55, 0], 'r': [-50, 0, 20]}}, ARMS_OUT))
    keys.append(K(0.7, [0.3, 0, -0.2], 0, KNEELB, body(hy=-0.515, hz=0.04, lean=-10, neck=(20, 0, 0)), {'rightUpperArm': r(20, 0, -20), 'leftUpperArm': r(20, 0, 20)}))
    keys.append(K(1.3, [0.3, 0, -0.2], 0, KNEELB, body(hy=-0.515, hz=0.04, lean=-6, neck=(10, 0, 0)), {'rightUpperArm': r(40, 0, -10), 'leftUpperArm': r(40, 0, 10), 'rightForearm': r(60)}))
    L.clip(a_id, 'Thrown off the pin', 1.3, keys, A.Frame('mat', [0.28, 0, -0.45, 0]),
           events=[ev(0.42, 'release'), ev(0.7, 'land', zone='knees')],
           desc='Attacker: covering, gets thrown off as the opponent kicks out; ends up on the knees beside them in disbelief.',
           tags=['pin', 'attacker', 'kick-out'], start_state='covering', end_state='kneeling', placement='center')
    PR.move('pair.kick-out', 'Kick-out', 'ground', a_id, d_id,
            [ev2(0.42, 'release', 'both'), ev2(0.42, 'recover', 'defender'), ev2(0.7, 'land', 'attacker', zone='knees'), ev2(1.3, 'animation_complete', 'both')],
            'From the cover: the defender kicks out at the last moment, throwing the attacker off.', tags=['pin', 'kick-out'])

    # ================================================================ roll-up and small package (defender standing with the back to the attacker, 0.6 m)
    DR = A.Frame('mat', [0, 0, -0.6, 0])
    def rollup(name, title, ball, a_desc, d_desc):
        d_id, a_id = f'ground.{name}-defender', f'ground.{name}-attacker'
        B = Body(0)
        LEGS_UP = {'rightUpperLeg': r(100 if ball else 80, 0, 6), 'leftUpperLeg': r(100 if ball else 80, 0, -6),
                   'rightLowerLeg': r(-110 if ball else -40), 'leftLowerLeg': r(-110 if ball else -40),
                   'rightUpperArm': r(30, 0, -40), 'leftUpperArm': r(30, 0, 40), 'neck': r(30 if ball else 20)}
        keys = [B.pose(0, [0, 0, -0.6], 0, A.GUARD, feet=stand_feet([0, 0, -0.6], 0))]
        keys.append(B.key(0.3, [0, 0.85, -0.5], [0, 0.95, 0.3], [0, 0.3, -0.95], A.STANCE, ARMS_OUT, feet=stand_feet([0, 0, -0.5], 0)))       # pulled back
        keys.append(B.key(0.55, [0, 0.45, -0.35], [0, 0.4, 0.92], [0, 0.92, -0.4], LEGS_UP))
        keys.append(B.key(0.8, [0, 0.62, -0.3], [0, -0.45, 0.89], [0, 0.89, 0.45], LEGS_UP, {'neck': r(45)}))                                   # rolled onto the shoulders
        keys.append(B.key(1.6, [0, 0.62, -0.3], [0, -0.48, 0.88], [0, 0.88, 0.48], LEGS_UP, {'neck': r(50)}))
        L.clip(d_id, f'{title} (pinned)', 1.6, keys, DR,
               events=[ev(0.1, 'grab', attachment='hips'), ev(0.55, 'land', zone='back'), ev(0.8, 'grip_locked')],
               desc=f'Defender: {d_desc}', tags=['pin', 'defender', name], end_state='rolled-up', placement='center', interrupt={'windows': []})
        legs = lambda t, s: P(d_id, t, 'leftLowerLeg' if s < 0 else 'rightLowerLeg', (0, -0.1, 0))
        SITR = {'hips': {'p': [0, -0.75, 0.05], 'r': [25, 0, 0]}, 'spine': r(-20), 'neck': r(20),
                'rightUpperLeg': r(70, 0, 25), 'leftUpperLeg': r(70, 0, -25), 'rightLowerLeg': r(-60), 'leftLowerLeg': r(-60)}
        keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
        keys.append(K(0.3, [0, 0, -0.12], 0, A.STANCE, body(hy=-0.3, lean=-20), lhand=P(d_id, 0.3, 'hips', (-0.15, 0.05, 0.1)), rhand=P(d_id, 0.3, 'hips', (0.15, 0.05, 0.1)),
                      feet=stand_feet([0, 0, -0.12], 0, width=0.2)))
        keys.append(K(0.55, [0, 0, -0.1], 0, SITR, body(hy=-0.55, lean=15), lhand=legs(0.55, -1), rhand=legs(0.55, 1)))
        keys.append(K(0.8, [0, 0, -0.08], 0, SITR, lhand=legs(0.8, -1), rhand=legs(0.8, 1)))
        keys.append(K(1.6, [0, 0, -0.08], 0, SITR, {'hips': {'p': [0, -0.75, 0.05], 'r': [32, 0, 0]}}, lhand=legs(1.6, -1), rhand=legs(1.6, 1)))
        L.clip(a_id, title, 1.6, keys, AT,
               events=[ev(0.1, 'attack_start'), ev(0.1, 'grab', attachment='leftHandGrip'), ev(0.55, 'land', zone='seat'), ev(0.8, 'grip_locked')],
               desc=f'Attacker: {a_desc}', tags=['pin', 'attacker', name], end_state='rolling-up', placement='center')
        PR.move(f'pair.{name}', title, 'ground', a_id, d_id,
                [ev2(0.1, 'attack_start', 'attacker'), ev2(0.1, 'grab', 'both'), ev2(0.55, 'land', 'both'), ev2(0.8, 'grip_locked', 'both'), ev2(1.6, 'animation_complete', 'both')],
                f'Defender standing with the back to the attacker, 0.6 m away. {d_desc} Run the count from 0.8 s.',
                contacts=[{'from': 0.1, 'to': 1.6, 'attacker': 'propLeftHand+propRightHand', 'defender': 'legs'}], tags=['pin', 'flash-pin'])
    rollup('roll-up', 'Roll-up', False, 'grab the opponent round the waist from behind, sit down and roll them back onto the shoulders, holding the legs.',
           'pulled backwards off the feet and rolled onto the shoulders, legs held up.')
    rollup('small-package', 'Small package', True, 'from behind, drag the opponent down and roll them up into a tight ball, trapping the legs.',
           'rolled up into a tight ball on the shoulders, knees to the chest, legs trapped.')

    # ================================================================ ground strikes (solo attacker clips; defender lies across in front)
    def drop(cid, title, keys, hit_t, zone, attach, desc, dur, end_state='lying-back'):
        L.clip(cid, title, dur, keys, AT, events=[ev(0.15, 'attack_start'), ev(hit_t, 'hit', zone=zone, attachment=attach, target='ground', reach=0.9),
               ev(hit_t, 'impact', surface='mat'), ev(hit_t + 0.02, 'land')], desc=desc, tags=['ground-attack', 'attacker', 'strike'],
               end_state=end_state, placement='center', interrupt={'windows': [[0, 0.1]]})
    # elbow drop: fall onto the right elbow across the chest
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(K(0.3, [0, 0, -0.1], 0, A.STANCE, body(hy=-0.1, turn=-20), {'rightUpperArm': r(80, 0, -60), 'rightForearm': r(130)}, feet=stand_feet([0, 0, -0.1], 0)))
    keys.append(K(0.45, [0.05, 0.25, -0.35], -60, A.STANCE, body(hy=-0.2, roll=-30), {'rightUpperArm': r(80, 0, -60), 'rightForearm': r(130), 'rightUpperLeg': r(30), 'leftUpperLeg': r(40)}))
    keys.append(K(0.6, [0.1, 0, -0.55], -90, A.LIE_BACK, body(hy=-0.75, lean=60, roll=-30), {'rightUpperArm': r(80, 0, -60), 'rightForearm': r(130)}))
    keys.append(K(0.8, [0.1, 0, -0.55], -90, A.LIE_BACK, {'hips': {'p': [0, -0.8, 0], 'r': [80, 0, -10]}}))
    keys.append(K(1.5, [0.1, 0, -0.55], -90, A.LIE_BACK, {'hips': {'p': [0, -0.83, 0], 'r': [90, 0, 0]}}))
    drop('ground.elbow-drop', 'Elbow drop', keys, 0.6, 'body', 'rightForearm',
         'Hop and fall sideways so the point of the right elbow lands across the downed opponent\'s chest. Ends lying beside them.', 1.5)
    # leg drop: jump and drop the back of the leg across the throat, landing seated
    LD = {'hips': {'p': [0, -0.78, 0.05], 'r': [25, 0, 0]}, 'spine': r(-14), 'neck': r(10),
          'rightUpperLeg': r(85, 0, 6), 'leftUpperLeg': r(80, 0, -6), 'rightLowerLeg': r(-5), 'leftLowerLeg': r(-10), 'rightUpperArm': r(-20, 0, -40), 'leftUpperArm': r(-20, 0, 40)}
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(K(0.3, [-0.35, 0, -0.75], 0, A.STANCE, body(hy=-0.25, lean=-10), ARMS_UP, feet=stand_feet([-0.35, 0, -0.75], 0)))
    keys.append(K(0.5, [-0.35, 0.55, -0.85], 0, A.STANCE, body(hy=-0.1, lean=10), ARMS_UP, {'rightUpperLeg': r(80, 0, 6), 'rightLowerLeg': r(-5), 'leftUpperLeg': r(20)}))
    keys.append(K(0.68, [-0.35, 0, -0.95], 0, LD))
    keys.append(K(1.5, [-0.35, 0, -0.95], 0, LD, {'neck': r(20)}))
    drop('ground.leg-drop', 'Leg drop', keys, 0.68, 'head', 'rightLowerLeg',
         'Step to the downed opponent\'s side, jump, swing the right leg out and drop the back of the leg across their throat, landing seated.', 1.5, end_state='sitting')
    # knee drop: drop knee-first onto the head/chest
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(K(0.3, [0.15, 0, -0.45], 0, A.STANCE, body(hy=-0.25, lean=-10), ARMS_OUT, feet=stand_feet([0.15, 0, -0.45], 0)))
    keys.append(K(0.45, [0.2, 0.35, -0.55], 0, A.STANCE, body(hy=-0.15), ARMS_OUT, {'rightUpperLeg': r(80), 'rightLowerLeg': r(-120), 'leftUpperLeg': r(10), 'leftLowerLeg': r(-60)}))
    KD = {'hips': {'p': [0, -0.4, 0.05]}, 'spine': r(-10), 'neck': r(20), 'rightUpperLeg': r(5, 0, 4), 'rightLowerLeg': r(-100), 'rightFoot': r(-55),
          'leftUpperLeg': r(85, 0, -6), 'leftLowerLeg': r(-90), 'leftFoot': r(10), 'rightUpperArm': r(30, 0, -30), 'leftUpperArm': r(30, 0, 30)}
    keys.append(K(0.6, [0.22, 0, -0.62], 0, KD))
    keys.append(K(1.0, [0.22, 0, -0.62], 0, KD))
    keys.append(K(1.4, [0.22, 0, -0.62], 0, A.STANCE, body(hy=-0.1), feet=stand_feet([0.22, 0, -0.62], 0)))
    drop('ground.knee-drop', 'Knee drop', keys, 0.6, 'head', 'rightLowerLeg',
         'Hop and drop the right knee onto the downed opponent\'s head and chest, then stand back up.', 1.4, end_state='standing')

    # lying hit reactions (solo)
    def jolt(t, k, front=False):
        base = A.LIE_FRONT if front else A.LIE_BACK
        return K(t, [0, 0, 0], 0, base, {'hips': {'p': [0, -0.83 + k * 0.05, 0], 'r': [(-90 if front else 90) + k * 6 * (-1 if front else 1), 0, 0]},
                 'neck': r((10 if front else 6) + k * 25), 'rightUpperLeg': r(k * 35, 0, 8), 'leftUpperLeg': r(k * 30, 0, -8),
                 'rightLowerLeg': r(-k * 50 - 8), 'leftLowerLeg': r(-k * 45 - 8)})
    for front, nm in ((False, 'back'), (True, 'front')):
        keys = [jolt(0, 0, front), jolt(0.08, 1.0, front), jolt(0.3, 0.6, front), jolt(0.7, 0.15, front), jolt(1.0, 0, front)]
        L.clip(f'reactions.lying-hit-{nm}', f'Hit while lying on the {nm}', 1.0, keys, A.center(),
               events=[ev(0, 'hit_received', zone='body'), ev(0.08, 'impact', surface='mat')],
               desc=f'Lying on the {nm}: jolted by an elbow drop, leg drop or stomp; legs curl up, then settle.',
               tags=['reaction', 'ground'], start_state=f'lying-{nm}', end_state=f'lying-{nm}', placement='center')

    # ================================================================ pick up a downed opponent (defender on the back, feet towards the attacker)
    d_id, a_id = 'ground.pick-up-opponent-defender', 'ground.pick-up-opponent-attacker'
    B = Body(180)
    BENTP = {'hips': {'p': [0, -0.1, 0.12], 'r': [-12, 0, 0]}, 'spine': r(-38), 'chest': r(-18), 'neck': r(30), 'head': r(6),
             'rightUpperArm': r(30, 0, -10), 'leftUpperArm': r(30, 0, 10), 'rightForearm': r(100), 'leftForearm': r(100)}
    SITUP = {'hips': {'p': [0, -0.8, 0.05], 'r': [15, 0, 0]}, 'spine': r(-10), 'neck': r(20),
             'rightUpperLeg': r(80, 0, 8), 'leftUpperLeg': r(80, 0, -8), 'rightLowerLeg': r(-30), 'leftLowerLeg': r(-30),
             'rightUpperArm': r(40, 0, -20), 'leftUpperArm': r(40, 0, 20)}
    keys = [B.pose(0, [0, 0, -1.3], 180, A.LIE_BACK)]
    keys.append(B.pose(0.5, [0, 0, -1.3], 180, A.LIE_BACK, {'neck': r(30), 'rightUpperArm': r(60, 0, 30), 'leftUpperArm': r(60, 0, -30)}))
    keys.append(B.pose(0.9, [0, 0, -1.15], 180, SITUP))
    keys.append(B.pose(1.4, [0, 0, -0.95], 180, A.STANCE, BENTP, body(hy=-0.35, hz=0.12, lean=-30, spine=(-38, 0, 0)), feet=stand_feet([0, 0, -0.85], 180, width=0.18)))
    keys.append(B.pose(1.8, [0, 0, -0.85], 180, A.STANCE, BENTP, feet=stand_feet([0, 0, -0.85], 180, width=0.15)))
    L.clip(d_id, 'Hauled to the feet', 1.8, keys, D_LB,
           events=[ev(0.5, 'grab', attachment='head'), ev(0.9, 'lift_start'), ev(1.4, 'lift_complete'), ev(1.5, 'release')],
           desc='Defender: grabbed by the head while flat on the back, hauled up to sitting and on to the feet, left bent over and groggy (set-up for power moves).',
           tags=['ground', 'defender', 'pick-up'], start_state='lying-back', end_state='bent-over', placement='center', interrupt={'windows': []})
    head = lambda t, s: P(d_id, t, 'head', (0.1 * s, 0.05, 0))
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(K(0.3, [0, 0, -0.55], 0, A.STANCE, body(hy=-0.04), feet=stand_feet([0, 0, -0.55], 0)))
    keys.append(K(0.5, [0, 0, -0.95], 0, A.STANCE, body(hy=-0.45, lean=-40), lhand=head(0.5, -1), rhand=head(0.5, 1), lfoot=plant(-0.28, -0.95), rfoot=plant(0.28, -0.9)))
    keys.append(K(0.9, [0, 0, -0.85], 0, A.STANCE, body(hy=-0.3, lean=-25), lhand=head(0.9, -1), rhand=head(0.9, 1), lfoot=plant(-0.25, -0.85), rfoot=plant(0.25, -0.8)))
    keys.append(K(1.4, [0, 0, -0.35], 0, A.STANCE, body(hy=-0.1, lean=-12), lhand=head(1.4, -1), rhand=head(1.4, 1), feet=stand_feet([0, 0, -0.35], 0, width=0.16)))
    keys.append(K(1.8, [0, 0, -0.3], 0, A.GUARD, feet=stand_feet([0, 0, -0.3], 0)))
    L.clip(a_id, 'Pick up a downed opponent', 1.8, keys, AT,
           events=[ev(0.3, 'footstep'), ev(0.5, 'grab', attachment='leftHandGrip'), ev(0.9, 'lift_start'), ev(1.4, 'lift_complete'), ev(1.5, 'release'), ev(1.75, 'recover')],
           desc='Attacker: stand over the downed opponent\'s legs, grab the head and haul them up, stepping back as they rise. Leaves them bent over in front.',
           tags=['ground', 'attacker', 'pick-up'], placement='center')
    PR.move('pair.pick-up-opponent', 'Pick up a downed opponent', 'ground', a_id, d_id,
            [ev2(0.5, 'grab', 'both'), ev2(0.9, 'lift_start', 'both'), ev2(1.4, 'lift_complete', 'both'), ev2(1.5, 'release', 'both'), ev2(1.8, 'animation_complete', 'both')],
            'Defender on the back, feet towards the attacker: hauled up by the head and left bent over 0.55 m in front of the attacker (powerbomb / fireman\'s carry set-up).',
            contacts=[{'from': 0.5, 'to': 1.5, 'attacker': 'propLeftHand+propRightHand', 'defender': 'head'}], tags=['ground', 'setup'])

    # ================================================================ drag a downed opponent by the feet (1.2 m back)
    d_id, a_id = 'ground.drag-opponent-defender', 'ground.drag-opponent-attacker'
    def d_drag(t, z, k=1.0, sw=0.0):
        return K(t, [0, 0, z], 180, A.LIE_BACK, {'rightUpperLeg': r(25 * k, 0, 6), 'leftUpperLeg': r(25 * k, 0, -6), 'rightLowerLeg': r(-5), 'leftLowerLeg': r(-5),
                 'rightUpperArm': r(0, 0, 100 + sw * 20), 'leftUpperArm': r(0, 0, -100 + sw * 20), 'neck': r(15)})
    keys = [K(0, [0, 0, -1.3], 180, A.LIE_BACK), d_drag(0.5, -1.3, 1.0), d_drag(1.0, -1.0, 1.0, 0.3), d_drag(1.5, -0.65, 1.0, -0.3), d_drag(2.0, -0.35, 1.0), d_drag(2.4, -0.3, 0.6)]
    L.clip(d_id, 'Dragged by the feet', 2.4, keys, D_LB,
           events=[ev(0.5, 'grab', attachment='feet'), ev(2.2, 'release')],
           desc='Defender: limp on the back, dragged about 1 m by the ankles, arms trailing over the head.',
           tags=['ground', 'defender', 'drag'], start_state='lying-back', end_state='lying-back', placement='center', interrupt={'windows': []})
    ank = lambda t, s: P(d_id, t, 'leftFoot' if s < 0 else 'rightFoot', (0, 0.06, 0))
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(K(0.5, [0, 0, 0.05], 0, A.STANCE, body(hy=-0.3, lean=-30), lhand=ank(0.5, -1), rhand=ank(0.5, 1), feet=stand_feet([0, 0, 0.05], 0, width=0.2)))
    for i, t in enumerate((1.0, 1.5, 2.0)):
        z = 0.05 + 0.33 * (i + 1)
        keys.append(K(t, [0, 0, z], 0, A.STANCE, body(hy=-0.25, lean=8), lhand=ank(t, -1), rhand=ank(t, 1),
                      lfoot=plant(-0.13, z + (0.1 if i % 2 else -0.1)), rfoot=plant(0.13, z + (-0.1 if i % 2 else 0.1))))
    keys.append(K(2.4, [0, 0, 1.08], 0, A.GUARD, feet=stand_feet([0, 0, 1.08], 0)))
    L.clip(a_id, 'Drag a downed opponent', 2.4, keys, AT,
           events=[ev(0.5, 'grab', attachment='leftHandGrip'), ev(1.0, 'footstep'), ev(1.5, 'footstep'), ev(2.0, 'footstep'), ev(2.2, 'release'), ev(2.35, 'recover')],
           desc='Attacker: grab both ankles and walk backwards, dragging the opponent about 1 m (towards the ropes, the corner or the middle of the ring).',
           tags=['ground', 'attacker', 'drag'], placement='center')
    PR.move('pair.drag-opponent', 'Drag a downed opponent', 'ground', a_id, d_id,
            [ev2(0.5, 'grab', 'both'), ev2(2.2, 'release', 'both'), ev2(2.4, 'animation_complete', 'both')],
            'Defender on the back, feet towards the attacker: dragged by the ankles about 1 m. Both travel the same distance.',
            contacts=[{'from': 0.5, 'to': 2.2, 'attacker': 'propLeftHand+propRightHand', 'defender': 'feet'}], tags=['ground'])
