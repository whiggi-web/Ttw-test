"""Phase 4, submissions. Each hold has an apply pair (attacker + defender, from the library lying states or a set-up)
and a hold loop pair (struggle). The hold loops start and end in the hold states, so the game can loop them while a
submission meter runs, then cut to a break or a tap-out.

Pair frame: attacker at the origin facing -z. Lying defenders: on the back with the feet towards the attacker
(frame [0, 0, -1.3, 180]), or face down with the feet towards the attacker (frame [0, 0, -1.25, 0]).
"""
from common import *
from pairs import *
from throws_lib import *

D_LB = A.Frame('mat', [0, 0, -1.3, 180])
D_LF = A.Frame('mat', [0, 0, -1.25, 0])
UP, DOWN = [0, 1, 0], [0, -1, 0]
PX, NX, PZ, NZ = [1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]

def walk_to(keys, t, root, yaw, *parts):
    keys.append(K(t, list(root), yaw, A.STANCE, *parts, feet=stand_feet(list(root), yaw)))

def hold_pair(L, PR, name, title, a_keys_fn, d_keys_fn, fa, fd, dur, a_state, d_state, desc, tags, n=4):
    """loop pair: keys functions take (t, phase 0..1) and must return identical poses at phase 0 and 1"""
    d_id, a_id = f'submissions.{name}-hold-defender', f'submissions.{name}-hold-attacker'
    ts = [dur * i / n for i in range(n + 1)]
    L.clip(d_id, f'{title}: in the hold (loop)', dur, [d_keys_fn(t, (i % n) / n) for i, t in enumerate(ts)], fd, loop=True,
           desc=f'Defender, looping: struggling in the {title.lower()}, reaching for the ropes.', tags=['submission', 'defender', 'loop', name] + tags,
           start_state=d_state, end_state=d_state, placement='center', gameplay={'rootMotion': 'none'})
    L.clip(a_id, f'{title}: hold (loop)', dur, [a_keys_fn(t, (i % n) / n) for i, t in enumerate(ts)], fa, loop=True,
           desc=f'Attacker, looping: wrenching back on the {title.lower()}.', tags=['submission', 'attacker', 'loop', name] + tags,
           start_state=a_state, end_state=a_state, placement='center', gameplay={'rootMotion': 'none'})
    PR.move(f'pair.{name}-hold', f'{title} (hold loop)', 'submissions', a_id, d_id, [ev2(dur, 'animation_complete', 'both')],
            f'Loop while the submission is applied. {desc}', interrupt={'windows': [[0, dur]], 'note': 'loop: cut to a break or tap-out at any time'},
            tags=['loop', name])

def osc(phase, amp):
    return amp * math.sin(phase * 2 * math.pi)


def build(L, PR):
    P = PR.p

    # ================================================================ figure-four leglock (defender on the back, feet towards the attacker)
    d_id, a_id = 'submissions.figure-four-defender', 'submissions.figure-four-attacker'
    def d_f4(t, writhe=0.0, sit=0.0, leg=1.0):
        return K(t, [0, 0, -1.3], 180, A.LIE_BACK, {'hips': {'p': [0, -0.83, 0], 'r': [90 - sit * 30, 0, writhe * 8]}, 'spine': r(-sit * 25), 'neck': r(sit * 20 + 10),
                 'rightUpperLeg': r(20 * leg, 0, 2), 'leftUpperLeg': r(25 * leg, 0, -12 * leg), 'rightLowerLeg': r(-30 * leg), 'leftLowerLeg': r(-10 * leg),
                 'rightUpperArm': r(sit * 50, 0, 40), 'leftUpperArm': r(sit * 50, 0, -40)})
    keys = [K(0, [0, 0, -1.3], 180, A.LIE_BACK), d_f4(0.6, leg=0.3), d_f4(1.2, leg=1.0), d_f4(1.8, writhe=0.5, sit=0.6), d_f4(2.4, sit=0.4)]
    L.clip(d_id, 'Caught in a figure-four', 2.4, keys, D_LB,
           events=[ev(0.6, 'grab', attachment='legs'), ev(1.8, 'grip_locked'), ev(1.8, 'hit_received', zone='legs')],
           desc='Defender: on the back; legs grabbed and twisted into the figure-four, sitting up in agony as it locks in.',
           tags=['submission', 'defender', 'figure-four', 'leg-work'], start_state='lying-back', end_state='figure-four-locked', placement='center', interrupt={'windows': []})
    ank = lambda t, s: P(d_id, t, 'leftFoot' if s < 0 else 'rightFoot', (0, 0.05, 0))
    SITF = {'hips': {'p': [0, -0.8, 0.05], 'r': [30, 0, 0]}, 'spine': r(-10), 'neck': r(10),
            'rightUpperLeg': r(70, 0, 10), 'leftUpperLeg': r(70, 0, -10), 'rightLowerLeg': r(-40), 'leftLowerLeg': r(-40)}
    F4 = {'rightUpperLeg': r(60, 0, 10), 'leftUpperLeg': r(30, 0, -10), 'rightLowerLeg': r(-100), 'leftLowerLeg': r(-40)}
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(K(0.6, [0, 0, -0.05], 0, A.STANCE, body(hy=-0.35, lean=-35), lhand=ank(0.6, -1), rhand=ank(0.6, 1), feet=stand_feet([0, 0, -0.05], 0, width=0.2)))
    keys.append(K(1.2, [0.05, 0, -0.05], -180, A.STANCE, body(hy=-0.25, lean=-15), F4, lhand=ank(1.2, -1), rhand=ank(1.2, 1),
                  lfoot=plant(0.15, -0.2), rfoot=air(-0.1, 0.35, -0.35)))                                        # spin round, leg through
    keys.append(K(1.8, [0, 0, 0.4], -360, A.LIE_BACK, {'hips': {'p': [0, -0.8, 0], 'r': [80, 0, 0]}}, F4, ARMS_OUT))
    keys.append(K(2.4, [0, 0, 0.42], -360, A.LIE_BACK, {'hips': {'p': [0, -0.78, 0], 'r': [70, 0, 0]}}, F4, {'rightUpperArm': r(0, 0, 60), 'leftUpperArm': r(0, 0, -60)}))
    L.clip(a_id, 'Apply a figure-four leglock', 2.4, keys, AT,
           events=[ev(0.5, 'attack_start'), ev(0.6, 'grab', attachment='leftHandGrip'), ev(1.2, 'footstep'), ev(1.8, 'land', zone='back'), ev(1.8, 'grip_locked')],
           desc='Attacker: at the opponent\'s feet, grab the legs, step through and spin round, then fall back with the legs locked in a figure-four.',
           tags=['submission', 'attacker', 'figure-four', 'leg-work'], end_state='figure-four-hold', placement='center')
    PR.move('pair.figure-four', 'Figure-four leglock', 'submissions', a_id, d_id,
            [ev2(0.5, 'attack_start', 'attacker'), ev2(0.6, 'grab', 'both'), ev2(1.8, 'grip_locked', 'both'), ev2(1.8, 'hit_received', 'defender', zone='legs'), ev2(2.4, 'animation_complete', 'both')],
            'Defender flat on the back, feet towards the attacker: the attacker spins into a figure-four and falls back to lock it.',
            contacts=[{'from': 0.6, 'to': 1.8, 'attacker': 'propLeftHand+propRightHand', 'defender': 'feet'}, {'from': 1.8, 'to': 2.4, 'attacker': 'legs', 'defender': 'legs'}],
            tags=['figure-four', 'leg-work'])
    hold_pair(L, PR, 'figure-four', 'Figure-four',
              lambda t, ph: K(t, [0, 0, 0.42], 0, A.LIE_BACK, {'hips': {'p': [0, -0.78, 0], 'r': [70 + osc(ph, 8), 0, 0]}}, F4,
                              {'rightUpperArm': r(0, 0, 60 + osc(ph, 15)), 'leftUpperArm': r(0, 0, -60 - osc(ph, 15))}),
              lambda t, ph: d_f4(t, writhe=osc(ph, 0.8), sit=0.4 + osc(ph * 2, 0.25)),
              A.Frame('mat', [0, 0, 0.42, 0]), D_LB, 2.4, 'figure-four-hold', 'figure-four-locked', 'Both on the mat, legs interlocked.', ['leg-work'])

    # ================================================================ sharpshooter and Boston crab (turn the opponent over)
    def turnover(name, title, cross, a_desc, d_desc):
        d_id, a_id = f'submissions.{name}-defender', f'submissions.{name}-attacker'
        B = Body(180)
        legs_up = lambda k: {'rightUpperLeg': r(-25 * k, 0, 6 if not cross else -10), 'leftUpperLeg': r(-25 * k, 0, -6 if not cross else 10),
                             'rightLowerLeg': r(-(30 if not cross else 100) * k), 'leftLowerLeg': r(-(30 if not cross else 100) * k)}
        keys = [B.pose(0, [0, 0, -1.3], 180, A.LIE_BACK)]
        keys.append(B.pose(0.6, [0, 0, -1.3], 180, A.LIE_BACK, {'rightUpperLeg': r(60, 0, 10), 'leftUpperLeg': r(60, 0, -10), 'rightLowerLeg': r(-80), 'leftLowerLeg': r(-80)}))
        keys.append(B.key(1.0, [0, 0.33, -1.3], NZ, PX, {'rightUpperArm': r(40, 0, -12), 'leftUpperArm': r(40, 0, 12), 'rightForearm': r(30), 'leftForearm': r(30)}, {'rightUpperLeg': r(50, 0, 10), 'leftUpperLeg': r(50, 0, -10), 'rightLowerLeg': r(-80), 'leftLowerLeg': r(-80)}))
        keys.append(B.key(1.4, [0, 0.16, -1.3], NZ, DOWN, A.only(A.LIE_FRONT, A.ARMS), legs_up(0.6)))
        keys.append(B.key(1.9, [0, 0.16, -1.3], [0, 0.25, -0.97], [0, -0.97, -0.25], A.only(A.LIE_FRONT, A.ARMS), legs_up(1.0),
                          {'spine': r(15), 'chest': r(10), 'neck': r(-25)}))
        L.clip(d_id, f'Caught in the {title.lower()}', 1.9, keys, D_LB,
               events=[ev(0.6, 'grab', attachment='legs'), ev(1.4, 'land', zone='front'), ev(1.9, 'grip_locked'), ev(1.9, 'hit_received', zone='back')],
               desc=f'Defender: {d_desc}', tags=['submission', 'defender', name, 'back-work'], start_state='lying-back', end_state=f'{name}-locked',
               placement='center', interrupt={'windows': []})
        legs = lambda t: P(d_id, t, 'leftLowerLeg' if cross else 'rightFoot', (0, -0.1, 0) if cross else (0, 0.0, 0))
        legs2 = lambda t: P(d_id, t, 'rightFoot' if cross else 'leftFoot', (0, 0.0, 0))
        keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
        keys.append(K(0.6, [0, 0, -0.1], 0, A.STANCE, body(hy=-0.35, lean=-35), lhand=legs2(0.6), rhand=legs(0.6), feet=stand_feet([0, 0, -0.1], 0, width=0.22)))
        keys.append(K(1.0, [0, 0, -0.55], 90, A.STANCE, body(hy=-0.2, lean=-20), lhand=legs2(1.0), rhand=legs(1.0), lfoot=plant(-0.05, -0.75), rfoot=plant(0.1, -0.35)))
        CRAB = body(hy=-0.45 if cross else -0.3, lean=18 if cross else 25, neck=(-10, 0, 0))
        keys.append(K(1.4, [0, 0, -0.85], 180, A.STANCE, CRAB, lhand=legs2(1.4), rhand=legs(1.4), feet=stand_feet([0, 0, -0.85], 180, width=0.25)))
        keys.append(K(1.9, [0, 0, -0.9], 180, A.STANCE, CRAB, lhand=legs2(1.9), rhand=legs(1.9), feet=stand_feet([0, 0, -0.9], 180, width=0.26)))
        L.clip(a_id, f'Apply the {title.lower()}', 1.9, keys, AT,
               events=[ev(0.5, 'attack_start'), ev(0.6, 'grab', attachment='leftHandGrip'), ev(1.0, 'footstep'), ev(1.4, 'footstep'), ev(1.9, 'grip_locked')],
               desc=f'Attacker: {a_desc}', tags=['submission', 'attacker', name, 'back-work'], end_state=f'{name}-hold', placement='center')
        PR.move(f'pair.{name}', title, 'submissions', a_id, d_id,
                [ev2(0.5, 'attack_start', 'attacker'), ev2(0.6, 'grab', 'both'), ev2(1.4, 'land', 'defender', zone='front'), ev2(1.9, 'grip_locked', 'both'),
                 ev2(1.9, 'hit_received', 'defender', zone='back'), ev2(1.9, 'animation_complete', 'both')],
                f'Defender flat on the back, feet towards the attacker. {d_desc}',
                contacts=[{'from': 0.6, 'to': 1.9, 'attacker': 'propLeftHand+propRightHand', 'defender': 'legs'}], tags=[name, 'back-work'])
        fa = A.Frame('mat', [0, 0, -0.9, 180])
        fd = A.Frame('mat', [0, 0, -1.3, 180])
        LOCKD = end_pose(L, d_id); LOCKA = end_pose(L, a_id)
        hold_pair(L, PR, name, title,
                  lambda t, ph: K(t, [0, 0, -0.9], 180, LOCKA, body(hy=(-0.45 if cross else -0.3) - osc(ph, 0.05), lean=(18 if cross else 25) + osc(ph, 10)),
                                  lhand=P(d_id, 1.9, 'rightFoot' if cross else 'leftFoot'), rhand=P(d_id, 1.9, 'leftLowerLeg' if cross else 'rightFoot', (0, -0.1, 0) if cross else (0, 0, 0)),
                                  feet=stand_feet([0, 0, -0.9], 180, width=0.26)),
                  lambda t, ph: K(t, [0, 0, -1.3], 180, LOCKD, {'neck': r(-25 + osc(ph, 15), osc(ph * 2, 20), 0), 'rightUpperArm': r(0, 0, 80 + osc(ph, 30)), 'leftUpperArm': r(0, 0, -80 + osc(ph, 20))}),
                  fa, fd, 2.4, f'{name}-hold', f'{name}-locked', 'Defender face down with the legs bent back; attacker sitting back over them.', ['back-work'])
    turnover('sharpshooter', 'Sharpshooter', True,
             'step between the opponent\'s legs, weave them round the left leg, turn them face down and sit back.',
             'legs wrapped round the attacker\'s leg, turned face down and bent back into the sharpshooter.')
    turnover('boston-crab', 'Boston crab', False,
             'grab both ankles under the arms, step over and turn the opponent face down, then sit back.',
             'ankles trapped, turned face down and folded back into a Boston crab.')

    # ================================================================ armbar (defender on the back; attacker sits across the chest)
    d_id, a_id = 'submissions.armbar-defender', 'submissions.armbar-attacker'
    def d_arm(t, k=1.0, wr=0.0):
        return K(t, [0, 0, -1.3], 180, A.LIE_BACK, {'leftUpperArm': r(95 * k, 0, -40 * (1 - k)), 'leftForearm': r(5), 'neck': r(15 + wr * 15, 0, -wr * 20),
                 'hips': {'p': [0, -0.83, 0], 'r': [90, 0, wr * 8]}, 'rightUpperArm': r(20 * k, 0, 50)})
    keys = [K(0, [0, 0, -1.3], 180, A.LIE_BACK), d_arm(0.8, 0.5), d_arm(1.4, 1.0), d_arm(2.0, 1.0, 0.6)]
    L.clip(d_id, 'Caught in an armbar', 2.0, keys, D_LB,
           events=[ev(0.8, 'grab', attachment='leftHand'), ev(1.4, 'grip_locked'), ev(1.5, 'hit_received', zone='arms')],
           desc='Defender: on the back; the left arm is pulled straight up and hyperextended across the attacker\'s hips.',
           tags=['submission', 'defender', 'armbar', 'arm-work'], start_state='lying-back', end_state='armbar-locked', placement='center', interrupt={'windows': []})
    wrist = lambda t: P(d_id, t, 'leftHand', (0, 0, 0))
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    walk_to(keys, 0.5, [0.45, 0, -0.75], 20, body(hy=-0.03))
    keys.append(K(0.8, [0.45, 0, -1.45], 90, A.STANCE, body(hy=-0.35, lean=-30), lhand=wrist(0.8), rhand=wrist(0.8), feet=stand_feet([0.45, 0, -1.45], 90, width=0.2)))
    ARMB = {'hips': {'p': [0, -0.78, 0], 'r': [82, 0, 0]}, 'spine': r(-10), 'neck': r(20),
            'rightUpperLeg': r(22, 0, 8), 'leftUpperLeg': r(30, 0, -8), 'rightLowerLeg': r(-10), 'leftLowerLeg': r(-25)}
    keys.append(K(1.4, [0.38, 0, -1.62], 90, ARMB, lhand=wrist(1.4), rhand=wrist(1.4)))
    keys.append(K(2.0, [0.38, 0, -1.62], 90, ARMB, {'hips': {'p': [0, -0.78, 0], 'r': [76, 0, 0]}}, lhand=wrist(2.0), rhand=wrist(2.0)))
    L.clip(a_id, 'Apply a cross armbar', 2.0, keys, AT,
           events=[ev(0.5, 'footstep'), ev(0.7, 'attack_start'), ev(0.8, 'grab', attachment='leftHandGrip'), ev(1.4, 'land', zone='back'), ev(1.4, 'grip_locked')],
           desc='Attacker: walk round to the opponent\'s left shoulder, take the wrist, sit down beside them with the legs across the chest and lean back, straightening the arm.',
           tags=['submission', 'attacker', 'armbar', 'arm-work'], end_state='armbar-hold', placement='center')
    PR.move('pair.armbar', 'Cross armbar', 'submissions', a_id, d_id,
            [ev2(0.7, 'attack_start', 'attacker'), ev2(0.8, 'grab', 'both'), ev2(1.4, 'grip_locked', 'both'), ev2(1.5, 'hit_received', 'defender', zone='arms'), ev2(2.0, 'animation_complete', 'both')],
            'Defender flat on the back: cross armbar from the left side.', contacts=[{'from': 0.8, 'to': 2.0, 'attacker': 'propLeftHand+propRightHand', 'defender': 'leftHand'}],
            tags=['armbar', 'arm-work'])
    fa = A.Frame('mat', [0.38, 0, -1.62, 90])
    hold_pair(L, PR, 'armbar', 'Cross armbar',
              lambda t, ph: K(t, [0.38, 0, -1.62], 90, ARMB, {'hips': {'p': [0, -0.78, 0], 'r': [76 + osc(ph, 6), 0, 0]}}, lhand=wrist(2.0), rhand=wrist(2.0)),
              lambda t, ph: d_arm(t, 1.0, 0.6 + osc(ph, 0.4)), fa, D_LB, 2.0, 'armbar-hold', 'armbar-locked', 'Attacker lying back across the chest.', ['arm-work'])

    # ================================================================ camel clutch (defender face down, feet towards the attacker)
    d_id, a_id = 'submissions.camel-clutch-defender', 'submissions.camel-clutch-attacker'
    def d_cc(t, k=1.0, wr=0.0):
        return K(t, [0, 0, -1.25], 0, A.LIE_FRONT, {'spine': r(22 * k), 'chest': r(18 * k), 'neck': r(-20 * k, wr * 15, 0), 'head': r(-10 * k),
                 'hips': {'p': [0, -0.84, 0], 'r': [-90, 0, wr * 5]},
                 'rightUpperArm': r(-30 * k, 0, 40 + 40 * (1 - k)), 'leftUpperArm': r(-30 * k, 0, -40 - 40 * (1 - k)), 'rightForearm': r(40 * k), 'leftForearm': r(40 * k)})
    keys = [K(0, [0, 0, -1.25], 0, A.LIE_FRONT), d_cc(0.9, 0.2), d_cc(1.5, 1.0), d_cc(2.0, 1.0, 0.5)]
    L.clip(d_id, 'Caught in a camel clutch', 2.0, keys, D_LF,
           events=[ev(0.9, 'grab', attachment='head'), ev(1.5, 'grip_locked'), ev(1.55, 'hit_received', zone='back')],
           desc='Defender: face down; sat on, arms draped over the attacker\'s knees and the chin wrenched back, bending the spine.',
           tags=['submission', 'defender', 'camel-clutch', 'back-work'], start_state='lying-front', end_state='camel-clutch-locked', placement='center', interrupt={'windows': []})
    chin = lambda t, s: P(d_id, t, 'head', (0.08 * s, -0.08, -0.08))
    CCS = {'hips': {'p': [0, -0.58, 0.04], 'r': [-10, 0, 0]}, 'spine': r(10), 'neck': r(10),
           'rightUpperLeg': r(70, 0, 30), 'leftUpperLeg': r(70, 0, -30), 'rightLowerLeg': r(-100), 'leftLowerLeg': r(-100)}
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    walk_to(keys, 0.5, [0, 0, -0.55], 0, body(hy=-0.04))
    keys.append(K(0.9, [0, 0, -1.0], 0, A.STANCE, body(hy=-0.4, lean=-20), lfoot=plant(-0.38, -1.0), rfoot=plant(0.38, -1.0)))
    keys.append(K(1.5, [0, 0, -1.05], 0, CCS, lhand=chin(1.5, -1), rhand=chin(1.5, 1), lfoot=plant(-0.42, -1.25), rfoot=plant(0.42, -1.25)))
    keys.append(K(2.0, [0, 0, -1.05], 0, CCS, {'hips': {'p': [0, -0.58, 0.04], 'r': [-2, 0, 0]}, 'spine': r(18)}, lhand=chin(2.0, -1), rhand=chin(2.0, 1),
                  lfoot=plant(-0.42, -1.25), rfoot=plant(0.42, -1.25)))
    L.clip(a_id, 'Apply a camel clutch', 2.0, keys, AT,
           events=[ev(0.5, 'footstep'), ev(0.8, 'attack_start'), ev(1.2, 'land', zone='seat'), ev(1.3, 'grab', attachment='leftHandGrip'), ev(1.5, 'grip_locked')],
           desc='Attacker: straddle the face-down opponent, sit on the lower back, drape their arms over the knees and pull the chin back.',
           tags=['submission', 'attacker', 'camel-clutch', 'back-work'], end_state='camel-clutch-hold', placement='center')
    PR.move('pair.camel-clutch', 'Camel clutch', 'submissions', a_id, d_id,
            [ev2(0.8, 'attack_start', 'attacker'), ev2(1.3, 'grab', 'both'), ev2(1.5, 'grip_locked', 'both'), ev2(1.55, 'hit_received', 'defender', zone='back'), ev2(2.0, 'animation_complete', 'both')],
            'Defender face down, feet towards the attacker: camel clutch.', contacts=[{'from': 1.3, 'to': 2.0, 'attacker': 'propLeftHand+propRightHand', 'defender': 'chin'}],
            tags=['camel-clutch', 'back-work'])
    fa = A.Frame('mat', [0, 0, -1.05, 0])
    hold_pair(L, PR, 'camel-clutch', 'Camel clutch',
              lambda t, ph: K(t, [0, 0, -1.05], 0, CCS, {'hips': {'p': [0, -0.58, 0.04], 'r': [-2 + osc(ph, 6), 0, 0]}, 'spine': r(18 + osc(ph, 6))},
                              lhand=chin(2.0, -1), rhand=chin(2.0, 1), lfoot=plant(-0.42, -1.25), rfoot=plant(0.42, -1.25)),
              lambda t, ph: d_cc(t, 1.0 + osc(ph, 0.1), 0.5 + osc(ph * 2, 0.5)), fa, D_LF, 2.0, 'camel-clutch-hold', 'camel-clutch-locked',
              'Attacker sitting on the opponent\'s back.', ['back-work'])

    # ================================================================ crossface (defender face down; attacker at the left side)
    d_id, a_id = 'submissions.crossface-defender', 'submissions.crossface-attacker'
    def d_cf(t, k=1.0, wr=0.0):
        return K(t, [0, 0, -1.25], 0, A.LIE_FRONT, {'neck': r(-25 * k, -25 * k + wr * 10, 0), 'spine': r(8 * k), 'hips': {'p': [0, -0.84, 0], 'r': [-90, 0, wr * 4]},
                 'leftUpperArm': r(-10, 0, -120 * k - 80 * (1 - k)), 'leftForearm': r(10)})
    keys = [K(0, [0, 0, -1.25], 0, A.LIE_FRONT), d_cf(1.0, 0.3), d_cf(1.5, 1.0), d_cf(2.0, 1.0, 0.6)]
    L.clip(d_id, 'Caught in a crossface', 2.0, keys, D_LF,
           events=[ev(1.0, 'grab', attachment='leftHand'), ev(1.5, 'grip_locked'), ev(1.55, 'hit_received', zone='head')],
           desc='Defender: face down; the left arm trapped and the face cranked back and to the side by the attacker\'s forearm.',
           tags=['submission', 'defender', 'crossface', 'neck-work'], start_state='lying-front', end_state='crossface-locked', placement='center', interrupt={'windows': []})
    face = lambda t, s: P(d_id, t, 'head', (0.09 * s, -0.04, -0.1))
    CFA = {'hips': {'p': [0, -0.68, 0.0], 'r': [-75, 0, -20]}, 'spine': r(-5), 'neck': r(30),
           'rightUpperLeg': r(20, 0, 20), 'leftUpperLeg': r(40, 0, -20), 'rightLowerLeg': r(-80), 'leftLowerLeg': r(-40), 'rightFoot': r(-50), 'leftFoot': r(-50)}
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    walk_to(keys, 0.6, [-0.55, 0, -0.9], 0, body(hy=-0.03))
    keys.append(K(1.0, [-0.5, 0, -1.25], 0, A.STANCE, body(hy=-0.45, lean=-35), lhand=face(1.0, -1), rhand=face(1.0, 1), feet=stand_feet([-0.5, 0, -1.25], 0, width=0.2)))
    CFR = [-0.3, 0, -1.4]
    cff = dict(lfoot=air(*[rel(CFR, -20, -0.25, 0, 0.75)[0], 0.13, rel(CFR, -20, -0.25, 0, 0.75)[2]], pitch=-60),
               rfoot=air(*[rel(CFR, -20, 0.2, 0, 0.7)[0], 0.13, rel(CFR, -20, 0.2, 0, 0.7)[2]], pitch=-60))
    keys.append(K(1.5, CFR, -20, CFA, lhand=face(1.5, -1), rhand=face(1.5, 1), **cff))
    keys.append(K(2.0, CFR, -20, CFA, {'hips': {'p': [0, -0.66, 0.0], 'r': [-65, 0, -20]}}, lhand=face(2.0, -1), rhand=face(2.0, 1), **cff))
    L.clip(a_id, 'Apply a crossface', 2.0, keys, AT,
           events=[ev(0.6, 'footstep'), ev(0.9, 'attack_start'), ev(1.0, 'grab', attachment='rightHandGrip'), ev(1.5, 'grip_locked')],
           desc='Attacker: kneel at the face-down opponent\'s left shoulder, trap the arm, lock the hands across the face and roll back, cranking the neck.',
           tags=['submission', 'attacker', 'crossface', 'neck-work'], end_state='crossface-hold', placement='center')
    PR.move('pair.crossface', 'Crossface', 'submissions', a_id, d_id,
            [ev2(0.9, 'attack_start', 'attacker'), ev2(1.0, 'grab', 'both'), ev2(1.5, 'grip_locked', 'both'), ev2(1.55, 'hit_received', 'defender', zone='head'), ev2(2.0, 'animation_complete', 'both')],
            'Defender face down: crossface from the left side.', contacts=[{'from': 1.0, 'to': 2.0, 'attacker': 'propLeftHand+propRightHand', 'defender': 'head'}], tags=['crossface'])
    fa = A.Frame('mat', [-0.3, 0, -1.4, -20])
    hold_pair(L, PR, 'crossface', 'Crossface',
              lambda t, ph: K(t, [-0.3, 0, -1.4], -20, CFA, {'hips': {'p': [0, -0.66, 0.0], 'r': [-65 + osc(ph, 8), 0, -20]}}, lhand=face(2.0, -1), rhand=face(2.0, 1), **cff),
              lambda t, ph: d_cf(t, 1.0 + osc(ph, 0.1), 0.6 + osc(ph * 2, 0.4)), fa, D_LF, 2.0, 'crossface-hold', 'crossface-locked', 'Attacker lying across the shoulders.', ['neck-work'])

    # ================================================================ ankle lock (defender face down, feet towards the attacker)
    d_id, a_id = 'submissions.ankle-lock-defender', 'submissions.ankle-lock-attacker'
    def d_al(t, k=1.0, wr=0.0):
        return K(t, [0, 0, -1.25], 0, A.LIE_FRONT, {'rightUpperLeg': r(-20 * k), 'rightLowerLeg': r(-60 * k), 'neck': r(-15 * k - wr * 10, 0, 0), 'spine': r(10 * wr),
                 'rightUpperArm': r(-60 * k, 0, 40), 'leftUpperArm': r(-60 * k, 0, -40), 'rightForearm': r(60 * k), 'leftForearm': r(60 * k)})
    keys = [K(0, [0, 0, -1.25], 0, A.LIE_FRONT), d_al(0.6, 0.5), d_al(1.2, 1.0), d_al(1.8, 1.0, 0.7)]
    L.clip(d_id, 'Caught in an ankle lock', 1.8, keys, D_LF,
           events=[ev(0.5, 'grab', attachment='rightFoot'), ev(1.2, 'grip_locked'), ev(1.25, 'hit_received', zone='legs')],
           desc='Defender: face down; the right ankle is grabbed, the leg lifted and the foot twisted; push up on the hands in pain.',
           tags=['submission', 'defender', 'ankle-lock', 'leg-work'], start_state='lying-front', end_state='ankle-lock-locked', placement='center', interrupt={'windows': []})
    ankle = lambda t: P(d_id, t, 'rightFoot', (0, 0.03, 0))
    SITB = {'hips': {'p': [0, -0.8, 0.05], 'r': [35, 0, 0]}, 'spine': r(-10), 'neck': r(20),
            'rightUpperLeg': r(60, 0, 10), 'leftUpperLeg': r(70, 0, -15), 'rightLowerLeg': r(-30), 'leftLowerLeg': r(-50)}
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(K(0.5, [0.12, 0, -0.1], 0, A.STANCE, body(hy=-0.4, lean=-35), lhand=ankle(0.5), rhand=ankle(0.5), feet=stand_feet([0.12, 0, -0.1], 0, width=0.2)))
    keys.append(K(0.8, [0.12, 0, -0.05], 0, A.STANCE, body(hy=-0.2, lean=-5), lhand=ankle(0.8), rhand=ankle(0.8), feet=stand_feet([0.12, 0, -0.05], 0)))
    keys.append(K(1.2, [0.15, 0, 0.1], 0, SITB, lhand=ankle(1.2), rhand=ankle(1.2)))
    keys.append(K(1.8, [0.15, 0, 0.12], 0, SITB, {'hips': {'p': [0, -0.8, 0.05], 'r': [50, 0, 0]}}, lhand=ankle(1.8), rhand=ankle(1.8)))
    L.clip(a_id, 'Apply an ankle lock', 1.8, keys, AT,
           events=[ev(0.4, 'attack_start'), ev(0.5, 'grab', attachment='leftHandGrip'), ev(1.2, 'land', zone='seat'), ev(1.2, 'grip_locked')],
           desc='Attacker: grab the face-down opponent\'s right ankle, lift it, sit down and fall back, wrenching the foot.',
           tags=['submission', 'attacker', 'ankle-lock', 'leg-work'], end_state='ankle-lock-hold', placement='center')
    PR.move('pair.ankle-lock', 'Ankle lock', 'submissions', a_id, d_id,
            [ev2(0.4, 'attack_start', 'attacker'), ev2(0.5, 'grab', 'both'), ev2(1.2, 'grip_locked', 'both'), ev2(1.25, 'hit_received', 'defender', zone='legs'), ev2(1.8, 'animation_complete', 'both')],
            'Defender face down, feet towards the attacker: ankle lock.', contacts=[{'from': 0.5, 'to': 1.8, 'attacker': 'propLeftHand+propRightHand', 'defender': 'rightFoot'}],
            tags=['ankle-lock', 'leg-work'])
    fa = A.Frame('mat', [0.15, 0, 0.12, 0])
    hold_pair(L, PR, 'ankle-lock', 'Ankle lock',
              lambda t, ph: K(t, [0.15, 0, 0.12], 0, SITB, {'hips': {'p': [0, -0.8, 0.05], 'r': [50 + osc(ph, 10), 0, 0]}}, lhand=ankle(1.8), rhand=ankle(1.8)),
              lambda t, ph: d_al(t, 1.0, 0.7 + osc(ph, 0.3)), fa, D_LF, 2.0, 'ankle-lock-hold', 'ankle-lock-locked', 'Attacker sitting back with the ankle.', ['leg-work'])

    # ================================================================ sleeper hold and abdominal stretch (from the rear waistlock)
    fa0, ra, ya, pa = from_setup(L, 'grappling.rear-waistlock-attacker')
    fd0, rd, yd, pd = from_setup(L, 'grappling.rear-waistlock-defender')
    KNEELS = {'hips': {'p': [0, -0.515, 0.04]}, 'rightUpperLeg': r(10, 0, 4), 'leftUpperLeg': r(10, 0, -4), 'rightLowerLeg': r(-100), 'leftLowerLeg': r(-100),
              'rightFoot': r(-55), 'leftFoot': r(-55)}
    d_id, a_id = 'submissions.sleeper-hold-defender', 'submissions.sleeper-hold-attacker'
    def d_sl(t, sink=1.0, fade=0.0):
        root = [rd[0], 0, rd[2]]
        if sink < 0.5:
            return K(t, root, yd, A.STANCE, body(hy=-0.05 - sink * 0.3, lean=10, neck=(-20, 0, 0)), {'rightUpperArm': r(60, 0, -20), 'leftUpperArm': r(60, 0, 20), 'rightForearm': r(110), 'leftForearm': r(110)},
                     feet=stand_feet(root, yd))
        return K(t, root, yd, KNEELS, body(hy=-0.49, hz=0.04, lean=6 + fade * 10, neck=(-15 + fade * 30, 0, fade * 10)),
                 {'rightUpperArm': r(60 - fade * 50, 0, -20), 'leftUpperArm': r(60 - fade * 50, 0, 20), 'rightForearm': r(110 - fade * 80), 'leftForearm': r(110 - fade * 80)})
    keys = [K(0, [rd[0], 0, rd[2]], yd, pd, feet=stand_feet([rd[0], 0, rd[2]], yd)), d_sl(0.4, 0.2), d_sl(0.9, 0.4), d_sl(1.4, 1.0), d_sl(2.0, 1.0, 0.2)]
    L.clip(d_id, 'Caught in a sleeper hold', 2.0, keys, fd0,
           events=[ev(0.3, 'grab', attachment='neck'), ev(0.5, 'grip_locked'), ev(1.4, 'land', zone='knees')],
           desc='Defender: grabbed from behind, the arm slides round the neck; claws at it and sinks to the knees.',
           tags=['submission', 'defender', 'sleeper', 'neck-work'], start_state='rear-locked', end_state='sleeper-locked', placement='center', interrupt={'windows': []})
    neck = lambda t, s: P(d_id, t, 'neck', (0.1 * s, 0.02, -0.08))
    def a_sl(t, kneel, ph=0.0, tt=None):
        root = [ra[0], 0, ra[2] + 0.05]
        if not kneel:
            return K(t, root, ya, A.STANCE, body(hy=-0.1, lean=-6), lhand=neck(t, 1), rhand=neck(t, -1), feet=stand_feet(root, ya, width=0.16))
        tn = tt if tt is not None else min(t, 2.0)
        return K(t, root, ya, KNEELS, body(hy=-0.5 - osc(ph, 0.02), hz=0.04, lean=-6 + osc(ph, 6)), lhand=neck(tn, 1), rhand=neck(tn, -1))
    fa_sl = A.Frame('mat', [ra[0], 0, ra[2] + 0.05, ya])
    keys = [K(0, [ra[0], 0, ra[2]], ya, pa, feet=stand_feet([ra[0], 0, ra[2]], ya, width=0.16)), a_sl(0.4, False), a_sl(0.9, False), a_sl(1.4, True), a_sl(2.0, True)]
    L.clip(a_id, 'Apply a sleeper hold', 2.0, keys, fa0,
           events=[ev(0.2, 'attack_start'), ev(0.3, 'grab', attachment='rightHandGrip'), ev(0.5, 'grip_locked'), ev(1.4, 'land', zone='knees')],
           desc='Attacker: from the rear waistlock, wrap the right arm round the neck, lock it with the left and ride the opponent down to their knees.',
           tags=['submission', 'attacker', 'sleeper', 'neck-work'], start_state='rear-lock-hold', end_state='sleeper-hold', placement='center')
    PR.move('pair.sleeper-hold', 'Sleeper hold', 'submissions', a_id, d_id,
            [ev2(0.2, 'attack_start', 'attacker'), ev2(0.3, 'grab', 'both'), ev2(0.5, 'grip_locked', 'both'), ev2(1.4, 'land', 'both', zone='knees'), ev2(2.0, 'animation_complete', 'both')],
            'From the rear waistlock: sleeper hold, both sinking to the knees.', contacts=[{'from': 0.3, 'to': 2.0, 'attacker': 'rightForearm+propLeftHand', 'defender': 'neck'}],
            tags=['sleeper', 'neck-work'])
    hold_pair(L, PR, 'sleeper-hold', 'Sleeper hold',
              lambda t, ph: a_sl(t, True, ph, tt=2.0), lambda t, ph: d_sl(t, 1.0, 0.25 + osc(ph, 0.2)),
              fa_sl, fd0, 2.4, 'sleeper-hold', 'sleeper-locked', 'Both kneeling, the defender fading.', ['neck-work'])

    d_id, a_id = 'submissions.abdominal-stretch-defender', 'submissions.abdominal-stretch-attacker'
    def d_ab(t, k=1.0, wr=0.0):
        root = [rd[0], 0, rd[2]]
        return K(t, root, yd, A.STANCE, body(hy=-0.08 * k, roll=-28 * k - wr * 6, lean=4, spine=(0, 0, -12 * k), neck=(0, 0, -10 * k)),
                 {'leftUpperArm': r(20, 0, -150 * k - 20 * (1 - k)), 'rightUpperArm': r(30, 0, -30)}, lfoot=plant(rd[0] - 0.2, rd[2]), rfoot=plant(rd[0] + 0.15, rd[2]))
    keys = [K(0, [rd[0], 0, rd[2]], yd, pd, feet=stand_feet([rd[0], 0, rd[2]], yd)), d_ab(0.5, 0.3), d_ab(1.0, 1.0), d_ab(1.6, 1.0, 0.8)]
    L.clip(d_id, 'Caught in an abdominal stretch', 1.6, keys, fd0,
           events=[ev(0.4, 'grab', attachment='leftHand'), ev(1.0, 'grip_locked'), ev(1.05, 'hit_received', zone='body')],
           desc='Defender: left leg hooked and left arm pulled over the attacker\'s neck; stretched sideways, the ribs pulled open.',
           tags=['submission', 'defender', 'abdominal-stretch'], start_state='rear-locked', end_state='abdominal-stretch-locked', placement='center', interrupt={'windows': []})
    larm = lambda t: P(d_id, t, 'leftHand', (0, 0, 0))
    def a_ab(t, k=1.0, ph=0.0, tt=None):
        root = [rd[0] - 0.25 * k, 0, ra[2] + 0.1]
        return K(t, root, ya - 20 * k, A.STANCE, body(hy=-0.12, roll=10 * k + osc(ph, 4), lean=-8), lhand=larm(tt if tt is not None else (1.0 if t > 1.0 else t)),
                 lfoot=plant(root[0] - 0.2, root[2] - 0.05), rfoot=air(rd[0] - 0.35, 0.12, rd[2] + 0.05) if k > 0.5 else plant(root[0] + 0.15, root[2]))
    keys = [K(0, [ra[0], 0, ra[2]], ya, pa, feet=stand_feet([ra[0], 0, ra[2]], ya, width=0.16)), a_ab(0.5, 0.4), a_ab(1.0, 1.0), a_ab(1.6, 1.0)]
    L.clip(a_id, 'Apply an abdominal stretch', 1.6, keys, fa0,
           events=[ev(0.3, 'attack_start'), ev(0.4, 'grab', attachment='leftHandGrip'), ev(0.8, 'footstep'), ev(1.0, 'grip_locked')],
           desc='Attacker: from behind, step the right leg over the opponent\'s left leg, drag their left arm over the head and lean away, stretching their side.',
           tags=['submission', 'attacker', 'abdominal-stretch'], start_state='rear-lock-hold', end_state='abdominal-stretch-hold', placement='center')
    PR.move('pair.abdominal-stretch', 'Abdominal stretch', 'submissions', a_id, d_id,
            [ev2(0.3, 'attack_start', 'attacker'), ev2(0.4, 'grab', 'both'), ev2(1.0, 'grip_locked', 'both'), ev2(1.05, 'hit_received', 'defender', zone='body'), ev2(1.6, 'animation_complete', 'both')],
            'From the rear waistlock: standing abdominal stretch.', contacts=[{'from': 0.4, 'to': 1.6, 'attacker': 'propLeftHand', 'defender': 'leftHand'}],
            tags=['abdominal-stretch'])
    hold_pair(L, PR, 'abdominal-stretch', 'Abdominal stretch',
              lambda t, ph: a_ab(t, 1.0, ph, tt=1.0), lambda t, ph: d_ab(t, 1.0, 0.8 + osc(ph, 0.4)), A.Frame('mat', [rd[0] - 0.25, 0, ra[2] + 0.1, ya - 20]), fd0, 2.0, 'abdominal-stretch-hold', 'abdominal-stretch-locked',
              'Standing, the attacker leaning away.', ['stretch'])
