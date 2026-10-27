"""Batch 2 animations: movement, striking, damage reactions, falls and recovery (47 clips).

Same file format and conventions as Batch 1 (tools/build-animations.py, which is not imported because
it writes the Batch 1 files when run). Shared poses are copied from Batch 1 verbatim so chained clips
line up exactly with the Batch 1 clips.

Extra root-motion field used here: rootMotion.endRotationY (degrees). The wrestler ends the clip facing
a different way (turn-180, rolls, sideways falls). loader-ext.js applies it; see README-batch2.md.

Usage (from assets/ttw-wrestlers):  python tools/batch2/build-animations-b2.py
"""
import json, copy, math, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'animations'
INDEX = []

# ---------------------------------------------------------------- helpers (same behaviour as batch 1)

def swap(n):
    if n.startswith('left'): return 'right' + n[4:]
    if n.startswith('right'): return 'left' + n[5:]
    return n

def mirror(pose):
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
def hips(p=None, rot=None):
    d = {}
    if p is not None: d['p'] = p
    if rot is not None: d['r'] = rot
    return {'hips': d}

def at(pose, p=None, rot=None):
    out = copy.deepcopy(pose)
    h = out.setdefault('hips', {})
    if p is not None: h['p'] = p
    if rot is not None: h['r'] = rot
    return out

def only(pose, bones):
    return {b: copy.deepcopy(v) for b, v in pose.items() if b in bones}

LEGS = {'hips', 'leftUpperLeg', 'leftLowerLeg', 'leftFoot', 'rightUpperLeg', 'rightLowerLeg', 'rightFoot'}
ARMS = {'leftUpperArm', 'leftForearm', 'leftHand', 'rightUpperArm', 'rightForearm', 'rightHand'}

def ev(t, name, **kw):
    e = {'time': t, 'name': name}; e.update(kw); return e

def dump(d):
    s = json.dumps(d, indent=2)
    s = re.sub(r'\[\s+(-?[\d.e-]+(?:,\s+-?[\d.e-]+)*)\s+\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', s)
    s = re.sub(r'\[\s+("[^"\n]*"(?:,\s+"[^"\n]*")*)\s+\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', s)
    return s + '\n'

def rnd(v): return round(v, 3) if isinstance(v, float) else v

def clip(cid, name, category, duration, loop, keys, events=(), root=None, desc='', tags=(), interp='smooth'):
    bones = sorted({b for _, p in keys for b in p})
    tracks = {}
    for b in bones:
        rot = [[t] + [rnd(v) for v in p.get(b, {}).get('r', [0, 0, 0])] for t, p in keys]
        tr = {}
        if any(any(abs(v) > 1e-9 for v in k[1:]) for k in rot): tr['rotation'] = rot
        if any('p' in p.get(b, {}) for _, p in keys):
            tr['position'] = [[t] + [rnd(v) for v in p.get(b, {}).get('p', [0, 0, 0])] for t, p in keys]
        if tr: tracks[b] = tr
    slug = cid.split('.', 1)[1]
    path = OUT / category / f'{slug}.json'
    rel = f'animations/{category}/{slug}.json'
    b1 = ROOT / 'tools' / 'animation-index.json'
    if path.exists() and any(a['file'] == rel for a in json.loads(b1.read_text())):
        raise SystemExit(f'refusing to overwrite batch 1 file {rel}')
    d = {
        'id': cid, 'name': name, 'category': category, 'description': desc,
        'skeleton': 'ttw-humanoid', 'skeletonVersion': 1,
        'duration': duration, 'loop': loop, 'clampWhenFinished': not loop,
        'interpolation': interp, 'sampleRate': 30, 'rotationUnits': 'degrees', 'positionMode': 'offsetFromRest',
        'rootMotion': root or {'mode': 'none'},
        'events': [dict(e) for e in events], 'tags': list(tags), 'batch': 2,
        'tracks': tracks,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump(d))
    INDEX.append({'id': cid, 'name': name, 'category': category, 'file': rel, 'duration': duration, 'loop': loop,
                  'rootMotion': d['rootMotion']['mode'], 'events': [e['name'] for e in events], 'tags': list(tags), 'batch': 2})

def baked(end, rotY=None, **kw):
    d = {'mode': 'baked', 'commit': 'hipsXZ', 'endOffset': end}
    if rotY is not None: d['endRotationY'] = rotY
    d.update(kw)
    return d

def mirror_events(events):
    def sw(s): return re.sub(r'left|right|Left|Right', lambda m: {'left': 'right', 'right': 'left', 'Left': 'Right', 'Right': 'Left'}[m.group(0)], s, count=1)
    out = []
    for e in events:
        c = dict(e)
        for k in ('attachment', 'bone'):
            if k in c: c[k] = sw(c[k])
        out.append(c)
    return out

def mirror_keys(keys): return [(t, mirror(p)) for t, p in keys]

# ---------------------------------------------------------------- batch 1 poses (copied verbatim)

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
LIE_BACK = {
    'hips': {'p': [0, -0.83, 0], 'r': [90, 0, 0]},
    'neck': r(6), 'head': r(0, 14, 0),
    'rightUpperArm': r(0, -10, 56), 'rightForearm': r(16),
    'leftUpperArm': r(0, 10, -56), 'leftForearm': r(16),
    'rightUpperLeg': r(0, 0, 8), 'leftUpperLeg': r(0, 0, -8),
    'rightLowerLeg': r(-8), 'leftLowerLeg': r(-8), 'rightFoot': r(-20, 0, -6), 'leftFoot': r(-20, 0, 6),
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
G1 = {
    'hips': {'p': [0, -0.83, 0], 'r': [25, 0, 0]},
    'spine': r(-10), 'chest': r(-6), 'neck': r(-6),
    'rightUpperLeg': r(20, 0, 6), 'leftUpperLeg': r(20, 0, -6),
    'rightLowerLeg': r(-60), 'leftLowerLeg': r(-60),
    'rightFoot': r(18), 'leftFoot': r(18),
    'rightUpperArm': r(-40, 0, 18), 'rightForearm': r(10),
    'leftUpperArm': r(-40, 0, -18), 'leftForearm': r(10),
}
G2 = {
    'hips': {'p': [0, -0.55, -0.1], 'r': [-35, 0, 0]},
    'spine': r(-12), 'chest': r(-6), 'neck': r(30), 'head': r(6),
    'rightUpperLeg': r(111, 0, 8), 'leftUpperLeg': r(111, 0, -8),
    'rightLowerLeg': r(-126), 'leftLowerLeg': r(-126),
    'rightFoot': r(50), 'leftFoot': r(50),
    'rightUpperArm': r(50, 0, -6), 'rightForearm': r(40),
    'leftUpperArm': r(50, 0, 6), 'leftForearm': r(40),
}
G3 = {
    'hips': {'p': [0, -0.2, -0.17], 'r': [-18, 0, 0]},
    'spine': r(-8), 'neck': r(16),
    'rightUpperLeg': r(52, 0, 6), 'leftUpperLeg': r(52, 0, -6),
    'rightLowerLeg': r(-64), 'leftLowerLeg': r(-64),
    'rightFoot': r(30), 'leftFoot': r(30),
    'rightUpperArm': r(30, 0, -10), 'rightForearm': r(40),
    'leftUpperArm': r(30, 0, 10), 'leftForearm': r(40),
}

# ---------------------------------------------------------------- new shared poses

LIE_FRONT = {
    'hips': {'p': [0, -0.84, 0], 'r': [-90, 0, 0]},
    'neck': r(10, 40, 0), 'head': r(0, 20, 0),
    'rightUpperArm': r(0, 0, 80), 'rightForearm': r(0, 0, 70),
    'leftUpperArm': r(0, 0, -80), 'leftForearm': r(0, 0, -70),
    'rightUpperLeg': r(0, 0, 6), 'leftUpperLeg': r(0, 0, -6),
    'rightLowerLeg': r(-6), 'leftLowerLeg': r(-6),
    'rightFoot': r(-50), 'leftFoot': r(-50),
}
CLUTCH = {  # arms wrapped over the stomach
    'rightUpperArm': r(30, 0, -14), 'rightForearm': r(105),
    'leftUpperArm': r(30, 0, 14), 'leftForearm': r(105),
}
LIMP_ARMS = {
    'rightUpperArm': r(4, 0, -6), 'rightForearm': r(8),
    'leftUpperArm': r(4, 0, 6), 'leftForearm': r(8),
}
BENT = {  # knees bent, weight down
    'rightUpperLeg': r(16, 0, 4), 'leftUpperLeg': r(16, 0, -4),
    'rightLowerLeg': r(-32), 'leftLowerLeg': r(-32),
    'rightFoot': r(16, 0, -4), 'leftFoot': r(16, 0, 4),
}

# ================================================================ MOVEMENT

# Fighting stance idle: guard with a light bounce
IF0 = at(GUARD, p=[0, -0.03, 0])
IF1 = merge(GUARD, {
    'hips': {'p': [0, -0.065, 0], 'r': [0, 3, 0]},
    'rightUpperLeg': r(13, 0, 4), 'leftUpperLeg': r(13, 0, -4),
    'rightLowerLeg': r(-26), 'leftLowerLeg': r(-26),
    'rightFoot': r(13, 0, -4), 'leftFoot': r(13, 0, 4),
    'chest': r(0, 4, 0), 'rightUpperArm': r(46, 0, -22), 'leftUpperArm': r(58, 0, 22),
})
clip('movement.idle-fight', 'Idle, fighting stance', 'movement', 1.0, True, [(0, IF0), (0.5, IF1), (1.0, IF0)],
     desc='Guard up with a light bounce on the knees.', tags=['idle', 'loop', 'guard'])

# Cocky walk: swagger, shoulders rolling, chin up, arms wide
def cocky(p, side=1):
    return merge(p, {
        'hips': {'p': p['hips'].get('p', [0, 0, 0]), 'r': [0, p['hips'].get('r', [0, 0, 0])[1] * 1.6, 4 * side]},
        'chest': r(0, -14 * side, 0), 'spine': r(2, -4 * side, -3 * side), 'neck': r(8, 10 * side, 0),
    })
CC = cocky(WC); CC['rightUpperArm'] = r(-28, 0, 10); CC['leftUpperArm'] = r(30, 0, -14); CC['rightForearm'] = r(20); CC['leftForearm'] = r(30)
CP = merge(WP, {'hips': {'p': [0, 0.02, 0]}, 'neck': r(8), 'spine': r(2),
                'rightUpperArm': r(0, 0, 14), 'leftUpperArm': r(0, 0, -14), 'rightForearm': r(18), 'leftForearm': r(18)})
clip('movement.walk-cocky', 'Walk, cocky', 'movement', 1.2, True, [(0, CC), (0.3, CP), (0.6, mirror(CC)), (0.9, mirror(CP)), (1.2, CC)],
     root={'mode': 'inPlace', 'speed': 1.2, 'direction': [0, 0, -1]},
     desc='Swaggering walk with rolling shoulders, chin up and arms held wide.', tags=['locomotion', 'loop'])

# Injured walk: limping on the right leg, right arm holding the ribs, hunched
HUNCH = {'spine': r(-14, 0, 4), 'chest': r(-6), 'neck': r(12),
         'rightUpperArm': r(22, 0, -30), 'rightForearm': r(112), 'rightHand': r(0, 0, -10)}
IL = merge(mirror(WC), {'leftUpperLeg': r(30), 'hips': {'p': [0, -0.03, 0], 'r': [0, -4, -2]}}, HUNCH, {'leftUpperArm': r(-10, 0, 12), 'leftForearm': r(20)})
IPL = merge(mirror(WP), {'hips': {'p': [0, 0.0, 0], 'r': [0, 0, -3]}}, HUNCH, {'leftUpperArm': r(4, 0, 12), 'leftForearm': r(22)})
IR = merge(WC, {'rightUpperLeg': r(16), 'rightLowerLeg': r(-10), 'hips': {'p': [0, -0.07, 0], 'r': [0, 3, 5]}}, HUNCH,
           {'leftUpperArm': r(16, 0, 14), 'leftForearm': r(26), 'neck': r(18, 0, 0)})
IPR = merge(WP, {'hips': {'p': [0, -0.06, 0], 'r': [0, 0, 5]}}, HUNCH, {'leftUpperArm': r(8, 0, 14), 'leftForearm': r(22)})
clip('movement.walk-injured', 'Walk, injured', 'movement', 1.6, True, [(0, IL), (0.45, IPL), (0.8, IR), (1.05, IPR), (1.6, IL)],
     root={'mode': 'inPlace', 'speed': 0.8, 'direction': [0, 0, -1]},
     desc='Limping walk favouring the right leg, hunched, right hand holding the ribs.', tags=['locomotion', 'loop', 'injured'])

# Sprint: stronger lean, bigger stride and arm drive
SC = merge(RC, {'hips': {'p': [0, -0.07, 0], 'r': [0, 10, 0]}, 'spine': r(-18, -4, 0), 'chest': r(-4, -10, 0), 'neck': r(16, 4, 0),
                'rightUpperLeg': r(48), 'rightLowerLeg': r(-26), 'leftUpperLeg': r(-34), 'leftLowerLeg': r(-92), 'leftFoot': r(-26),
                'rightUpperArm': r(-52, 0, -8), 'rightForearm': r(86), 'leftUpperArm': r(62, 0, 8), 'leftForearm': r(100)})
SF = merge(RF, {'hips': {'p': [0, 0.035, 0]}, 'spine': r(-18), 'chest': r(-4), 'neck': r(16),
                'rightUpperLeg': r(-20), 'rightLowerLeg': r(-56), 'leftUpperLeg': r(56), 'leftLowerLeg': r(-122)})
clip('movement.sprint', 'Sprint', 'movement', 0.5, True, [(0, SC), (0.125, SF), (0.25, mirror(SC)), (0.375, mirror(SF)), (0.5, SC)],
     root={'mode': 'inPlace', 'speed': 6.5, 'direction': [0, 0, -1]},
     desc='Flat-out sprint, deep lean and long stride.', tags=['locomotion', 'loop'])

# Backpedal: the walk legs played in reverse, guard up
def bp(p): return merge(only(p, LEGS), only(GUARD, ARMS), {'spine': r(-6), 'neck': r(6)})
clip('movement.backpedal', 'Backpedal', 'movement', 1.0, True,
     [(0, bp(WC)), (0.25, bp(mirror(WP))), (0.5, bp(mirror(WC))), (0.75, bp(WP)), (1.0, bp(WC))],
     root={'mode': 'inPlace', 'speed': 1.2, 'direction': [0, 0, 1]},
     desc='Walking backwards with the guard up. Move the wrestler along +Z (backwards).', tags=['locomotion', 'loop', 'guard'])

# Sidestep left, guard up
SS0 = GUARD
SS1 = merge(GUARD, {'hips': {'p': [-0.04, -0.03, 0]}, 'leftUpperLeg': r(10, 0, -20), 'leftLowerLeg': r(-22), 'leftFoot': r(10, 0, 18),
                    'rightUpperLeg': r(8, 0, 8), 'rightFoot': r(8, 0, -8)})
SS2 = merge(GUARD, {'hips': {'p': [-0.08, -0.06, 0]}, 'leftUpperLeg': r(10, 0, -13), 'rightUpperLeg': r(10, 0, 13),
                    'leftLowerLeg': r(-22), 'rightLowerLeg': r(-22), 'leftFoot': r(10, 0, 13), 'rightFoot': r(10, 0, -13)})
SS3 = merge(GUARD, {'hips': {'p': [-0.04, -0.03, 0]}, 'rightUpperLeg': r(16, 0, -6), 'rightLowerLeg': r(-34), 'rightFoot': r(16, 0, 6),
                    'leftUpperLeg': r(8, 0, -8), 'leftFoot': r(8, 0, 8)})
SSL = [(0, SS0), (0.2, SS1), (0.4, SS2), (0.6, SS3), (0.8, SS0)]
clip('movement.sidestep-left', 'Sidestep left', 'movement', 0.8, True, SSL,
     root={'mode': 'inPlace', 'speed': 1.0, 'direction': [-1, 0, 0]},
     desc='Shuffle step to the left with the guard up. Move the wrestler along -X.', tags=['locomotion', 'loop', 'guard'])
clip('movement.sidestep-right', 'Sidestep right', 'movement', 0.8, True, mirror_keys(SSL),
     root={'mode': 'inPlace', 'speed': 1.0, 'direction': [1, 0, 0]},
     desc='Shuffle step to the right with the guard up. Move the wrestler along +X.', tags=['locomotion', 'loop', 'guard'])

# Turn 180 to the left, stepping round
T1 = merge(STANCE, {'hips': {'p': [0, -0.04, 0], 'r': [0, 55, 0]}, 'chest': r(0, 15, 0), 'neck': r(0, 20, 0),
                    'rightUpperLeg': r(6, -55, 4), 'leftUpperLeg': r(30, -10, -4), 'leftLowerLeg': r(-46), 'leftFoot': r(10)})
T2 = merge(STANCE, {'hips': {'p': [0, -0.04, 0], 'r': [0, 125, 0]}, 'chest': r(0, 12, 0), 'neck': r(0, 12, 0),
                    'leftUpperLeg': r(6, -30, -4), 'rightUpperLeg': r(30, -40, 4), 'rightLowerLeg': r(-46), 'rightFoot': r(10)})
T3 = at(STANCE, p=[0, -0.02, 0], rot=[0, 180, 0])
clip('movement.turn-180', 'Turn around', 'movement', 0.7, False, [(0, STANCE), (0.22, T1), (0.46, T2), (0.7, T3)],
     events=[ev(0.6, 'recover')],
     root=baked([0, 0, 0], 180),
     desc='Step round to face the opposite way. Ends facing backwards; the wrestler is turned 180 degrees when the next clip starts (loader-ext.js).',
     tags=['turn'])

# Stumble forward
SF1 = merge(STANCE, {'hips': {'p': [0, -0.06, -0.12], 'r': [-14, 0, 0]}, 'spine': r(-14), 'neck': r(14),
                     'rightUpperArm': r(60, 0, 30), 'leftUpperArm': r(60, 0, -30), 'rightForearm': r(30), 'leftForearm': r(30),
                     'rightUpperLeg': r(30), 'rightLowerLeg': r(-24), 'leftUpperLeg': r(-6), 'leftLowerLeg': r(-12)})
SF2 = merge(STANCE, {'hips': {'p': [0, -0.12, -0.35], 'r': [-20, 0, 0]}, 'spine': r(-10), 'neck': r(18),
                     'rightUpperArm': r(40, 0, 60), 'leftUpperArm': r(40, 0, -60), 'rightForearm': r(20), 'leftForearm': r(20),
                     'leftUpperLeg': r(40), 'leftLowerLeg': r(-34), 'leftFoot': r(14), 'rightUpperLeg': r(-6), 'rightLowerLeg': r(-36)})
SF3 = merge(STANCE, {'hips': {'p': [0, -0.07, -0.5], 'r': [-8, 0, 0]}, 'spine': r(-6), 'neck': r(8),
                     'rightUpperArm': r(20, 0, 30), 'leftUpperArm': r(20, 0, -30),
                     'rightUpperLeg': r(26), 'rightLowerLeg': r(-26), 'leftUpperLeg': r(-6), 'leftLowerLeg': r(-14)})
clip('movement.stumble-forward', 'Stumble forward', 'movement', 0.95, False,
     [(0, STANCE), (0.12, SF1), (0.36, SF2), (0.6, SF3), (0.95, at(STANCE, p=[0, -0.02, -0.5]))],
     events=[ev(0.8, 'recover')], root=baked([0, 0, -0.5]),
     desc='Lurch forward two steps with arms out, catch balance.', tags=['stumble'])

SB1 = merge(STANCE, {'hips': {'p': [0, -0.05, 0.12], 'r': [12, 0, 0]}, 'spine': r(8), 'neck': r(-4),
                     'rightUpperArm': r(70, 0, 30), 'leftUpperArm': r(70, 0, -30), 'rightForearm': r(20), 'leftForearm': r(20),
                     'rightUpperLeg': r(-16), 'rightLowerLeg': r(-26)})
SB2 = merge(STANCE, {'hips': {'p': [0, -0.1, 0.32], 'r': [8, 0, 0]}, 'spine': r(-4), 'neck': r(4),
                     'rightUpperArm': r(110, 0, 40), 'leftUpperArm': r(30, 0, -50), 'rightForearm': r(30), 'leftForearm': r(20),
                     'leftUpperLeg': r(-22), 'leftLowerLeg': r(-30), 'rightUpperLeg': r(14), 'rightLowerLeg': r(-20)})
SB3 = merge(STANCE, {'hips': {'p': [0, -0.07, 0.44], 'r': [2, 0, 0]}, 'spine': r(-6),
                     'rightUpperArm': r(30, 0, 40), 'leftUpperArm': r(40, 0, -40), **BENT})
clip('movement.stumble-backward', 'Stumble backward', 'movement', 0.95, False,
     [(0, STANCE), (0.12, SB1), (0.36, SB2), (0.62, SB3), (0.95, at(STANCE, p=[0, -0.02, 0.45]))],
     events=[ev(0.8, 'recover')], root=baked([0, 0, 0.45]),
     desc='Backpedal off balance two steps with arms windmilling, recover.', tags=['stumble'])

# Stagger while moving: loose, swaying walk
def stag(p, side):
    return merge(p, {'hips': {'p': [0.06 * side, p['hips'].get('p', [0, 0, 0])[1] - 0.02, 0], 'r': [0, 0, -6 * side]},
                     'spine': r(-6, 0, 8 * side), 'chest': r(-4, 0, 3 * side), 'neck': r(-12, 0, 10 * side),
                     'rightUpperArm': r(6, 0, 18), 'leftUpperArm': r(6, 0, -18), 'rightForearm': r(8), 'leftForearm': r(8)})
clip('movement.stagger-move', 'Stagger while moving', 'movement', 1.4, True,
     [(0, stag(WC, -1)), (0.35, stag(WP, 0)), (0.7, stag(mirror(WC), 1)), (1.05, stag(mirror(WP), 0)), (1.4, stag(WC, -1))],
     root={'mode': 'inPlace', 'speed': 0.7, 'direction': [0, 0, -1]},
     desc='Dazed, swaying walk with loose arms and head lolling.', tags=['locomotion', 'loop', 'injured'])

# ================================================================ STRIKING (all from and back to GUARD)

def strike(cid, name, dur, keys, hit_t, desc, tags=(), **hitkw):
    clip(cid, name, 'striking', dur, False, keys, events=[ev(hit_t, 'hit', **hitkw)], desc=desc, tags=['strike'] + list(tags))

J_HIT = merge(GUARD, {'hips': {'p': [0, -0.03, -0.03], 'r': [0, -4, 0]}, 'spine': r(-6, -4, 0), 'chest': r(-2, -10, 0), 'neck': r(4, 10, 0),
                      'leftUpperArm': r(88, 0, 4), 'leftForearm': r(4), 'leftHand': r(0, 0, 6)})
strike('striking.jab', 'Jab', 0.45, [(0, GUARD), (0.06, merge(GUARD, {'leftForearm': r(128)})), (0.15, J_HIT),
                                     (0.22, merge(J_HIT, {'leftForearm': r(16)})), (0.45, GUARD)],
       0.15, 'Quick lead-hand jab, straight back to guard.', ['left', 'fast'], attachment='leftHandGrip', zone='head', reach=0.7)

H_WIND = merge(GUARD, {'hips': {'r': [0, -6, 0], 'p': [0, -0.03, 0.01]}, 'spine': r(-4, -6, 0), 'chest': r(0, -20, 0), 'neck': r(4, 22, 0),
                       'rightUpperArm': r(0, -10, 70), 'rightForearm': r(100)})
H_HIT = merge(GUARD, {'hips': {'p': [0, -0.05, -0.03], 'r': [0, 10, 0]}, 'spine': r(-6, 10, 0), 'chest': r(0, 22, 0), 'neck': r(4, -28, 0),
                      'rightUpperArm': r(0, 55, 72), 'rightForearm': r(95),
                      'rightUpperLeg': r(6, 0, 4), 'leftUpperLeg': r(12, 0, -4), 'leftLowerLeg': r(-22)})
H_FOL = merge(H_HIT, {'chest': r(0, 30, 0), 'rightUpperArm': r(0, 70, 70), 'rightForearm': r(100)})
HOOK = [(0, GUARD), (0.18, H_WIND), (0.32, H_HIT), (0.42, H_FOL), (0.75, GUARD)]
strike('striking.hook-right', 'Hook punch, right', 0.75, HOOK, 0.32, 'Looping right hook with full hip and chest turn.', ['right'],
       attachment='rightHandGrip', zone='head', reach=0.6)
strike('striking.hook-left', 'Hook punch, left', 0.75, mirror_keys(HOOK), 0.32, 'Looping left hook with full hip and chest turn.', ['left'],
       attachment='leftHandGrip', zone='head', reach=0.6)

U_DIP = merge(GUARD, {'hips': {'p': [0, -0.12, 0], 'r': [0, -8, 0]}, **{k: v for k, v in BENT.items()},
                      'rightUpperLeg': r(22, 0, 4), 'leftUpperLeg': r(22, 0, -4), 'rightLowerLeg': r(-44), 'leftLowerLeg': r(-44),
                      'rightFoot': r(22, 0, -4), 'leftFoot': r(22, 0, 4),
                      'spine': r(-10, -6, -6), 'chest': r(0, -10, 0), 'rightUpperArm': r(30, 0, -12), 'rightForearm': r(130)})
U_HIT = merge(GUARD, {'hips': {'p': [0, -0.0, -0.04], 'r': [0, 10, 0]},
                      'rightUpperLeg': r(4, 0, 4), 'leftUpperLeg': r(4, 0, -4), 'rightLowerLeg': r(-8), 'leftLowerLeg': r(-8),
                      'rightFoot': r(4, 0, -4), 'leftFoot': r(4, 0, 4),
                      'spine': r(4, 8, 0), 'chest': r(2, 16, 0), 'neck': r(-4, -14, 0),
                      'rightUpperArm': r(122, 0, -14), 'rightForearm': r(100)})
strike('striking.uppercut', 'Uppercut', 0.8, [(0, GUARD), (0.18, U_DIP), (0.32, U_HIT), (0.44, merge(U_HIT, {'rightForearm': r(118)})), (0.8, GUARD)],
       0.32, 'Dip at the knees and drive a right uppercut up under the chin.', ['right'], attachment='rightHandGrip', zone='head', reach=0.5)

BP_WIND = merge(GUARD, {'chest': r(0, -12, 0), 'rightForearm': r(130), 'hips': {'p': [0, -0.08, 0]}})
BP_HIT = merge(GUARD, {'hips': {'p': [0, -0.14, -0.06], 'r': [0, 8, 0]},
                       'rightUpperLeg': r(24, 0, 4), 'leftUpperLeg': r(24, 0, -4), 'rightLowerLeg': r(-46), 'leftLowerLeg': r(-46),
                       'rightFoot': r(22, 0, -4), 'leftFoot': r(22, 0, 4),
                       'spine': r(-16, 8, 0), 'chest': r(-4, 14, 0), 'neck': r(18, -14, 0),
                       'rightUpperArm': r(62, 0, -4), 'rightForearm': r(16)})
strike('striking.body-punch', 'Body punch', 0.7, [(0, GUARD), (0.14, BP_WIND), (0.28, BP_HIT), (0.38, merge(BP_HIT, {'rightForearm': r(24)})), (0.7, GUARD)],
       0.28, 'Drop low and dig a right hand into the body.', ['right'], attachment='rightHandGrip', zone='body', reach=0.7)

LK_WIND = merge(GUARD, {'hips': {'r': [0, -12, 0]}, 'rightUpperLeg': r(10, 0, 18), 'rightLowerLeg': r(-30), 'leftUpperLeg': r(10, 0, -4)})
LK_HIT = merge(GUARD, {'hips': {'p': [0, -0.04, -0.02], 'r': [0, 28, 0]}, 'spine': r(0, 8, 0), 'chest': r(0, 6, 0), 'neck': r(0, -30, 0),
                       'rightUpperLeg': r(38, 0, -6), 'rightLowerLeg': r(-14), 'rightFoot': r(10),
                       'leftUpperLeg': r(6, -24, -4), 'leftLowerLeg': r(-18), 'leftFoot': r(8, 0, 4),
                       'rightUpperArm': r(-20, 0, -10), 'rightForearm': r(60)})
strike('striking.low-kick', 'Low kick', 0.8, [(0, GUARD), (0.16, LK_WIND), (0.3, LK_HIT), (0.4, merge(LK_HIT, {'rightLowerLeg': r(-24)})), (0.8, GUARD)],
       0.3, 'Right shin swung low into the opponent\'s thigh.', ['right', 'kick'], bone='rightLowerLeg', zone='legs', reach=0.9)

RH_CH = merge(GUARD, {'hips': {'p': [0, -0.03, 0.02], 'r': [0, 40, -10]}, 'spine': r(0, 10, 14), 'neck': r(0, -30, -6),
                      'rightUpperLeg': r(40, 0, 75), 'rightLowerLeg': r(-100), 'rightFoot': r(10),
                      'leftUpperLeg': r(4, -40, -4), 'leftLowerLeg': r(-14), 'leftFoot': r(6, 0, 4),
                      'leftUpperArm': r(20, 0, -50), 'leftForearm': r(60), 'rightUpperArm': r(-10, 0, -20), 'rightForearm': r(40)})
RH_HIT = merge(RH_CH, {'hips': {'p': [0, -0.02, 0.04], 'r': [0, 60, -14]}, 'spine': r(0, 14, 20), 'neck': r(0, -44, -10),
                       'rightUpperLeg': r(30, 0, 102), 'rightLowerLeg': r(-8), 'rightFoot': r(-10), 'leftUpperLeg': r(4, -60, -4)})
strike('striking.roundhouse', 'Roundhouse kick', 1.0,
       [(0, GUARD), (0.26, RH_CH), (0.42, RH_HIT), (0.52, merge(RH_HIT, {'rightLowerLeg': r(-20)})), (0.72, merge(RH_CH, {'rightUpperLeg': r(30, 0, 40)})), (1.0, GUARD)],
       0.42, 'Pivot on the left foot and whip the right leg round at head height.', ['right', 'kick'], bone='rightFoot', zone='head', reach=1.1)

KN_CL = merge(GUARD, {'rightUpperArm': r(85, 0, -10), 'leftUpperArm': r(85, 0, 10), 'rightForearm': r(40), 'leftForearm': r(40)})
KN_HIT = merge(GUARD, {'hips': {'p': [0, 0.02, -0.06], 'r': [-6, 0, 0]}, 'spine': r(-10), 'neck': r(10),
                       'rightUpperLeg': r(105, 0, 4), 'rightLowerLeg': r(-125), 'rightFoot': r(30),
                       'leftUpperLeg': r(-6, 0, -4), 'leftLowerLeg': r(-6), 'leftFoot': r(6, 0, 4),
                       'rightUpperArm': r(70, 0, -12), 'leftUpperArm': r(70, 0, 12), 'rightForearm': r(70), 'leftForearm': r(70)})
strike('striking.knee', 'Knee strike', 0.7, [(0, GUARD), (0.14, KN_CL), (0.28, KN_HIT), (0.38, KN_HIT), (0.7, GUARD)],
       0.28, 'Clinch the head and drive the right knee up into the body.', ['right', 'knee'], bone='rightLowerLeg', zone='body', reach=0.5)

E_WIND = merge(GUARD, {'chest': r(0, -16, 0), 'rightUpperArm': r(0, -20, 75), 'rightForearm': r(140)})
E_HIT = merge(GUARD, {'hips': {'p': [0, -0.04, -0.06], 'r': [0, 10, 0]}, 'spine': r(-6, 10, 0), 'chest': r(0, 26, 0), 'neck': r(0, -24, 0),
                      'rightUpperArm': r(0, 60, 80), 'rightForearm': r(145)})
strike('striking.elbow', 'Elbow strike', 0.7, [(0, GUARD), (0.14, E_WIND), (0.26, E_HIT), (0.36, E_HIT), (0.7, GUARD)],
       0.26, 'Short horizontal right elbow at head height.', ['right'], bone='rightForearm', zone='head', reach=0.45)

C_WIND = merge(GUARD, {'chest': r(0, -14, 0), 'rightUpperArm': r(0, -40, 80), 'rightForearm': r(4),
                       'leftUpperLeg': r(26, 0, -4), 'leftLowerLeg': r(-14), 'rightUpperLeg': r(-14, 0, 4), 'rightLowerLeg': r(-20)})
C_HIT = merge(GUARD, {'hips': {'p': [0, -0.04, 0], 'r': [0, 10, 0]}, 'chest': r(0, 18, 0), 'neck': r(0, -20, 0),
                      'rightUpperArm': r(0, 30, 86), 'rightForearm': r(4),
                      'rightUpperLeg': r(26, 0, 4), 'rightLowerLeg': r(-10), 'leftUpperLeg': r(-16, 0, -4), 'leftLowerLeg': r(-24)})
C_FOL = merge(C_HIT, {'chest': r(0, 26, 0), 'rightUpperArm': r(0, 62, 84)})
clip('striking.clothesline', 'Clothesline', 'striking', 1.0, False, [(0, GUARD), (0.16, C_WIND), (0.4, C_HIT), (0.55, C_FOL), (1.0, GUARD)],
     events=[ev(0.4, 'hit', bone='rightForearm', zone='head', reach=0.8)],
     root={'mode': 'speedCurve', 'direction': [0, 0, -1], 'speedCurve': [[0, 1.5], [0.35, 3.0], [0.55, 1.5], [0.8, 0], [1.0, 0]]},
     desc='Charge two steps and swing the straight right arm through at neck height.', tags=['strike', 'right'])

D_UP = merge(GUARD, {'hips': {'p': [0, -0.01, 0.02]}, 'spine': r(10), 'chest': r(6), 'neck': r(-4),
                     'rightUpperArm': r(165, 0, -32), 'leftUpperArm': r(165, 0, 32), 'rightForearm': r(40), 'leftForearm': r(40),
                     'rightFoot': r(-4, 0, -4), 'leftFoot': r(-4, 0, 4)})
D_HIT = merge(GUARD, {'hips': {'p': [0, -0.1, -0.05]}, 'spine': r(-24), 'chest': r(-10), 'neck': r(20),
                      'rightUpperArm': r(55, 0, -30), 'leftUpperArm': r(55, 0, 30), 'rightForearm': r(14), 'leftForearm': r(14),
                      'rightUpperLeg': r(20, 0, 4), 'leftUpperLeg': r(20, 0, -4), 'rightLowerLeg': r(-40), 'leftLowerLeg': r(-40),
                      'rightFoot': r(20, 0, -4), 'leftFoot': r(20, 0, 4)})
strike('striking.double-axe', 'Double axe handle', 0.9, [(0, GUARD), (0.3, D_UP), (0.45, D_HIT), (0.56, D_HIT), (0.9, GUARD)],
       0.45, 'Clasp both hands overhead and club down.', ['two-hand'], attachment='rightHandGrip', zone='head', reach=0.6)

# ================================================================ REACTIONS

def react(cid, name, dur, keys, end, desc, tags=(), zone='body', recover=None, extra_events=(), rotY=None, **rootkw):
    evs = [ev(0.0, 'hit_received', zone=zone)] + list(extra_events)
    if recover is not None: evs.append(ev(recover, 'recover'))
    clip(cid, name, 'reactions', dur, False, keys, events=evs, root=baked(end, rotY, **rootkw), desc=desc, tags=['reaction'] + list(tags))

RFB1 = merge(STANCE, BENT, CLUTCH, {'hips': {'p': [0, -0.08, 0.08]}, 'spine': r(-28), 'chest': r(-16), 'neck': r(14)})
RFB2 = merge(STANCE, CLUTCH, {'hips': {'p': [0, -0.06, 0.14]}, 'spine': r(-20), 'chest': r(-8), 'neck': r(10),
                              'rightUpperLeg': r(-14, 0, 4), 'rightLowerLeg': r(-22), 'leftUpperLeg': r(16, 0, -4), 'leftLowerLeg': r(-22)})
react('reactions.hit-front-body', 'Hit from front, body', 0.8,
      [(0, STANCE), (0.1, RFB1), (0.35, RFB2), (0.8, at(STANCE, p=[0, -0.02, 0.13]))], [0, 0, 0.13],
      'Winded by a blow to the stomach: doubles over, step back, recover.', ['front'], 'body', 0.65)

RBB1 = merge(STANCE, {'hips': {'p': [0, -0.04, -0.1], 'r': [-4, 0, 0]}, 'spine': r(16), 'chest': r(10), 'neck': r(14),
                      'rightUpperArm': r(-30, 0, 30), 'leftUpperArm': r(-30, 0, -30), 'rightForearm': r(20), 'leftForearm': r(20)})
RBB2 = merge(STANCE, {'hips': {'p': [0, -0.06, -0.16]}, 'spine': r(6), 'neck': r(4),
                      'rightUpperArm': r(10, 0, 20), 'leftUpperArm': r(30, 0, -20),
                      'leftUpperLeg': r(30, 0, -4), 'leftLowerLeg': r(-22), 'rightUpperLeg': r(-12, 0, 4), 'rightLowerLeg': r(-20)})
react('reactions.hit-back-body', 'Hit from behind, body', 0.8,
      [(0, STANCE), (0.1, RBB1), (0.35, RBB2), (0.8, at(STANCE, p=[0, -0.02, -0.15]))], [0, 0, -0.15],
      'Struck in the lower back: arches, arms fly back, stumble step forward.', ['back'], 'back', 0.65)

HL1 = merge(STANCE, {'hips': {'p': [0.08, -0.04, 0], 'r': [0, 0, -4]}, 'spine': r(0, -8, -10), 'chest': r(0, -6, -8),
                     'neck': r(0, -20, -22), 'head': r(0, -10, -8),
                     'leftUpperArm': r(10, 0, -40), 'rightUpperArm': r(10, 0, 30), 'leftForearm': r(30), 'rightForearm': r(30)})
HL2 = merge(STANCE, {'hips': {'p': [0.16, -0.05, 0]}, 'spine': r(0, -4, -4), 'neck': r(0, -8, -8),
                     'rightUpperLeg': r(4, 0, 18), 'rightLowerLeg': r(-16), 'rightFoot': r(4, 0, -16), 'leftUpperLeg': r(4, 0, 2),
                     'leftUpperArm': r(6, 0, -20), 'rightUpperArm': r(6, 0, 20)})
HLK = [(0, STANCE), (0.08, HL1), (0.3, HL2), (0.75, at(STANCE, p=[0.14, -0.02, 0]))]
react('reactions.hit-left', 'Hit from left', 0.75, HLK, [0.14, 0, 0],
      'Hit on the left side of the head: snaps to the right, side step right, recover.', ['side', 'left-side'], 'head', 0.6)
react('reactions.hit-right', 'Hit from right', 0.75, mirror_keys(HLK), [-0.14, 0, 0],
      'Hit on the right side of the head: snaps to the left, side step left, recover.', ['side', 'right-side'], 'head', 0.6)

HK1 = merge(STANCE, BENT, CLUTCH, {'hips': {'p': [0, -0.1, 0.1]}, 'spine': r(-34), 'chest': r(-18), 'neck': r(20)})
HK2 = merge(STANCE, CLUTCH, {'hips': {'p': [0, -0.08, 0.22]}, 'spine': r(-26), 'chest': r(-10), 'neck': r(14),
                             'rightUpperLeg': r(-16, 0, 4), 'rightLowerLeg': r(-24), 'leftUpperLeg': r(18, 0, -4), 'leftLowerLeg': r(-26)})
HK3 = merge(STANCE, CLUTCH, {'hips': {'p': [0, -0.06, 0.3]}, 'spine': r(-14), 'neck': r(8),
                             'leftUpperLeg': r(-14, 0, -4), 'leftLowerLeg': r(-22), 'rightUpperLeg': r(14, 0, 4), 'rightLowerLeg': r(-20)})
react('reactions.hit-kick', 'Hit by kick', 0.95,
      [(0, STANCE), (0.08, HK1), (0.3, HK2), (0.55, HK3), (0.95, at(STANCE, p=[0, -0.02, 0.32]))], [0, 0, 0.32],
      'Kicked in the body: folds in half and is driven back two steps.', ['front', 'heavy'], 'body', 0.8)

HC1 = merge(STANCE, {'hips': {'p': [0, -0.05, 0.15], 'r': [30, 0, 0]}, 'spine': r(10), 'neck': r(30),
                     'rightUpperArm': r(120, 0, 40), 'leftUpperArm': r(120, 0, -40), 'rightForearm': r(10), 'leftForearm': r(10),
                     'rightUpperLeg': r(50, 0, 4), 'leftUpperLeg': r(40, 0, -4), 'rightLowerLeg': r(-10), 'leftLowerLeg': r(-20)})
HC2 = merge(LIE_BACK, {'hips': {'p': [0, -0.5, 0.5], 'r': [80, 0, 0]}, 'neck': r(-10),
                       'rightUpperLeg': r(50, 0, 6), 'leftUpperLeg': r(50, 0, -6), 'rightLowerLeg': r(-20), 'leftLowerLeg': r(-20),
                       'rightUpperArm': r(60, 0, 50), 'leftUpperArm': r(60, 0, -50)})
HC3 = merge(F3, {'hips': {'p': [0, -0.83, 0.75], 'r': [92, 0, 0]}})
HC4 = merge(F4, {'hips': {'p': [0, -0.79, 0.75], 'r': [86, 0, 0]}})
react('reactions.hit-clothesline', 'Hit by clothesline', 1.4,
      [(0, STANCE), (0.1, HC1), (0.3, HC2), (0.5, HC3), (0.62, HC4), (1.4, at(LIE_BACK, p=[0, -0.83, 0.75]))], [0, 0, 0.75],
      'Clotheslined: legs fly up, flips back and lands flat on the back. Holds lying on the back.',
      ['front', 'heavy', 'ends-lying-back'], 'head', None, extra_events=[ev(0.5, 'land', zone='back')])

CH1 = merge(STANCE, {'hips': {'p': [0, -0.18, 0.04]}, 'spine': r(-10), 'neck': r(-24), 'head': r(-10),
                     'rightUpperLeg': r(24, 0, 4), 'leftUpperLeg': r(24, 0, -4), 'rightLowerLeg': r(-50), 'leftLowerLeg': r(-50),
                     'rightFoot': r(24, 0, -4), 'leftFoot': r(24, 0, 4),
                     'rightUpperArm': r(120, 0, 40), 'leftUpperArm': r(120, 0, -40), 'rightForearm': r(120), 'leftForearm': r(120)})
CH2 = merge(CH1, {'hips': {'p': [0, -0.12, 0.12]}, 'spine': r(-14), 'neck': r(-14),
                  'rightUpperLeg': r(-10, 0, 4), 'rightLowerLeg': r(-30), 'leftUpperLeg': r(20, 0, -4), 'leftLowerLeg': r(-34)})
CH3 = merge(STANCE, {'hips': {'p': [0, -0.06, 0.16]}, 'spine': r(-8), 'neck': r(-4),
                     'rightUpperArm': r(40, 0, 10), 'leftUpperArm': r(40, 0, -10), 'rightForearm': r(60), 'leftForearm': r(60)})
react('reactions.hit-chair', 'Hit by chair', 1.1,
      [(0, STANCE), (0.08, CH1), (0.4, CH2), (0.75, CH3), (1.1, at(STANCE, p=[0, -0.02, 0.16]))], [0, 0, 0.16],
      'Chair shot to the head: knees buckle, hands to the head, stagger back.', ['front', 'weapon', 'heavy'], 'head', 0.9)

def sway(base, dx, dz, tilt, neckz, neckx=-16, extra=None):
    p = merge(base, {'hips': {'p': [dx, base['hips']['p'][1], dz], 'r': [0, 0, tilt]}, 'spine': r(-8, 0, -tilt * 1.2),
                     'neck': r(neckx, 0, neckz)})
    return merge(p, extra or {})
ST_BASE = merge(STANCE, LIMP_ARMS, {'hips': {'p': [0, -0.05, 0]}, 'rightLowerLeg': r(-16), 'leftLowerLeg': r(-16)})
clip('reactions.stunned', 'Stunned', 'reactions', 2.0, True,
     [(0, sway(ST_BASE, 0.03, 0, -3, 6)), (0.5, sway(ST_BASE, 0, -0.03, 0, 0, -20)), (1.0, sway(ST_BASE, -0.03, 0, 3, -6)),
      (1.5, sway(ST_BASE, 0, 0.03, 0, 0, -12)), (2.0, sway(ST_BASE, 0.03, 0, -3, 6))],
     desc='Standing stunned: limp arms, head drooping, slow circular sway. Loop until the game recovers the wrestler.',
     tags=['reaction', 'loop', 'stunned'])

DZ_BASE = merge(STANCE, {'hips': {'p': [0, -0.05, 0]}})
clip('reactions.dizzy', 'Dizzy', 'reactions', 1.6, True,
     [(0, sway(DZ_BASE, 0.06, 0, -6, 16, -10, {'rightUpperArm': r(10, 0, 26), 'leftUpperArm': r(10, 0, -8), 'neck': r(-10, 12, 16)})),
      (0.4, sway(DZ_BASE, 0, -0.06, 0, 0, -18, {'leftUpperLeg': r(18, 0, -4), 'leftLowerLeg': r(-34), 'rightUpperArm': r(16, 0, 10), 'leftUpperArm': r(16, 0, -10)})),
      (0.8, sway(DZ_BASE, -0.06, 0, 6, -16, -10, {'leftUpperArm': r(10, 0, -26), 'rightUpperArm': r(10, 0, 8), 'neck': r(-10, -12, -16)})),
      (1.2, sway(DZ_BASE, 0, 0.06, 0, 0, -4, {'rightUpperLeg': r(18, 0, 4), 'rightLowerLeg': r(-34), 'rightUpperArm': r(20, 0, 14), 'leftUpperArm': r(20, 0, -14)})),
      (1.6, sway(DZ_BASE, 0.06, 0, -6, 16, -10, {'rightUpperArm': r(10, 0, 26), 'leftUpperArm': r(10, 0, -8), 'neck': r(-10, 12, 16)}))],
     desc='Dizzy: wide wobbling sway, head rolling, arms flailing for balance, feet shuffling. Loop.',
     tags=['reaction', 'loop', 'stunned'])

KB1 = merge(STANCE, {'hips': {'p': [0, -0.04, 0.12], 'r': [8, 0, 0]}, 'spine': r(10), 'chest': r(8), 'neck': r(16),
                     'rightUpperArm': r(50, 0, 30), 'leftUpperArm': r(50, 0, -30), 'rightForearm': r(30), 'leftForearm': r(30)})
KB2 = merge(STANCE, {'hips': {'p': [0, -0.06, 0.4], 'r': [6, 0, 0]}, 'spine': r(4), 'neck': r(6),
                     'rightUpperLeg': r(-24, 0, 4), 'rightLowerLeg': r(-16), 'leftUpperLeg': r(18, 0, -4), 'leftLowerLeg': r(-24),
                     'rightUpperArm': r(140, 0, 30), 'leftUpperArm': r(-20, 0, -40), 'rightForearm': r(20), 'leftForearm': r(20)})
KB3 = merge(STANCE, {'hips': {'p': [0, -0.07, 0.68], 'r': [4, 0, 0]},
                     'leftUpperLeg': r(-24, 0, -4), 'leftLowerLeg': r(-16), 'rightUpperLeg': r(18, 0, 4), 'rightLowerLeg': r(-24),
                     'leftUpperArm': r(140, 0, -30), 'rightUpperArm': r(-20, 0, 40), 'rightForearm': r(20), 'leftForearm': r(20)})
KB4 = merge(STANCE, BENT, {'hips': {'p': [0, -0.08, 0.86]}, 'spine': r(-8), 'rightUpperArm': r(20, 0, 50), 'leftUpperArm': r(20, 0, -50)})
react('reactions.knocked-back', 'Knocked backwards', 1.1,
      [(0, STANCE), (0.08, KB1), (0.3, KB2), (0.55, KB3), (0.8, KB4), (1.1, at(STANCE, p=[0, -0.02, 0.9]))], [0, 0, 0.9],
      'Big shove: driven back three steps with arms windmilling, regains footing.', ['front', 'heavy'], 'body', 0.95)

SR1 = merge(STANCE, {'hips': {'p': [0, -0.06, 0.12], 'r': [6, 0, 0]}, 'neck': r(10),
                     'rightUpperArm': r(30, 0, 30), 'leftUpperArm': r(30, 0, -30), 'rightUpperLeg': r(-14, 0, 4), 'rightLowerLeg': r(-24)})
SR2 = {'hips': {'p': [0, -0.25, 0.25]}, 'spine': r(-40), 'chest': r(-10), 'neck': r(30),
       'rightUpperArm': r(50, 0, -6), 'leftUpperArm': r(50, 0, 6), 'rightForearm': r(20), 'leftForearm': r(20),
       'rightUpperLeg': r(30, 0, 6), 'leftUpperLeg': r(30, 0, -6), 'rightLowerLeg': r(-55), 'leftLowerLeg': r(-55),
       'rightFoot': r(25, 0, -6), 'leftFoot': r(25, 0, 6)}
SR3 = merge(SR2, {'hips': {'p': [0, -0.23, 0.25]}, 'spine': r(-36), 'neck': r(26)})
react('reactions.stumble-recover', 'Stumble and recover', 1.4,
      [(0, STANCE), (0.12, SR1), (0.4, SR2), (0.85, SR3), (1.4, at(STANCE, p=[0, -0.02, 0.25]))], [0, 0, 0.25],
      'Stagger back, hands on knees to catch a breath, straighten up.', ['front'], 'body', 1.2)

# ================================================================ FALLS AND RECOVERY

def fall(cid, name, dur, keys, end, desc, tags=(), land=None, rotY=None, extra_events=(), recover=None, mode='baked'):
    evs = list(extra_events)
    if land is not None: evs.insert(0, ev(land[0], 'land', zone=land[1]))
    if recover is not None: evs.append(ev(recover, 'recover'))
    root = baked(end, rotY) if mode == 'baked' else {'mode': 'none'}
    clip(cid, name, 'falls', dur, False, keys, events=evs, root=root, desc=desc, tags=['fall'] + list(tags))

FF1 = merge(STANCE, {'hips': {'p': [0, -0.04, -0.06], 'r': [-8, 0, 0]}, 'spine': r(-10), 'neck': r(10),
                     'rightUpperArm': r(60, 0, 20), 'leftUpperArm': r(60, 0, -20), 'rightForearm': r(20), 'leftForearm': r(20)})
FF2 = {'hips': {'p': [0, -0.35, -0.35], 'r': [-40, 0, 0]}, 'neck': r(24),
       'rightUpperArm': r(100, 0, 25), 'leftUpperArm': r(100, 0, -25), 'rightForearm': r(10), 'leftForearm': r(10),
       'rightUpperLeg': r(16, 0, 4), 'leftUpperLeg': r(16, 0, -4), 'rightLowerLeg': r(-6), 'leftLowerLeg': r(-6)}
FF3 = merge(LIE_FRONT, {'hips': {'p': [0, -0.82, -0.62], 'r': [-90, 0, 0]}, 'neck': r(20, 30, 0),
                        'rightForearm': r(0, 0, 50), 'leftForearm': r(0, 0, -50)})
FF4 = merge(FF3, {'hips': {'p': [0, -0.79, -0.62], 'r': [-85, 0, 0]}, 'rightUpperLeg': r(-10, 0, 6), 'leftUpperLeg': r(-10, 0, -6),
                  'rightLowerLeg': r(-30), 'leftLowerLeg': r(-30)})
fall('falls.fall-forward', 'Fall forwards', 1.5,
     [(0, STANCE), (0.15, FF1), (0.4, FF2), (0.62, FF3), (0.75, FF4), (1.5, at(LIE_FRONT, p=[0, -0.84, -0.62]))], [0, 0, -0.62],
     'Topple forward, hands out, land face down. Holds face down.', ['front', 'ends-lying-front'], (0.62, 'front'))

# Sideways fall to the character's left, then roll onto the back. Head ends towards -X, so the
# wrestler is turned -90 degrees when the next clip starts and the lying pose matches LIE_BACK.
SL1 = merge(STANCE, {'hips': {'p': [-0.04, -0.03, 0], 'r': [0, 0, 8]}, 'neck': r(0, 0, -16),
                     'rightUpperArm': r(20, 0, 40), 'leftUpperArm': r(20, 0, -50), 'rightForearm': r(30), 'leftForearm': r(20)})
SL2 = {'hips': {'p': [-0.45, -0.33, 0], 'r': [0, 0, 45]}, 'neck': r(0, 0, -20), 'spine': r(0, 0, -8),
       'leftUpperArm': r(0, 0, -80), 'leftForearm': r(10), 'rightUpperArm': r(30, 0, 60), 'rightForearm': r(40),
       'rightUpperLeg': r(10, 0, 22), 'rightLowerLeg': r(-20), 'leftUpperLeg': r(0, 0, -2), 'leftLowerLeg': r(-8)}
SL3 = {'hips': {'p': [-0.78, -0.8, 0], 'r': [0, 0, 88]}, 'neck': r(0, 0, -14),
       'leftUpperArm': r(0, 0, -100), 'leftForearm': r(20), 'rightUpperArm': r(20, 0, 30), 'rightForearm': r(30),
       'rightUpperLeg': r(10, 0, 10), 'rightLowerLeg': r(-30), 'leftUpperLeg': r(0, 0, 0), 'leftLowerLeg': r(-10)}
SL4 = merge(SL3, {'hips': {'p': [-0.78, -0.77, 0], 'r': [0, 0, 84]}})
SL5 = merge(LIE_BACK, {'hips': {'p': [-0.78, -0.8, 0], 'r': [45, 0, 89]}, 'rightUpperLeg': r(20, 0, 8), 'rightLowerLeg': r(-30)})
SL6 = at(LIE_BACK, p=[-0.78, -0.83, 0], rot=[90, 0, 90])
FALL_LEFT = [(0, STANCE), (0.15, SL1), (0.42, SL2), (0.64, SL3), (0.76, SL4), (1.15, SL5), (1.6, SL6)]
fall('falls.fall-left', 'Fall sideways, left', 1.6, FALL_LEFT, [-0.78, 0, 0],
     'Topple to the left, land on the side, roll flat onto the back. Holds lying on the back.',
     ['side', 'ends-lying-back'], (0.64, 'side'), rotY=-90)
fall('falls.fall-right', 'Fall sideways, right', 1.6, mirror_keys(FALL_LEFT), [0.78, 0, 0],
     'Topple to the right, land on the side, roll flat onto the back. Holds lying on the back.',
     ['side', 'ends-lying-back'], (0.64, 'side'), rotY=90)

CK1 = merge(STANCE, LIMP_ARMS, {'hips': {'p': [0, -0.2, 0]}, 'spine': r(-10), 'neck': r(-14),
                                'rightUpperLeg': r(30, 0, 4), 'leftUpperLeg': r(30, 0, -4), 'rightLowerLeg': r(-60), 'leftLowerLeg': r(-60),
                                'rightFoot': r(30, 0, -4), 'leftFoot': r(30, 0, 4)})
CK2 = merge(LIMP_ARMS, {'hips': {'p': [0, -0.5, 0.04]}, 'spine': r(-6), 'neck': r(-16),
                        'rightUpperLeg': r(20, 0, 4), 'leftUpperLeg': r(20, 0, -4), 'rightLowerLeg': r(-110), 'leftLowerLeg': r(-110),
                        'rightFoot': r(-30), 'leftFoot': r(-30)})
CK3 = merge(CK2, {'hips': {'p': [0, -0.48, 0.05]}})
CK4 = merge({'hips': {'p': [0, -0.62, 0.12]}, 'spine': r(-24), 'chest': r(-10), 'neck': r(-30),
             'rightUpperArm': r(14, 0, -8), 'leftUpperArm': r(14, 0, 8), 'rightForearm': r(10), 'leftForearm': r(10),
             'rightUpperLeg': r(44, 0, 6), 'leftUpperLeg': r(44, 0, -6), 'rightLowerLeg': r(-134), 'leftLowerLeg': r(-134),
             'rightFoot': r(-30), 'leftFoot': r(-30)})
fall('falls.collapse-knees', 'Collapse to knees', 1.2,
     [(0, STANCE), (0.2, CK1), (0.5, CK2), (0.62, CK3), (1.2, CK4)], [0, 0, 0],
     'Legs give way: drop onto the knees and slump back onto the heels. Holds kneeling.',
     ['ends-kneeling'], (0.5, 'knees'), mode='none')

SP1 = merge(STANCE, {'hips': {'p': [0, -0.1, 0.15], 'r': [10, 0, 0]}, 'spine': r(-35), 'chest': r(-20), 'neck': r(20),
                     'rightUpperArm': r(70, 0, 30), 'leftUpperArm': r(70, 0, -30), 'rightForearm': r(20), 'leftForearm': r(20),
                     'rightUpperLeg': r(30, 0, 4), 'leftUpperLeg': r(30, 0, -4), 'rightLowerLeg': r(-20), 'leftLowerLeg': r(-20)})
SP2 = {'hips': {'p': [0, -0.3, 0.7], 'r': [40, 0, 0]}, 'spine': r(-30), 'chest': r(-10), 'neck': r(20),
       'rightUpperArm': r(80, 0, 30), 'leftUpperArm': r(80, 0, -30), 'rightForearm': r(20), 'leftForearm': r(20),
       'rightUpperLeg': r(50, 0, 6), 'leftUpperLeg': r(50, 0, -6), 'rightLowerLeg': r(-20), 'leftLowerLeg': r(-20)}
SP3 = merge(F3, {'hips': {'p': [0, -0.83, 1.2], 'r': [92, 0, 0]}, 'rightUpperArm': r(0, -10, 75), 'leftUpperArm': r(0, 10, -75),
                 'rightUpperLeg': r(40, 0, 6), 'leftUpperLeg': r(40, 0, -6)})
SP4 = merge(F4, {'hips': {'p': [0, -0.78, 1.22], 'r': [85, 0, 0]}})
fall('falls.fall-spear', 'Fall after spear', 1.4,
     [(0, STANCE), (0.06, SP1), (0.3, SP2), (0.55, SP3), (0.7, SP4), (1.4, at(LIE_BACK, p=[0, -0.83, 1.25]))], [0, 0, 1.25],
     'Speared through the middle: folded in half, driven back through the air, slammed flat. Holds lying on the back.',
     ['heavy', 'ends-lying-back'], (0.55, 'back'))

SLM0 = merge(LIE_BACK, {'hips': {'p': [0, 0.0, 0], 'r': [90, 0, 0]}, 'neck': r(-10),
                        'rightUpperLeg': r(30, 0, 6), 'leftUpperLeg': r(30, 0, -6), 'rightLowerLeg': r(-40), 'leftLowerLeg': r(-40),
                        'rightUpperArm': r(30, 0, 40), 'leftUpperArm': r(30, 0, -40)})
SLM1 = merge(F3, {'hips': {'p': [0, -0.83, 0], 'r': [92, 0, 0]}, 'rightUpperArm': r(0, -10, 75), 'leftUpperArm': r(0, 10, -75)})
SLM2 = merge(F4, {'hips': {'p': [0, -0.76, 0], 'r': [86, 0, 0]}, 'rightUpperLeg': r(30, 0, 6), 'leftUpperLeg': r(30, 0, -6),
                  'rightLowerLeg': r(-40), 'leftLowerLeg': r(-40)})
SLM3 = merge(LIE_BACK, {'hips': {'p': [0, -0.8, 0], 'r': [86, 0, 0]}, 'spine': r(12), 'chest': r(6), 'neck': r(-8),
                        'rightUpperArm': r(-20, 0, 40), 'leftUpperArm': r(-20, 0, -40), 'rightForearm': r(40), 'leftForearm': r(40),
                        'rightUpperLeg': r(40, 0, 6), 'leftUpperLeg': r(40, 0, -6), 'rightLowerLeg': r(-80), 'leftLowerLeg': r(-80),
                        'rightFoot': r(30), 'leftFoot': r(30)})
fall('falls.fall-slam', 'Fall after body slam', 1.6,
     [(0, SLM0), (0.25, SLM1), (0.38, SLM2), (0.8, SLM3), (1.6, LIE_BACK)], [0, 0, 0],
     'Receiver end of a body slam: starts held horizontal at waist height, slams flat, arches in pain. Holds lying on the back.',
     ['heavy', 'starts-airborne-back', 'ends-lying-back'], (0.25, 'back'), mode='none')

clip('falls.lie-back', 'Lie on back', 'falls', 3.0, True,
     [(0, LIE_BACK), (1.5, merge(LIE_BACK, {'chest': r(4), 'neck': r(4, 0, 0), 'rightForearm': r(22), 'leftForearm': r(22)})), (3.0, LIE_BACK)],
     desc='Lying flat on the back, breathing. Loop.', tags=['fall', 'loop', 'starts-lying-back', 'ends-lying-back'])
clip('falls.lie-front', 'Lie face down', 'falls', 3.0, True,
     [(0, LIE_FRONT), (1.5, merge(LIE_FRONT, {'hips': {'p': [0, -0.832, 0], 'r': [-90, 0, 0]}, 'chest': r(-3)})), (3.0, LIE_FRONT)],
     desc='Lying face down, breathing. Loop.', tags=['fall', 'loop', 'starts-lying-front', 'ends-lying-front'])

# Rolls: rotate about the body's long axis. Euler (-90, -t, 0) == roll of the face-down pose; the end pose
# equals LIE_BACK turned 180 degrees, which loader-ext.js commits as endRotationY.
RT_MID = {'rightUpperArm': r(20, 0, 30), 'leftUpperArm': r(20, 0, -30), 'rightForearm': r(40), 'leftForearm': r(40),
          'rightUpperLeg': r(40, 0, 6), 'rightLowerLeg': r(-60), 'leftUpperLeg': r(6, 0, -6), 'leftLowerLeg': r(-10)}
def roll_keys(start, end, sign0, lift=0.04):
    ks = []
    for i, (t, th) in enumerate([(0, 0), (0.3, 45), (0.55, 90), (0.8, 135), (1.1, 180)]):
        u = th / 180
        base = start if u < 0.5 else end
        pose = copy.deepcopy(base)
        if 0 < u < 1: pose = merge(pose, RT_MID)
        y = -0.84 + 0.01 * u + lift * math.sin(math.pi * u)
        pose['hips'] = {'p': [round(0.42 * u, 3), round(y, 3), 0], 'r': [sign0 * 90, -sign0 * th, 0]}  # rolls towards +X
        ks.append((t, pose))
    return ks
fall('falls.roll-to-back', 'Roll onto back', 1.1, roll_keys(LIE_FRONT, LIE_BACK, -1), [0.42, 0, 0],
     'Roll from face down onto the back. The wrestler is turned 180 degrees when the next clip starts.',
     ['roll', 'starts-lying-front', 'ends-lying-back'], rotY=180)
fall('falls.roll-to-front', 'Roll onto stomach', 1.1, roll_keys(LIE_BACK, LIE_FRONT, 1), [0.42, 0, 0],
     'Roll from the back onto the stomach. The wrestler is turned 180 degrees when the next clip starts.',
     ['roll', 'starts-lying-back', 'ends-lying-front'], rotY=180)

GF1 = {'hips': {'p': [0, -0.7, 0.08], 'r': [-78, 0, 0]}, 'neck': r(30),
       'rightUpperArm': r(78, 0, -6), 'leftUpperArm': r(78, 0, 6), 'rightForearm': r(8), 'leftForearm': r(8),
       'rightFoot': r(-50), 'leftFoot': r(-50)}
GF2 = {'hips': {'p': [0, -0.5, 0.3], 'r': [-75, 0, 0]}, 'neck': r(40),
       'rightUpperLeg': r(75, 0, 4), 'leftUpperLeg': r(75, 0, -4), 'rightLowerLeg': r(-90), 'leftLowerLeg': r(-90),
       'rightFoot': r(-40), 'leftFoot': r(-40),
       'rightUpperArm': r(75, 0, -6), 'leftUpperArm': r(75, 0, 6)}
GF3 = {'hips': {'p': [0, -0.45, 0.12], 'r': [-15, 0, 0]}, 'spine': r(-10), 'neck': r(10),
       'rightUpperLeg': r(95, 0, 6), 'rightLowerLeg': r(-80), 'rightFoot': r(0),
       'leftUpperLeg': r(15, 0, -4), 'leftLowerLeg': r(-90), 'leftFoot': r(-40),
       'rightUpperArm': r(40, 0, -10), 'rightForearm': r(40), 'leftUpperArm': r(30, 0, 10), 'leftForearm': r(30)}
fall('falls.getup-front', 'Get up from stomach', 2.0,
     [(0, LIE_FRONT), (0.5, GF1), (1.0, GF2), (1.5, GF3), (2.0, at(STANCE, p=[0, -0.02, -0.2]))], [0, 0, -0.2],
     'Push up, onto hands and knees, one knee up, stand. Starts where fall-forward ends.',
     ['getup', 'starts-lying-front'], recover=1.8)

GI1 = merge(G1, {'spine': r(-20), 'neck': r(-14), 'rightUpperArm': r(-30, 0, 30), 'rightForearm': r(90)})
GI2 = merge(G1, {'hips': {'p': [0, -0.83, 0], 'r': [45, 0, 0]}, 'neck': r(-20), 'rightUpperArm': r(-30, 0, 30), 'rightForearm': r(90)})
GI3 = merge(G2, {'spine': r(-20), 'neck': r(36), 'rightUpperArm': r(20, 0, -20), 'rightForearm': r(100)})
GI4 = merge(G3, {'spine': r(-18), 'neck': r(22), 'rightUpperArm': r(20, 0, -24), 'rightForearm': r(108)})
GI5 = merge(at(STANCE, p=[0, -0.04, -0.19]), {'spine': r(-12), 'neck': r(10), 'rightUpperArm': r(22, 0, -28), 'rightForearm': r(110)})
fall('falls.getup-injured', 'Get up slowly, injured', 3.4,
     [(0, LIE_BACK), (0.8, GI1), (1.2, GI2), (1.7, GI1), (2.4, GI3), (2.95, GI4), (3.4, GI5)], [0, 0, -0.19],
     'Struggle to sit up, slump back, try again, rise holding the ribs. Starts where fall-backward ends.',
     ['getup', 'starts-lying-back', 'injured'], recover=3.2)

Q1 = {'hips': {'p': [0, -0.78, 0.1], 'r': [130, 0, 0]}, 'neck': r(-20),
      'rightUpperLeg': r(20, 0, 6), 'leftUpperLeg': r(20, 0, -6), 'rightLowerLeg': r(-60), 'leftLowerLeg': r(-60),
      'rightUpperArm': r(160, 0, -10), 'leftUpperArm': r(160, 0, 10), 'rightForearm': r(130), 'leftForearm': r(130)}
Q2 = {'hips': {'p': [0, -0.3, -0.12], 'r': [28, 0, 0]}, 'spine': r(18), 'chest': r(8), 'neck': r(-14),
      'rightUpperLeg': r(70, 0, 6), 'leftUpperLeg': r(70, 0, -6), 'rightLowerLeg': r(-100), 'leftLowerLeg': r(-100),
      'rightUpperArm': r(150, 0, -10), 'leftUpperArm': r(150, 0, 10), 'rightForearm': r(40), 'leftForearm': r(40)}
Q3 = merge(G2, {'hips': {'p': [0, -0.5, -0.3], 'r': [-30, 0, 0]}, 'rightUpperArm': r(60, 0, -20), 'leftUpperArm': r(60, 0, 20),
                'rightForearm': r(30), 'leftForearm': r(30)})
fall('falls.quick-recovery', 'Quick recovery', 1.1,
     [(0, LIE_BACK), (0.3, Q1), (0.5, Q2), (0.66, Q3), (1.1, at(GUARD, p=[0, -0.03, -0.38]))], [0, 0, -0.38],
     'Kip-up: rock back onto the shoulders and spring straight to the feet, landing in guard. Starts where fall-backward ends.',
     ['getup', 'starts-lying-back', 'fast'], extra_events=[ev(0.42, 'jump'), ev(0.66, 'land', zone='feet')], recover=0.9)

KO = merge(LIE_BACK, {'neck': r(4, 30, 0), 'head': r(0, 20, 0),
                      'rightUpperArm': r(0, -10, 80), 'leftUpperArm': r(0, 10, -76), 'rightForearm': r(24), 'leftForearm': r(10),
                      'rightUpperLeg': r(0, 0, 12), 'leftUpperLeg': r(8, 0, -14), 'leftLowerLeg': r(-24), 'rightLowerLeg': r(-6)})
clip('falls.knockout', 'Knockout idle', 'falls', 4.0, True,
     [(0, KO), (2.0, merge(KO, {'chest': r(2)})), (4.0, KO)],
     desc='Out cold on the back, limbs splayed, head turned, slow breathing. Loop.',
     tags=['fall', 'loop', 'starts-lying-back', 'ends-lying-back', 'knockout'])

# ---------------------------------------------------------------- index
(ROOT / 'tools' / 'batch2' / 'animation-index-b2.json').write_text(json.dumps(INDEX, indent=2) + '\n')
from collections import Counter
print(len(INDEX), 'animations', dict(Counter(a['category'] for a in INDEX)))
