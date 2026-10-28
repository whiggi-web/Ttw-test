"""Shared helpers for the Phase 2 ring-interaction generators."""
import sys, pathlib, math, copy
sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'lib'))
from ttwanim import *          # noqa: F401,F403
import ttwanim as A
import numpy as np

ROPE_TOP, ROPE_MID, ROPE_BOT = A.ROPES[2], A.ROPES[1], A.ROPES[0]
ANKLE = 0.095                  # ankle joint height above the sole
RR = A.ROPE_R

def rel(root, yaw, lx=0.0, ly=0.0, lz=0.0):
    """frame coords of a point given relative to a body (root position + yaw): x right, y up, -z forward"""
    return list(np.array(root, float) + A.Ry(yaw) @ np.array([lx, ly, lz], float))

def body(hy=-0.02, hx=0.0, hz=0.0, lean=0.0, turn=0.0, roll=0.0, spine=(0, 0, 0), chest=(0, 0, 0), neck=(0, 0, 0), head=(0, 0, 0)):
    """hips offset/rotation and torso. lean: +back / -forward (deg); turn: +left; roll: +lean to the left"""
    p = {'hips': {'p': [hx, hy, hz], 'r': [lean, turn, roll]}}
    if any(spine): p['spine'] = {'r': list(spine)}
    if any(chest): p['chest'] = {'r': list(chest)}
    if any(neck): p['neck'] = {'r': list(neck)}
    if any(head): p['head'] = {'r': list(head)}
    return p

def K(t, root, yaw, *parts, feet=None, hands=None, lfoot=None, rfoot=None, lhand=None, rhand=None, poles=None):
    """one key: root (frame coords), yaw (frame deg), pose parts merged in order, optional IK targets (frame coords)"""
    pose = A.merge(*parts) if parts else {}
    pose['root'] = {'p': list(root), 'yaw': yaw}
    ik = {}
    if feet: lfoot, rfoot = feet
    if hands: lhand, rhand = hands
    for name, tgt in (('leftFoot', lfoot), ('rightFoot', rfoot), ('leftHand', lhand), ('rightHand', rhand)):
        if tgt is None: continue
        spec = dict(tgt) if isinstance(tgt, dict) else {'at': list(tgt)}
        if poles and name in poles: spec['pole'] = poles[name]
        ik[name] = spec
    if ik: pose['ik'] = ik
    return (t, pose)

def plant(x, z, y=0.0, yaw=None, pitch=0.0):
    """ankle target for a foot standing flat on a surface at height y (frame coords)"""
    d = {'at': [x, y + ANKLE, z], 'pitch': pitch}
    if yaw is not None: d['yaw'] = yaw
    return d

def air(x, y, z, pitch=0.0, yaw=None, flat=True):
    d = {'at': [x, y, z], 'pitch': pitch, 'flat': flat}
    if yaw is not None: d['yaw'] = yaw
    return d

def on_rope(x, h, z, yaw=None):
    """ankle target for a foot standing on a rope of height h (above the mat)"""
    d = {'at': [x, h + RR + ANKLE, z]}
    if yaw is not None: d['yaw'] = yaw
    return d

def grip(x, h, z, up=0.055):
    """wrist target for a hand holding a rope at (x, h, z)"""
    return [x, h + up, z]

def stand_feet(root, yaw, width=0.12, y=None, fwd=0.0):
    yy = root[1] if y is None else y
    L = rel([root[0], yy, root[2]], yaw, -width, 0, fwd)
    Rr = rel([root[0], yy, root[2]], yaw, width, 0, -fwd)
    return plant(L[0], L[2], yy, yaw=yaw), plant(Rr[0], Rr[2], yy, yaw=yaw)

ARMS_DOWN = {'rightUpperArm': r(6, 0, -10), 'leftUpperArm': r(6, 0, 10), 'rightForearm': r(14), 'leftForearm': r(14)}
ARMS_OUT = {'rightUpperArm': r(10, 0, 55), 'leftUpperArm': r(10, 0, -55), 'rightForearm': r(20), 'leftForearm': r(20)}
ARMS_BALANCE = {'rightUpperArm': r(20, 0, 70), 'leftUpperArm': r(20, 0, -70), 'rightForearm': r(10), 'leftForearm': r(10)}
ARMS_FWD = {'rightUpperArm': r(80, 0, -8), 'leftUpperArm': r(80, 0, 8), 'rightForearm': r(20), 'leftForearm': r(20)}
ARMS_GUARD = A.only(A.GUARD, A.ARMS)
ARMS_UP = {'rightUpperArm': r(170, 0, -10), 'leftUpperArm': r(170, 0, 10), 'rightForearm': r(10), 'leftForearm': r(10)}
HUNCH = {'spine': r(-14, 0, 4), 'chest': r(-6), 'neck': r(12), 'rightUpperArm': r(22, 0, -30), 'rightForearm': r(112)}
ARMS_SUPERMAN = {'rightUpperArm': r(170, 0, -12), 'leftUpperArm': r(170, 0, 12), 'rightForearm': r(6), 'leftForearm': r(6)}

def stance_at(t, root, yaw, *extra, hy=-0.02):
    return K(t, root, yaw, A.STANCE, body(hy=hy), *extra, feet=stand_feet(root, yaw))

def ev(t, name, **kw):
    e = {'time': round(t, 3), 'name': name}; e.update(kw); return e

def steps(*times): return [ev(t, 'footstep') for t in times]

def support_limbs(pose, root, yaw, surface=0.0, hands=True, feet=True, toe_pitch=-60, hand_fwd=0.06, skip=()):
    """IK targets (frame coords) that put the hands on the surface under the shoulders and the toes on it
    (heels up), for push-up / hands-and-knees / getting-up poses. pose: a body pose dict without root."""
    W = A.fk(copy.deepcopy(pose))
    out = {}
    for side in ('left', 'right'):
        if hands and side + 'Hand' not in skip:
            sh = W[side + 'UpperArm'][1]
            out[side + 'Hand'] = list(np.array(rel(root, yaw, sh[0], 0, sh[2] - hand_fwd)) + np.array([0, surface + 0.035 - root[1], 0]))
        if feet and side + 'Foot' not in skip:
            an = W[side + 'Foot'][1]
            p = rel(root, yaw, an[0], 0, an[2])
            out[side + 'Foot'] = {'at': [p[0], surface + 0.155, p[2]], 'pitch': toe_pitch, 'yaw': yaw}
    return out

def on_support(t, root, yaw, *parts, surface=0.0, **kw):
    """K() with hands/feet placed by support_limbs"""
    pose = A.merge(*parts)
    s = support_limbs(pose, root, yaw, surface, **kw)
    return K(t, root, yaw, pose, lhand=s.get('leftHand'), rhand=s.get('rightHand'), lfoot=s.get('leftFoot'), rfoot=s.get('rightFoot'))

# ------------------------------------------------------------------ shared library clips (sampled, so chained clips line up)
def _load_clip(rel_path):
    for base in (A.PACK, pathlib.Path('/home/claude/ttw-pack/assets/ttw-wrestlers')):
        p = base / rel_path
        if p.exists():
            import json
            return json.loads(p.read_text())
    raise FileNotFoundError(rel_path)

RUN_DEF = _load_clip('animations/movement/run.json')   # 0.64 s cycle, 4 m/s, two strides
RUN_SPEED, RUN_CYCLE = 4.0, 0.64

def run_pose(t):
    """pose of the library run cycle at cycle time t (no root)"""
    p = A.sample_pose(RUN_DEF, t % RUN_CYCLE)
    p.pop('root', None)
    return p

def body_point(L, cid, frame, t, bone, local=(0, 0, 0)):
    """frame coords of a point on another clip's body (bone origin + local offset) at time t.
    `frame` is the frame that clip was authored in (any frame sharing the same ring reference works)."""
    d = L.defs[cid]
    W = A.fk(A.sample_pose(d, t))
    R, T = W[bone]
    clip_frame = A.Frame(d['placement']['frame'], d['placement']['frameStart'])
    return list(clip_frame.to_frame(T + R @ np.asarray(local, float)))

def mirror_keys(keys):
    """left/right mirror of a list of K() keys (root x and yaw, bones, IK targets)"""
    out = []
    for t, pose in keys:
        pose = copy.deepcopy(pose)
        root = pose.pop('root', None)
        ik = pose.get('ik')
        m = A.mirror(pose)
        if ik:
            for k, v in m['ik'].items():
                if v.get('yaw') is not None: v['yaw'] = -v['yaw']
        if root is not None:
            m['root'] = {'p': [-root['p'][0], root['p'][1], root['p'][2]], 'yaw': -root.get('yaw', 0)}
        out.append((t, m))
    return out

def mirror_events(evs):
    out = []
    for e in evs:
        e = dict(e)
        for k in ('attachment', 'foot', 'side'):
            if isinstance(e.get(k), str):
                e[k] = e[k].replace('Right', '#').replace('Left', 'Right').replace('#', 'Left').replace('right', '#').replace('left', 'right').replace('#', 'left')
        out.append(e)
    return out
