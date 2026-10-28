"""Authoring helpers for paired moves.

Both roles are authored in ONE shared mat frame ("pair frame"): the attacker starts at the origin facing -z, the
defender starts in front of them. Each role's clip gets its own start placement in that frame, so the paired JSON's
defender offset is computed, never typed. The defender is usually built first; the attacker's hands are then pinned to
points on the defender's built clip (body_point) at the same key times, so contacts line up exactly at every key.
"""
import json
from common import *
import group_paired as GP

ev2 = GP.ev2
AT = A.Frame('mat', [0, 0, 0, 0])                    # attacker start

def dframe(d=0.62, yaw=180, x=0.0):
    return A.Frame('mat', [x, 0, -d, yaw])

class PairBook:
    def __init__(self, L, out_dir):
        self.L, self.out, self.index = L, out_dir, []

    def p(self, cid, t, bone, local=(0, 0, 0)):
        """frame point on a built clip's body"""
        return body_point(self.L, cid, None, t, bone, local)

    def move(self, pid, name, category, attacker, defender, events, desc, **kw):
        self.index.append(GP.pair(self.L, self.out, pid, name, category, attacker, defender, events, desc, **kw))

    def save(self, path):
        path.write_text(json.dumps(self.index, indent=2) + '\n')

# common body landmarks (bone, local offset) on the defender
NECK_BACK = ('neck', (0, 0.06, 0.07))
HEAD = ('head', (0, 0.08, 0))
CHEST = ('chest', (0, 0.12, -0.12))
WAIST_L = ('hips', (-0.17, 0.02, 0))
WAIST_R = ('hips', (0.17, 0.02, 0))
CROTCH = ('hips', (0, -0.1, 0))
THIGH_L = ('leftUpperLeg', (0, -0.18, 0))
THIGH_R = ('rightUpperLeg', (0, -0.18, 0))
ELBOW_L = ('leftForearm', (0, 0, 0))
ELBOW_R = ('rightForearm', (0, 0, 0))
WRIST_L = ('leftHand', (0, 0, 0))
WRIST_R = ('rightHand', (0, 0, 0))
ANKLE_L = ('leftFoot', (0, 0, 0))
ANKLE_R = ('rightFoot', (0, 0, 0))

def pose_at(L, cid, t):
    """bone pose of a built clip at time t, without the root (to start another clip exactly there)"""
    p = A.sample_pose(L.defs[cid], t)
    p.pop('root', None)
    return p

def end_pose(L, cid):
    return pose_at(L, cid, L.defs[cid]['duration'])

def discard(L, cid):
    """drop a pre-pass clip (used to measure contact points before the real build)"""
    import pathlib
    d = L.defs.pop(cid)
    L.index = [e for e in L.index if e['id'] != cid]
    L.reports.pop(cid, None)
    cat, name = cid.split('.', 1)
    p = L.out / cat / f'{name}.json'
    if p.exists(): p.unlink()
    return d

def mirror_point_fn(sep):
    """map a point from my start frame into the start frame of an opponent playing the SAME clip,
    who started `sep` metres in front of me and facing me"""
    return lambda p: [-p[0], p[1], -sep - p[2]]

def end_place(L, cid):
    """[x, y, z, yawDeg] in the shared frame where a built clip ends (its start placement plus its root curve end)"""
    d = L.defs[cid]
    fs = d['placement']['frameStart']
    rm = d['rootMotion']
    off, yaw = (rm.get('endOffset', [0, 0, 0]), rm.get('endYaw', 0)) if rm['mode'] == 'curve' else ([0, 0, 0], 0)
    p = A.Ry(fs[3]) @ np.asarray(off, float) + np.asarray(fs[:3], float)
    return [round(float(p[0]), 4), round(float(p[1]), 4), round(float(p[2]), 4), round(fs[3] + yaw, 3)]

def from_setup(L, cid):
    """(frame, root, yaw, pose) to start a new clip exactly where `cid` ended"""
    e = end_place(L, cid)
    return A.Frame('mat', e), e[:3], e[3], end_pose(L, cid)
