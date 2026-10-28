"""Phase 3, damage reactions. Mat frame: the wrestler starts at the origin facing -z, the attacker in front.
Reactions start from the fighting stance (or the stated state) and say where they end up via root motion."""
from common import *

GUARD = A.GUARD

def G(t, root, yaw, *parts, lf=None, rf=None, lh=None, rh=None, w=0.13, base=GUARD):
    f = stand_feet(list(root), yaw, width=w)
    return K(t, list(root), yaw, base, *parts, lfoot=lf or f[0], rfoot=rf or f[1], lhand=lh, rhand=rh)

def clip(L, cid, name, dur, keys, events, desc, tags, f=None, **kw):
    kw.setdefault('placement', 'center')
    L.clip(cid, name, dur, keys, f or A.center(), events=events, desc=desc, tags=['reaction'] + tags, **kw)

HUNCHED = {'spine': r(-24), 'chest': r(-12), 'neck': r(20),
           'rightUpperArm': r(30, 0, -10), 'leftUpperArm': r(30, 0, 10), 'rightForearm': r(100), 'leftForearm': r(100)}
CLUTCH_GUT = lambda root, yaw: dict(lh=[*rel(root, yaw, -0.06, 0, -0.2)[:1], 1.0, rel(root, yaw, -0.06, 0, -0.2)[2]],
                                    rh=[*rel(root, yaw, 0.06, 0, -0.2)[:1], 0.98, rel(root, yaw, 0.06, 0, -0.2)[2]])


def build(L):
    O = [0, 0, 0]

    # ---------------------------------------------------------------- chop sell
    keys = [G(0, O, 0)]
    keys.append(G(0.08, [0, 0, 0.06], 0, body(hy=-0.04, lean=18, neck=(-30, 0, 0), chest=(8, 0, 0)), ARMS_OUT))
    keys.append(G(0.3, [0, 0, 0.3], 0, body(hy=-0.08, lean=14, neck=(-34, 0, 0), chest=(6, 0, 0)), ARMS_OUT, lf=plant(-0.13, 0.2), rf=plant(0.14, 0.45)))
    keys.append(G(0.6, [0, 0, 0.35], 0, body(hy=-0.1, lean=-14, turn=-14, neck=(10, 0, 0)), {'leftUpperArm': r(40, 0, 10), 'leftForearm': r(110)},
                  lh=None, rh=[-0.02, 1.36, 0.17], lf=plant(-0.13, 0.25), rf=plant(0.14, 0.45)))                       # hand to the chest
    keys.append(G(0.95, [0, 0, 0.38], 0, body(hy=-0.06, lean=-6, turn=10, neck=(-20, 0, 0)), rh=[-0.04, 1.38, 0.2], lf=plant(-0.13, 0.28), rf=plant(0.14, 0.45)))
    keys.append(G(1.4, [0, 0, 0.38], 0))
    clip(L, 'reactions.chop-sell', 'Sell a chest chop', 1.4, keys,
         [ev(0, 'hit_received', zone='body'), ev(0.3, 'footstep'), ev(1.35, 'recover')],
         'Chopped across the chest: jolt back with the head thrown up, stumble a step, clutch and rub the chest, shake it off.',
         ['chop', 'body'], interrupt={'windows': [[1.0, 1.4]]})

    # ---------------------------------------------------------------- head snaps (left authored, right mirrored)
    keys = [G(0, O, 0)]
    keys.append(G(0.06, [0, 0, 0.02], 25, body(hy=-0.04, roll=8, neck=(0, 45, 14), head=(0, 20, 6)), {'leftUpperArm': r(20, 0, 40), 'rightUpperArm': r(40, 0, -20)}))
    keys.append(G(0.25, [-0.12, 0, 0.12], 70, body(hy=-0.12, roll=12, lean=6, neck=(10, 30, 16)), ARMS_OUT, lf=plant(-0.3, 0.12), rf=plant(0.08, -0.05)))
    keys.append(G(0.5, [-0.2, 0, 0.18], 85, body(hy=-0.14, roll=6, neck=(18, 10, 8)), HUNCHED, lf=plant(-0.3, 0.3), rf=plant(-0.05, 0.06)))
    keys.append(G(0.8, [-0.2, 0, 0.18], 40, body(hy=-0.08, neck=(8, 0, 0))))
    keys.append(G(1.05, [-0.2, 0, 0.18], 0))
    evs = [ev(0, 'hit_received', zone='head', side='right'), ev(0.25, 'footstep', foot='left'), ev(0.5, 'footstep', foot='right'), ev(0.05, 'stun_start'), ev(1.0, 'recover')]
    clip(L, 'reactions.head-snap-left', 'Head snapped to the left', 1.05, keys, evs,
         'A big hit to the right side of the face whips the head to the left; the body follows through a quarter turn and a stagger step, then squares up again.',
         ['head', 'heavy'], interrupt={'windows': [[0.8, 1.05]]})
    clip(L, 'reactions.head-snap-right', 'Head snapped to the right', 1.05, mirror_keys(keys), mirror_events(evs),
         'Mirror of head-snap-left: hit on the left side of the face, head whips to the right with a quarter turn and stagger.',
         ['head', 'heavy'], interrupt={'windows': [[0.8, 1.05]]})

    # ---------------------------------------------------------------- doubled over (gut) -> bent-over state
    BENT = {'hips': {'p': [0, -0.1, 0.12], 'r': [-12, 0, 0]}, 'spine': r(-38), 'chest': r(-18), 'neck': r(30), 'head': r(6)}
    def bent(t, root=(0, 0, 0.3), sway=0.0, dip=0.0):
        root = list(root)
        return G(t, root, 0, BENT, body(hy=-0.1 - dip, hz=0.12, lean=-12, roll=sway * 20, spine=(-38, 0, 0), chest=(-18, 0, 0), neck=(30, 0, 0)),
                 **CLUTCH_GUT(root, 0), w=0.15)
    keys = [G(0, O, 0)]
    keys.append(G(0.08, [0, 0, 0.05], 0, BENT, body(hy=-0.12, hz=0.12, lean=-20, spine=(-40, 0, 0), chest=(-20, 0, 0), neck=(10, 0, 0)), ARMS_FWD))
    keys.append(G(0.35, [0, 0, 0.22], 0, BENT, body(hy=-0.16, hz=0.14, lean=-16, spine=(-42, 0, 0), chest=(-20, 0, 0), neck=(26, 0, 0)), **CLUTCH_GUT([0, 0, 0.22], 0),
                  lf=plant(-0.14, 0.12), rf=plant(0.15, 0.36)))
    keys.append(bent(0.7, dip=0.03))
    keys.append(bent(1.0))
    clip(L, 'reactions.doubled-over', 'Doubled over', 1.0, keys,
         [ev(0, 'hit_received', zone='body'), ev(0.35, 'footstep'), ev(0.4, 'stun_start')],
         'Hit in the gut: fold forward clutching the stomach and back off a step. Ends bent over, the set-up position for DDTs, suplexes and powerbombs.',
         ['body', 'setup'], end_state='bent-over', interrupt={'windows': []})
    keys = [bent(0), bent(0.6, sway=0.1, dip=0.02), bent(1.2, sway=-0.02, dip=-0.02), bent(1.8, sway=-0.1, dip=0.02), bent(2.4)]
    clip(L, 'reactions.bent-over-idle', 'Bent over, winded (loop)', 2.4, keys, [],
         'Bent over clutching the stomach, swaying and gasping. Grapple set-ups (DDT, suplex, powerbomb) start from here.',
         ['body', 'setup', 'loop'], loop=True, start_state='bent-over', end_state='bent-over', placement='center')

    # ---------------------------------------------------------------- spin-out fall (clothesline / lariat)
    keys = [G(0, O, 0)]
    keys.append(G(0.08, [0, 0.05, 0.12], -40, body(hy=-0.02, lean=30, neck=(-30, 0, 0)), ARMS_OUT))
    keys.append(G(0.3, [0.05, 0.1, 0.32], -150, body(hy=-0.06, lean=40, roll=-14, neck=(-20, 0, 0)), ARMS_OUT, lf=air(-0.1, 0.25, 0.4), rf=plant(0.1, 0.3)))
    keys.append(G(0.5, [0.1, 0.0, 0.5], -260, body(hy=-0.25, lean=-30, roll=-10), ARMS_FWD, lf=plant(0.0, 0.62), rf=air(0.2, 0.3, 0.45)))
    keys.append(K(0.72, [0.12, 0, 0.6], -300, A.LIE_FRONT, body(hy=-0.6, lean=-70), ARMS_FWD))
    keys.append(K(0.86, [0.12, 0, 0.62], -320, A.LIE_FRONT))
    keys.append(K(1.5, [0.12, 0, 0.62], -320, A.LIE_FRONT))
    clip(L, 'reactions.spin-out-fall', 'Spin out and fall', 1.5, keys,
         [ev(0, 'hit_received', zone='head'), ev(0.3, 'footstep'), ev(0.5, 'footstep'), ev(0.86, 'land', zone='front'), ev(0.86, 'impact', surface='mat')],
         'Caught by a clothesline: the upper body is whipped round, the wrestler spins nearly a full turn and pitches face down.',
         ['head', 'knockdown', 'heavy'], end_state='lying-front', interrupt={'windows': []})

    # ---------------------------------------------------------------- long staggers
    keys = [G(0, O, 0)]
    keys.append(G(0.1, [0, 0, 0.1], 0, body(hy=-0.02, lean=22, neck=(-24, 0, 0)), ARMS_OUT))
    keys.append(G(0.38, [0.05, 0, 0.45], 0, body(hy=-0.08, lean=20, roll=6), ARMS_OUT, lf=plant(-0.1, 0.25), rf=plant(0.18, 0.62)))
    keys.append(G(0.66, [0.02, 0, 0.85], 0, body(hy=-0.1, lean=18, roll=-6), ARMS_OUT, lf=plant(-0.16, 1.0), rf=plant(0.16, 0.7)))
    keys.append(G(0.96, [0.04, 0, 1.2], 0, body(hy=-0.22, lean=12, roll=4), ARMS_BALANCE, lf=plant(-0.13, 1.05), rf=plant(0.16, 1.38)))     # nearly goes down
    keys.append(G(1.25, [0.04, 0, 1.3], 0, body(hy=-0.18, lean=-14), HUNCHED, lf=plant(-0.13, 1.18), rf=plant(0.16, 1.38)))
    keys.append(G(1.6, [0.04, 0, 1.3], 0))
    clip(L, 'reactions.stagger-back-long', 'Long stagger backwards', 1.6, keys,
         [ev(0, 'hit_received', zone='body'), ev(0.38, 'footstep'), ev(0.66, 'footstep'), ev(0.96, 'footstep'), ev(1.55, 'recover')],
         'A heavy hit sends them reeling back three steps, arms windmilling, almost going down before catching themselves 1.3 m back.',
         ['body', 'heavy', 'stagger'], interrupt={'windows': [[1.2, 1.6]]})

    keys = [G(0, O, 0)]
    keys.append(G(0.1, [0, 0, -0.1], 0, body(hy=-0.04, lean=-26, neck=(-20, 0, 0)), {'rightUpperArm': r(-40, 0, -30), 'leftUpperArm': r(-40, 0, 30)}))
    keys.append(G(0.38, [0, 0, -0.5], 0, body(hy=-0.1, lean=-30, roll=6), ARMS_FWD, lf=plant(-0.13, -0.68), rf=plant(0.14, -0.3)))
    keys.append(G(0.66, [0, 0, -0.95], 0, body(hy=-0.12, lean=-26, roll=-6), ARMS_FWD, lf=plant(-0.13, -0.8), rf=plant(0.14, -1.12)))
    keys.append(G(0.96, [0, 0, -1.3], 0, body(hy=-0.2, lean=-20), ARMS_BALANCE, lf=plant(-0.13, -1.48), rf=plant(0.14, -1.2)))
    keys.append(G(1.25, [0, 0, -1.38], 0, body(hy=-0.1, lean=-8), lf=plant(-0.13, -1.5), rf=plant(0.14, -1.3)))
    keys.append(G(1.6, [0, 0, -1.4], 0))
    clip(L, 'reactions.stagger-forward-long', 'Long stagger forwards', 1.6, keys,
         [ev(0, 'hit_received', zone='back'), ev(0.38, 'footstep'), ev(0.66, 'footstep'), ev(0.96, 'footstep'), ev(1.55, 'recover')],
         'Hit hard from behind: thrown forward, stumbling three steps with the arms out before regaining balance 1.4 m ahead.',
         ['back', 'heavy', 'stagger'], interrupt={'windows': [[1.2, 1.6]]})

    # ---------------------------------------------------------------- limb selling and kneeling
    def arm_hurt(t, sway=0.0, look=0):
        root = [0, 0, 0]
        return G(t, root, 0, A.STANCE, body(hy=-0.05, turn=-12 + sway * 20, roll=-6, lean=-6, neck=(16, look, 0)),
                 {'rightUpperArm': r(20, 0, -6), 'rightForearm': r(70)}, lh=[0.13, 1.18, -0.2], base=A.STANCE)
    keys = [arm_hurt(0), arm_hurt(0.8, 0.2, -20), arm_hurt(1.6, -0.15, 15), arm_hurt(2.4)]
    clip(L, 'reactions.arm-hurt-loop', 'Hurt arm (loop)', 2.4, keys, [],
         'Selling an injured right arm: elbow tucked in, cradled by the left hand, shoulders hunched, rolling it gingerly.',
         ['limb', 'injury', 'loop'], loop=True, start_state='standing', end_state='standing')

    KNEEL = {'hips': {'p': [0, -0.515, 0.04]}, 'spine': r(-14), 'neck': r(-6),
             'rightUpperLeg': r(10, 0, 4), 'leftUpperLeg': r(10, 0, -4), 'rightLowerLeg': r(-100), 'leftLowerLeg': r(-100), 'rightFoot': r(-55), 'leftFoot': r(-55)}
    def kneel(t, sway=0.0, sag=0.0, look=0):
        return K(t, [0, 0, 0], 0, KNEEL, body(hy=-0.515 - sag, hz=0.04, roll=sway * 25, lean=-8, spine=(-16, 0, 0), neck=(22 + sag * 100, look, 0)),
                 {'rightUpperArm': r(10, 0, -12), 'leftUpperArm': r(10, 0, 12), 'rightForearm': r(20), 'leftForearm': r(20)})
    keys = [kneel(0), kneel(0.8, 0.1, 0.03, 15), kneel(1.6, -0.08, -0.01, -10), kneel(2.4)]
    clip(L, 'reactions.kneeling-stunned', 'Stunned on the knees (loop)', 2.4, keys, [],
         'Up on both knees, arms hanging, head lolling and swaying. A sitting duck for kicks to the head.',
         ['stunned', 'loop', 'kneeling'], loop=True, start_state='kneeling', end_state='kneeling')

    # ---------------------------------------------------------------- hit while propped in the corner (corner frame)
    S2 = 0.70711
    diag = lambda d: [d * S2, 0, d * S2]
    def corner_back(t, sag=0.0, lean=12, look=0, push=0.0):
        root = diag(0.48 - push)
        return K(t, root, -135, A.LEAN, body(hy=-0.06 - sag, hz=0.14 + push, lean=lean, neck=(-6, look, 0)),
                 lhand=grip(0.48, ROPE_TOP, 0.0, 0.0), rhand=grip(0.0, ROPE_TOP, 0.48, 0.0), feet=stand_feet(root, -135, width=0.15))
    f = A.Frame('corner', diag(0.48) + [-135])
    keys = [corner_back(0), corner_back(0.07, push=0.06, lean=24, sag=-0.02), corner_back(0.2, push=0.04, lean=20, sag=0.05),
            corner_back(0.45, lean=-4, sag=0.1, look=10), corner_back(0.75, lean=8, sag=0.04), corner_back(1.1)]
    L.clip('reactions.hit-in-corner', 'Hit in the corner', 1.1, keys, f,
           events=[ev(0, 'hit_received', zone='body'), ev(0.07, 'impact', surface='turnbuckle'), ev(0.1, 'rope_contact', attachment='back')],
           desc='Propped in the corner and hit by a splash or charge: slammed back into the turnbuckle, folds forward, then sags back into the corner.',
           tags=['reaction', 'corner'], start_state='corner-back', end_state='corner-back', placement='inside-back-to-corner')

    # ---------------------------------------------------------------- knockdowns
    keys = [G(0, O, 0)]
    keys.append(G(0.15, [0, 0, 0.02], 0, body(hy=-0.25, roll=10, neck=(20, 0, 10)), {'rightUpperArm': r(10, 0, -20), 'leftUpperArm': r(10, 0, 20)}))   # knees go
    keys.append(K(0.4, [0.05, 0, 0.0], 0, KNEEL, body(hy=-0.52, roll=14, neck=(26, 0, 0))))
    keys.append(K(0.62, [0.18, 0, -0.1], 20, A.LIE_FRONT, body(hy=-0.55, lean=-55, roll=30), ARMS_FWD))
    keys.append(K(0.82, [0.25, 0, -0.18], 30, A.LIE_FRONT))
    keys.append(K(1.3, [0.25, 0, -0.18], 30, A.LIE_FRONT))
    clip(L, 'reactions.knee-buckle-fall', 'Knees buckle', 1.3, keys,
         [ev(0, 'hit_received', zone='head'), ev(0.4, 'land', zone='knees'), ev(0.82, 'land', zone='front'), ev(0.82, 'impact', surface='mat')],
         'Out on their feet: the knees go first, they drop to kneeling and topple forward onto the face.',
         ['knockdown', 'ko'], end_state='lying-front', interrupt={'windows': []})

    flip = {'rightUpperLeg': r(30, 0, 6), 'leftUpperLeg': r(30, 0, -6), 'rightLowerLeg': r(-40), 'leftLowerLeg': r(-40)}
    keys = [G(0, O, 0)]
    keys.append(G(0.08, [0, 0.05, 0.12], 0, body(hy=-0.02, lean=40, neck=(-40, 0, 0)), ARMS_OUT))
    keys.append(K(0.28, [0, 0.55, 0.45], 0, flip, ARMS_OUT, body(hy=-0.2, lean=150)))
    keys.append(K(0.46, [0, 0.45, 0.8], 0, flip, ARMS_OUT, body(hy=-0.4, lean=240)))
    keys.append(K(0.6, [0, 0, 1.05], 0, A.LIE_FRONT, body(hy=-0.8, lean=270)))
    keys.append(K(0.76, [0, 0, 1.1], 0, A.LIE_FRONT, body(hy=-0.84, lean=270)))
    keys.append(K(1.3, [0, 0, 1.1], 0, A.LIE_FRONT, body(hy=-0.84, lean=270)))
    clip(L, 'reactions.flip-bump', 'Flip bump', 1.3, keys,
         [ev(0, 'hit_received', zone='head'), ev(0.28, 'apex'), ev(0.6, 'land', zone='front'), ev(0.6, 'impact', surface='mat')],
         'Sells a big lariat by flipping inside out: feet go over the head in a full backwards flip and they land face down about 1 m back.',
         ['knockdown', 'heavy', 'bump'], end_state='lying-front', interrupt={'windows': []})

    keys = [G(0, O, 0)]
    keys.append(G(0.06, [0, 0, 0.03], 0, body(hy=-0.02, lean=16, neck=(-40, 0, 0), head=(-14, 0, 0)), ARMS_OUT))                       # jaw snaps up
    keys.append(G(0.25, [0, 0, 0.06], 0, body(hy=-0.4, lean=6, neck=(-30, 0, 0)), {'rightUpperArm': r(0, 0, -20), 'leftUpperArm': r(0, 0, 20)}))   # limp drop
    keys.append(K(0.45, [0, 0, 0.12], 0, A.F3, body(hy=-0.65, lean=40), ARMS_OUT))
    keys.append(K(0.62, [0, 0, 0.18], 0, A.LIE_BACK, body(hy=-0.83, lean=90)))
    keys.append(K(1.4, [0, 0, 0.18], 0, A.LIE_BACK))
    clip(L, 'reactions.superkick-drop', 'Dropped by a superkick', 1.4, keys,
         [ev(0, 'hit_received', zone='head'), ev(0.62, 'land', zone='back'), ev(0.62, 'impact', surface='mat'), ev(0.65, 'stun_start')],
         'Jaw snapped up, then out cold on the feet: the legs fold and they drop straight down and back, flat out.',
         ['knockdown', 'ko', 'head'], end_state='lying-back', interrupt={'windows': []})

    keys = [G(0, O, 0)]
    keys.append(G(0.06, [0, 0.05, 0.2], 0, body(hy=-0.02, lean=30, neck=(-30, 0, 0)), ARMS_OUT))
    keys.append(K(0.26, [0, 0.45, 0.85], 0, A.STANCE, body(hy=-0.25, lean=60), ARMS_OUT, {'rightUpperLeg': r(40), 'leftUpperLeg': r(50), 'rightLowerLeg': r(-30)}))
    keys.append(K(0.46, [0, 0.2, 1.45], 0, A.LIE_BACK, body(hy=-0.5, lean=82), ARMS_OUT))
    keys.append(K(0.6, [0, 0, 1.7], 0, A.LIE_BACK, {'hips': {'p': [0, -0.8, 0], 'r': [90, 0, 0]}}))
    keys.append(K(0.85, [0, 0, 1.95], 0, A.LIE_BACK))                                                       # slides on the canvas
    keys.append(K(1.4, [0, 0, 1.98], 0, A.LIE_BACK))
    clip(L, 'reactions.dropkick-fly-back', 'Blasted back by a dropkick', 1.4, keys,
         [ev(0, 'hit_received', zone='body'), ev(0.26, 'apex'), ev(0.6, 'land', zone='back'), ev(0.6, 'impact', surface='mat')],
         'Both feet to the chest launch them backwards off their feet; they land flat on the back about 1.7 m away and slide.',
         ['knockdown', 'heavy', 'body'], end_state='lying-back', interrupt={'windows': []})
