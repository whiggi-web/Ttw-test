"""Helpers for throws: drive a thrown body by WORLD orientation (where the head and the chest point) and hips position,
convert to the clip's local hips Euler with continuity, and finish exactly in the library lying poses."""
import math
from common import *

HIPS_REST = 1.0           # hips height above the root at rest

def R_from(head, chest):
    """world rotation whose +y (head) and -z (chest) point the given ways"""
    y = A.unit(head); c = np.asarray(chest, float)
    z = -A.unit(c - y * np.dot(c, y))
    x = np.cross(y, z)
    return np.column_stack([x, y, z])

def _alt(e):
    return [e[0] + 180, 180 - e[1], e[2] + 180]

def _near(v, ref):
    while v - ref > 180: v -= 360
    while v - ref < -180: v += 360
    return v

def cont_euler(R, prev):
    e = A.euler(R)
    best = None
    for cand in (e, _alt(e)):
        c = [_near(cand[i], prev[i]) for i in range(3)] if prev else cand
        score = max(abs(c[i] - prev[i]) for i in range(3)) if prev else abs(c[1])
        if best is None or score < best[0]: best = (score, c)
    return [round(v, 2) for v in best[1]]

class Body:
    """keys for a body moved by world orientation. Call .key(t, hips_pos, head, chest, *parts, yaw=..).
    Keeps the hips Euler angles and the root yaw continuous from key to key, so interpolation never takes the long way round."""
    def __init__(self, yaw):
        self.prev = None; self.yaw = yaw; self.last_yaw = yaw
    def _yaw(self, yaw):
        yaw = self.yaw if yaw is None else yaw
        yaw = _near(yaw, self.last_yaw); self.last_yaw = yaw
        return yaw
    def key(self, t, hips, head, chest, *parts, yaw=None, **kw):
        yaw = self._yaw(yaw)
        Rl = A.Ry(-yaw) @ R_from(head, chest)
        e = cont_euler(Rl, self.prev); self.prev = e
        root = [hips[0], hips[1] - HIPS_REST, hips[2]]
        return K(t, root, yaw, *parts, {'hips': {'p': [0, 0, 0], 'r': e}}, **kw)
    def pose(self, t, root, yaw, *parts, **kw):
        """an ordinary pose key; its hips rotation is re-expressed continuously with the previous key"""
        yaw = self._yaw(yaw)
        k = K(t, root, yaw, *parts, **kw)
        hips = k[1].setdefault('hips', {})
        hr = hips.get('r', [0, 0, 0])
        e = cont_euler(A.E(hr), self.prev) if self.prev else list(hr)
        hips['r'] = e; self.prev = e
        return k

def yaw_for_lying_back(head):
    """root yaw so that LIE_BACK (head behind the root) has the head pointing `head` (horizontal)"""
    return math.degrees(math.atan2(head[0], head[2]))

def yaw_for_lying_front(head):
    """root yaw so that LIE_FRONT (head in front) has the head pointing `head`"""
    return math.degrees(math.atan2(-head[0], -head[2]))

LIMP = A.only(A.LIE_BACK, A.ARMS + A.LEGS + ['neck', 'head'])
TUCK = {'rightUpperLeg': r(30, 0, 6), 'leftUpperLeg': r(30, 0, -6), 'rightLowerLeg': r(-40), 'leftLowerLeg': r(-40),
        'rightUpperArm': r(20, 0, -40), 'leftUpperArm': r(20, 0, 40), 'rightForearm': r(40), 'leftForearm': r(40)}
FLAIL = {'rightUpperArm': r(30, 0, -80), 'leftUpperArm': r(30, 0, 80), 'rightForearm': r(20), 'leftForearm': r(20),
         'rightUpperLeg': r(10, 0, 10), 'leftUpperLeg': r(20, 0, -10), 'rightLowerLeg': r(-20), 'leftLowerLeg': r(-35)}
