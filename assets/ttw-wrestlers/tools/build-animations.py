"""Generate the shared TTW animation library (animations/<category>/<name>.json).

Poses are written as { bone: {"r": [x, y, z], "p": [x, y, z]} } in degrees and metres,
local to the bone and relative to the neutral pose. Bones left out of a pose sit at neutral.

Usage (from assets/ttw-wrestlers):  python tools/build-animations.py
"""
import json, copy, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'animations'

# ---------------------------------------------------------------- helpers

def swap(n):
    if n.startswith('left'): return 'right' + n[4:]
    if n.startswith('right'): return 'left' + n[5:]
    return n

def mirror(pose):
    """Left/right mirror: swap sides, keep X, negate Y and Z (positions: negate X)."""
    out = {}
    for bone, ch in pose.items():
        nb = swap(bone); out[nb] = {}
        if 'r' in ch: x, y, z = ch['r']; out[nb]['r'] = [x, -y, -z]
        if 'p' in ch: x, y, z = ch['p']; out[nb]['p'] = [-x, y, z]
    return out

def merge(*poses):
    out = {}
    for p in poses:
        for b, ch in p.items():
            out.setdefault(b, {}).update(copy.deepcopy(ch))
    return out

def r(x=0, y=0, z=0): return {'r': [x, y, z]}
def hp(p, rot=None):
    d = {'p': p}
    if rot: d['r'] = rot
    return {'hips': d}

LIBRARY = []

def clip(cid, name, category, duration, loop, keys, events=(), root=None, desc='', clamp=None, interp='smooth', tags=()):
    bones = sorted({b for _, p in keys for b in p})
    tracks = {}
    for b in bones:
        rot = [[t] + p.get(b, {}).get('r', [0, 0, 0]) for t, p in keys]
        tr = {}
        if any(any(abs(v) > 1e-9 for v in k[1:]) for k in rot): tr['rotation'] = rot
        if any('p' in p.get(b, {}) for _, p in keys):
            tr['position'] = [[t] + p.get(b, {}).get('p', [0, 0, 0]) for t, p in keys]
        if tr: tracks[b] = tr
    slug = cid.split('.', 1)[1]
    d = {
        'id': cid,
        'name': name,
        'category': category,
        'description': desc,
        'skeleton': 'ttw-humanoid',
        'skeletonVersion': 1,
        'duration': duration,
        'loop': loop,
        'clampWhenFinished': (not loop) if clamp is None else clamp,
        'interpolation': interp,
        'sampleRate': 30,
        'rotationUnits': 'degrees',
        'positionMode': 'offsetFromRest',
        'rootMotion': root or {'mode': 'none'},
        'events': [dict(e) for e in events],
        'tags': list(tags),
        'tracks': tracks,
    }
    path = OUT / category / f'{slug}.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    s = json.dumps(d, indent=2)
    s = re.sub(r'\[\s+(-?[\d.e-]+(?:,\s+-?[\d.e-]+)*)\s+\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', s)
    s = re.sub(r'\[\s+("[^"\n]*"(?:,\s+"[^"\n]*")*)\s+\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', s)
    path.write_text(s + '\n')
    LIBRARY.append({'id': cid, 'name': name, 'category': category, 'file': f'animations/{category}/{slug}.json',
                    'duration': duration, 'loop': loop, 'rootMotion': d['rootMotion']['mode'],
                    'events': [e['name'] for e in events], 'tags': list(tags)})

def ev(t, name, **kw):
    e = {'time': t, 'name': name}
    e.update(kw)
    return e

# ---------------------------------------------------------------- shared poses

STANCE = {
    'hips': {'p': [0, -0.02, 0]},
    'rightUpperLeg': r(6, 0, 4), 'leftUpperLeg': r(6, 0, -4),
    'rightLowerLeg': r(-12), 'leftLowerLeg': r(-12),
    'rightFoot': r(6, 0, -4), 'leftFoot': r(6, 0, 4),
    'rightUpperArm': r(6, 0, -10), 'leftUpperArm': r(6, 0, 10),
    'rightForearm': r(14), 'leftForearm': r(14),
}

GUARD = {
    'hips': {'p': [0, -0.03, 0]},
    'rightUpperLeg': r(8, 0, 4), 'leftUpperLeg': r(8, 0, -4),
    'rightLowerLeg': r(-16), 'leftLowerLeg': r(-16),
    'rightFoot': r(8, 0, -4), 'leftFoot': r(8, 0, 4),
    'spine': r(-4), 'neck': r(4),
    'rightUpperArm': r(50, 0, -22), 'rightForearm': r(118),
    'leftUpperArm': r(55, 0, 22), 'leftForearm': r(120),
}

def at(pose, **hips):
    """Copy a pose and move/rotate the hips: at(STANCE, p=[0,0,0.1])"""
    out = copy.deepcopy(pose)
    h = out.setdefault('hips', {})
    if 'p' in hips: h['p'] = hips['p']
    if 'r' in hips: h['r'] = hips['r']
    return out

# ---------------------------------------------------------------- movement

I0 = merge(STANCE, {'head': r(0, -3, 0)})
I1 = merge(STANCE, {
    'hips': {'p': [0.015, -0.025, 0], 'r': [0, 0, -1.5]},
    'spine': r(0, 0, 1.5), 'chest': r(2.5, 0, 0), 'neck': r(-1.5, 0, 0), 'head': r(0, 4, 0),
    'rightUpperArm': r(5, 0, -7), 'leftUpperArm': r(5, 0, 7),
    'rightUpperLeg': r(6, 0, 3), 'leftUpperLeg': r(6, 0, -5),
})
clip('movement.idle', 'Idle', 'movement', 2.4, True, [(0, I0), (1.2, I1), (2.4, I0)],
     desc='Relaxed stance with chest breathing and a slow weight shift.', tags=['idle', 'loop'])

WC = {
    'hips': {'p': [0, -0.035, 0], 'r': [0, 6, 0]},
    'spine': r(-3, -3, 0), 'chest': r(0, -6, 0), 'neck': r(0, 3, 0),
    'rightUpperLeg': r(26), 'rightLowerLeg': r(-6), 'rightFoot': r(8),
    'leftUpperLeg': r(-20), 'leftLowerLeg': r(-24), 'leftFoot': r(-14),
    'rightUpperArm': r(-20, 0, -10), 'rightForearm': r(12),
    'leftUpperArm': r(22, 0, 10), 'leftForearm': r(26),
}
WP = {
    'hips': {'p': [0, 0.012, 0]},
    'spine': r(-3),
    'rightUpperLeg': r(2), 'rightLowerLeg': r(-6), 'rightFoot': r(4),
    'leftUpperLeg': r(12), 'leftLowerLeg': r(-48), 'leftFoot': r(4),
    'rightUpperArm': r(0, 0, -10), 'rightForearm': r(16),
    'leftUpperArm': r(2, 0, 10), 'leftForearm': r(18),
}
clip('movement.walk', 'Walk', 'movement', 1.0, True, [(0, WC), (0.25, WP), (0.5, mirror(WC)), (0.75, mirror(WP)), (1.0, WC)],
     root={'mode': 'inPlace', 'speed': 1.5, 'direction': [0, 0, -1]},
     desc='Normal walk, in place. Move the wrestler at rootMotion.speed along its forward (-Z).', tags=['locomotion', 'loop'])

RC = {
    'hips': {'p': [0, -0.06, 0], 'r': [0, 9, 0]},
    'spine': r(-10, -4, 0), 'chest': r(-2, -9, 0), 'neck': r(8, 4, 0),
    'rightUpperLeg': r(34), 'rightLowerLeg': r(-18), 'rightFoot': r(10),
    'leftUpperLeg': r(-26), 'leftLowerLeg': r(-68), 'leftFoot': r(-22),
    'rightUpperArm': r(-34, 0, -8), 'rightForearm': r(80),
    'leftUpperArm': r(42, 0, 8), 'leftForearm': r(96),
}
RF = {
    'hips': {'p': [0, 0.03, 0]},
    'spine': r(-10), 'chest': r(-2), 'neck': r(8),
    'rightUpperLeg': r(-14), 'rightLowerLeg': r(-40), 'rightFoot': r(-12),
    'leftUpperLeg': r(40), 'leftLowerLeg': r(-105), 'leftFoot': r(0),
    'rightUpperArm': r(4, 0, -8), 'rightForearm': r(88),
    'leftUpperArm': r(4, 0, 8), 'leftForearm': r(88),
}
clip('movement.run', 'Run', 'movement', 0.64, True, [(0, RC), (0.16, RF), (0.32, mirror(RC)), (0.48, mirror(RF)), (0.64, RC)],
     root={'mode': 'inPlace', 'speed': 4.0, 'direction': [0, 0, -1]},
     desc='Run cycle, in place, forward lean and pumping arms.', tags=['locomotion', 'loop'])

# ---------------------------------------------------------------- striking

P_WIND = merge(GUARD, {
    'hips': {'p': [0, -0.03, 0.02], 'r': [0, -5, 0]},
    'spine': r(-4, -6, 0), 'chest': r(0, -14, 0), 'neck': r(4, 18, 0),
    'rightUpperArm': r(40, 0, -24), 'rightForearm': r(128),
})
P_HIT = merge(GUARD, {
    'hips': {'p': [0, -0.04, -0.05], 'r': [0, 7, 0]},
    'spine': r(-8, 8, 0), 'chest': r(-2, 16, 0), 'neck': r(6, -24, 0), 'head': r(0, -7, 0),
    'rightUpperArm': r(86, 0, -6), 'rightForearm': r(6), 'rightHand': r(0, 0, -6),
    'leftUpperArm': r(52, 0, 28), 'leftForearm': r(124),
    'rightUpperLeg': r(2, 0, 4), 'rightLowerLeg': r(-10), 'rightFoot': r(6, 0, -4),
    'leftUpperLeg': r(16, 0, -4), 'leftLowerLeg': r(-22), 'leftFoot': r(8, 0, 4),
})
P_HOLD = merge(P_HIT, {'rightForearm': r(12), 'chest': r(-2, 14, 0)})
clip('striking.punch', 'Punch', 'striking', 0.8, False, [(0, GUARD), (0.16, P_WIND), (0.3, P_HIT), (0.4, P_HOLD), (0.8, GUARD)],
     events=[ev(0.3, 'hit', attachment='rightHandGrip', zone='head', reach=0.75)],
     desc='Right straight punch from guard with hip and chest rotation. Ends in guard.', tags=['strike', 'right'])

K_CHAMBER = merge(GUARD, {
    'hips': {'p': [0, -0.03, 0.02], 'r': [6, 0, 0]},
    'spine': r(4), 'chest': r(2), 'neck': r(-6),
    'rightUpperLeg': r(84, 0, 2), 'rightLowerLeg': r(-108), 'rightFoot': r(14),
    'leftUpperLeg': r(-4, 0, -4), 'leftLowerLeg': r(-14), 'leftFoot': r(4, 0, 4),
    'leftUpperArm': r(40, 0, 30), 'leftForearm': r(110),
})
K_EXT = merge(GUARD, {
    'hips': {'p': [0, -0.02, 0.06], 'r': [14, 0, 0]},
    'spine': r(8), 'chest': r(4), 'neck': r(-14), 'head': r(-4),
    'rightUpperLeg': r(80, 0, 2), 'rightLowerLeg': r(-6), 'rightFoot': r(22),
    'leftUpperLeg': r(-14, 0, -4), 'leftLowerLeg': r(-8), 'leftFoot': r(2, 0, 4),
    'rightUpperArm': r(30, 0, -34), 'rightForearm': r(100),
    'leftUpperArm': r(20, 0, 40), 'leftForearm': r(80),
})
K_HOLD = merge(K_EXT, {'rightLowerLeg': r(-16), 'rightUpperLeg': r(78, 0, 2)})
clip('striking.kick', 'Kick', 'striking', 0.9, False,
     [(0, GUARD), (0.2, K_CHAMBER), (0.34, K_EXT), (0.44, K_HOLD), (0.62, K_CHAMBER), (0.9, GUARD)],
     events=[ev(0.34, 'hit', bone='rightFoot', zone='body', reach=1.0)],
     desc='Right front kick: chamber the knee, snap the foot out, re-chamber and land back in guard.', tags=['strike', 'right', 'kick'])

# ---------------------------------------------------------------- reactions

HF1 = merge(STANCE, {
    'hips': {'p': [0, -0.04, 0.06], 'r': [5, 0, 0]},
    'spine': r(8), 'chest': r(10), 'neck': r(26), 'head': r(12, 0, 4),
    'rightUpperArm': r(24, 0, 34), 'rightForearm': r(40),
    'leftUpperArm': r(24, 0, -34), 'leftForearm': r(40),
    'rightUpperLeg': r(8, 0, 4), 'leftUpperLeg': r(8, 0, -4),
    'rightLowerLeg': r(-18), 'leftLowerLeg': r(-18),
})
HF2 = merge(STANCE, {
    'hips': {'p': [0, -0.06, 0.13], 'r': [2, 0, 0]},
    'spine': r(2), 'chest': r(2), 'neck': r(8), 'head': r(2),
    'rightUpperArm': r(16, 0, 20), 'rightForearm': r(36),
    'leftUpperArm': r(16, 0, -20), 'leftForearm': r(36),
    'rightUpperLeg': r(-16, 0, 4), 'rightLowerLeg': r(-26), 'rightFoot': r(10, 0, -4),
    'leftUpperLeg': r(20, 0, -4), 'leftLowerLeg': r(-18), 'leftFoot': r(6, 0, 4),
})
HF3 = at(STANCE, p=[0, -0.02, 0.12])
clip('reactions.hit-front', 'Hit reaction, front', 'reactions', 0.75, False, [(0, STANCE), (0.08, HF1), (0.3, HF2), (0.75, HF3)],
     events=[ev(0.0, 'hit_received', zone='head'), ev(0.6, 'recover')],
     root={'mode': 'baked', 'commit': 'hipsXZ', 'endOffset': [0, 0, 0.12]},
     desc='Snapped back by a hit to the front, one step back, recover to stance.', tags=['reaction', 'front'])

HB1 = merge(STANCE, {
    'hips': {'p': [0, -0.04, -0.07], 'r': [-6, 0, 0]},
    'spine': r(-14), 'chest': r(-10), 'neck': r(18), 'head': r(8),
    'rightUpperArm': r(-34, 0, 26), 'rightForearm': r(24),
    'leftUpperArm': r(-34, 0, -26), 'leftForearm': r(24),
    'rightUpperLeg': r(-6, 0, 4), 'leftUpperLeg': r(-6, 0, -4),
})
HB2 = merge(STANCE, {
    'hips': {'p': [0, -0.07, -0.14], 'r': [-4, 0, 0]},
    'spine': r(-10), 'chest': r(-6), 'neck': r(6),
    'rightUpperArm': r(-10, 0, 16), 'rightForearm': r(30),
    'leftUpperArm': r(30, 0, -16), 'leftForearm': r(40),
    'leftUpperLeg': r(34, 0, -4), 'leftLowerLeg': r(-30), 'leftFoot': r(-2, 0, 4),
    'rightUpperLeg': r(-12, 0, 4), 'rightLowerLeg': r(-20), 'rightFoot': r(12, 0, -4),
})
HB3 = at(STANCE, p=[0, -0.02, -0.12])
clip('reactions.hit-back', 'Hit reaction, back', 'reactions', 0.75, False, [(0, STANCE), (0.08, HB1), (0.3, HB2), (0.75, HB3)],
     events=[ev(0.0, 'hit_received', zone='back'), ev(0.6, 'recover')],
     root={'mode': 'baked', 'commit': 'hipsXZ', 'endOffset': [0, 0, -0.12]},
     desc='Shoved forward by a hit from behind, head whips back, stumble step forward, recover.', tags=['reaction', 'back'])

# ---------------------------------------------------------------- falls

F1 = {
    'hips': {'p': [0, -0.03, 0.06], 'r': [6, 0, 0]},
    'spine': r(6), 'chest': r(8), 'neck': r(10), 'head': r(6),
    'rightUpperArm': r(35, 0, 25), 'rightForearm': r(40),
    'leftUpperArm': r(35, 0, -25), 'leftForearm': r(40),
    'rightUpperLeg': r(10, 0, 4), 'leftUpperLeg': r(10, 0, -4),
    'rightLowerLeg': r(-20), 'leftLowerLeg': r(-20), 'rightFoot': r(10), 'leftFoot': r(10),
}
F2 = {
    'hips': {'p': [0, -0.40, 0.32], 'r': [42, 0, 0]},
    'spine': r(4), 'neck': r(-18), 'head': r(-8),
    'rightUpperArm': r(30, 0, 55), 'rightForearm': r(30),
    'leftUpperArm': r(30, 0, -55), 'leftForearm': r(30),
    'rightUpperLeg': r(28, 0, 6), 'leftUpperLeg': r(28, 0, -6),
    'rightLowerLeg': r(-45), 'leftLowerLeg': r(-45), 'rightFoot': r(10), 'leftFoot': r(10),
}
F3 = {
    'hips': {'p': [0, -0.83, 0.62], 'r': [92, 0, 0]},
    'neck': r(-26), 'head': r(-6),
    'rightUpperArm': r(0, -10, 72), 'rightForearm': r(10),
    'leftUpperArm': r(0, 10, -72), 'leftForearm': r(10),
    'rightUpperLeg': r(30, 0, 6), 'leftUpperLeg': r(30, 0, -6),
    'rightLowerLeg': r(-14), 'leftLowerLeg': r(-14), 'rightFoot': r(-10), 'leftFoot': r(-10),
}
F4 = merge(F3, {
    'hips': {'p': [0, -0.79, 0.62], 'r': [86, 0, 0]},
    'neck': r(-18),
    'rightUpperLeg': r(24, 0, 6), 'leftUpperLeg': r(24, 0, -6),
    'rightLowerLeg': r(-22), 'leftLowerLeg': r(-22),
    'rightForearm': r(16), 'leftForearm': r(16),
})
F5 = {
    'hips': {'p': [0, -0.83, 0.62], 'r': [90, 0, 0]},
    'neck': r(-8),
    'rightUpperArm': r(0, -10, 62), 'rightForearm': r(18),
    'leftUpperArm': r(0, 10, -62), 'leftForearm': r(18),
    'rightUpperLeg': r(6, 0, 7), 'leftUpperLeg': r(6, 0, -7),
    'rightLowerLeg': r(-14), 'leftLowerLeg': r(-14), 'rightFoot': r(-18), 'leftFoot': r(-18),
}
LIE_BACK = {
    'hips': {'p': [0, -0.83, 0], 'r': [90, 0, 0]},
    'neck': r(6), 'head': r(0, 14, 0),
    'rightUpperArm': r(0, -10, 56), 'rightForearm': r(16),
    'leftUpperArm': r(0, 10, -56), 'leftForearm': r(16),
    'rightUpperLeg': r(0, 0, 8), 'leftUpperLeg': r(0, 0, -8),
    'rightLowerLeg': r(-8), 'leftLowerLeg': r(-8), 'rightFoot': r(-20, 0, -6), 'leftFoot': r(-20, 0, 6),
}
F6 = at(LIE_BACK, p=[0, -0.83, 0.62])
clip('falls.fall-backward', 'Fall backwards', 'falls', 1.8, False,
     [(0, STANCE), (0.18, F1), (0.45, F2), (0.7, F3), (0.82, F4), (1.05, F5), (1.8, F6)],
     events=[ev(0.7, 'land', zone='back')],
     root={'mode': 'baked', 'commit': 'hipsXZ', 'endOffset': [0, 0, 0.62]},
     desc='Backward fall and back bump onto the mat. Holds flat on the back. Pairs with falls.getup-back.', tags=['fall', 'back', 'ends-lying-back'])

# Get up from back. Starts from LIE_BACK with the fall's offset already committed (hips over the object origin).
G1 = {  # sit up, knees up, hands behind
    'hips': {'p': [0, -0.83, 0], 'r': [25, 0, 0]},
    'spine': r(-10), 'chest': r(-6), 'neck': r(-6),
    'rightUpperLeg': r(20, 0, 6), 'leftUpperLeg': r(20, 0, -6),
    'rightLowerLeg': r(-60), 'leftLowerLeg': r(-60),
    'rightFoot': r(18), 'leftFoot': r(18),
    'rightUpperArm': r(-40, 0, 18), 'rightForearm': r(10),
    'leftUpperArm': r(-40, 0, -18), 'leftForearm': r(10),
}
G2 = {  # rock forward into a squat over the feet
    'hips': {'p': [0, -0.55, -0.1], 'r': [-35, 0, 0]},
    'spine': r(-12), 'chest': r(-6), 'neck': r(30), 'head': r(6),
    'rightUpperLeg': r(111, 0, 8), 'leftUpperLeg': r(111, 0, -8),
    'rightLowerLeg': r(-126), 'leftLowerLeg': r(-126),
    'rightFoot': r(50), 'leftFoot': r(50),
    'rightUpperArm': r(50, 0, -6), 'rightForearm': r(40),
    'leftUpperArm': r(50, 0, 6), 'leftForearm': r(40),
}
G3 = {  # rising
    'hips': {'p': [0, -0.2, -0.17], 'r': [-18, 0, 0]},
    'spine': r(-8), 'neck': r(16),
    'rightUpperLeg': r(52, 0, 6), 'leftUpperLeg': r(52, 0, -6),
    'rightLowerLeg': r(-64), 'leftLowerLeg': r(-64),
    'rightFoot': r(30), 'leftFoot': r(30),
    'rightUpperArm': r(30, 0, -10), 'rightForearm': r(40),
    'leftUpperArm': r(30, 0, 10), 'leftForearm': r(40),
}
G4 = at(STANCE, p=[0, -0.02, -0.19])
clip('falls.getup-back', 'Get up from back', 'falls', 2.0, False,
     [(0, LIE_BACK), (0.55, G1), (1.1, G2), (1.55, G3), (2.0, G4)],
     events=[ev(1.55, 'recover')],
     root={'mode': 'baked', 'commit': 'hipsXZ', 'endOffset': [0, 0, -0.19], 'startPose': 'lying-back'},
     desc='Sit up, rock forward onto the feet and stand. Starts where falls.fall-backward ends.', tags=['getup', 'starts-lying-back'])

# ---------------------------------------------------------------- ropes
# Rope convention: the ropes are BEHIND the wrestler (+Z), top rope about 1.25 m above the mat,
# about 0.4 m behind the feet. The game turns the wrestler to face away from the ropes first.

LEAN = {
    'hips': {'p': [0, -0.03, 0.15], 'r': [14, 0, 0]},
    'spine': r(2), 'chest': r(4), 'neck': r(-10), 'head': r(-4),
    'rightUpperLeg': r(-6, 0, 5), 'leftUpperLeg': r(-6, 0, -5),
    'rightLowerLeg': r(-6), 'leftLowerLeg': r(-6),
    'rightFoot': r(-2, 0, -4), 'leftFoot': r(-2, 0, 4),
    # arms out and back so the elbows hook over the top rope, forearms hanging behind it
    'rightUpperArm': r(0, -35, 28), 'rightForearm': r(0, 0, -55),
    'leftUpperArm': r(0, 35, -28), 'leftForearm': r(0, 0, 55),
}
LEAN_IN = merge(STANCE, {
    'hips': {'p': [0, -0.03, 0.08], 'r': [6, 0, 0]},
    'neck': r(-4),
    'rightUpperArm': r(0, -15, 20), 'rightForearm': r(10, 0, -15),
    'leftUpperArm': r(0, 15, -20), 'leftForearm': r(10, 0, 15),
})
clip('ropes.rope-lean', 'Rope lean', 'ropes', 0.7, False, [(0, STANCE), (0.22, LEAN_IN), (0.45, LEAN), (0.7, LEAN)],
     events=[ev(0.3, 'rope_contact', attachment='back')],
     desc='Back up into the ropes and rest the elbows over the top rope. Holds the lean. Ropes are behind the wrestler (+Z).',
     tags=['ropes', 'hold', 'ends-rope-lean'])

STRETCH = {
    'hips': {'p': [0, -0.06, 0.3], 'r': [24, 0, 0]},
    'spine': r(4), 'chest': r(6), 'neck': r(-18), 'head': r(-6),
    'rightUpperLeg': r(-2, 0, 5), 'leftUpperLeg': r(-2, 0, -5),
    'rightLowerLeg': r(-14), 'leftLowerLeg': r(-14),
    'rightFoot': r(-6, 0, -4), 'leftFoot': r(-6, 0, 4),
    'rightUpperArm': r(0, -45, 34), 'rightForearm': r(0, 0, -62),
    'leftUpperArm': r(0, 45, -34), 'leftForearm': r(0, 0, 62),
}
LAUNCH = {
    'hips': {'p': [0, -0.08, 0.04], 'r': [-14, 0, 0]},
    'spine': r(-12), 'chest': r(-6), 'neck': r(14),
    'rightUpperLeg': r(-22), 'rightLowerLeg': r(-20), 'rightFoot': r(-14),
    'leftUpperLeg': r(46), 'leftLowerLeg': r(-70), 'leftFoot': r(0),
    'rightUpperArm': r(50, 0, -8), 'rightForearm': r(90),
    'leftUpperArm': r(-30, 0, 8), 'leftForearm': r(80),
}
clip('ropes.rope-rebound', 'Rope rebound', 'ropes', 0.8, False,
     [(0, LEAN), (0.2, STRETCH), (0.36, LAUNCH), (0.56, RF), (0.8, RC)],
     events=[ev(0.0, 'rope_contact', attachment='back'), ev(0.32, 'rebound'), ev(0.8, 'release', next='movement.run')],
     root={'mode': 'speedCurve', 'direction': [0, 0, -1], 'speedCurve': [[0, 0], [0.3, 0], [0.42, 3.2], [0.8, 4.0]]},
     desc='From the rope lean: sink into the ropes, spring off and come out running. Ends on the run cycle contact pose, so chain into movement.run.',
     tags=['ropes', 'starts-rope-lean', 'chains-to-run'])

# ---------------------------------------------------------------- write index

(ROOT / 'tools' / 'animation-index.json').write_text(json.dumps(LIBRARY, indent=2) + '\n')
for a in LIBRARY:
    print(f"{a['id']:28} {a['duration']:>5}s  loop={a['loop']!s:5}  root={a['rootMotion']:10}  events={a['events']}")
