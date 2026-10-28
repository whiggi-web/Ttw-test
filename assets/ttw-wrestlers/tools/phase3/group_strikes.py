"""Phase 3, strikes. Every strike starts and ends in the batch fighting stance (GUARD == movement.idle-fight frame 0)
unless its start/end state says otherwise. Mat frame: start at the origin facing -z; the opponent is assumed square
on, about 0.8 m ahead (hit targets below), and each hit event carries zone and reach so combat can resolve it.
"""
from common import *

T_HEAD, T_JAW, T_CHEST, T_GUT = [0, 1.62, -0.6], [0, 1.55, -0.62], [0, 1.36, -0.6], [0, 1.1, -0.58]
GUARD = A.GUARD
LEAD = {'leftUpperArm': r(55, 0, 22), 'leftForearm': r(120)}           # left hand stays up in guard
REAR = {'rightUpperArm': r(50, 0, -22), 'rightForearm': r(118)}

def G(t, root, yaw, *parts, lf=None, rf=None, lh=None, rh=None, w=0.13, base=GUARD, poles=None):
    root = list(root)
    f = stand_feet(root, yaw, width=w)
    return K(t, root, yaw, base, *parts, lfoot=lf or f[0], rfoot=rf or f[1], lhand=lh, rhand=rh, poles=poles)

def stepped(root, yaw, lead=0.25, back=0.12, w=0.13):
    """feet in a fighting step: left foot forward"""
    a = rel(root, yaw, -w, 0, -lead); b = rel(root, yaw, w, 0, back)
    return plant(a[0], a[2], yaw=yaw), plant(b[0], b[2], yaw=yaw)

def at(root, yaw, x, y, z):
    p = rel(root, yaw, x, 0, z); return [p[0], y, p[2]]

def hitev(t, zone, attachment='propRightHand', reach=0.6, **kw):
    return ev(t, 'hit', zone=zone, attachment=attachment, reach=reach, **kw)

def clip(L, cid, name, dur, keys, events, desc, tags, f=None, **kw):
    kw.setdefault('placement', 'center')
    L.clip(cid, name, dur, keys, f or A.center(), events=events, desc=desc, tags=['strike'] + tags, **kw)


def build(L):
    O = [0, 0, 0]

    # ---------------------------------------------------------------- knife-edge chop
    lf, rf = stepped([0, 0, -0.08], 0)
    keys = [G(0, O, 0)]
    keys.append(G(0.3, [0, 0, 0.02], 0, body(hy=-0.06, turn=-38, spine=(0, -10, 0)), LEAD, rh=[0.62, 1.5, 0.12], poles={'rightHand': [0.3, -1, 0.6]}))
    keys.append(G(0.42, [0, 0, -0.08], 0, body(hy=-0.07, turn=6, lean=0, spine=(0, 4, 0)), LEAD, rh=[0.12, 1.38, -0.72], lf=lf, rf=rf))
    keys.append(G(0.56, [0, 0, -0.1], 0, body(hy=-0.06, turn=38, lean=-4, spine=(0, 14, 0)), LEAD, rh=[-0.38, 1.25, -0.4], lf=lf, rf=rf))
    keys.append(G(0.8, [0, 0, -0.06], 0, body(hy=-0.04, turn=8), lf=lf, rf=rf))
    keys.append(G(1.05, [0, 0, -0.04], 0))
    clip(L, 'striking.chop', 'Knife-edge chop', 1.05, keys,
         [ev(0.18, 'attack_start'), hitev(0.42, 'body', reach=0.72), ev(0.42, 'footstep', foot='left'), ev(1.0, 'recover')],
         'Wind the right arm back and lash an open-hand chop across the opponent\'s chest, stepping in on the left foot.',
         ['chop', 'open-hand'], phases=[('approach', 0, 0.3), ('contact', 0.3, 0.5), ('recovery', 0.5, 1.05)], interrupt={'windows': [[0, 0.15], [0.75, 1.05]]})

    # ---------------------------------------------------------------- forearm smash
    lf, rf = stepped([0, 0, -0.1], 0)
    keys = [G(0, O, 0)]
    keys.append(G(0.28, [0, 0, 0.02], 0, body(hy=-0.07, turn=-34), LEAD, rh=[0.42, 1.68, 0.02], poles={'rightHand': [1, 0.6, 0.2]}))
    keys.append(G(0.38, [0, 0, -0.1], 0, body(hy=-0.08, turn=18, lean=-10), LEAD, rh=[-0.12, 1.62, -0.48], lf=lf, rf=rf, poles={'rightHand': [1, 0.4, -0.4]}))
    keys.append(G(0.52, [0, 0, -0.12], 0, body(hy=-0.07, turn=30, lean=-8), LEAD, rh=[-0.36, 1.5, -0.3], lf=lf, rf=rf, poles={'rightHand': [1, 0.3, -0.6]}))
    keys.append(G(0.9, [0, 0, -0.08], 0, lf=lf, rf=rf))
    clip(L, 'striking.forearm-smash', 'Forearm smash', 0.9, keys,
         [ev(0.16, 'attack_start'), hitev(0.38, 'head', attachment='rightForearm', reach=0.5), ev(0.38, 'footstep', foot='left'), ev(0.85, 'recover')],
         'Cock the right elbow high and club the forearm across the side of the opponent\'s head.',
         ['forearm', 'brawl'], interrupt={'windows': [[0, 0.12], [0.65, 0.9]]})

    # ---------------------------------------------------------------- european uppercut
    lf, rf = stepped([0, 0, -0.06], 0, lead=0.28)
    keys = [G(0, O, 0)]
    keys.append(G(0.22, [0, 0, 0.0], 0, body(hy=-0.2, turn=-20, lean=-12), LEAD, rh=[0.25, 1.0, -0.15], lf=lf, rf=rf))
    keys.append(G(0.36, [0, 0, -0.06], 0, body(hy=0.0, turn=12, lean=6), LEAD, rh=[0.02, 1.6, -0.46], lf=lf, rf=rf, poles={'rightHand': [0.6, -0.5, -0.2]}))
    keys.append(G(0.5, [0, 0, -0.06], 0, body(hy=0.01, turn=16, lean=10), LEAD, rh=[0.0, 1.85, -0.35], lf=lf, rf=rf))
    keys.append(G(0.9, [0, 0, -0.04], 0))
    clip(L, 'striking.european-uppercut', 'European uppercut', 0.9, keys,
         [ev(0.12, 'attack_start'), hitev(0.36, 'head', attachment='rightForearm', reach=0.5), ev(0.85, 'recover')],
         'Dip, then drive the right forearm straight up under the opponent\'s chin, rising onto the toes.',
         ['forearm', 'uppercut'], interrupt={'windows': [[0, 0.1], [0.65, 0.9]]})

    # ---------------------------------------------------------------- back elbow (opponent behind)
    keys = [G(0, O, 0)]
    keys.append(G(0.22, [0, 0, -0.03], 0, body(hy=-0.08, turn=25, neck=(0, -50, 0)), LEAD, {'rightUpperArm': r(70, 0, -10), 'rightForearm': r(130)}))
    keys.append(G(0.36, [0, 0, 0.06], 0, body(hy=-0.1, turn=-30, lean=8, neck=(0, -60, 0)), LEAD, {'rightUpperArm': r(-55, 0, -18), 'rightForearm': r(135)},
                  lf=plant(-0.13, -0.02), rf=plant(0.15, 0.2)))
    keys.append(G(0.5, [0, 0, 0.06], 0, body(hy=-0.08, turn=-34, lean=6, neck=(0, -50, 0)), LEAD, {'rightUpperArm': r(-60, 0, -20), 'rightForearm': r(135)},
                  lf=plant(-0.13, -0.02), rf=plant(0.15, 0.2)))
    keys.append(G(0.9, [0, 0, 0.04], 0))
    clip(L, 'striking.back-elbow', 'Back elbow', 0.9, keys,
         [ev(0.18, 'attack_start'), hitev(0.36, 'head', attachment='rightForearm', reach=-0.45, direction='behind'), ev(0.36, 'footstep', foot='right'), ev(0.85, 'recover')],
         'Opponent behind: glance back and drive the right elbow backwards into their face. Hit reach is negative (behind).',
         ['elbow', 'counter', 'rear'], interrupt={'windows': [[0, 0.12], [0.65, 0.9]]})

    # ---------------------------------------------------------------- spinning backfist
    keys = [G(0, O, 0)]
    keys.append(G(0.18, [0.05, 0, -0.1], 0, body(hy=-0.08, turn=12), lf=plant(-0.05, -0.32), rf=plant(0.16, 0.05)))   # step across
    keys.append(G(0.34, [0.05, 0, -0.14], -120, body(hy=-0.1, turn=-20), {'rightUpperArm': r(20, 0, -40), 'rightForearm': r(100)}, LEAD,
                  lf=plant(-0.05, -0.32), rf=air(0.25, 0.2, -0.15)))
    keys.append(G(0.48, [0.02, 0, -0.18], -250, body(hy=-0.08, turn=-30, neck=(0, -40, 0)), {'rightUpperArm': r(0, 0, 80), 'rightForearm': r(40)}, LEAD,
                  lf=plant(-0.05, -0.32), rf=plant(0.12, -0.05)))
    keys.append(G(0.58, [0, 0, -0.2], -345, body(hy=-0.08, turn=-10), LEAD, rh=at([0, 0, -0.2], -345, 0.05, 1.62, -0.55), lf=plant(-0.1, -0.38), rf=plant(0.14, -0.08)))
    keys.append(G(0.72, [0, 0, -0.2], -370, body(hy=-0.07, turn=10), LEAD, rh=at([0, 0, -0.2], -370, -0.3, 1.55, -0.45), lf=plant(-0.12, -0.38), rf=plant(0.14, -0.06)))
    keys.append(G(1.1, [0, 0, -0.2], -360, w=0.13))
    clip(L, 'striking.spinning-backfist', 'Spinning backfist', 1.1, keys,
         [ev(0.18, 'footstep', foot='left'), ev(0.3, 'attack_start'), hitev(0.6, 'head', attachment='propRightHand', reach=0.65), ev(0.62, 'footstep', foot='right'), ev(1.05, 'recover')],
         'Step across, spin a full turn to the right and whip the back of the right fist into the opponent\'s head. Ends facing the same way (endYaw -360).',
         ['spin', 'backfist'], interrupt={'windows': [[0, 0.12], [0.85, 1.1]]})

    # ---------------------------------------------------------------- superkick
    keys = [G(0, O, 0)]
    keys.append(G(0.14, [0, 0, 0.03], 0, body(hy=-0.06), LEAD, REAR, lf=plant(-0.1, -0.06), rf=plant(0.14, 0.12)))
    keys.append(G(0.3, [0, 0, 0.03], 0, body(hy=-0.04, lean=14, turn=8), {'rightUpperArm': r(-20, 0, -40), 'leftUpperArm': r(30, 0, 50)},
                  lf=plant(-0.1, -0.02), rf=air(0.12, 0.85, -0.3, pitch=10)))                                   # chamber
    keys.append(G(0.42, [0, 0, 0.05], 0, body(hy=-0.02, lean=34, turn=12, neck=(-24, 0, 0)), {'rightUpperArm': r(-30, 0, -50), 'leftUpperArm': r(40, 0, 60)},
                  lf=plant(-0.1, -0.02), rf=air(0.08, 1.52, -0.66, pitch=75)))                                   # sole to the jaw
    keys.append(G(0.56, [0, 0, 0.04], 0, body(hy=-0.04, lean=22, turn=8), {'rightUpperArm': r(-20, 0, -40), 'leftUpperArm': r(30, 0, 50)},
                  lf=plant(-0.1, -0.02), rf=air(0.1, 0.7, -0.35, pitch=10)))
    keys.append(G(0.75, [0, 0, -0.06], 0, body(hy=-0.08), lf=plant(-0.12, -0.02), rf=plant(0.13, -0.2)))
    keys.append(G(1.1, [0, 0, -0.06], 0))
    clip(L, 'striking.superkick', 'Superkick', 1.1, keys,
         [ev(0.14, 'attack_start'), hitev(0.42, 'head', attachment='rightFoot', reach=0.75), ev(0.75, 'footstep', foot='right'), ev(1.05, 'recover')],
         'Chamber the right knee and snap the sole of the foot into the opponent\'s jaw, leaning well back for height.',
         ['kick', 'finisher'], interrupt={'windows': [[0, 0.1], [0.85, 1.1]]})

    # ---------------------------------------------------------------- big boot
    keys = [G(0, O, 0)]
    keys.append(G(0.3, [0, 0, -0.3], 0, body(hy=-0.03, lean=-4), lf=plant(-0.1, -0.5), rf=plant(0.14, -0.12)))         # step in
    keys.append(G(0.5, [0, 0, -0.42], 0, body(hy=0.0, lean=12), {'rightUpperArm': r(-10, 0, -30), 'leftUpperArm': r(20, 0, 30)},
                  lf=plant(-0.1, -0.5), rf=air(0.12, 1.0, -0.8, pitch=50)))
    keys.append(G(0.62, [0, 0, -0.45], 0, body(hy=0.02, lean=18, neck=(-8, 0, 0)), {'rightUpperArm': r(-20, 0, -40), 'leftUpperArm': r(30, 0, 40)},
                  lf=plant(-0.1, -0.5), rf=air(0.1, 1.45, -1.08, pitch=80)))
    keys.append(G(0.8, [0, 0, -0.45], 0, body(hy=-0.02, lean=8), lf=plant(-0.1, -0.5), rf=air(0.12, 0.6, -0.75, pitch=20)))
    keys.append(G(0.98, [0, 0, -0.55], 0, body(hy=-0.06), lf=plant(-0.12, -0.5), rf=plant(0.13, -0.68)))
    keys.append(G(1.3, [0, 0, -0.58], 0))
    clip(L, 'striking.big-boot', 'Big boot', 1.3, keys,
         [ev(0.3, 'footstep', foot='left'), ev(0.36, 'attack_start'), hitev(0.62, 'head', attachment='rightFoot', reach=1.2), ev(0.98, 'footstep', foot='right'), ev(1.25, 'recover')],
         'Big man\'s boot: step in and swing a straight right leg up so the sole meets the opponent\'s face. Travels 0.58 m.',
         ['kick', 'power'], interrupt={'windows': [[0, 0.2], [1.05, 1.3]]})

    # ---------------------------------------------------------------- headbutt
    hs = lambda s: [0.12 * s, 1.66, -0.6]
    keys = [G(0, O, 0)]
    keys.append(G(0.2, [0, 0, -0.05], 0, body(hy=-0.04, lean=-6), lh=hs(1), rh=hs(-1)))
    keys.append(G(0.34, [0, 0, -0.03], 0, body(hy=-0.03, lean=16, neck=(-20, 0, 0), head=(-10, 0, 0)), lh=hs(1), rh=hs(-1)))   # rear back
    keys.append(G(0.44, [0, 0, -0.1], 0, body(hy=-0.06, lean=-18, spine=(-8, 0, 0), neck=(20, 0, 0), head=(8, 0, 0)), lh=hs(1), rh=hs(-1),
                  lf=plant(-0.12, -0.3), rf=plant(0.13, 0.0)))
    keys.append(G(0.6, [0, 0, -0.08], 0, body(hy=-0.05, lean=-6), lf=plant(-0.12, -0.3), rf=plant(0.13, 0.0)))
    keys.append(G(0.95, [0, 0, -0.06], 0))
    clip(L, 'striking.headbutt', 'Headbutt', 0.95, keys,
         [ev(0.2, 'grab', attachment='leftHandGrip'), ev(0.3, 'attack_start'), hitev(0.44, 'head', attachment='head', reach=0.45), ev(0.5, 'release'), ev(0.9, 'recover')],
         'Grab the opponent\'s head with both hands, rear back and slam the forehead into theirs.',
         ['headbutt', 'brawl'], interrupt={'windows': [[0, 0.12], [0.7, 0.95]]})

    # ---------------------------------------------------------------- lariat (wrist pull)
    keys = [G(0, O, 0)]
    keys.append(G(0.22, [0, 0, -0.05], 0, body(hy=-0.05, turn=-10), lh=[-0.08, 1.15, -0.55], rh=[0.5, 1.35, 0.05]))          # grab the wrist
    keys.append(G(0.4, [0, 0, -0.02], 0, body(hy=-0.07, turn=-30, lean=6), lh=[-0.2, 1.1, -0.25], rh=[0.62, 1.4, 0.2]))       # yank them in
    keys.append(G(0.52, [0, 0, -0.28], 0, body(hy=-0.08, turn=20, lean=-10), {'leftUpperArm': r(30, 0, 20), 'leftForearm': r(60)}, {'rightUpperArm': r(10, 0, 92), 'rightForearm': r(6)},
                  lf=plant(-0.13, -0.55), rf=plant(0.13, -0.12)))
    keys.append(G(0.66, [0, 0, -0.4], 0, body(hy=-0.07, turn=40, lean=-12), {'leftUpperArm': r(20, 0, 20), 'leftForearm': r(60)}, {'rightUpperArm': r(30, 0, 70), 'rightForearm': r(10)},
                  lf=plant(-0.13, -0.6), rf=plant(0.16, -0.3)))
    keys.append(G(1.0, [0, 0, -0.45], 0, body(hy=-0.04), lf=plant(-0.13, -0.6), rf=plant(0.13, -0.32)))
    keys.append(G(1.25, [0, 0, -0.45], 0))
    clip(L, 'striking.lariat', 'Short-arm lariat', 1.25, keys,
         [ev(0.22, 'grab', attachment='leftHandGrip'), ev(0.3, 'attack_start'), ev(0.42, 'release'), hitev(0.54, 'head', attachment='rightForearm', reach=0.45),
          ev(0.54, 'footstep', foot='left'), ev(1.2, 'recover')],
         'Take the opponent\'s wrist, yank them in and drive a straight right arm across the neck as they arrive.',
         ['lariat', 'power'], interrupt={'windows': [[0, 0.15], [0.95, 1.25]]})

    # ---------------------------------------------------------------- leg kick combo (left then right)
    keys = [G(0, O, 0)]
    keys.append(G(0.2, [0, 0, 0.02], 0, body(hy=-0.06, turn=-24), lf=air(-0.2, 0.4, -0.35, pitch=10), rf=plant(0.13, 0.05)))
    keys.append(G(0.32, [0, 0, 0.02], 0, body(hy=-0.06, turn=-40, roll=10), lf=air(0.12, 0.55, -0.66, pitch=20), rf=plant(0.13, 0.05)))      # left kick, inside thigh
    keys.append(G(0.5, [0, 0, -0.02], 0, body(hy=-0.07, turn=0), lf=plant(-0.13, -0.15), rf=plant(0.13, 0.05)))
    keys.append(G(0.7, [0, 0, -0.04], 0, body(hy=-0.06, turn=24), lf=plant(-0.13, -0.15), rf=air(0.2, 0.42, -0.3, pitch=10)))
    keys.append(G(0.82, [0, 0, -0.04], 0, body(hy=-0.06, turn=42, roll=-10), lf=plant(-0.13, -0.15), rf=air(-0.1, 0.6, -0.68, pitch=20)))      # right kick, outside thigh
    keys.append(G(1.02, [0, 0, -0.04], 0, body(hy=-0.06, turn=8), lf=plant(-0.13, -0.15), rf=plant(0.14, 0.08)))
    keys.append(G(1.25, [0, 0, 0.1], 0, body(hy=-0.04), lf=plant(-0.13, 0.0), rf=plant(0.14, 0.2)))                                          # step back out
    keys.append(G(1.5, [0, 0, 0.1], 0))
    clip(L, 'striking.leg-kick-combo', 'Leg kick combination', 1.5, keys,
         [ev(0.15, 'attack_start'), hitev(0.32, 'legs', attachment='leftFoot', reach=0.65, side='left'), ev(0.5, 'footstep', foot='left'),
          hitev(0.82, 'legs', attachment='rightFoot', reach=0.68, side='right'), ev(1.02, 'footstep', foot='right'), ev(1.25, 'footstep'), ev(1.45, 'recover')],
         'Two low kicks to the thighs, left then right, then step back out of range. Two hit events.',
         ['kick', 'combo', 'low'], interrupt={'windows': [[0, 0.1], [0.5, 0.6], [1.2, 1.5]]})

    # ---------------------------------------------------------------- stomp (opponent down)
    keys = [G(0, O, 0)]
    keys.append(G(0.25, [0, 0, -0.08], 0, body(hy=-0.02, lean=-10, neck=(30, 0, 0)), {'rightUpperArm': r(-20, 0, -30), 'leftUpperArm': r(-20, 0, 30)},
                  lf=plant(-0.12, -0.1), rf=air(0.12, 0.75, -0.45, pitch=-10)))                         # knee high
    keys.append(G(0.38, [0, 0, -0.1], 0, body(hy=-0.12, lean=-14, neck=(34, 0, 0)), {'rightUpperArm': r(-30, 0, -40), 'leftUpperArm': r(-30, 0, 40)},
                  lf=plant(-0.12, -0.1), rf=air(0.08, 0.22, -0.55, pitch=0)))                           # stomp
    keys.append(G(0.56, [0, 0, -0.08], 0, body(hy=-0.06, lean=-8, neck=(24, 0, 0)), lf=plant(-0.12, -0.1), rf=air(0.12, 0.35, -0.35)))
    keys.append(G(0.8, [0, 0, -0.06], 0))
    clip(L, 'striking.stomp', 'Stomp', 0.8, keys,
         [ev(0.2, 'attack_start'), hitev(0.38, 'body', attachment='rightFoot', reach=0.55, target='ground'), ev(0.75, 'recover')],
         'Opponent on the mat in front: raise the right knee and stomp down onto their body.',
         ['stomp', 'ground-attack'], interrupt={'windows': [[0, 0.1], [0.6, 0.8]]})

    # ---------------------------------------------------------------- mount, mounted punches, dismount (opponent lying on the back, feet towards us)
    MOUNT = {'hips': {'p': [0, -0.6, 0.02], 'r': [-8, 0, 0]}, 'spine': r(-8), 'neck': r(14),
             'rightUpperLeg': r(80, 0, 40), 'leftUpperLeg': r(80, 0, -40), 'rightLowerLeg': r(-120), 'leftLowerLeg': r(-120),
             'rightFoot': r(-60), 'leftFoot': r(-60)}
    def mount(t, punch=None, lean=-8):
        root = [0, 0, -0.95]
        parts = [MOUNT, body(hy=-0.6, hz=0.02, lean=lean, spine=(-8, 0, 0), neck=(18, 0, 0))]
        lh = rh = None
        if punch == 'R': parts.append({'chest': r(0, 18, 0)}); rh = [0.02, 0.28, -1.55]; lh = [-0.25, 0.75, -1.05]
        elif punch == 'L': parts.append({'chest': r(0, -18, 0)}); lh = [-0.02, 0.28, -1.55]; rh = [0.25, 0.75, -1.05]
        elif punch == 'r': rh = [0.32, 1.25, -0.85]; lh = [-0.2, 0.6, -1.3]
        elif punch == 'l': lh = [-0.32, 1.25, -0.85]; rh = [0.2, 0.6, -1.3]
        else: lh, rh = [-0.25, 0.75, -1.15], [0.25, 0.75, -1.15]
        return K(t, root, 0, A.STANCE, *parts, lhand=lh, rhand=rh, lfoot=air(-0.4, 0.17, -0.75, pitch=-60), rfoot=air(0.4, 0.17, -0.75, pitch=-60))
    keys = [stance_at(0, [0, 0, 0], 0)]
    keys.append(K(0.35, [0, 0, -0.5], 0, A.STANCE, body(hy=-0.1, lean=-12, neck=(28, 0, 0)), lfoot=plant(-0.3, -0.62), rfoot=plant(0.14, -0.2)))   # step over
    keys.append(K(0.65, [0, 0, -0.85], 0, A.STANCE, body(hy=-0.35, lean=-10, neck=(20, 0, 0)), lfoot=plant(-0.38, -0.82), rfoot=plant(0.38, -0.78)))
    keys.append(mount(0.95))
    keys.append(mount(1.2))
    L.clip('striking.mount', 'Mount a downed opponent', 1.2, keys, A.center(),
           events=[ev(0.35, 'footstep'), ev(0.65, 'footstep'), ev(0.95, 'grip_locked')],
           desc='Opponent flat on the back with the feet towards you: step over them and drop into a mount, kneeling astride the waist.',
           tags=['strike', 'ground-attack', 'mount'], end_state='mounted', placement='center')
    keys = [mount(0), mount(0.15, 'r'), mount(0.3, 'R'), mount(0.45, 'l'), mount(0.6, 'L'), mount(0.75, 'r'), mount(0.9, 'R'), mount(1.05, 'l'), mount(1.2, 'L'), mount(1.4)]
    L.clip('striking.mounted-punches', 'Mounted punches (loop)', 1.4, keys, A.center(), loop=True,
           events=[hitev(0.3, 'head', reach=0.6, target='ground'), hitev(0.6, 'head', attachment='propLeftHand', reach=0.6, target='ground'),
                   hitev(0.9, 'head', reach=0.6, target='ground'), hitev(1.2, 'head', attachment='propLeftHand', reach=0.6, target='ground')],
           desc='Mounted: alternating right and left punches down to the opponent\'s head, four per loop.',
           tags=['strike', 'ground-attack', 'mount', 'loop'], start_state='mounted', end_state='mounted', placement='center')
    keys = [mount(0)]
    keys.append(K(0.3, [0, 0, -0.85], 0, A.STANCE, body(hy=-0.35, lean=-10), lfoot=plant(-0.38, -0.82), rfoot=plant(0.38, -0.78)))
    keys.append(K(0.6, [0, 0, -0.5], 0, A.STANCE, body(hy=-0.08, lean=-6), lfoot=plant(-0.3, -0.62), rfoot=plant(0.14, -0.3)))
    keys.append(K(0.9, [0, 0, -0.3], 0, GUARD, feet=stand_feet([0, 0, -0.3], 0)))
    keys.append(K(1.1, [0, 0, -0.3], 0, GUARD, feet=stand_feet([0, 0, -0.3], 0)))
    L.clip('striking.mount-off', 'Get off the mount', 1.1, keys, A.center(),
           events=[ev(0.3, 'footstep'), ev(0.6, 'footstep'), ev(1.05, 'recover')],
           desc='From the mount: push up off the opponent and step back over them into a fighting stance.',
           tags=['strike', 'ground-attack', 'mount'], start_state='mounted', placement='center')

    # ---------------------------------------------------------------- running attacks (from the run cycle)
    def run_in(keys, n=2):
        for i in range(n + 1):
            keys.append(K(i * 0.16, [0, 0, -i * 0.64], 0, run_pose(i * 0.16)))
    keys = []; run_in(keys)
    keys.append(K(0.44, [0, 0, -1.6], 0, run_pose(0.48), body(lean=-14, turn=-40, hy=-0.12), {'rightUpperArm': r(-10, 0, -10), 'leftUpperArm': r(40, 0, 20)}))
    keys.append(K(0.54, [0, 0, -1.95], 0, A.STANCE, body(hy=-0.2, lean=-22, turn=-50, spine=(-10, -10, 0)), {'rightUpperArm': r(20, 0, -20), 'rightForearm': r(100)},
                  lfoot=plant(-0.15, -2.1), rfoot=plant(0.15, -1.75)))                                   # shoulder lands
    keys.append(K(0.78, [0, 0, -2.25], 0, A.STANCE, body(hy=-0.1, lean=-8, turn=-20), lfoot=plant(-0.13, -2.3), rfoot=plant(0.13, -2.1)))
    keys.append(K(1.15, [0, 0, -2.3], 0, GUARD, feet=stand_feet([0, 0, -2.3], 0)))
    keys.append(K(1.4, [0, 0, -2.3], 0, GUARD, feet=stand_feet([0, 0, -2.3], 0)))
    clip(L, 'striking.shoulder-block', 'Running shoulder block', 1.4, keys,
         [ev(0.16, 'footstep'), ev(0.32, 'footstep'), ev(0.4, 'attack_start'), hitev(0.54, 'body', attachment='rightUpperArm', reach=0.4), ev(0.78, 'footstep'), ev(1.35, 'recover')],
         'From a run: dip and turn the right shoulder in, smash it into the opponent\'s chest and come to a stop.',
         ['running-attack', 'tackle'], start_state='running', interrupt={'windows': [[0, 0.3], [1.1, 1.4]]})

    keys = []; run_in(keys)
    keys.append(K(0.44, [0, 0, -1.55], 0, A.STANCE, body(hy=-0.2, lean=-12), ARMS_FWD, lfoot=plant(-0.13, -1.6), rfoot=air(0.13, 0.25, -1.4)))          # take-off
    knee = {'rightUpperLeg': r(110, 0, 4), 'rightLowerLeg': r(-120), 'leftUpperLeg': r(-10, 0, -4), 'leftLowerLeg': r(-60),
            'rightUpperArm': r(-30, 0, -30), 'leftUpperArm': r(-30, 0, 30), 'neck': r(-10)}
    keys.append(K(0.6, [0, 0.45, -1.95], 0, A.STANCE, body(hy=0.0, lean=12), knee))                                                                     # knee to the face
    keys.append(K(0.78, [0, 0.2, -2.25], 0, A.STANCE, body(hy=-0.04), ARMS_OUT, lfoot=air(-0.13, 0.25, -2.3), rfoot=air(0.13, 0.35, -2.2)))
    keys.append(K(0.9, [0, 0, -2.45], 0, A.STANCE, body(hy=-0.3, lean=-12), ARMS_OUT, feet=stand_feet([0, 0, -2.45], 0, width=0.16)))
    keys.append(K(1.25, [0, 0, -2.5], 0, GUARD, feet=stand_feet([0, 0, -2.5], 0)))
    clip(L, 'striking.running-knee', 'Running knee', 1.25, keys,
         [ev(0.16, 'footstep'), ev(0.32, 'footstep'), ev(0.44, 'jump'), ev(0.44, 'attack_start'), hitev(0.6, 'head', attachment='rightLowerLeg', reach=0.4), ev(0.6, 'apex'),
          ev(0.9, 'land'), ev(1.2, 'recover')],
         'From a run: leap and drive the right knee into the opponent\'s face, land and settle.',
         ['running-attack', 'knee', 'aerial'], start_state='running', interrupt={'windows': [[0, 0.3], [1.0, 1.25]]})

    # ---------------------------------------------------------------- discus clothesline (full spin)
    keys = [G(0, O, 0)]
    keys.append(G(0.25, [0.02, 0, -0.1], -90, body(hy=-0.1), ARMS_OUT, lf=plant(-0.05, -0.32), rf=plant(0.18, 0.05)))
    keys.append(G(0.45, [0.0, 0, -0.25], -200, body(hy=-0.1, turn=-10), ARMS_OUT, lf=plant(-0.08, -0.4), rf=air(0.15, 0.15, -0.15)))
    keys.append(G(0.62, [-0.02, 0, -0.38], -300, body(hy=-0.1, turn=-30), {'rightUpperArm': r(-20, 0, 90), 'rightForearm': r(4)}, lf=plant(-0.1, -0.45), rf=plant(0.12, -0.3)))
    keys.append(G(0.74, [0, 0, -0.5], -360, body(hy=-0.09, turn=-10), {'rightUpperArm': r(10, 0, 92), 'rightForearm': r(4)}, lf=plant(-0.12, -0.62), rf=plant(0.13, -0.32)))  # hit
    keys.append(G(0.9, [0, 0, -0.56], -380, body(hy=-0.08, turn=20), {'rightUpperArm': r(30, 0, 70), 'rightForearm': r(10)}, lf=plant(-0.12, -0.62), rf=plant(0.15, -0.36)))
    keys.append(G(1.3, [0, 0, -0.56], -360))
    clip(L, 'striking.discus-clothesline', 'Discus clothesline', 1.3, keys,
         [ev(0.25, 'footstep'), ev(0.45, 'attack_start'), ev(0.62, 'footstep'), hitev(0.74, 'head', attachment='rightForearm', reach=0.55), ev(1.25, 'recover')],
         'Spin a full turn to the right with the arms out, gathering speed, and lash the right arm across the opponent\'s neck as you come round.',
         ['spin', 'clothesline', 'finisher'], interrupt={'windows': [[0, 0.15], [1.05, 1.3]]})

    # ---------------------------------------------------------------- spinning heel kick
    keys = [G(0, O, 0)]
    keys.append(G(0.2, [0.04, 0, -0.08], -60, body(hy=-0.12), ARMS_OUT, lf=plant(-0.04, -0.28), rf=plant(0.2, 0.02)))
    keys.append(G(0.38, [0.02, 0, -0.14], -190, body(hy=-0.08, lean=-10, roll=-20), ARMS_OUT, lf=plant(-0.06, -0.32), rf=air(0.2, 0.9, 0.2, pitch=-10)))
    keys.append(G(0.5, [0.0, 0, -0.15], -290, body(hy=-0.06, lean=-14, roll=-30), ARMS_OUT, lf=plant(-0.06, -0.32), rf=air(0.45, 1.45, -0.3, pitch=0)))   # heel through the head
    keys.append(G(0.62, [0, 0, -0.15], -350, body(hy=-0.08, roll=-10), ARMS_OUT, lf=plant(-0.06, -0.32), rf=air(0.1, 0.6, -0.5)))
    keys.append(G(0.82, [0, 0, -0.15], -360, body(hy=-0.06), lf=plant(-0.12, -0.32), rf=plant(0.13, -0.04)))
    keys.append(G(1.2, [0, 0, -0.15], -360))
    clip(L, 'striking.spinning-heel-kick', 'Spinning heel kick', 1.2, keys,
         [ev(0.2, 'attack_start'), hitev(0.5, 'head', attachment='rightFoot', reach=0.7), ev(0.82, 'footstep', foot='right'), ev(1.15, 'recover')],
         'Pivot on the left foot through a full turn to the right, the straight right leg sweeping the heel through the opponent\'s head.',
         ['spin', 'kick'], interrupt={'windows': [[0, 0.12], [0.95, 1.2]]})

    # ---------------------------------------------------------------- dropkick (lands on the back)
    keys = [G(0, O, 0)]
    keys.append(G(0.2, [0, 0, -0.25], 0, body(hy=-0.25, lean=-14), ARMS_FWD, lf=plant(-0.13, -0.32), rf=plant(0.13, -0.15)))
    dk = {'rightUpperLeg': r(12, 0, 4), 'leftUpperLeg': r(18, 0, -4), 'rightLowerLeg': r(-8), 'leftLowerLeg': r(-14),
          'rightFoot': r(60), 'leftFoot': r(60), 'rightUpperArm': r(30, 0, -70), 'leftUpperArm': r(30, 0, 70)}
    keys.append(K(0.4, [0, 0.5, -0.5], 0, dk, body(hy=-0.25, lean=55)))
    keys.append(K(0.5, [0, 0.45, -0.55], 0, dk, body(hy=-0.3, lean=78)))                                    # feet to the chest
    keys.append(K(0.72, [0, 0.25, -0.62], 0, A.LIE_BACK, body(hy=-0.5, lean=82), ARMS_OUT))
    keys.append(K(0.86, [0, 0, -0.55], 0, A.LIE_BACK, {'hips': {'p': [0, -0.8, 0], 'r': [90, 0, 0]}}))
    keys.append(K(1.3, [0, 0, -0.55], 0, A.LIE_BACK))
    clip(L, 'striking.dropkick', 'Dropkick', 1.3, keys,
         [ev(0.2, 'jump'), ev(0.25, 'attack_start'), hitev(0.5, 'body', attachment='rightFoot', reach=0.75, both_feet=True), ev(0.5, 'apex'),
          ev(0.86, 'land', zone='back'), ev(0.86, 'impact', surface='mat')],
         'Leap and drive both feet into the opponent\'s chest with the body near horizontal, then crash down flat on the back.',
         ['kick', 'aerial', 'high-flyer'], end_state='lying-back', interrupt={'windows': [[0, 0.1]]},
         phases=[('launch', 0, 0.25), ('flight', 0.25, 0.86), ('landing', 0.86, 1.0), ('recovery', 1.0, 1.3)])

    # ---------------------------------------------------------------- enzuigiri (ends sitting)
    keys = [G(0, O, 0)]
    keys.append(G(0.2, [0, 0, -0.18], 0, body(hy=-0.22, lean=-10), ARMS_OUT, lf=plant(-0.13, -0.25), rf=plant(0.13, -0.1)))
    ez = {'leftUpperLeg': r(20, 0, -10), 'leftLowerLeg': r(-40), 'rightUpperLeg': r(20, 0, 70), 'rightLowerLeg': r(-10),
          'rightUpperArm': r(0, 0, 40), 'leftUpperArm': r(0, 0, -90), 'leftForearm': r(10)}
    keys.append(K(0.38, [0, 0.45, -0.35], -30, ez, body(hy=-0.1, roll=40, turn=-20)))
    keys.append(K(0.48, [0, 0.55, -0.4], -50, ez, body(hy=-0.1, roll=75, turn=-30), rfoot=air(0.05, 1.7, -0.95, flat=False)))     # foot to the back of the head
    keys.append(K(0.66, [0, 0.2, -0.4], -50, ez, body(hy=-0.4, roll=60, turn=-20)))
    SIT = {'hips': {'p': [0, -0.78, 0.1], 'r': [10, 0, 0]}, 'spine': r(-14), 'neck': r(12),
           'rightUpperLeg': r(80, 0, 8), 'rightLowerLeg': r(-30), 'leftUpperLeg': r(75, 0, -8), 'leftLowerLeg': r(-50),
           'rightUpperArm': r(-30, 0, -30), 'leftUpperArm': r(-30, 0, 30), 'rightForearm': r(10), 'leftForearm': r(10)}
    keys.append(K(0.84, [0, 0, -0.45], -30, SIT))
    keys.append(K(1.4, [0, 0, -0.45], -30, SIT, {'neck': r(4)}))
    clip(L, 'striking.enzuigiri', 'Enzuigiri', 1.4, keys,
         [ev(0.2, 'jump'), ev(0.3, 'attack_start'), hitev(0.48, 'head', attachment='rightFoot', reach=0.95, from_side='right'), ev(0.48, 'apex'),
          ev(0.84, 'land', zone='back'), ev(0.84, 'impact', surface='mat')],
         'Jump and swing the right leg up and over so the foot clips the back of the opponent\'s head, falling to a seated landing on the mat.',
         ['kick', 'aerial', 'high-flyer'], end_state='sitting', interrupt={'windows': [[0, 0.1]]},
         phases=[('launch', 0, 0.3), ('flight', 0.3, 0.84), ('landing', 0.84, 1.0), ('recovery', 1.0, 1.4)])
