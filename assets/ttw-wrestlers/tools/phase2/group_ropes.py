"""Phase 2, group B: working the ropes. Holding, leaning, running and rebounding, whips, tangles, draped and hung
positions, the springboard launch and being pulled over the top rope.

Rope frame: rope line along X at z = 0, ring towards +z, mat at y = 0. Yaw 0 faces the ropes from inside,
yaw 180 has the ropes behind. For yaw 0 the wrestler's right is +x; for yaw 180 it is -x.
"""
from common import *

D_ = A.DROP
Z_LEAN = 0.42          # batch 1 rope-lean: feet 0.42 m from the rope line, ropes behind
Z_HOLD = 0.36          # facing the ropes, hands on the top rope

def hold_hands(root, w=0.3, h=ROPE_TOP, yaw=0):
    """left and right hand on a rope in front (yaw 0) or behind (yaw 180)"""
    a = rel(root, yaw, -w, 0, 0); b = rel(root, yaw, w, 0, 0)
    return grip(a[0], h, 0), grip(b[0], h, 0)

def hold_key(t, z=Z_HOLD, lean=-8, hy=-0.03, look=0, shift=0.0, x=0.0, yaw=0, neck=0):
    root = [x, 0, z]
    return K(t, root, yaw, A.STANCE, body(hy=hy, hx=shift, lean=lean, spine=(-4, 0, 0), neck=(neck, look * 0.6, 0), head=(0, look * 0.4, 0)),
             hands=hold_hands(root, yaw=yaw), feet=stand_feet(root, yaw, width=0.13))

def lean_key(t, z=Z_LEAN, *extra):
    root = [0, 0, z]
    return K(t, root, 180, A.LEAN, *extra, feet=stand_feet(root, 180, width=0.12))

def run_key(t, z, phase, yaw=0, x=0.0, *extra):
    return K(t, [x, 0, z], yaw, run_pose(phase), *extra)

# clothesline / crossbody arm shapes
CLOTHES_R = {'rightUpperArm': r(10, 0, 92), 'rightForearm': r(6), 'chest': r(0, -10, 0)}
CROSS_ARMS = {'rightUpperArm': r(30, 0, 100), 'leftUpperArm': r(30, 0, -100), 'rightForearm': r(10), 'leftForearm': r(10)}
DRAPED = {'hips': {'p': [0, 0.12, -0.18], 'r': [-100, 0, 0]}, 'spine': r(-12), 'chest': r(-10), 'neck': r(-20), 'head': r(-10),
          'rightUpperArm': r(170, 0, 8), 'leftUpperArm': r(170, 0, -8), 'rightForearm': r(10), 'leftForearm': r(10)}
HUNG = {'hips': {'p': [0, -0.48, -0.06], 'r': [-62, 0, 0]}, 'spine': r(-14), 'chest': r(-10), 'neck': r(-8),
        'rightUpperArm': r(130, 0, 20), 'leftUpperArm': r(130, 0, -20), 'rightForearm': r(20), 'leftForearm': r(20),
        'rightUpperLeg': r(75, 0, 6), 'leftUpperLeg': r(75, 0, -6), 'rightLowerLeg': r(-100), 'leftLowerLeg': r(-100),
        'rightFoot': r(-55), 'leftFoot': r(-55)}
TANGLED = {'hips': {'p': [0, -0.16, 0.12], 'r': [10, 0, 0]}, 'spine': r(6), 'chest': r(4), 'neck': r(22), 'head': r(6),
           'rightUpperArm': r(-20, 0, 96), 'leftUpperArm': r(-20, 0, -96), 'rightForearm': r(0, 0, 0), 'leftForearm': r(0, 0, 0),
           'rightUpperLeg': r(14, 0, 6), 'leftUpperLeg': r(14, 0, -6), 'rightLowerLeg': r(-34), 'leftLowerLeg': r(-34)}


def build(L):
    # ================================================================ holding the ropes
    f = A.inside_facing_ropes(0.6)
    T = [0, 0.3, 0.55, 0.85]
    keys = [stance_at(0, [0, 0, 0.6], 0)]
    r1 = [0, 0, 0.47]
    keys.append(K(T[1], r1, 0, A.STANCE, body(hy=-0.03, lean=-6), {'rightUpperArm': r(70, 0, -10), 'leftUpperArm': r(70, 0, 10), 'rightForearm': r(30), 'leftForearm': r(30)},
                  lfoot=plant(-0.12, 0.45), rfoot=air(0.13, 0.08, 0.5, pitch=8)))
    keys.append(hold_key(T[2], lean=-12, hy=-0.05))
    keys.append(hold_key(T[3]))
    L.clip('ropes.grab-ropes', 'Grab the ropes', T[3], keys, f,
           desc='Step up to the ropes and take hold of the top rope with both hands. Ends holding the ropes, facing out.',
           events=[ev(0.28, 'footstep'), ev(T[2] - 0.04, 'rope_contact', attachment='rightHandGrip'), ev(T[2], 'grip_locked')],
           tags=['ropes', 'hold'], end_state='rope-hold', placement='inside-facing-ropes',
           phases=[('approach', 0, T[1]), ('contact', T[1], T[2]), ('recovery', T[2], T[3])])

    f = A.inside_facing_ropes(Z_HOLD)
    keys = [hold_key(0), hold_key(0.6, lean=-10, hy=-0.05, look=-28, shift=-0.03), hold_key(1.2, lean=-4, hy=-0.02, neck=-10),
            hold_key(1.8, lean=-10, hy=-0.05, look=30, shift=0.03), hold_key(2.4)]
    L.clip('ropes.hold-ropes', 'Hold the ropes (loop)', 2.4, keys, f, loop=True,
           desc='Holding the top rope with both hands, facing out: breathing, glancing along the ropes.',
           tags=['ropes', 'hold', 'loop'], start_state='rope-hold', end_state='rope-hold', placement='inside-facing-ropes',
           gameplay={'rootMotion': 'none'})

    f = A.inside_facing_ropes(Z_HOLD)
    T = [0, 0.25, 0.5, 0.75, 1.05]
    keys = [hold_key(0)]
    r1 = [0, 0, Z_HOLD + 0.03]
    keys.append(K(T[1], r1, 0, A.STANCE, body(hy=-0.04, turn=-30, lean=-4), {'leftUpperArm': r(10, 0, 20)}, rhand=grip(0.3, ROPE_TOP, 0),
                  feet=stand_feet(r1, 0, width=0.13)))
    r2 = [0, 0, Z_HOLD + 0.04]
    keys.append(K(T[2], r2, -90, A.STANCE, body(hy=-0.04), ARMS_DOWN, lfoot=plant(-0.12, Z_HOLD + 0.1), rfoot=plant(0.1, Z_HOLD - 0.02)))
    r3 = [0, 0, Z_LEAN]
    keys.append(K(T[3], r3, -165, A.STANCE, body(hy=-0.03), ARMS_DOWN, feet=stand_feet(r3, -165)))
    keys.append(stance_at(T[4], [0, 0, Z_LEAN + 0.02], -180))
    L.clip('ropes.turn-from-ropes', 'Turn away from the ropes', T[4], keys, f,
           desc='Let go of the top rope and turn round to face the ring, back to the ropes.',
           events=[ev(0.2, 'rope_release'), ev(0.5, 'footstep'), ev(0.75, 'footstep'), ev(T[4] - 0.05, 'recover')],
           tags=['ropes', 'turn'], start_state='rope-hold', placement='inside-facing-ropes', end_placement='inside-back-to-ropes')

    # ================================================================ back to the ropes
    f = A.back_to_ropes(0.5)
    T = [0, 0.22, 0.45, 0.7]
    keys = [stance_at(0, [0, 0, 0.5], 180)]
    keys.append(K(T[1], [0, 0, 0.47], 180, A.STANCE, body(hy=-0.04, lean=6), {'rightUpperArm': r(-40, 0, 40), 'leftUpperArm': r(-40, 0, -40)},
                  feet=stand_feet([0, 0, 0.47], 180)))
    keys.append(lean_key(T[2], Z_LEAN + 0.02))
    keys.append(lean_key(T[3]))
    L.clip('ropes.grab-hold', 'Reach back and brace on the ropes', T[3], keys, f,
           desc='Back to the ropes: reach behind, grab the top rope and brace against it (rope break, or a rest). Ends in the batch 1 rope-lean.',
           events=[ev(T[2], 'rope_contact', attachment='back'), ev(T[2] + 0.02, 'grip_locked')],
           tags=['ropes', 'brace', 'rope-break'], end_state='rope-lean', placement='inside-back-to-ropes')

    f = A.back_to_ropes(0.5)
    T = [0, 0.4, 0.9, 1.4, 1.9, 2.4, 2.9, 3.3]
    keys = [stance_at(0, [0, 0, 0.5], 180)]
    def spread(t, z, hy, lean, up=0.0, lfoot=None, rfoot=None, neck=-10):
        root = [0, 0, z]
        lh = grip(rel(root, 180, -0.62)[0], ROPE_TOP, 0); rh = grip(rel(root, 180, 0.62)[0], ROPE_TOP, 0)
        lf, rf = stand_feet(root, 180, width=0.16)
        return K(t, root, 180, A.STANCE, body(hy=hy, lean=lean, spine=(4, 0, 0), chest=(4, 0, 0), neck=(neck, 0, 0)),
                 lhand=lh, rhand=rh, lfoot=lfoot or lf, rfoot=rfoot or rf)
    keys.append(spread(T[1], 0.46, -0.03, 4))
    keys.append(spread(T[2], 0.5, -0.05, 18, neck=-24))
    keys.append(spread(T[3], 0.48, -0.42, 8, neck=-6))                     # deep squat with the ropes
    keys.append(spread(T[4], 0.5, -0.06, 16, neck=-20))
    keys.append(spread(T[5], 0.52, -0.1, 6, rfoot=air(-0.16, 0.3, 0.92, pitch=10)))   # knee up, rope-assisted quad stretch
    keys.append(spread(T[6], 0.5, -0.04, 10))
    keys.append(stance_at(T[7], [0, 0, 0.52], 180))
    L.clip('ropes.stretch', 'Stretch on the ropes', T[7], keys, f,
           desc='Arms spread along the top rope: lean back, deep squat, knee raise. A warm-up taunt in the corner of the ring.',
           events=[ev(T[1], 'rope_contact', attachment='back'), ev(T[6] + 0.1, 'rope_release'), ev(T[7] - 0.05, 'recover')],
           tags=['ropes', 'taunt', 'warm-up'], placement='inside-back-to-ropes')

    # ================================================================ running into the ropes
    f = A.Frame('rope', [0, 0, 2.6, 0])
    keys = [run_key(0, 2.6, 0), run_key(0.16, 1.96, 0.16), run_key(0.32, 1.32, 0.32)]
    keys.append(K(0.46, [0.04, 0, 0.82], 70, run_pose(0.48), body(hy=-0.06, lean=-6)))                 # plant and spin
    keys.append(K(0.58, [0.02, 0, 0.5], 165, A.LEAN, body(hy=-0.05, hz=0.08, lean=4), feet=stand_feet([0.02, 0, 0.5], 165)))
    keys.append(K(0.68, [0, 0, Z_LEAN], 180, A.STRETCH, feet=stand_feet([0, 0, Z_LEAN], 180)))        # ropes stretch
    keys.append(lean_key(0.95))
    L.clip('ropes.run-into', 'Run into the ropes', 0.95, keys, f,
           desc='From a run: plant, spin and hit the ropes back first. The ropes stretch and settle; ends in rope-lean, ready to rebound.',
           events=[ev(0.16, 'footstep'), ev(0.32, 'footstep'), ev(0.46, 'footstep'), ev(0.6, 'rope_contact', attachment='back'), ev(0.68, 'impact', surface='ropes')],
           tags=['ropes', 'running'], start_state='running', end_state='rope-lean', placement='running-to-ropes', end_placement='inside-back-to-ropes',
           phases=[('approach', 0, 0.46), ('contact', 0.46, 0.68), ('recovery', 0.68, 0.95)],
           interrupt={'windows': [[0, 0.3]], 'note': 'commit after the last stride'})

    keys = [run_key(0, 2.6, 0), run_key(0.16, 1.96, 0.16), run_key(0.32, 1.32, 0.32)]
    keys.append(K(0.46, [0.04, 0, 0.82], 70, run_pose(0.48), body(hy=-0.06, lean=-6)))
    keys.append(K(0.58, [0.02, 0, 0.5], 165, A.LEAN, body(hy=-0.05, hz=0.08, lean=4), feet=stand_feet([0.02, 0, 0.5], 165)))
    keys.append(K(0.68, [0, 0, Z_LEAN], 180, A.STRETCH, feet=stand_feet([0, 0, Z_LEAN], 180)))
    keys.append(K(0.8, [0, 0, 0.62], 180, run_pose(0.0), body(lean=-14), feet=None))
    keys.append(run_key(0.96, 1.15, 0.16, 180))
    keys.append(run_key(1.12, 1.8, 0.32, 180))
    keys.append(run_key(1.28, 2.44, 0.48, 180))
    L.clip('ropes.bounce-running', 'Bounce off the ropes', 1.28, keys, f,
           desc='Run in, spin, hit the ropes and spring straight back out at full speed. Ends running (run cycle at 0.48 s).',
           events=[ev(0.16, 'footstep'), ev(0.32, 'footstep'), ev(0.6, 'rope_contact', attachment='back'), ev(0.7, 'rebound'),
                   ev(0.96, 'footstep'), ev(1.12, 'footstep'), ev(1.28, 'release', next='movement.run')],
           tags=['ropes', 'running', 'rebound', 'chains-to-run'], start_state='running', end_state='running',
           placement='running-to-ropes', end_placement='center',
           phases=[('approach', 0, 0.46), ('contact', 0.46, 0.8), ('launch', 0.8, 0.96), ('recovery', 0.96, 1.28)],
           interrupt={'windows': [[0, 0.3], [1.0, 1.28]]})

    # ================================================================ rebounds from rope-lean
    f = A.back_to_ropes(Z_LEAN)
    def rebound_keys():
        ks = [lean_key(0)]
        ks.append(K(0.18, [0, 0, Z_LEAN - 0.03], 180, A.STRETCH, feet=stand_feet([0, 0, Z_LEAN - 0.03], 180)))     # sink into the ropes
        ks.append(K(0.34, [0, 0, 0.6], 180, run_pose(0.0), body(lean=-26, hy=-0.06), feet=None))                   # catapult
        return ks
    keys = rebound_keys()
    keys.append(K(0.5, [0, 0, 1.1], 180, run_pose(0.16), body(lean=-20)))
    keys.append(K(0.68, [0, 0, 1.75], 180, run_pose(0.32), body(lean=-12)))
    keys.append(run_key(0.84, 2.4, 0.48, 180))
    keys.append(run_key(1.0, 3.04, 0.0, 180))
    L.clip('ropes.rebound-sprint', 'Rebound into a sprint', 1.0, keys, f,
           desc='From rope-lean: sink into the ropes, get catapulted out low and drive into a full sprint. Ends running (cycle time 0).',
           events=[ev(0.18, 'rebound'), ev(0.34, 'footstep'), ev(0.5, 'footstep'), ev(0.68, 'footstep'), ev(0.84, 'footstep'), ev(1.0, 'release', next='movement.run')],
           tags=['ropes', 'rebound', 'running', 'chains-to-run'], start_state='rope-lean', end_state='running', placement='inside-back-to-ropes', end_placement='center',
           phases=[('contact', 0, 0.18), ('launch', 0.18, 0.5), ('recovery', 0.5, 1.0)])

    keys = rebound_keys()
    keys.append(K(0.5, [0, 0, 1.1], 180, run_pose(0.16), body(lean=-16)))
    keys.append(K(0.68, [0, 0, 1.72], 180, run_pose(0.32), body(lean=-10), {'rightUpperArm': r(20, 0, 60)}))
    keys.append(K(0.82, [0, 0, 2.25], 180, run_pose(0.48), body(lean=-4, turn=20), CLOTHES_R))
    keys.append(K(0.9, [0, 0, 2.5], 180, run_pose(0.0), body(lean=0, turn=-22), CLOTHES_R, {'chest': r(0, 14, 0)}))     # hit
    keys.append(K(1.08, [0, 0, 2.86], 180, A.STANCE, body(hy=-0.1, turn=-40, lean=-6), {'rightUpperArm': r(30, 0, 70), 'rightForearm': r(30)},
                  lfoot=plant(0.12, 2.98), rfoot=plant(-0.14, 2.76)))
    keys.append(K(1.3, [0, 0, 3.0], 180, A.GUARD, body(hy=-0.06), feet=stand_feet([0, 0, 3.0], 180)))
    keys.append(K(1.5, [0, 0, 3.0], 180, A.STANCE, feet=stand_feet([0, 0, 3.0], 180)))
    L.clip('ropes.rebound-clothesline', 'Rebound clothesline', 1.5, keys, f,
           desc='From rope-lean: catapult off the ropes, two strides and a running right-arm clothesline about 2.5 m out, then stop.',
           events=[ev(0.18, 'rebound'), ev(0.34, 'footstep'), ev(0.5, 'footstep'), ev(0.68, 'footstep'), ev(0.74, 'attack_start'),
                   ev(0.9, 'hit', attachment='propRightHand', zone='head', reach=0.75), ev(1.08, 'footstep'), ev(1.45, 'recover')],
           tags=['ropes', 'rebound', 'strike', 'running-attack'], start_state='rope-lean', placement='inside-back-to-ropes', end_placement='center',
           phases=[('contact', 0, 0.18), ('launch', 0.18, 0.74), ('contact', 0.74, 0.95), ('recovery', 0.95, 1.5)])

    keys = rebound_keys()
    keys.append(K(0.5, [0, 0, 1.1], 180, run_pose(0.16), body(lean=-14)))
    keys.append(K(0.66, [0, 0, 1.66], 180, A.STANCE, body(hy=-0.24, lean=-18), ARMS_FWD, lfoot=plant(0.12, 1.7), rfoot=plant(-0.12, 1.6)))   # take-off
    air_body = {'hips': {'p': [0, 0.0, 0], 'r': [-20, 0, 82]}, 'spine': r(0, 0, 6), 'neck': r(0, 0, -20),
                'rightUpperLeg': r(10, 0, 8), 'leftUpperLeg': r(20, 0, -8), 'rightLowerLeg': r(-30), 'leftLowerLeg': r(-40)}
    keys.append(K(0.84, [0, 0.62, 2.3], 180, air_body, CROSS_ARMS))                                     # horizontal, side first
    keys.append(K(1.0, [0, 0.4, 2.75], 200, air_body, CROSS_ARMS))
    keys.append(K(1.14, [-0.2, 0.0, 3.0], 255, A.LIE_FRONT, body(hy=-0.74, lean=-80, roll=20), CROSS_ARMS))
    keys.append(K(1.3, [-0.25, 0, 3.0], 270, A.LIE_FRONT))
    keys.append(K(1.6, [-0.25, 0, 3.0], 270, A.LIE_FRONT))
    L.clip('ropes.rebound-crossbody', 'Rebound crossbody', 1.6, keys, f,
           desc='From rope-lean: catapult out, one stride, leap and fly horizontally side-first, arms spread. Solo version lands face down '
                '(the paired version lands across the opponent).',
           events=[ev(0.18, 'rebound'), ev(0.34, 'footstep'), ev(0.5, 'footstep'), ev(0.66, 'jump'), ev(0.84, 'apex'), ev(1.0, 'hit', zone='body', reach=0.4),
                   ev(1.14, 'land', zone='front'), ev(1.14, 'impact', surface='mat')],
           tags=['ropes', 'rebound', 'aerial', 'running-attack'], start_state='rope-lean', end_state='lying-front', placement='inside-back-to-ropes', end_placement='center',
           phases=[('contact', 0, 0.18), ('launch', 0.18, 0.66), ('flight', 0.66, 1.1), ('landing', 1.1, 1.3), ('recovery', 1.3, 1.6)])

    # ================================================================ irish whip into the ropes (pair parts)
    # defender: stands at z 3.0 facing the attacker (yaw 180), is yanked round, stumbles to the ropes, spins and hits back first
    f = A.Frame('rope', [0, 0, 3.0, 180])
    keys = [K(0, [0, 0, 3.0], 180, A.GUARD, body(hy=-0.04), feet=stand_feet([0, 0, 3.0], 180))]
    keys.append(K(0.22, [0.05, 0, 2.98], 180, A.STANCE, body(hy=-0.06, lean=-6), {'rightUpperArm': r(60, 0, -30), 'rightForearm': r(10)},
                  feet=stand_feet([0.05, 0, 2.98], 180)))
    keys.append(K(0.45, [0.1, 0, 2.7], 30, run_pose(0.48), body(lean=-18, hy=-0.06), {'rightUpperArm': r(-50, 0, -20), 'rightForearm': r(10)}))   # flung round
    keys.append(K(0.62, [0.06, 0, 2.1], 0, run_pose(0.0), body(lean=-14)))
    keys.append(run_key(0.78, 1.45, 0.16))
    keys.append(K(0.92, [0.03, 0, 0.88], 70, run_pose(0.32), body(hy=-0.06, lean=-6)))
    keys.append(K(1.04, [0.01, 0, 0.5], 165, A.LEAN, body(hy=-0.05, hz=0.08, lean=4), feet=stand_feet([0.01, 0, 0.5], 165)))
    keys.append(K(1.14, [0, 0, Z_LEAN], 180, A.STRETCH, feet=stand_feet([0, 0, Z_LEAN], 180)))
    keys.append(lean_key(1.4))
    L.clip('ropes.whipped-into', 'Whipped into the ropes', 1.4, keys, f,
           desc='Defender of an Irish whip: wrist yanked, flung round, stumble-run 2.5 m to the ropes, spin and hit them back first. '
                'Ends in rope-lean, so any rebound clip can follow.',
           events=[ev(0.1, 'grab', attachment='rightHand'), ev(0.42, 'release'), ev(0.62, 'footstep'), ev(0.78, 'footstep'), ev(0.92, 'footstep'),
                   ev(1.06, 'rope_contact', attachment='back'), ev(1.14, 'impact', surface='ropes')],
           tags=['ropes', 'whip', 'defender', 'irish-whip'], end_state='rope-lean', placement='center', end_placement='inside-back-to-ropes',
           phases=[('contact', 0, 0.42), ('traversal', 0.42, 1.04), ('landing', 1.04, 1.14), ('recovery', 1.14, 1.4)],
           interrupt={'windows': [], 'note': 'paired: not interruptible'})

    # attacker: 0.75 m further from the ropes, facing them (yaw 0)
    fA = A.Frame('rope', [0, 0, 3.75, 0])
    wrist = lambda t: body_point(L, 'ropes.whipped-into', f, t, 'rightHand')
    keys = [K(0, [0, 0, 3.75], 0, A.GUARD, feet=stand_feet([0, 0, 3.75], 0))]
    keys.append(K(0.1, [0, 0, 3.72], 0, A.STANCE, body(hy=-0.05, turn=10), lhand=wrist(0.1), feet=stand_feet([0, 0, 3.72], 0)))
    keys.append(K(0.22, [0, 0, 3.7], 0, A.STANCE, body(hy=-0.07, turn=30, lean=4), lhand=wrist(0.22), lfoot=plant(-0.14, 3.62), rfoot=plant(0.16, 3.82)))
    keys.append(K(0.4, [0, 0, 3.62], 0, A.STANCE, body(hy=-0.1, turn=-35, lean=-10), {'leftUpperArm': r(70, 0, 40), 'leftForearm': r(10)},
                  lfoot=plant(-0.14, 3.48), rfoot=plant(0.16, 3.82)))
    keys.append(K(0.6, [0, 0, 3.6], 0, A.STANCE, body(hy=-0.08, turn=-20, lean=-6), {'leftUpperArm': r(80, 0, 20), 'leftForearm': r(10)},
                  lfoot=plant(-0.14, 3.48), rfoot=plant(0.15, 3.76)))
    keys.append(K(1.0, [0, 0, 3.6], 0, A.GUARD, body(hy=-0.05), feet=stand_feet([0, 0, 3.6], 0)))
    keys.append(K(1.4, [0, 0, 3.6], 0, A.GUARD, feet=stand_feet([0, 0, 3.6], 0)))
    L.clip('ropes.irish-whip', 'Irish whip', 1.4, keys, fA,
           desc='Attacker: take the opponent\'s right wrist with the left hand, load the hips and sling them towards the ropes, then wait in guard for the rebound.',
           events=[ev(0.1, 'grab', attachment='leftHandGrip'), ev(0.2, 'grip_locked'), ev(0.3, 'attack_start'), ev(0.42, 'release'), ev(1.3, 'recover')],
           tags=['ropes', 'whip', 'attacker', 'irish-whip'], placement='center',
           phases=[('contact', 0, 0.22), ('launch', 0.22, 0.42), ('recovery', 0.42, 1.4)],
           interrupt={'windows': [[0.9, 1.4]], 'note': 'free once the opponent is on the way'})

    # ================================================================ shoved into the ropes (pair parts)
    fD = A.Frame('rope', [0, 0, 1.0, 180])
    keys = [K(0, [0, 0, 1.0], 180, A.GUARD, feet=stand_feet([0, 0, 1.0], 180))]
    keys.append(K(0.28, [0, 0, 0.98], 180, A.STANCE, body(hy=-0.04, lean=10, spine=(6, 0, 0), neck=(-14, 0, 0)), ARMS_OUT, feet=stand_feet([0, 0, 0.98], 180)))
    keys.append(K(0.46, [0, 0, 0.7], 180, A.STANCE, body(hy=-0.06, lean=16, neck=(-10, 0, 0)), ARMS_OUT, lfoot=plant(0.12, 0.62), rfoot=air(-0.12, 0.12, 0.84)))
    keys.append(K(0.6, [0, 0, 0.5], 180, A.STRETCH, feet=stand_feet([0, 0, 0.5], 180)))
    keys.append(lean_key(0.8))
    keys.append(lean_key(1.0))
    L.clip('ropes.pushed-against', 'Shoved into the ropes', 1.0, keys, fD,
           desc='Defender: two-handed shove to the chest drives them back-pedalling into the ropes. Ends in rope-lean.',
           events=[ev(0.28, 'hit_received', zone='body'), ev(0.46, 'footstep'), ev(0.6, 'rope_contact', attachment='back'), ev(0.62, 'impact', surface='ropes')],
           tags=['ropes', 'defender', 'shove'], end_state='rope-lean', placement='center', end_placement='inside-back-to-ropes',
           phases=[('contact', 0, 0.3), ('traversal', 0.3, 0.6), ('recovery', 0.6, 1.0)], interrupt={'windows': []})

    fA = A.Frame('rope', [0, 0, 1.7, 0])
    chest = lambda t, side: body_point(L, 'ropes.pushed-against', fD, t, 'chest', (0.14 * side, 0.12, -0.14))
    keys = [K(0, [0, 0, 1.7], 0, A.GUARD, feet=stand_feet([0, 0, 1.7], 0))]
    keys.append(K(0.16, [0, 0, 1.62], 0, A.STANCE, body(hy=-0.08, lean=-6), {'rightUpperArm': r(40, 0, -10), 'leftUpperArm': r(40, 0, 10), 'rightForearm': r(90), 'leftForearm': r(90)},
                  lfoot=plant(-0.13, 1.6), rfoot=plant(0.13, 1.82)))
    keys.append(K(0.28, [0, 0, 1.5], 0, A.STANCE, body(hy=-0.1, lean=-14), lhand=chest(0.28, -1), rhand=chest(0.28, 1),
                  lfoot=plant(-0.13, 1.36), rfoot=plant(0.13, 1.74)))
    keys.append(K(0.42, [0, 0, 1.44], 0, A.STANCE, body(hy=-0.08, lean=-16), {'rightUpperArm': r(84, 0, -8), 'leftUpperArm': r(84, 0, 8), 'rightForearm': r(4), 'leftForearm': r(4)},
                  lfoot=plant(-0.13, 1.3), rfoot=plant(0.13, 1.66)))
    keys.append(K(0.75, [0, 0, 1.36], 0, A.GUARD, body(hy=-0.05), feet=stand_feet([0, 0, 1.36], 0)))
    keys.append(K(1.0, [0, 0, 1.36], 0, A.GUARD, feet=stand_feet([0, 0, 1.36], 0)))
    L.clip('ropes.push-into-ropes', 'Shove into the ropes', 1.0, keys, fA,
           desc='Attacker: step in and drive both palms into the opponent\'s chest, sending them into the ropes behind them.',
           events=[ev(0.16, 'attack_start'), ev(0.28, 'hit', attachment='propRightHand', zone='body', reach=0.5), ev(0.36, 'footstep'), ev(0.95, 'recover')],
           tags=['ropes', 'attacker', 'shove'], placement='center', phases=[('approach', 0, 0.16), ('contact', 0.16, 0.42), ('recovery', 0.42, 1.0)],
           interrupt={'windows': [[0.6, 1.0]]})

    # ================================================================ tangled in the ropes
    f = A.back_to_ropes(Z_LEAN)
    def tangled(t, sway=0.0, sag=0.0, look=0):
        root = [0, 0, 0.3]
        lh = grip(rel(root, 180, -0.62)[0], ROPE_MID, 0, up=-0.05); rh = grip(rel(root, 180, 0.62)[0], ROPE_MID, 0, up=-0.05)
        return K(t, root, 180, TANGLED, body(hy=-0.16 - sag, hx=sway, hz=0.12, lean=10, roll=sway * 60, neck=(22, look, 0)),
                 lhand=lh, rhand=rh, feet=stand_feet(root, 180, width=0.17))
    keys = [lean_key(0)]
    keys.append(K(0.25, [0, 0, 0.38], 180, A.STRETCH, body(hy=-0.08, hz=0.3, lean=26), feet=stand_feet([0, 0, 0.38], 180)))
    keys.append(K(0.5, [0, 0, 0.33], 180, TANGLED, body(hy=-0.1, hz=0.14, lean=16), {'rightUpperArm': r(-60, 0, 110), 'leftUpperArm': r(-60, 0, -110)},
                  feet=stand_feet([0, 0, 0.33], 180, width=0.16)))
    keys.append(tangled(0.8, sag=0.04))
    keys.append(tangled(1.1))
    L.clip('ropes.get-tangled', 'Get tangled in the ropes', 1.1, keys, f,
           desc='From rope-lean: slump through the ropes so both arms end up hooked over the middle rope and under the top rope, body hanging.',
           events=[ev(0.25, 'rope_contact', attachment='back'), ev(0.8, 'stun_start')],
           tags=['ropes', 'tangled', 'stunned'], start_state='rope-lean', end_state='rope-tangled', placement='inside-back-to-ropes')

    keys = [tangled(0), tangled(0.5, sway=0.06, sag=0.03, look=20), tangled(1.0, sway=-0.02, sag=-0.03), tangled(1.5, sway=-0.06, sag=0.03, look=-20), tangled(2.0)]
    L.clip('ropes.tangled-struggle', 'Struggle in the ropes (loop)', 2.0, keys, f, loop=True,
           desc='Arms tangled in the ropes: twisting and heaving to get free.',
           tags=['ropes', 'tangled', 'loop', 'stunned'], start_state='rope-tangled', end_state='rope-tangled', placement='inside-back-to-ropes')

    keys = [tangled(0), tangled(0.3, sway=0.07, sag=0.05, look=25)]
    keys.append(K(0.6, [0, 0, 0.36], 180, TANGLED, body(hy=-0.12, hz=0.08, lean=4), {'rightUpperArm': r(-10, 0, 60), 'leftUpperArm': r(-70, 0, -110), 'rightForearm': r(40)},
                  feet=stand_feet([0, 0, 0.36], 180)))
    keys.append(K(0.85, [0, 0, 0.5], 180, A.STANCE, HUNCH, body(hy=-0.08, lean=-10), lfoot=plant(0.12, 0.62), rfoot=plant(-0.12, 0.42)))
    keys.append(K(1.15, [0, 0, 0.72], 180, A.STANCE, HUNCH, body(hy=-0.05, lean=-8), feet=stand_feet([0, 0, 0.72], 180)))
    keys.append(stance_at(1.4, [0, 0, 0.72], 180))
    L.clip('ropes.tangled-escape', 'Break free of the ropes', 1.4, keys, f,
           desc='Yank one arm free, then the other, and stumble forward out of the ropes.',
           events=[ev(0.6, 'rope_release'), ev(0.85, 'footstep'), ev(1.15, 'footstep'), ev(1.35, 'recover')],
           tags=['ropes', 'tangled', 'escape'], start_state='rope-tangled', placement='inside-back-to-ropes', end_placement='center')

    # ================================================================ draped over the top rope
    f = A.inside_facing_ropes(0.7)
    def draped(t, sway=0.0, sag=0.0):
        root = [0, 0, 0.32]
        return K(t, root, 0, DRAPED, body(hy=0.12 - sag, hz=-0.18, lean=-100, roll=sway * 40, neck=(-20, 0, 0)),
                 {'rightUpperArm': r(170, 0, 8 + sway * 40), 'leftUpperArm': r(170, 0, -8 + sway * 40)},
                 lfoot=plant(-0.12, 0.44, pitch=-35), rfoot=plant(0.12, 0.44, pitch=-35))
    keys = [K(0, [0, 0, 0.7], 0, A.STANCE, HUNCH, feet=stand_feet([0, 0, 0.7], 0))]
    keys.append(K(0.22, [0, 0, 0.55], 0, A.STANCE, body(hy=-0.04, lean=-24, spine=(-14, 0, 0)), ARMS_FWD, lfoot=plant(-0.12, 0.5), rfoot=air(0.12, 0.1, 0.62)))
    keys.append(K(0.4, [0, 0, 0.38], 0, A.STANCE, body(hy=0.02, lean=-60, spine=(-14, 0, 0)), {'rightUpperArm': r(150, 0, -10), 'leftUpperArm': r(150, 0, 10)},
                  lfoot=plant(-0.12, 0.42), rfoot=plant(0.12, 0.46)))
    keys.append(draped(0.62, sag=-0.04))
    keys.append(draped(0.9))
    L.clip('ropes.drape-over-top', 'Fold over the top rope', 0.9, keys, f,
           desc='Stumbling forward into the ropes and folding over the top rope at the waist: head and arms hang outside, toes on the mat.',
           events=[ev(0.22, 'footstep'), ev(0.45, 'rope_contact', attachment='body'), ev(0.62, 'impact', surface='ropes'), ev(0.7, 'stun_start')],
           tags=['ropes', 'draped', 'stunned'], end_state='rope-draped', placement='inside-facing-ropes', end_placement='rope-draped')

    f = A.inside_facing_ropes(0.32)
    keys = [draped(0), draped(0.7, sway=0.1, sag=0.02), draped(1.4, sway=-0.08), draped(2.1, sway=0.05, sag=0.02), draped(2.8)]
    L.clip('ropes.hang-over-top', 'Draped over the top rope (loop)', 2.8, keys, f, loop=True,
           desc='Folded over the top rope, arms dangling outside, swaying. The pull-over-top setup.',
           tags=['ropes', 'draped', 'loop', 'stunned'], start_state='rope-draped', end_state='rope-draped', placement='rope-draped')

    keys = [draped(0), draped(0.3, sag=0.05)]
    keys.append(K(0.6, [0, 0, 0.36], 0, A.STANCE, body(hy=0.0, lean=-50, spine=(-14, 0, 0)), hands=hold_hands([0, 0, 0.36]),
                  lfoot=plant(-0.12, 0.44), rfoot=plant(0.12, 0.44)))
    keys.append(K(0.95, [0, 0, 0.5], 0, A.STANCE, HUNCH, body(hy=-0.06, lean=-10), lfoot=plant(-0.12, 0.6), rfoot=plant(0.12, 0.44)))
    keys.append(K(1.25, [0, 0, 0.6], -180, A.STANCE, HUNCH, body(hy=-0.04), feet=stand_feet([0, 0, 0.6], -180)))
    keys.append(stance_at(1.5, [0, 0, 0.6], -180))
    L.clip('ropes.drape-recover', 'Push off the top rope', 1.5, keys, f,
           desc='Draped over the top rope: push back up with both hands, step back and turn to face the ring.',
           events=[ev(0.6, 'rope_contact', attachment='rightHandGrip'), ev(0.8, 'rope_release'), ev(0.95, 'footstep'), ev(1.25, 'footstep'), ev(1.45, 'recover')],
           tags=['ropes', 'draped', 'recover'], start_state='rope-draped', placement='rope-draped', end_placement='inside-back-to-ropes')

    # ================================================================ hung between the ropes (619 position)
    f = A.inside_facing_ropes(0.75)
    def hung(t, sway=0.0, sag=0.0):
        root = [0, 0, 0.42]
        return K(t, root, 0, HUNG, body(hy=-0.48 - sag, hz=-0.06, lean=-62, roll=sway * 30),
                 {'rightUpperArm': r(130, 0, 20 + sway * 30), 'leftUpperArm': r(130, 0, -20 + sway * 30)})
    keys = [K(0, [0, 0, 0.75], 0, A.STANCE, HUNCH, feet=stand_feet([0, 0, 0.75], 0))]
    keys.append(K(0.25, [0, 0, 0.6], 0, A.STANCE, body(hy=-0.06, lean=-30), ARMS_FWD, lfoot=plant(-0.12, 0.56), rfoot=air(0.12, 0.1, 0.7)))
    keys.append(K(0.5, [0, 0, 0.48], 0, A.STANCE, body(hy=-0.3, lean=-55), {'rightUpperArm': r(130, 0, -20), 'leftUpperArm': r(130, 0, 20)},
                  lfoot=plant(-0.12, 0.62), rfoot=plant(0.12, 0.62)))
    keys.append(hung(0.8, sag=0.06))
    keys.append(hung(1.1))
    L.clip('ropes.hang-between', 'Slump between the ropes', 1.1, keys, f,
           desc='Staggering into the ropes and sinking to the knees with the chest over the middle rope, head and arms hanging out between middle and top ropes.',
           events=[ev(0.25, 'footstep'), ev(0.6, 'rope_contact', attachment='body'), ev(0.8, 'land', zone='knees'), ev(0.85, 'stun_start')],
           tags=['ropes', 'hung', 'stunned', '619-setup'], end_state='rope-hung', placement='inside-facing-ropes')

    f = A.inside_facing_ropes(0.42)
    keys = [hung(0), hung(0.75, sway=0.1, sag=0.02), hung(1.5, sway=-0.06), hung(2.25, sway=0.04, sag=0.02), hung(3.0)]
    L.clip('ropes.hung-between-idle', 'Hung between the ropes (loop)', 3.0, keys, f, loop=True,
           desc='Kneeling with the chest on the middle rope, arms dangling outside: a sitting duck.',
           tags=['ropes', 'hung', 'loop', 'stunned'], start_state='rope-hung', end_state='rope-hung', placement='inside-facing-ropes')

    keys = [hung(0)]
    keys.append(K(0.35, [0, 0, 0.42], 0, HUNG, body(hy=-0.45, hz=0.04, lean=-40), hands=hold_hands([0, 0, 0.42], h=ROPE_MID)))
    keys.append(K(0.7, [0, 0, 0.45], 0, A.STANCE, body(hy=-0.4, lean=-26, spine=(-12, 0, 0)), hands=hold_hands([0, 0, 0.45], h=ROPE_MID),
                  lfoot=plant(-0.12, 0.6), rfoot=plant(0.13, 0.42)))
    keys.append(K(1.05, [0, 0, 0.5], 0, A.STANCE, HUNCH, body(hy=-0.08, lean=-12), feet=stand_feet([0, 0, 0.5], 0)))
    keys.append(K(1.4, [0, 0, 0.62], -180, A.STANCE, HUNCH, body(hy=-0.04), feet=stand_feet([0, 0, 0.62], -180)))
    keys.append(stance_at(1.6, [0, 0, 0.62], -180))
    L.clip('ropes.hung-recover', 'Climb out of the ropes', 1.6, keys, f,
           desc='From hung between the ropes: grab the middle rope, push up to the feet and turn to face the ring.',
           events=[ev(0.35, 'rope_contact', attachment='rightHandGrip'), ev(0.7, 'footstep'), ev(0.9, 'rope_release'), ev(1.4, 'footstep'), ev(1.55, 'recover')],
           tags=['ropes', 'hung', 'recover'], start_state='rope-hung', placement='inside-facing-ropes', end_placement='inside-back-to-ropes')

    # ================================================================ apron: up onto the middle rope, springboard
    f = A.apron_facing_ring(0.3)
    hm = ROPE_MID + RR
    T = [0, 0.35, 0.7, 1.0, 1.3]
    keys = [K(0, [0, 0, -0.3], 180, A.STANCE, body(hy=-0.03), hands=hold_hands([0, 0, -0.3], yaw=180), feet=stand_feet([0, 0, -0.3], 180))]
    r1 = [0, 0, -0.26]
    keys.append(K(T[1], r1, 180, A.STANCE, body(hy=-0.08, lean=-8), hands=hold_hands(r1, yaw=180), lfoot=plant(0.12, -0.3), rfoot=on_rope(-0.13, ROPE_MID, -0.05)))
    r2 = [0, hm, -0.08]
    keys.append(K(T[2], r2, 180, A.STANCE, body(hy=-0.3, lean=-16, spine=(-10, 0, 0)), hands=hold_hands(r2, yaw=180),
                  lfoot=on_rope(0.13, ROPE_MID, -0.05), rfoot=on_rope(-0.13, ROPE_MID, -0.05)))
    keys.append(K(T[3], [0, hm, -0.07], 180, A.STANCE, body(hy=-0.36, lean=-20, spine=(-10, 0, 0), neck=(20, 0, 0)), hands=hold_hands(r2, yaw=180),
                  lfoot=on_rope(0.13, ROPE_MID, -0.05), rfoot=on_rope(-0.13, ROPE_MID, -0.05)))
    keys.append(K(T[4], [0, hm, -0.07], 180, A.STANCE, body(hy=-0.34, lean=-18, spine=(-10, 0, 0), neck=(16, 0, 0)), hands=hold_hands(r2, yaw=180),
                  lfoot=on_rope(0.13, ROPE_MID, -0.05), rfoot=on_rope(-0.13, ROPE_MID, -0.05)))
    L.clip('ropes.climb-to-middle', 'Climb onto the middle rope', T[4], keys, f,
           desc='From the apron holding the top rope: step up onto the middle rope with both feet and crouch, facing the ring. '
                'Ends perched on the middle rope (for second-rope attacks into the ring).',
           events=[ev(T[1], 'footstep'), ev(T[2], 'footstep'), ev(T[3], 'grip_locked')],
           tags=['ropes', 'apron', 'climb', 'aerial-setup'], start_state='apron-hold', end_state='rope-middle-perched',
           start_loc='apron', end_loc='apron', placement='apron-facing-ring')

    f = A.apron_facing_ring(0.45)
    T = [0, 0.25, 0.42, 0.55, 0.72, 0.92, 1.1, 1.4]
    keys = [stance_at(0, [0, 0, -0.45], 180)]
    keys.append(K(T[1], [0, 0, -0.4], 180, A.STANCE, body(hy=-0.22, lean=-14), {'rightUpperArm': r(-30, 0, -20), 'leftUpperArm': r(-30, 0, 20)},
                  feet=stand_feet([0, 0, -0.4], 180, width=0.15)))                                   # crouch, arms back
    keys.append(K(T[2], [0, 0.42, -0.2], 180, A.STANCE, body(hy=-0.18, lean=-6), ARMS_UP,
                  lfoot=air(0.12, 0.62, -0.24, pitch=-20), rfoot=on_rope(-0.08, ROPE_TOP, -0.02)))     # right foot onto the top rope
    keys.append(K(T[3], [0, 0.66, -0.02], 180, A.STANCE, body(hy=-0.36, lean=-10), ARMS_UP,
                  lfoot=air(0.14, 1.5, 0.05), rfoot=on_rope(-0.06, ROPE_TOP, 0.0)))                    # spring load
    keys.append(K(T[4], [0, 1.15, 0.6], 180, A.STANCE, body(hy=-0.1, lean=-14), ARMS_SUPERMAN,
                  lfoot=air(0.13, 1.5, 0.75), rfoot=air(-0.13, 1.45, 0.62)))                          # launch apex
    keys.append(K(T[5], [0, 0.55, 1.35], 180, A.STANCE, body(hy=-0.12), ARMS_OUT, lfoot=air(0.15, 0.62, 1.45), rfoot=air(-0.15, 0.62, 1.45)))
    keys.append(K(T[6], [0, 0, 1.7], 180, A.STANCE, body(hy=-0.4, lean=-16, spine=(-10, 0, 0)), ARMS_OUT, feet=stand_feet([0, 0, 1.7], 180, width=0.17)))
    keys.append(stance_at(T[7], [0, 0, 1.7], 180))
    L.clip('ropes.springboard-launch', 'Springboard off the top rope', T[7], keys, f,
           desc='From the apron: hop onto the top rope with the right foot, ride the rope down and spring high into the ring, landing about 1.7 m inside. '
                'Base for springboard attacks (aerial variants branch at the apex, 0.72 s).',
           events=[ev(0.3, 'jump'), ev(T[2], 'rope_contact', attachment='rightFoot'), ev(T[3], 'rebound'), ev(T[3] + 0.02, 'rope_release'),
                   ev(T[4], 'apex'), ev(T[6], 'land'), ev(T[7] - 0.05, 'recover')],
           tags=['ropes', 'apron', 'springboard', 'aerial-setup', 'athletic'], start_loc='apron', end_loc='ring', placement='apron-facing-ring',
           end_placement='center', phases=[('approach', 0, T[1]), ('contact', T[1], T[3]), ('flight', T[3], T[6]), ('landing', T[6], T[7])])

    # ================================================================ pulled over the top rope to the floor (pair parts)
    # defender starts draped over the top rope (inside), attacker stands on the floor below, facing the ring
    fD = A.inside_facing_ropes(0.32)
    keys = [draped(0)]
    keys.append(draped(0.3, sag=-0.04))
    keys.append(K(0.55, [0, 0.55, 0.05], 0, DRAPED, body(hy=0.1, hz=-0.1, lean=-145, neck=(-30, 0, 0)), {'rightUpperArm': r(120, 0, 30), 'leftUpperArm': r(120, 0, -30)},
                  lfoot=air(-0.12, 0.6, 0.45), rfoot=air(0.12, 0.6, 0.45)))                         # legs come over
    keys.append(K(0.8, [-0.2, 0.2, -1.0], 0, A.LIE_BACK, body(hy=0.0, lean=-200, neck=(10, 0, 0))))     # over and falling, back first
    keys.append(K(1.02, [-0.35, D_, -2.05], 0, A.LIE_BACK, body(hy=-0.83, lean=-270)))
    keys.append(K(1.4, [-0.35, D_, -2.05], 0, A.LIE_BACK, body(hy=-0.83, lean=-270)))
    L.clip('ropes.pulled-over-top', 'Pulled over the top rope', 1.4, keys, fD,
           desc='Defender: draped over the top rope, grabbed by the head and arm from the floor and dragged over head first. '
                'Flips over and lands flat on the back on the arena floor.',
           events=[ev(0.1, 'grab', attachment='head'), ev(0.3, 'grip_locked'), ev(0.55, 'rope_release'), ev(1.02, 'land', zone='back', height=1.16),
                   ev(1.02, 'impact', surface='floor')],
           tags=['ropes', 'defender', 'to-floor', 'elimination'], start_state='rope-draped', end_state='lying-back', start_loc='ring', end_loc='floor',
           placement='rope-draped', end_placement='floor-facing-out', phases=[('contact', 0, 0.3), ('traversal', 0.3, 0.9), ('landing', 0.9, 1.1), ('recovery', 1.1, 1.4)],
           interrupt={'windows': []})

    # attacker stands a little to the side so the opponent comes down past them, not on them
    X0 = 0.45
    fA = A.Frame('rope', [X0, D_, -1.05, 180])
    head = lambda t, side: body_point(L, 'ropes.pulled-over-top', fD, t, 'head', (0.09 * side, 0.05, 0))
    keys = [stance_at(0, [X0, D_, -1.05], 180)]
    keys.append(K(0.1, [X0 - 0.03, D_, -0.98], 180, A.STANCE, body(hy=0.0, lean=-6), lhand=head(0.1, 1), rhand=head(0.1, -1), feet=stand_feet([X0 - 0.03, D_, -0.98], 180, width=0.15)))
    keys.append(K(0.3, [X0 - 0.03, D_, -0.98], 180, A.STANCE, body(hy=-0.02, lean=-4), lhand=head(0.3, 1), rhand=head(0.3, -1), feet=stand_feet([X0 - 0.03, D_, -0.98], 180, width=0.15)))
    keys.append(K(0.55, [X0 + 0.05, D_, -1.15], 200, A.STANCE, body(hy=-0.18, lean=10, spine=(6, 0, 0)), lhand=head(0.55, 1), rhand=head(0.55, -1),
                  lfoot=plant(X0 + 0.2, -1.25, D_), rfoot=plant(X0 - 0.08, -1.05, D_)))                     # heave, turning the hips
    keys.append(K(0.8, [X0 + 0.4, D_, -1.25], 225, A.STANCE, body(hy=-0.12, lean=6), ARMS_OUT, lfoot=plant(X0 + 0.55, -1.32, D_), rfoot=plant(X0 + 0.3, -1.12, D_)))   # step aside
    keys.append(K(1.1, [X0 + 0.45, D_, -1.3], 215, A.GUARD, feet=stand_feet([X0 + 0.45, D_, -1.3], 215)))
    keys.append(K(1.4, [X0 + 0.45, D_, -1.3], 215, A.GUARD, feet=stand_feet([X0 + 0.45, D_, -1.3], 215)))
    L.clip('ropes.pull-over-top', 'Pull opponent over the top rope', 1.4, keys, fA,
           desc='Attacker on the floor: reach up to an opponent draped over the top rope, grab the head and heave them over, stepping aside as they crash down.',
           events=[ev(0.1, 'grab', attachment='rightHandGrip'), ev(0.3, 'grip_locked'), ev(0.35, 'attack_start'), ev(0.6, 'release'), ev(0.8, 'footstep'), ev(1.3, 'recover')],
           tags=['ropes', 'attacker', 'floor', 'elimination'], start_loc='floor', end_loc='floor', placement='floor-facing-ring',
           phases=[('contact', 0, 0.3), ('launch', 0.3, 0.6), ('recovery', 0.6, 1.4)], interrupt={'windows': [[1.0, 1.4]]})
