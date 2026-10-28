"""TTW animation authoring library (Python, numpy).

Shared by the phase generators. Provides:
  - forward kinematics for the ttw-humanoid skeleton (same maths as Three.js: Euler XYZ, degrees)
  - analytic two-bone IK for arms and legs (hands on ropes, feet on ropes, turnbuckles, apron)
  - ring reference frames built from the arena geometry (ring-reference.json)
  - a clip writer that turns keyed poses into TTW animation JSON with declared root motion
  - geometry checks: feet versus mat/apron/floor/rope surfaces, limbs versus ropes

Conventions (same as every TTW clip):
  metres, Y up, the wrestler faces -Z; bone rotations are local Euler XYZ in degrees relative to
  the neutral pose; positions are offsets from the bone's rest position.
  The ROOT bone carries world travel. It is always declared as rootMotion.mode = "curve"
  (keys [t, x, y, z, yawDeg] in the wrestler's start frame), so gameplay can own the position.
"""
import json, math, copy, pathlib, re
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
PACK = HERE.parents[1]                       # assets/ttw-wrestlers
SKELETON_PATH = PACK / 'skeleton.json'
if not SKELETON_PATH.exists():                # running from the overlay folder during development
    SKELETON_PATH = pathlib.Path('/home/claude/ttw-pack/assets/ttw-wrestlers/skeleton.json')
SK = json.loads(SKELETON_PATH.read_text())
BONES = {b['name']: b for b in SK['bones']}
ORDER = [b['name'] for b in SK['bones']]
ATT = {a['name']: a for a in SK['attachments']}
RING = json.loads((PACK / 'viewer' / 'ring-reference.json').read_text())
D = math.pi / 180

# ------------------------------------------------------------------ rotations

def Rx(a): c, s = math.cos(a * D), math.sin(a * D); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Ry(a): c, s = math.cos(a * D), math.sin(a * D); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rz(a): c, s = math.cos(a * D), math.sin(a * D); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def E(r): return Rx(r[0]) @ Ry(r[1]) @ Rz(r[2])

def euler(R):
    """rotation matrix -> Three.js Euler XYZ in degrees"""
    m13 = max(-1.0, min(1.0, R[0, 2]))
    y = math.asin(m13)
    if abs(m13) < 0.9999999:
        x = math.atan2(-R[1, 2], R[2, 2]); z = math.atan2(-R[0, 1], R[0, 0])
    else:
        x = math.atan2(R[2, 1], R[1, 1]); z = 0.0
    return [x / D, y / D, z / D]

def unit(v):
    v = np.asarray(v, float); n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v

# ------------------------------------------------------------------ poses

def r(x=0, y=0, z=0): return {'r': [x, y, z]}

def merge(*poses):
    out = {}
    for p in poses:
        for b, ch in p.items():
            if b == 'ik':
                out.setdefault('ik', {}).update(copy.deepcopy(ch)); continue
            out.setdefault(b, {}).update(copy.deepcopy(ch))
    return out

def swap(n):
    if n.startswith('left'): return 'right' + n[4:]
    if n.startswith('right'): return 'left' + n[5:]
    return n

def mirror(pose):
    """left/right mirror of a pose (bones and IK targets). Positions negate X, rotations negate Y and Z."""
    out = {}
    for b, ch in pose.items():
        if b == 'ik':
            out['ik'] = {}
            for k, v in ch.items():
                v = dict(v); v['at'] = [-v['at'][0], v['at'][1], v['at'][2]]
                if 'pole' in v: v['pole'] = [-v['pole'][0], v['pole'][1], v['pole'][2]]
                out['ik'][swap(k)] = v
            continue
        nb = swap(b); out[nb] = {}
        if 'r' in ch: x, y, z = ch['r']; out[nb]['r'] = [x, -y, -z]
        if 'p' in ch: x, y, z = ch['p']; out[nb]['p'] = [-x, y, z]
    return out

def only(pose, bones): return {b: copy.deepcopy(v) for b, v in pose.items() if b in bones}

LEGS = ['leftUpperLeg', 'leftLowerLeg', 'leftFoot', 'rightUpperLeg', 'rightLowerLeg', 'rightFoot']
ARMS = ['leftUpperArm', 'leftForearm', 'leftHand', 'rightUpperArm', 'rightForearm', 'rightHand']

# Library poses (identical values to Batch 1/2 so chained clips line up)
STANCE = {
    'hips': {'p': [0, -0.02, 0]},
    'rightUpperLeg': r(6, 0, 4), 'leftUpperLeg': r(6, 0, -4), 'rightLowerLeg': r(-12), 'leftLowerLeg': r(-12),
    'rightFoot': r(6, 0, -4), 'leftFoot': r(6, 0, 4),
    'rightUpperArm': r(6, 0, -10), 'leftUpperArm': r(6, 0, 10), 'rightForearm': r(14), 'leftForearm': r(14),
}
GUARD = {
    'hips': {'p': [0, -0.03, 0]},
    'rightUpperLeg': r(8, 0, 4), 'leftUpperLeg': r(8, 0, -4), 'rightLowerLeg': r(-16), 'leftLowerLeg': r(-16),
    'rightFoot': r(8, 0, -4), 'leftFoot': r(8, 0, 4), 'spine': r(-4), 'neck': r(4),
    'rightUpperArm': r(50, 0, -22), 'rightForearm': r(118), 'leftUpperArm': r(55, 0, 22), 'leftForearm': r(120),
}
LIE_BACK = {
    'hips': {'p': [0, -0.83, 0], 'r': [90, 0, 0]}, 'neck': r(6), 'head': r(0, 14, 0),
    'rightUpperArm': r(0, -10, 56), 'rightForearm': r(16), 'leftUpperArm': r(0, 10, -56), 'leftForearm': r(16),
    'rightUpperLeg': r(0, 0, 8), 'leftUpperLeg': r(0, 0, -8), 'rightLowerLeg': r(-8), 'leftLowerLeg': r(-8),
    'rightFoot': r(-20, 0, -6), 'leftFoot': r(-20, 0, 6),
}
LIE_FRONT = {
    'hips': {'p': [0, -0.84, 0], 'r': [-90, 0, 0]}, 'neck': r(10, 40, 0), 'head': r(0, 20, 0),
    'rightUpperArm': r(0, 0, 80), 'rightForearm': r(0, 0, 70), 'leftUpperArm': r(0, 0, -80), 'leftForearm': r(0, 0, -70),
    'rightUpperLeg': r(0, 0, 6), 'leftUpperLeg': r(0, 0, -6), 'rightLowerLeg': r(-6), 'leftLowerLeg': r(-6),
    'rightFoot': r(-50), 'leftFoot': r(-50),
}
LEAN = {  # batch 1 rope lean (ropes behind)
    'hips': {'p': [0, -0.03, 0.15], 'r': [14, 0, 0]}, 'spine': r(2), 'chest': r(4), 'neck': r(-10), 'head': r(-4),
    'rightUpperLeg': r(-6, 0, 5), 'leftUpperLeg': r(-6, 0, -5), 'rightLowerLeg': r(-6), 'leftLowerLeg': r(-6),
    'rightFoot': r(-2, 0, -4), 'leftFoot': r(-2, 0, 4),
    'rightUpperArm': r(0, -35, 28), 'rightForearm': r(0, 0, -55), 'leftUpperArm': r(0, 35, -28), 'leftForearm': r(0, 0, 55),
}
STRETCH = {
    'hips': {'p': [0, -0.06, 0.3], 'r': [24, 0, 0]}, 'spine': r(4), 'chest': r(6), 'neck': r(-18), 'head': r(-6),
    'rightUpperLeg': r(-2, 0, 5), 'leftUpperLeg': r(-2, 0, -5), 'rightLowerLeg': r(-14), 'leftLowerLeg': r(-14),
    'rightFoot': r(-6, 0, -4), 'leftFoot': r(-6, 0, 4),
    'rightUpperArm': r(0, -45, 34), 'rightForearm': r(0, 0, -62), 'leftUpperArm': r(0, 45, -34), 'leftForearm': r(0, 0, 62),
}
RC = {
    'hips': {'p': [0, -0.06, 0], 'r': [0, 9, 0]}, 'spine': r(-10, -4, 0), 'chest': r(-2, -9, 0), 'neck': r(8, 4, 0),
    'rightUpperLeg': r(34), 'rightLowerLeg': r(-18), 'rightFoot': r(10), 'leftUpperLeg': r(-26), 'leftLowerLeg': r(-68), 'leftFoot': r(-22),
    'rightUpperArm': r(-34, 0, -8), 'rightForearm': r(80), 'leftUpperArm': r(42, 0, 8), 'leftForearm': r(96),
}
RF = {
    'hips': {'p': [0, 0.03, 0]}, 'spine': r(-10), 'chest': r(-2), 'neck': r(8),
    'rightUpperLeg': r(-14), 'rightLowerLeg': r(-40), 'rightFoot': r(-12), 'leftUpperLeg': r(40), 'leftLowerLeg': r(-105), 'leftFoot': r(0),
    'rightUpperArm': r(4, 0, -8), 'rightForearm': r(88), 'leftUpperArm': r(4, 0, 8), 'leftForearm': r(88),
}
WC = {
    'hips': {'p': [0, -0.035, 0], 'r': [0, 6, 0]}, 'spine': r(-3, -3, 0), 'chest': r(0, -6, 0), 'neck': r(0, 3, 0),
    'rightUpperLeg': r(26), 'rightLowerLeg': r(-6), 'rightFoot': r(8), 'leftUpperLeg': r(-20), 'leftLowerLeg': r(-24), 'leftFoot': r(-14),
    'rightUpperArm': r(-20, 0, -10), 'rightForearm': r(12), 'leftUpperArm': r(22, 0, 10), 'leftForearm': r(26),
}
WP = {
    'hips': {'p': [0, 0.012, 0]}, 'spine': r(-3),
    'rightUpperLeg': r(2), 'rightLowerLeg': r(-6), 'rightFoot': r(4), 'leftUpperLeg': r(12), 'leftLowerLeg': r(-48), 'leftFoot': r(4),
    'rightUpperArm': r(0, 0, -10), 'rightForearm': r(16), 'leftUpperArm': r(2, 0, 10), 'leftForearm': r(18),
}
F3 = {
    'hips': {'p': [0, -0.83, 0], 'r': [92, 0, 0]}, 'neck': r(-26), 'head': r(-6),
    'rightUpperArm': r(0, -10, 72), 'rightForearm': r(10), 'leftUpperArm': r(0, 10, -72), 'leftForearm': r(10),
    'rightUpperLeg': r(30, 0, 6), 'leftUpperLeg': r(30, 0, -6), 'rightLowerLeg': r(-14), 'leftLowerLeg': r(-14),
    'rightFoot': r(-10), 'leftFoot': r(-10),
}
F4 = merge(F3, {'hips': {'p': [0, -0.79, 0], 'r': [86, 0, 0]}, 'neck': r(-18),
                'rightUpperLeg': r(24, 0, 6), 'leftUpperLeg': r(24, 0, -6), 'rightLowerLeg': r(-22), 'leftLowerLeg': r(-22),
                'rightForearm': r(16), 'leftForearm': r(16)})

# ------------------------------------------------------------------ forward kinematics

def fk(pose):
    """world (start-frame) rotation and position of every bone. pose['root'] carries travel."""
    W = {}
    for n in ORDER:
        b = BONES[n]
        R = E(pose.get(n, {}).get('r', [0, 0, 0]))
        t = np.array(b['position'], float) + np.array(pose.get(n, {}).get('p', [0, 0, 0]), float)
        if b['parent']:
            PR, PT = W[b['parent']]
            W[n] = (PR @ R, PT + PR @ t)
        else:
            W[n] = (R, t)
    return W

def att(W, name):
    a = ATT[name]; R, T = W[a['bone']]
    return R @ E(a['rotation']), T + R @ np.array(a['position'], float)

SOLE = {'heel': np.array([0, -0.09, 0.07]), 'toe': np.array([0, -0.09, -0.18]), 'mid': np.array([0, -0.09, -0.05])}

def probe_points(W):
    """named body points used by the geometry checks"""
    P = {}
    for side in ('left', 'right'):
        R, T = W[side + 'Foot']
        for k, v in SOLE.items(): P[f'{side}_{k}'] = T + R @ v
        P[f'{side}_knee'] = W[side + 'LowerLeg'][1]
        P[f'{side}_hand'] = att(W, 'propLeftHand' if side == 'left' else 'propRightHand')[1]
        P[f'{side}_elbow'] = W[side + 'Forearm'][1]
    R, T = W['head']; P['head_top'] = T + R @ np.array([0, 0.24, 0])
    P['hips'] = W['hips'][1]; P['chest'] = W['chest'][1]
    return P

# ------------------------------------------------------------------ two-bone IK

def _rest_dir(child): return unit(BONES[child]['position'])

def _frame_from(a, b):
    e1 = unit(a); e2 = unit(b - np.dot(b, e1) * e1); return np.column_stack([e1, e2, np.cross(e1, e2)])

def two_bone(W, upper, lower, end, target, pole, bend_sign, pose):
    """Solve upper/lower bone local rotations so the `end` joint reaches `target` (start-frame coords).
    The lower bone bends about its local X only (bend_sign: -1 knees, +1 elbows). Writes into pose."""
    parent = BONES[upper]['parent']
    RP, TP = W[parent]
    O = TP + RP @ np.array(BONES[upper]['position'], float)          # joint origin
    L1 = np.linalg.norm(BONES[lower]['position']); L2 = np.linalg.norm(BONES[end]['position'])
    d1 = _rest_dir(lower); d2 = _rest_dir(end)                      # rest directions in their own frames
    T = np.asarray(target, float)
    v = T - O; Dist = np.linalg.norm(v)
    # never fold a joint past 150 degrees (elbows/knees): targets closer than that are reached as far as possible
    d1 = _rest_dir(lower); d2 = _rest_dir(end)
    _dx, _dy = d2[0], math.hypot(d2[1], d2[2])
    want_max = math.acos(max(-1, min(1, _dx * _dx + _dy * _dy * math.cos(math.radians(150)))))
    dmin = math.sqrt(max(1e-9, L1 * L1 + L2 * L2 + 2 * L1 * L2 * math.cos(want_max)))
    Dist = min(max(Dist, dmin), L1 + L2 - 1e-4)
    a = unit(v)
    # elbow/knee position in the plane of the pole
    cos_alpha = (L1 * L1 + Dist * Dist - L2 * L2) / (2 * L1 * Dist)
    alpha = math.acos(max(-1, min(1, cos_alpha)))
    p = np.asarray(pole, float); b = unit(p - np.dot(p, a) * a)
    u1 = a * math.cos(alpha) + b * math.sin(alpha)
    joint = O + L1 * u1
    u2 = unit((O + a * Dist) - joint)
    # local bend angle that gives the same angle between u1 and u2 (lower bone rotates about local X)
    want = math.acos(max(-1, min(1, np.dot(u1, u2))))                # angle between the two bone directions
    dx, dy = d2[0], math.hypot(d2[1], d2[2])
    # angle between d2 and Rx(t) d2 satisfies cos = dx^2 + dy^2 cos t (d2 has no z component)
    c = (math.cos(want) - dx * dx) / max(dy * dy, 1e-9)
    t = math.acos(max(-1, min(1, c))) * bend_sign
    b_local = E([t / D, 0, 0]) @ d2
    # upper bone world rotation mapping (d1, R_lower_rest*b_local) -> (u1, u2)
    a_loc = d1
    R_world = _frame_from(u1, u2) @ _frame_from(a_loc, b_local).T
    R_local = RP.T @ R_world
    pose[upper] = {'r': [round(v, 2) for v in euler(R_local)]}
    pose[lower] = {'r': [round(t / D, 2), 0, 0]}
    return R_world @ E([t / D, 0, 0])

def solve_ik(pose):
    """Apply pose['ik'] targets: {'leftFoot': {'at': [x,y,z], 'pole': [..], 'flat': yawDeg|None, 'pitch': deg}, 'rightHand': {...}}
    Targets are joint positions (ankle / wrist) in the clip's start frame."""
    pose = copy.deepcopy(pose)
    ik = pose.pop('ik', {})
    for limb in ('leftFoot', 'rightFoot', 'leftHand', 'rightHand'):
        if limb not in ik: continue
        spec = ik[limb]
        W = fk(pose)
        side = 'left' if limb.startswith('left') else 'right'
        if limb.endswith('Foot'):
            R_root = W['hips'][0]
            pole = spec.get('pole')
            if not pole:
                # knee points forward; when the leg itself reaches forward (sitting, kneeling up) the knee points up
                fwd = R_root @ np.array([0.15 if side == 'right' else -0.15, 0, -1.0])
                a = unit(np.asarray(spec['at'], float) - W[side + 'UpperLeg'][1])
                ahead = max(0.0, float(np.dot(a, unit(R_root @ np.array([0, 0, -1.0])))))
                pole = list(fwd + R_root @ np.array([0, 1.0, 0]) * (2.5 * ahead * ahead))
            R_lower = two_bone(W, side + 'UpperLeg', side + 'LowerLeg', side + 'Foot', spec['at'], pole, -1, pose)
            if spec.get('flat', True) is not False:
                yaw = spec.get('yaw')
                if yaw is None:
                    fwd = W['hips'][0] @ np.array([0, 0, -1.0]); yaw = math.degrees(math.atan2(-fwd[0], -fwd[2]))
                want = Ry(yaw) @ Rx(spec.get('pitch', 0)) @ Rz(spec.get('roll', 0))
                pose[side + 'Foot'] = {'r': [round(v, 2) for v in euler(R_lower.T @ want)]}
        else:
            R_chest = W['chest'][0]
            pole = spec.get('pole') or list(R_chest @ np.array([0.6 if side == 'right' else -0.6, -0.4, 0.7]))
            two_bone(W, side + 'UpperArm', side + 'Forearm', side + 'Hand', spec['at'], pole, 1, pose)
    return pose

# ------------------------------------------------------------------ ring frames

MAT = RING['matHeight']; FLOOR = RING['floorHeight']; DROP = FLOOR - MAT          # -1.16
ROPES = [h - MAT for h in RING['ropeHeights']]                                     # 0.45, 0.85, 1.25 above the mat
APRON = RING['apronEdge'] - RING['ropeLine']                                       # 0.6
ROPE_R = RING['ropeRadius']

class Frame:
    """A ring reference frame (rope side or corner) in mat-level coordinates, plus a start placement."""
    def __init__(self, kind, start):
        self.kind, self.start = kind, start      # start: [x, y, z, yawDeg] in frame coords

    def to_local(self, p):
        x0, y0, z0, yaw0 = self.start
        return Ry(-yaw0) @ (np.asarray(p, float) - np.array([x0, y0, z0]))

    def to_frame(self, p):
        x0, y0, z0, yaw0 = self.start
        return Ry(yaw0) @ np.asarray(p, float) + np.array([x0, y0, z0])

    def surface(self, x, z):
        """support height under (x, z) in frame coords"""
        w = 0.05   # tolerance: touching the apron skirt is fine, going under it is not
        if self.kind == 'rope':      # rope line along X at z=0, ring is z > 0
            return 0.0 if z > -APRON + w else DROP
        if self.kind == 'corner':    # post at the origin, ropes along +X and +Z, ring is x>0 and z>0
            return 0.0 if (x > -APRON + w and z > -APRON + w) else DROP
        return 0.0

    def ropes(self):
        """rope segments [(a, b, radius)] in frame coords"""
        segs = []
        for h in ROPES:
            if self.kind == 'rope':
                segs.append((np.array([-3.5, h, 0.0]), np.array([3.5, h, 0.0])))
            elif self.kind == 'corner':
                segs.append((np.array([0.0, h, 0.0]), np.array([7.0, h, 0.0])))
                segs.append((np.array([0.0, h, 0.0]), np.array([0.0, h, 7.0])))
        return segs

# Standard placements (frame coords of the wrestler's start: x, y, z, yaw)
def inside_facing_ropes(d=0.55): return Frame('rope', [0, 0, d, 0])
def back_to_ropes(d=0.42): return Frame('rope', [0, 0, d, 180])
def apron_facing_ring(d=0.3): return Frame('rope', [0, 0, -d, 180])
def floor_facing_ring(e=0.35): return Frame('rope', [0, DROP, -(APRON + e), 180])
def facing_corner(d=0.75): return Frame('corner', [d * 0.7071, 0, d * 0.7071, 45])
PERCH = [0.19, ROPES[2] + ROPE_R, 0.19, -135]                                         # standing on the top turnbuckle, facing the ring
def perched(): return Frame('corner', PERCH)

PLACEMENTS = {
    'inside-facing-ropes': 'inside the ring, facing the ropes',
    'inside-back-to-ropes': 'inside the ring, back to the ropes (ropes behind, +Z)',
    'apron-facing-ring': 'on the apron outside the ropes, facing the ring',
    'floor-facing-ring': 'on the arena floor at ringside, facing the ring',
    'inside-facing-corner': 'inside the ring, facing a corner post along the diagonal',
    'perched': 'standing on the top turnbuckle, facing the ring',
    'corner-climb': 'on the turnbuckle ropes, facing the corner',
    'apron-facing-out': 'on the apron outside the ropes, facing away from the ring',
    'floor-facing-out': 'on the arena floor at ringside, facing away from the ring',
    'center': 'in the open ring, away from the ropes',
    'running-to-ropes': 'running at the ropes from about 2 m inside the ring',
    'rope-draped': 'folded over the top rope from inside, head and arms outside',
    'anywhere': 'no ring reference needed',
}
def center(x=0.0, z=0.0, yaw=0.0): return Frame('mat', [x, 0, z, yaw])

# ------------------------------------------------------------------ clip writer

def _catmull(keys, t):
    if len(keys) == 1 or t <= keys[0][0]: return list(keys[0][1:])
    if t >= keys[-1][0]: return list(keys[-1][1:])
    i = 0
    while i < len(keys) - 2 and t > keys[i + 1][0]: i += 1
    k1, k2 = keys[i], keys[i + 1]
    u = (t - k1[0]) / ((k2[0] - k1[0]) or 1)
    k0 = keys[i - 1] if i > 0 else k1
    k3 = keys[i + 2] if i + 2 < len(keys) else k2
    out = []
    for c in range(1, len(k1)):
        p0, p1, p2, p3 = k0[c], k1[c], k2[c], k3[c]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    return out

def dump(obj):
    s = json.dumps(obj, indent=2)
    s = re.sub(r'\[\s+(-?[\d.e-]+(?:,\s+-?[\d.e-]+)*)\s+\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', s)
    s = re.sub(r'\[\s+("[^"\n]*"(?:,\s+"[^"\n]*")*)\s+\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', s)
    return s + '\n'

def rp(v): return [round(float(x), 4) for x in v]

# ------------------------------------------------------------------ contact repair
# Interpolating rotations between keys can swing a hand or foot through the mat, apron or floor even when every
# authored key is clean. repair_contacts samples the written clip, finds the worst hand/foot penetration, solves IK
# for that limb lifted clear (keeping the foot's world orientation) and inserts the result as an extra key on that
# limb's tracks only. Repeats until clean or out of budget. Torso/head contacts are reported, never "repaired".

_LIMB = {'toe': 'leg', 'heel': 'leg', 'mid': 'leg', 'knee': 'leg', 'hand': 'arm', 'elbow': 'arm'}

def _unwrap_to(vals, ref):
    out = []
    for v, r_ in zip(vals, ref):
        while v - r_ > 180: v -= 360
        while v - r_ < -180: v += 360
        out.append(v)
    return out

def _insert_key(track, t, vals, n_ref_times):
    keys = track.setdefault('rotation', [[tt, 0, 0, 0] for tt in n_ref_times])
    for k in keys:
        if abs(k[0] - t) < 2e-3:
            k[1:] = [round(v, 2) for v in vals]; return
    keys.append([round(t, 4)] + [round(v, 2) for v in vals]); keys.sort(key=lambda k: k[0])

def repair_contacts(d, frame, budget=48, fps=30):
    fixes = 0
    times = sorted({k[0] for tr in d['tracks'].values() for k in tr.get('rotation', [])})
    tried = set()
    for _ in range(budget):
        n = int(d['duration'] * fps) + 1
        worst = None
        for i in range(n):
            t = min(d['duration'], i / fps)
            if d.get('loop') and (t < 0.05 or t > d['duration'] - 0.05): continue
            W = fk(sample_pose(d, t)); P = probe_points(W)
            for name, pnt in P.items():
                side, _, part = name.partition('_')
                if part not in _LIMB: continue
                fp = frame.to_frame(pnt)
                surf = frame.surface(fp[0], fp[2])
                ropes = frame.ropes()
                if any(_seg_dist(fp, a, b) < 0.06 and fp[1] >= a[1] - 0.02 for a, b in ropes): continue
                allow = 0.03 if part in ('toe', 'heel', 'mid') else 0.0
                pen = surf - fp[1] - allow
                if pen > 0.02 and pen < 0.45 and (worst is None or pen > worst[0]) and (round(t, 3), name) not in tried:
                    worst = (pen, t, side, part)
        if worst is None: break
        pen, t, side, part = worst
        tried.add((round(t, 3), side + '_' + part))
        # snap to a nearby existing key time
        near = [k for k in times if abs(k - t) < 0.034]
        if near: t = near[0]
        t = round(t, 4)
        pose = sample_pose(d, t)
        W = fk(pose)
        lift = np.array([0, pen + 0.015 + (0.03 if part in ('toe', 'heel', 'mid') else 0), 0])
        new = copy.deepcopy(pose)
        if _LIMB[part] == 'leg':
            chain = [side + 'UpperLeg', side + 'LowerLeg', side + 'Foot']
            R_foot = W[side + 'Foot'][0]
            new['ik'] = {side + 'Foot': {'at': list(W[side + 'Foot'][1] + lift), 'flat': False}}
            if part == 'knee':
                sx = 1.0 if side == 'right' else -1.0
                new['ik'][side + 'Foot']['pole'] = list(W['hips'][0] @ np.array([0.15 * sx, 1.0, -0.6]))
            new = solve_ik(new)
            W2 = fk(new)
            new[side + 'Foot'] = {'r': euler(W2[side + 'LowerLeg'][0].T @ R_foot)}
        else:
            chain = [side + 'UpperArm', side + 'Forearm']
            new['ik'] = {side + 'Hand': {'at': list(W[side + 'Hand'][1] + lift)}}
            if part == 'elbow':
                sx = 1.0 if side == 'right' else -1.0
                new['ik'][side + 'Hand'] = {'at': list(W[side + 'Hand'][1] + lift * 0.5), 'pole': list(W['chest'][0] @ np.array([0.8 * sx, 0.9, 0.2]))}
            new = solve_ik(new)
        ok = True; vals = {}
        for b in chain:
            ref = pose.get(b, {}).get('r', [0, 0, 0])
            v = _unwrap_to(new.get(b, {}).get('r', [0, 0, 0]), ref)
            if max(abs(a - b_) for a, b_ in zip(v, ref)) > 100: ok = False
            vals[b] = v
        if not ok: continue
        for b in chain:
            _insert_key(d['tracks'].setdefault(b, {}), t, vals[b], times)
        if all(abs(t - k) > 2e-3 for k in times): times.append(t); times.sort()
        fixes += 1
    return fixes

# ------------------------------------------------------------------ rope interaction (ropes give way)
# Real ropes are pushed, parted and pulled. Instead of pretending a body never overlaps a rope, every library clip
# records how far each rope has to give way, per frame, so the arena (or the lab) can bend that rope around the body.

_CAPS = [('hips', 'neck', 0.15), ('neck', 'head', 0.1)] + [
    (s + a, s + b, r_) for s in ('left', 'right') for a, b, r_ in
    (('UpperArm', 'Forearm', 0.065), ('Forearm', 'Hand', 0.055), ('UpperLeg', 'LowerLeg', 0.095), ('LowerLeg', 'Foot', 0.07))]
LEVELS = ['bottom', 'middle', 'top']

def _closest_seg_seg(p1, q1, p2, q2):
    d1 = q1 - p1; d2 = q2 - p2; r_ = p1 - p2
    a = d1 @ d1; e = d2 @ d2; f = d2 @ r_
    c = d1 @ r_; b = d1 @ d2; den = a * e - b * b
    s_ = min(1.0, max(0.0, (b * f - c * e) / den)) if den > 1e-12 else 0.0
    t_ = (b * s_ + f) / e
    if t_ < 0: t_ = 0.0; s_ = min(1.0, max(0.0, -c / a))
    elif t_ > 1: t_ = 1.0; s_ = min(1.0, max(0.0, (b - c) / a))
    return p1 + d1 * s_, p2 + d2 * t_

def rope_interaction(d, frame, fps=30):
    ropes = frame.ropes()
    names = []
    for i, (a, b) in enumerate(ropes):
        axis = 'x' if abs(b[0] - a[0]) > 0 else 'z'
        names.append((LEVELS[ROPES.index(min(ROPES, key=lambda h: abs(h - a[1])))], axis))
    tracks = [[] for _ in ropes]
    n = int(d['duration'] * fps) + 1
    for i in range(n):
        t = min(d['duration'], i / fps)
        W = fk(sample_pose(d, t))
        for ri, (ra, rb) in enumerate(ropes):
            best = None
            for j0, j1, rad in _CAPS:
                A_ = frame.to_frame(W[j0][1]); B_ = frame.to_frame(W[j1][1])
                pb, pr = _closest_seg_seg(A_, B_, ra, rb)
                v = pr - pb; dist = np.linalg.norm(v)
                push = rad + ROPE_R - dist
                if push > 0.005 and (best is None or push > best[0]):
                    dirn = v / dist if dist > 1e-6 else np.array([0, 1.0, 0])
                    along = rb - ra; along = along / np.linalg.norm(along)
                    dirn = dirn - along * (dirn @ along); dirn = dirn / max(1e-6, np.linalg.norm(dirn))
                    s_ = float(pr @ along)          # along the rope, from the frame origin
                    best = (push, s_, dirn * push)
            if best: tracks[ri].append([round(t, 3), round(best[1], 3)] + [round(float(x), 3) for x in best[2]])
    out = []
    for (level, axis), keys in zip(names, tracks):
        if not keys: continue
        mx = max(math.sqrt(k[2] ** 2 + k[3] ** 2 + k[4] ** 2) for k in keys)
        out.append({'rope': level, 'axis': axis, 'maxDisplacement': round(mx, 3), 'keys': keys})
    return out

class Library:
    def __init__(self, out_dir, batch, index_path):
        self.out = pathlib.Path(out_dir); self.batch = batch; self.index_path = pathlib.Path(index_path)
        self.index = []; self.reports = {}; self.defs = {}

    def clip(self, cid, name, duration, keys, frame, *, loop=False, events=(), desc='', tags=(), start_state='standing',
             end_state='standing', start_loc='ring', end_loc='ring', placement='anywhere', end_placement=None,
             phases=(), interrupt=None, gameplay=None, check=True):
        """keys: [(t, pose)] where pose may include 'root': {'p': frame coords [x,y,z], 'yaw': deg (frame)} and 'ik'.
        Root positions are authored in the ring frame and converted to the wrestler's start frame."""
        category = cid.split('.', 1)[0]
        solved = []
        for t, pose in keys:
            pose = copy.deepcopy(pose)
            root = pose.pop('root', None)
            if root is None:
                root = {'p': list(frame.start[:3]), 'yaw': frame.start[3]}
            lp = frame.to_local(root['p'])
            lyaw = root.get('yaw', frame.start[3]) - frame.start[3]
            pose['root'] = {'p': rp(lp), 'r': [0, round(lyaw, 3), 0]}
            # IK targets are authored in frame coords too
            if 'ik' in pose:
                for k, v in pose['ik'].items():
                    v['at'] = list(frame.to_local(v['at']))
                    if 'pole' in v: v['pole'] = list(Ry(-frame.start[3]) @ np.asarray(v['pole'], float))
                    if v.get('yaw') is not None: v['yaw'] = v['yaw'] - frame.start[3]
            solved.append((t, solve_ik(pose)))
        bones = sorted({b for _, p in solved for b in p}, key=lambda b: ORDER.index(b))
        tracks = {}
        for b in bones:
            rot = [[t] + [round(v, 2) for v in p.get(b, {}).get('r', [0, 0, 0])] for t, p in solved]
            tr = {}
            if any(any(abs(v) > 1e-9 for v in k[1:]) for k in rot) or b == 'root': tr['rotation'] = rot
            if any('p' in p.get(b, {}) for _, p in solved):
                tr['position'] = [[t] + [round(v, 4) for v in p.get(b, {}).get('p', [0, 0, 0])] for t, p in solved]
            if tr: tracks[b] = tr
        curve = [[t] + p['root']['p'] + [p['root']['r'][1]] for t, p in solved]
        moved = any(abs(c[1]) + abs(c[2]) + abs(c[3]) + abs(c[4]) > 1e-6 for c in curve)
        evs = sorted([dict(e) for e in events] + [{'time': duration, 'name': 'animation_complete'}], key=lambda e: e['time'])
        root_motion = {'mode': 'none'}
        if moved:
            root_motion = {
                'mode': 'curve', 'space': 'start-frame', 'policy': 'gameplay',
                'curve': curve, 'endOffset': curve[-1][1:4], 'endYaw': curve[-1][4],
                'heightChange': round(curve[-1][2], 4),
                'note': 'Travel of the wrestler in its own start frame (x right, y up, -z forward). Gameplay moves the '
                        'authoritative position along this curve; the root bone shows the same motion only in "visual" policy.',
            }
        else:
            tracks.pop('root', None)
        d = {
            'id': cid, 'name': name, 'category': category, 'description': desc,
            'skeleton': SK['id'], 'skeletonVersion': 1, 'libraryVersion': 3, 'batch': self.batch,
            'duration': duration, 'loop': loop, 'clampWhenFinished': not loop, 'interpolation': 'smooth', 'sampleRate': 30,
            'rotationUnits': 'degrees', 'positionMode': 'offsetFromRest',
            'rootMotion': root_motion,
            'startState': start_state, 'endState': end_state, 'startLocation': start_loc, 'endLocation': end_loc,
            'placement': {'start': placement, 'end': end_placement or placement, 'frame': frame.kind, 'frameStart': frame.start,
                          'note': PLACEMENTS.get(placement, '')},
            'phases': [{'name': n, 'start': a, 'end': b} for n, a, b in phases],
            'interrupt': interrupt or {'windows': [[0, round(duration * 0.15, 3)]] if not loop else [[0, duration]],
                                       'note': 'times when gameplay may cut to another clip without a visible snap'},
            'events': evs, 'tags': list(tags) + [f'starts-{start_state}', f'ends-{end_state}'],
            'tracks': tracks,
        }
        if gameplay: d['gameplay'] = gameplay
        fixes = repair_contacts(d, frame) if check else 0
        if check and frame.kind in ('rope', 'corner'):
            ri = rope_interaction(d, frame)
            if ri:
                d['ropeInteraction'] = {
                    'frame': frame.kind, 'ropes': ri,
                    'note': 'How far each rope gives way: keys [t, s, dx, dy, dz] in placement-frame metres; s is the contact point '
                            'along the rope from the frame origin, (dx, dy, dz) the rope displacement there. Bend the rope with a smooth '
                            'falloff around s (ttw-anim-runtime.js ropeDisplacement). Optional: games with static ropes can ignore it.'}
        path = self.out / category / f"{cid.split('.', 1)[1]}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(dump(d))
        rel = f"animations/{category}/{path.name}"
        self.index.append({'id': cid, 'name': name, 'category': category, 'file': rel, 'duration': duration, 'loop': loop,
                           'rootMotion': root_motion['mode'], 'events': [e['name'] for e in evs], 'tags': d['tags'],
                           'startState': start_state, 'endState': end_state, 'startLocation': start_loc, 'endLocation': end_loc,
                           'placement': placement, 'batch': self.batch})
        self.defs[cid] = d
        if check: self.reports[cid] = dict(check_clip(d, frame), contactFixes=fixes, ropePush=max([r_['maxDisplacement'] for r_ in d.get('ropeInteraction', {}).get('ropes', [])] or [0]))
        return d

    def save_index(self):
        self.index_path.write_text(json.dumps(self.index, indent=2) + '\n')

# ------------------------------------------------------------------ sampling a written clip + geometry checks

def sample_pose(d, t):
    pose = {}
    for b, tr in d['tracks'].items():
        e = {}
        if 'rotation' in tr: e['r'] = _catmull(tr['rotation'], t)
        if 'position' in tr: e['p'] = _catmull(tr['position'], t)
        pose[b] = e
    return pose

def _seg_dist(p, a, b):
    ab = b - a; t = max(0, min(1, np.dot(p - a, ab) / np.dot(ab, ab)))
    return np.linalg.norm(p - (a + t * ab))

def _segseg(p1, q1, p2, q2):
    # closest distance between two segments (sampled; precise enough for checks)
    best = 9.0
    for s in np.linspace(0, 1, 7):
        best = min(best, _seg_dist(p1 + s * (q1 - p1), p2, q2))
    return best

LIMBS = [('UpperLeg', 'LowerLeg', 0.11), ('LowerLeg', 'Foot', 0.085), ('UpperArm', 'Forearm', 0.085), ('Forearm', 'Hand', 0.07)]

def check_clip(d, frame, fps=30):
    """feet/knees/hands/head versus support surfaces and ropes, in ring frame coords"""
    worst_floor, worst_t, worst_pt = 0.0, 0.0, ''
    rope_hits = 0; worst_rope = 0.0; rope_info = ''
    n = int(d['duration'] * fps) + 1
    ropes = frame.ropes()
    for i in range(n):
        t = min(d['duration'], i / fps)
        W = fk(sample_pose(d, t))
        P = probe_points(W)
        for name, p in P.items():
            fp = frame.to_frame(p)
            surf = frame.surface(fp[0], fp[2])
            # standing on a rope counts as support
            on_rope = any(_seg_dist(fp, a, b) < 0.06 and fp[1] >= a[1] - 0.02 for a, b in ropes)
            if on_rope: continue
            pen = surf - fp[1]
            allow = 0.03 if ('heel' in name or 'toe' in name or 'mid' in name) else 0.0
            if pen > allow and pen - allow > worst_floor:
                worst_floor, worst_t, worst_pt = pen - allow, t, name
        # limbs through ropes
        for side in ('left', 'right'):
            for a_, b_, rad in LIMBS:
                A = frame.to_frame(W[side + a_][1]); B = frame.to_frame(W[side + b_][1])
                for ra, rb in ropes:
                    dd = _segseg(A, B, ra, rb)
                    if dd < rad * 0.6:
                        rope_hits += 1
                        if rad - dd > worst_rope: worst_rope, rope_info = rad - dd, f'{side}{a_}@{t:.2f} rope {ra[1]:.2f}'
        A = frame.to_frame(W['hips'][1]); B = frame.to_frame(W['neck'][1])
        for ra, rb in ropes:
            dd = _segseg(A, B, ra, rb)
            if dd < 0.1:
                rope_hits += 1
                if 0.16 - dd > worst_rope: worst_rope, rope_info = 0.16 - dd, f'torso@{t:.2f} rope {ra[1]:.2f}'
    return {'floorPenetration': round(worst_floor, 3), 'at': round(worst_t, 2), 'point': worst_pt,
            'ropeOverlapFrames': rope_hits, 'ropeDepth': round(worst_rope, 3), 'ropeWorst': rope_info}
