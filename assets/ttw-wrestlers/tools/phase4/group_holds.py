"""Phase 4, grappling holds: the lock-up and everything that branches from it (headlock, hammerlock, wristlock,
front facelock, waistlocks, shove-off).

Pair frame: attacker starts at the origin facing -z. From the lock-up the defender stands 0.61 m in front, facing +z
(yaw 180). The defender's left is +x (the attacker's right).
"""
from common import *
from pairs import *

SEP = 0.61
START_SEP = 1.25
BENT = {'hips': {'p': [0, -0.1, 0.12], 'r': [-14, 0, 0]}, 'spine': r(-36), 'chest': r(-18), 'neck': r(26)}
LP = {'leftHand': [-0.6, -1.0, 0.2], 'rightHand': [0.8, -0.8, 0.3]}     # elbows down and out
LOCK_BODY = dict(hy=-0.08, lean=-14, spine=(-8, 0, 0), neck=(8, 0, 0))

def stag(root, yaw, lead=0.2, back=0.18, w=0.14):
    a = rel(root, yaw, -w, 0, -lead); b = rel(root, yaw, w, 0, back)
    return plant(a[0], a[2], yaw=yaw), plant(b[0], b[2], yaw=yaw)


def build(L, PR):
    # ================================================================ lock-up (one clip, both roles)
    mirror = mirror_point_fn(START_SEP)
    def lock_keys(targets):
        ks = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
        r1 = [0, 0, -0.16]
        ks.append(K(0.28, r1, 0, A.GUARD, body(hy=-0.06, lean=-6), lfoot=stag(r1, 0)[0], rfoot=plant(0.13, 0.0)))
        r2 = [0, 0, -0.32]
        lh, rh = targets(0.5)
        ks.append(K(0.5, r2, 0, A.STANCE, body(**LOCK_BODY), lhand=lh, rhand=rh, feet=stag(r2, 0), poles=LP))
        lh, rh = targets(0.75)
        ks.append(K(0.75, r2, 0, A.STANCE, body(hy=-0.1, lean=-16, spine=(-8, 0, 0), neck=(10, 0, 0)), lhand=lh, rhand=rh, feet=stag(r2, 0), poles=LP))
        lh, rh = targets(1.0)
        ks.append(K(1.0, r2, 0, A.STANCE, body(**LOCK_BODY), lhand=lh, rhand=rh, feet=stag(r2, 0), poles=LP))
        return ks
    guess = lambda t: ([0.0, 1.55, -0.68], [0.26, 1.15, -0.56])
    L.clip('grappling.lockup-pre', 'pre', 1.0, lock_keys(guess), AT, check=False)
    for _ in range(4):            # converge: my hands go to where the opponent's neck and left elbow actually are
        tg = lambda t: (mirror(PR.p('grappling.lockup-pre', t, *NECK_BACK)), mirror(PR.p('grappling.lockup-pre', t, 'leftForearm', (0.02, 0.0, 0.0))))
        ks = lock_keys(tg); discard(L, 'grappling.lockup-pre'); L.clip('grappling.lockup-pre', 'pre', 1.0, ks, AT, check=False)
    tg = lambda t: (mirror(PR.p('grappling.lockup-pre', t, *NECK_BACK)), mirror(PR.p('grappling.lockup-pre', t, 'leftForearm', (0.02, 0.0, 0.0))))
    ks = lock_keys(tg); discard(L, 'grappling.lockup-pre')
    L.clip('grappling.lockup', 'Collar-and-elbow lock-up', 1.0, ks, AT,
           events=[ev(0.28, 'footstep'), ev(0.48, 'grab', attachment='leftHandGrip'), ev(0.5, 'footstep'), ev(0.55, 'grip_locked')],
           desc='Step in and tie up: left hand behind the opponent\'s neck, right hand on their left elbow, heads together. Played by BOTH wrestlers '
                'from 1.25 m apart; they meet 0.61 m apart in the lock-up.',
           tags=['grapple', 'lockup', 'shared-role'], end_state='lockup', placement='center',
           phases=[('approach', 0, 0.45), ('contact', 0.45, 0.6), ('hold', 0.6, 1.0)], interrupt={'windows': [[0, 0.3]]})
    LOCK = end_pose(L, 'grappling.lockup')

    # lock-up struggle loop (both roles), recomputed hand targets from the lockup end pose
    def lock_hold(t, push=0.0, sway=0.0):
        r_ = [0, 0, -push]
        return K(t, r_, 0, LOCK, body(hy=-0.1, hz=-push * 0.3, lean=-14 - push * 40, roll=sway * 20, spine=(-8, 0, 0), neck=(8, 0, 0)), feet=stag(r_, 0))
    keys = [lock_hold(0), lock_hold(0.5, 0.06, 0.1), lock_hold(1.0, -0.05, -0.05), lock_hold(1.5, 0.03, -0.1), lock_hold(2.0)]
    f = A.Frame('mat', [0, 0, 0, 0])
    keys_r = []
    for t, pose in keys:  # the lock-up clip ended at z -0.32; this loop is authored around its own start
        keys_r.append((t, pose))
    L.clip('grappling.lockup-idle', 'Lock-up struggle (loop)', 2.0, keys_r, f, loop=True,
           desc='Tied up in the lock-up: shoving for position, weight rocking back and forth. Played by both wrestlers.',
           tags=['grapple', 'lockup', 'loop', 'shared-role'], start_state='lockup', end_state='lockup', placement='center',
           gameplay={'rootMotion': 'none'})
    PR.move('pair.lockup', 'Lock-up', 'grappling', 'grappling.lockup', 'grappling.lockup',
            [ev2(0.28, 'footstep', 'both'), ev2(0.48, 'grab', 'both', attachment='leftHandGrip'), ev2(0.55, 'grip_locked', 'both'), ev2(1.0, 'animation_complete', 'both')],
            'Both wrestlers play grappling.lockup from 1.25 m apart and meet in a collar-and-elbow tie-up 0.61 m apart.',
            contacts=[{'from': 0.48, 'to': 1.0, 'attacker': 'leftHandGrip->neck,rightHandGrip->leftElbow', 'defender': 'leftHandGrip->neck,rightHandGrip->leftElbow'}],
            phases=[('approach', 0, 0.45), ('contact', 0.45, 0.6), ('hold', 0.6, 1.0)], tags=['lockup', 'shared-role'], start=([0, 0, -START_SEP], 180))

    # ---------------------------------------------------------------- lock-up break (both step back)
    keys = [K(0, [0, 0, 0], 0, LOCK, feet=stag([0, 0, 0], 0))]
    keys.append(K(0.25, [0, 0, 0.06], 0, LOCK, body(hy=-0.06, lean=-6), {'leftUpperArm': r(60, 0, 30), 'rightUpperArm': r(60, 0, -30), 'leftForearm': r(40), 'rightForearm': r(40)},
                  feet=stag([0, 0, 0.06], 0)))
    keys.append(K(0.5, [0, 0, 0.3], 0, A.GUARD, body(hy=-0.05), lfoot=plant(-0.13, 0.18), rfoot=plant(0.13, 0.45)))
    keys.append(K(0.8, [0, 0, 0.32], 0, A.GUARD, feet=stand_feet([0, 0, 0.32], 0)))
    L.clip('grappling.lockup-break', 'Break the lock-up', 0.8, keys, A.Frame('mat', [0, 0, 0, 0]),
           events=[ev(0.2, 'release'), ev(0.5, 'footstep'), ev(0.75, 'recover')],
           desc='Clean break: both let go, hands up, and step back into fighting stance (about 1.25 m apart). Played by both wrestlers.',
           tags=['grapple', 'lockup', 'shared-role'], start_state='lockup', placement='center')

    # ================================================================ shove-off (from lock-up)
    DF = dframe(SEP)
    keys = [K(0, [0, 0, -SEP], 180, LOCK, feet=stag([0, 0, -SEP], 180))]
    keys.append(K(0.18, [0, 0, -SEP - 0.05], 180, A.STANCE, body(hy=-0.05, lean=12, neck=(-14, 0, 0)), ARMS_OUT, feet=stag([0, 0, -SEP - 0.05], 180)))
    keys.append(K(0.45, [0, 0, -SEP - 0.5], 180, A.STANCE, body(hy=-0.08, lean=16), ARMS_OUT, lfoot=plant(0.13, -SEP - 0.35), rfoot=plant(-0.13, -SEP - 0.72)))
    keys.append(K(0.75, [0, 0, -SEP - 0.85], 180, A.STANCE, body(hy=-0.1, lean=4), ARMS_BALANCE, lfoot=plant(0.13, -SEP - 0.98), rfoot=plant(-0.13, -SEP - 0.75)))
    keys.append(K(1.1, [0, 0, -SEP - 0.9], 180, A.GUARD, feet=stand_feet([0, 0, -SEP - 0.9], 180)))
    L.clip('grappling.shove-off-defender', 'Shoved out of the lock-up', 1.1, keys, DF,
           events=[ev(0.15, 'hit_received', zone='body'), ev(0.45, 'footstep'), ev(0.75, 'footstep'), ev(1.05, 'recover')],
           desc='Defender: shoved hard out of the lock-up, back-pedals about 0.9 m and squares up.', tags=['grapple', 'lockup', 'defender'],
           start_state='lockup', placement='center', interrupt={'windows': [[0.8, 1.1]]})
    keys = [K(0, [0, 0, 0], 0, LOCK, feet=stag([0, 0, 0], 0))]
    keys.append(K(0.08, [0, 0, -0.02], 0, A.STANCE, body(hy=-0.1, lean=-10), lhand=PR.p('grappling.shove-off-defender', 0.08, 'chest', (0.12, 0.1, -0.13)),
                  rhand=PR.p('grappling.shove-off-defender', 0.08, 'chest', (-0.12, 0.1, -0.13)), feet=stag([0, 0, -0.02], 0)))
    keys.append(K(0.18, [0, 0, -0.12], 0, A.STANCE, body(hy=-0.1, lean=-16), {'leftUpperArm': r(84, 0, 8), 'rightUpperArm': r(84, 0, -8), 'leftForearm': r(4), 'rightForearm': r(4)},
                  feet=stag([0, 0, -0.12], 0)))
    keys.append(K(0.5, [0, 0, -0.12], 0, A.GUARD, body(hy=-0.06), feet=stag([0, 0, -0.12], 0)))
    keys.append(K(1.1, [0, 0, -0.12], 0, A.GUARD, feet=stand_feet([0, 0, -0.12], 0)))
    L.clip('grappling.shove-off-attacker', 'Shove out of the lock-up', 1.1, keys, AT,
           events=[ev(0.05, 'attack_start'), ev(0.12, 'release'), ev(0.15, 'hit', attachment='propRightHand', zone='body', reach=0.5), ev(1.05, 'recover')],
           desc='Attacker: break the lock-up with a two-handed shove to the chest.', tags=['grapple', 'lockup', 'attacker'], start_state='lockup', placement='center')
    PR.move('pair.shove-off', 'Shove out of the lock-up', 'grappling', 'grappling.shove-off-attacker', 'grappling.shove-off-defender',
            [ev2(0.05, 'attack_start', 'attacker'), ev2(0.12, 'release', 'both'), ev2(0.15, 'hit', 'attacker', zone='body'), ev2(0.15, 'hit_received', 'defender', zone='body'),
             ev2(0.45, 'footstep', 'defender'), ev2(1.05, 'recover', 'both'), ev2(1.1, 'animation_complete', 'both')],
            'From the lock-up the attacker shoves the defender away; the defender back-pedals about 0.9 m.',
            contacts=[{'from': 0.05, 'to': 0.18, 'attacker': 'propLeftHand+propRightHand', 'defender': 'chest'}],
            interrupt={'windows': [[0.6, 1.1]]}, tags=['lockup', 'shove'])

    # ================================================================ side headlock (from lock-up)
    # defender bends over facing +z at its own spot; attacker swings round to the defender's left side to face +z
    keys = [K(0, [0, 0, -SEP], 180, LOCK, feet=stag([0, 0, -SEP], 180))]
    keys.append(K(0.3, [0, 0, -SEP], 180, A.STANCE, BENT, body(hy=-0.08, hz=0.06, lean=-20, spine=(-24, 0, 0), neck=(16, 0, 0)),
                  lhand=[0.2, 1.05, -0.25], rhand=[0.05, 1.1, -0.3], feet=stand_feet([0, 0, -SEP], 180, width=0.15)))
    def dhead(t, sway=0.0):
        r_ = [0, 0, -SEP]
        return K(t, r_, 180, A.STANCE, BENT, body(hy=-0.12, hz=0.12, lean=-16, roll=sway * 15, spine=(-38, 0, 0), chest=(-18, 0, 0), neck=(18, 0, 0)),
                 lhand=[0.42, 0.95, -0.3], rhand=[0.3, 1.0, -0.12], feet=stand_feet(r_, 180, width=0.16))
    keys += [dhead(0.6), dhead(0.9)]
    L.clip('grappling.side-headlock-defender', 'Caught in a side headlock', 0.9, keys, DF,
           events=[ev(0.3, 'grab', attachment='head'), ev(0.6, 'grip_locked')],
           desc='Defender: from the lock-up, head pulled down and trapped under the attacker\'s right arm, bent at the waist, hands on the attacker\'s back.',
           tags=['grapple', 'headlock', 'defender'], start_state='lockup', end_state='headlocked', placement='center', interrupt={'windows': []})
    head = lambda t, lx, ly, lz: PR.p('grappling.side-headlock-defender', t, 'head', (lx, ly, lz))
    keys = [K(0, [0, 0, 0], 0, LOCK, feet=stag([0, 0, 0], 0))]
    keys.append(K(0.3, [0.2, 0, -0.18], 90, A.STANCE, body(hy=-0.12, lean=-10), lhand=head(0.3, 0.02, 0.12, 0.05), rhand=head(0.3, -0.1, 0.05, 0.05),
                  lfoot=plant(0.35, -0.12), rfoot=plant(0.12, -0.36)))
    def ahead(t, crank=0.0):
        r_ = [0.32, 0, -0.36]
        return K(t, r_, 180, A.STANCE, body(hy=-0.16 - crank * 0.05, lean=-12 - crank * 10, roll=-8, turn=10 + crank * 10),
                 rhand=head(t, 0.0, -0.06, -0.14), lhand=head(t, 0.1, -0.02, -0.16), feet=stand_feet(r_, 180, width=0.17))
    keys += [ahead(0.6), ahead(0.9)]
    L.clip('grappling.side-headlock-attacker', 'Apply a side headlock', 0.9, keys, AT,
           events=[ev(0.2, 'attack_start'), ev(0.3, 'grab', attachment='rightHandGrip'), ev(0.3, 'footstep'), ev(0.6, 'grip_locked')],
           desc='Attacker: from the lock-up, step round to the opponent\'s left side, pull the head down and wrap it under the right arm. Ends holding the headlock, facing the same way as the opponent.',
           tags=['grapple', 'headlock', 'attacker'], start_state='lockup', end_state='headlock-hold', placement='center')
    PR.move('pair.side-headlock', 'Side headlock', 'grappling', 'grappling.side-headlock-attacker', 'grappling.side-headlock-defender',
            [ev2(0.2, 'attack_start', 'attacker'), ev2(0.3, 'grab', 'both'), ev2(0.6, 'grip_locked', 'both'), ev2(0.9, 'animation_complete', 'both')],
            'From the lock-up: the attacker steps round and traps the defender\'s head under the right arm. Ends in headlock-hold / headlocked.',
            contacts=[{'from': 0.3, 'to': 0.9, 'attacker': 'rightForearm+propLeftHand', 'defender': 'head'}], tags=['headlock'])

    # ---------------------------------------------------------------- headlock takeover (from the side headlock)
    DH = A.Frame('mat', [0, 0, -SEP, 180])
    DHEAD = pose_at(L, 'grappling.side-headlock-defender', 0.9)
    keys = [K(0, [0, 0, -SEP], 180, DHEAD, feet=stand_feet([0, 0, -SEP], 180, width=0.16))]
    keys.append(K(0.3, [0.05, 0, -SEP + 0.2], 180, A.STANCE, BENT, body(hy=-0.3, hz=0.1, lean=-30, roll=-20, spine=(-38, 0, 0), neck=(20, 0, 0)), ARMS_OUT,
                  lfoot=plant(0.18, -SEP + 0.12), rfoot=plant(-0.1, -SEP + 0.35)))
    keys.append(K(0.55, [0.12, 0, -SEP + 0.45], 180 - 50, A.LIE_BACK, body(hy=-0.55, lean=60, roll=-30), ARMS_OUT))
    keys.append(K(0.75, [0.15, 0, -SEP + 0.55], 180 - 70, A.LIE_BACK, body(hy=-0.83, lean=90, roll=-10)))
    keys.append(K(1.2, [0.15, 0, -SEP + 0.55], 180 - 70, A.LIE_BACK, {'neck': r(30)}))
    L.clip('grappling.headlock-takeover-defender', 'Taken over by the headlock', 1.2, keys, DH,
           events=[ev(0.75, 'land', zone='back'), ev(0.75, 'impact', surface='mat')],
           desc='Defender: still headlocked, gets cartwheeled over onto the back as the attacker drops. Ends lying on the back, head still trapped.',
           tags=['grapple', 'headlock', 'defender', 'takedown'], start_state='headlocked', end_state='lying-back', placement='center', interrupt={'windows': []})
    head = lambda t, lx, ly, lz: PR.p('grappling.headlock-takeover-defender', t, 'head', (lx, ly, lz))
    AHEAD = pose_at(L, 'grappling.side-headlock-attacker', 0.9)
    keys = [K(0, [0.32, 0, -0.36], 180, AHEAD, rhand=head(0, 0.0, -0.06, -0.14), lhand=head(0, 0.1, -0.02, -0.16), feet=stand_feet([0.32, 0, -0.36], 180, width=0.17))]
    keys.append(K(0.3, [0.35, 0, -0.2], 180, A.STANCE, body(hy=-0.35, lean=-25, roll=-14), rhand=head(0.3, 0.0, -0.06, -0.14), lhand=head(0.3, 0.1, -0.02, -0.16),
                  lfoot=plant(0.5, -0.1), rfoot=plant(0.2, -0.3)))
    SIDE_SIT = {'hips': {'p': [0, -0.8, 0.05], 'r': [30, 0, -60]}, 'spine': r(-10), 'neck': r(10),
                'rightUpperLeg': r(60, 0, 20), 'leftUpperLeg': r(40, 0, -10), 'rightLowerLeg': r(-60), 'leftLowerLeg': r(-30)}
    keys.append(K(0.6, [0.45, 0, -0.05], 180 - 30, SIDE_SIT, body(hy=-0.6, lean=20, roll=-40), rhand=head(0.6, 0.0, -0.06, -0.14), lhand=head(0.6, 0.1, -0.02, -0.16)))
    keys.append(K(0.85, [0.5, 0, 0.0], 180 - 50, SIDE_SIT, rhand=head(0.85, 0.0, -0.06, -0.14), lhand=head(0.85, 0.1, -0.02, -0.16)))
    keys.append(K(1.2, [0.5, 0, 0.0], 180 - 50, SIDE_SIT, rhand=head(1.2, 0.0, -0.06, -0.14), lhand=head(1.2, 0.1, -0.02, -0.16)))
    L.clip('grappling.headlock-takeover-attacker', 'Headlock takeover', 1.2, keys, A.Frame('mat', [0.32, 0, -0.36, 180]),
           events=[ev(0.1, 'attack_start'), ev(0.6, 'land', zone='back'), ev(0.75, 'impact', surface='mat')],
           desc='Attacker: keep the side headlock, sit through and drop to the hip, taking the opponent over onto their back. Ends seated on the mat cranking the headlock.',
           tags=['grapple', 'headlock', 'attacker', 'takedown'], start_state='headlock-hold', end_state='ground-headlock', placement='center')
    PR.move('pair.headlock-takeover', 'Headlock takeover', 'grappling', 'grappling.headlock-takeover-attacker', 'grappling.headlock-takeover-defender',
            [ev2(0.1, 'attack_start', 'attacker'), ev2(0.6, 'land', 'attacker', zone='back'), ev2(0.75, 'land', 'defender', zone='back'),
             ev2(0.75, 'impact', 'defender', surface='mat'), ev2(1.2, 'animation_complete', 'both')],
            'From the side headlock the attacker sits through and drags the defender over onto the back, keeping the headlock on the mat.',
            contacts=[{'from': 0, 'to': 1.2, 'attacker': 'rightForearm+propLeftHand', 'defender': 'head'}], tags=['headlock', 'takedown'])

    # ================================================================ wristlock (from lock-up)
    keys = [K(0, [0, 0, -SEP], 180, LOCK, feet=stag([0, 0, -SEP], 180))]
    keys.append(K(0.3, [0, 0, -SEP], 180, A.STANCE, body(hy=-0.08, lean=-6, turn=-20, neck=(10, -20, 0)), {'rightUpperArm': r(70, 0, -10), 'rightForearm': r(10)},
                  lhand=[0.0, 1.2, -0.45], feet=stand_feet([0, 0, -SEP], 180, width=0.15)))
    def dwrist(t, sag=0.0):
        r_ = [0.05, 0, -SEP - 0.05]
        return K(t, r_, 150, A.STANCE, body(hy=-0.18 - sag, lean=-22, roll=14, turn=-25, neck=(20, -30, 0)), {'rightUpperArm': r(40, 0, -60), 'rightForearm': r(15)},
                 lhand=[0.15, 1.1, -0.42], lfoot=plant(0.0, -SEP + 0.1), rfoot=plant(0.2, -SEP - 0.2))
    keys += [dwrist(0.55), dwrist(0.8, 0.03), dwrist(1.0)]
    L.clip('grappling.wristlock-defender', 'Caught in a wristlock', 1.0, keys, DF,
           events=[ev(0.3, 'grab', attachment='rightHand'), ev(0.55, 'grip_locked'), ev(0.6, 'hit_received', zone='arms')],
           desc='Defender: the right wrist is twisted up and out; turns and stoops to ease the pressure, reaching across with the left hand.',
           tags=['grapple', 'wristlock', 'defender', 'arm-work'], start_state='lockup', end_state='wristlocked', placement='center', interrupt={'windows': []})
    wr = lambda t, dx=0.0: PR.p('grappling.wristlock-defender', t, 'rightHand', (dx, -0.04, 0))
    keys = [K(0, [0, 0, 0], 0, LOCK, feet=stag([0, 0, 0], 0))]
    keys.append(K(0.3, [0, 0, -0.04], 0, A.STANCE, body(hy=-0.08, lean=-8), lhand=wr(0.3, 0.04), rhand=wr(0.3, -0.04), feet=stag([0, 0, -0.04], 0)))
    keys.append(K(0.55, [-0.1, 0, -0.08], -20, A.STANCE, body(hy=-0.1, lean=-10, turn=15), lhand=wr(0.55, 0.04), rhand=wr(0.55, -0.04), feet=stag([-0.1, 0, -0.08], -20)))
    keys.append(K(0.8, [-0.1, 0, -0.08], -20, A.STANCE, body(hy=-0.12, lean=-12, turn=22), lhand=wr(0.8, 0.04), rhand=wr(0.8, -0.04), feet=stag([-0.1, 0, -0.08], -20)))
    keys.append(K(1.0, [-0.1, 0, -0.08], -20, A.STANCE, body(hy=-0.1, lean=-10, turn=18), lhand=wr(1.0, 0.04), rhand=wr(1.0, -0.04), feet=stag([-0.1, 0, -0.08], -20)))
    L.clip('grappling.wristlock-attacker', 'Apply a wristlock', 1.0, keys, AT,
           events=[ev(0.25, 'attack_start'), ev(0.3, 'grab', attachment='leftHandGrip'), ev(0.55, 'grip_locked')],
           desc='Attacker: from the lock-up, take the opponent\'s right wrist in both hands and twist it up and outwards.',
           tags=['grapple', 'wristlock', 'attacker', 'arm-work'], start_state='lockup', end_state='wristlock-hold', placement='center')
    PR.move('pair.wristlock', 'Wristlock', 'grappling', 'grappling.wristlock-attacker', 'grappling.wristlock-defender',
            [ev2(0.25, 'attack_start', 'attacker'), ev2(0.3, 'grab', 'both'), ev2(0.55, 'grip_locked', 'both'), ev2(0.6, 'hit_received', 'defender', zone='arms'),
             ev2(1.0, 'animation_complete', 'both')],
            'From the lock-up the attacker twists the defender\'s right wrist; the defender turns and stoops.',
            contacts=[{'from': 0.3, 'to': 1.0, 'attacker': 'propLeftHand+propRightHand', 'defender': 'rightHand'}], tags=['wristlock', 'arm-work'])

    # ================================================================ hammerlock (from lock-up): attacker ends behind the defender
    keys = [K(0, [0, 0, -SEP], 180, LOCK, feet=stag([0, 0, -SEP], 180))]
    keys.append(K(0.35, [0, 0, -SEP], 180 - 40, A.STANCE, body(hy=-0.08, lean=-6), {'leftUpperArm': r(50, 0, 30), 'leftForearm': r(60)},
                  feet=stand_feet([0, 0, -SEP], 140, width=0.15)))
    def dham(t, sag=0.0):
        r_ = [0, 0, -SEP - 0.05]
        return K(t, r_, 180 - 90, A.STANCE, body(hy=-0.12 - sag, lean=-24, neck=(26, 0, 0)), {'leftUpperArm': r(-60, 0, 30), 'leftForearm': r(130),
                 'rightUpperArm': r(10, 0, -20), 'rightForearm': r(30)}, feet=stand_feet(r_, 90, width=0.16))
    keys += [dham(0.7), dham(0.95, 0.03), dham(1.2)]
    L.clip('grappling.hammerlock-defender', 'Caught in a hammerlock', 1.2, keys, DF,
           events=[ev(0.3, 'grab', attachment='leftHand'), ev(0.7, 'grip_locked'), ev(0.75, 'hit_received', zone='arms')],
           desc='Defender: the left arm is wrenched behind the back and cranked up; turned side-on and bent forward.',
           tags=['grapple', 'hammerlock', 'defender', 'arm-work'], start_state='lockup', end_state='hammerlocked', placement='center', interrupt={'windows': []})
    wr = lambda t: PR.p('grappling.hammerlock-defender', t, 'leftHand', (0, -0.02, 0))
    el = lambda t: PR.p('grappling.hammerlock-defender', t, 'leftForearm', (0, 0, 0))
    keys = [K(0, [0, 0, 0], 0, LOCK, feet=stag([0, 0, 0], 0))]
    keys.append(K(0.35, [0.3, 0, -0.35], 45, A.STANCE, body(hy=-0.1, lean=-8), rhand=wr(0.35), lhand=el(0.35), lfoot=plant(0.2, -0.45), rfoot=plant(0.42, -0.25)))
    def aham(t):
        r_ = [0.45, 0, -SEP - 0.1]
        return K(t, r_, 90, A.STANCE, body(hy=-0.1, lean=-14), rhand=wr(t), lhand=el(t), feet=stand_feet(r_, 90, width=0.16))
    keys += [aham(0.7), aham(0.95), aham(1.2)]
    L.clip('grappling.hammerlock-attacker', 'Apply a hammerlock', 1.2, keys, AT,
           events=[ev(0.25, 'attack_start'), ev(0.3, 'grab', attachment='rightHandGrip'), ev(0.35, 'footstep'), ev(0.7, 'grip_locked')],
           desc='Attacker: from the lock-up, slip round behind the opponent, wrenching their left arm up behind their back (right hand on the wrist, left on the elbow).',
           tags=['grapple', 'hammerlock', 'attacker', 'arm-work'], start_state='lockup', end_state='hammerlock-hold', placement='center')
    PR.move('pair.hammerlock', 'Hammerlock', 'grappling', 'grappling.hammerlock-attacker', 'grappling.hammerlock-defender',
            [ev2(0.25, 'attack_start', 'attacker'), ev2(0.3, 'grab', 'both'), ev2(0.7, 'grip_locked', 'both'), ev2(0.75, 'hit_received', 'defender', zone='arms'),
             ev2(1.2, 'animation_complete', 'both')],
            'From the lock-up the attacker moves behind the defender and cranks the left arm up the back.',
            contacts=[{'from': 0.3, 'to': 1.2, 'attacker': 'propRightHand->wrist,propLeftHand->elbow', 'defender': 'leftHand'}], tags=['hammerlock', 'arm-work'])

    # ================================================================ front facelock (from lock-up): suplex / DDT set-up
    def dface(t, sag=0.0):
        r_ = [0, 0, -SEP - 0.05]
        return K(t, r_, 180, A.STANCE, BENT, body(hy=-0.14 - sag, hz=0.14, lean=-18, spine=(-40, 0, 0), chest=(-20, 0, 0), neck=(10, 0, 0)),
                 lhand=[0.22, 1.0, -0.35], rhand=[-0.2, 1.0, -0.35], feet=stand_feet(r_, 180, width=0.16))
    keys = [K(0, [0, 0, -SEP], 180, LOCK, feet=stag([0, 0, -SEP], 180)), dface(0.35, 0.03), dface(0.6), dface(0.85)]
    L.clip('grappling.front-facelock-defender', 'Caught in a front facelock', 0.85, keys, DF,
           events=[ev(0.25, 'grab', attachment='head'), ev(0.35, 'grip_locked')],
           desc='Defender: from the lock-up, head snapped down and trapped under the attacker\'s arm, bent forward with hands on the attacker\'s waist.',
           tags=['grapple', 'facelock', 'defender', 'setup'], start_state='lockup', end_state='facelocked', placement='center', interrupt={'windows': []})
    head = lambda t, lx, ly, lz: PR.p('grappling.front-facelock-defender', t, 'head', (lx, ly, lz))
    def aface(t):
        r_ = [0, 0, -0.05]
        return K(t, r_, 0, A.STANCE, body(hy=-0.12, lean=-14, spine=(-6, 0, 0)), rhand=head(t, 0.12, -0.06, -0.12), lhand=head(t, -0.1, 0.02, 0.05),
                 poles={'rightHand': [1, -0.5, 0]}, feet=stand_feet(r_, 0, width=0.16))
    keys = [K(0, [0, 0, 0], 0, LOCK, feet=stag([0, 0, 0], 0)), aface(0.35), aface(0.6), aface(0.85)]
    L.clip('grappling.front-facelock-attacker', 'Apply a front facelock', 0.85, keys, AT,
           events=[ev(0.2, 'attack_start'), ev(0.25, 'grab', attachment='rightHandGrip'), ev(0.35, 'grip_locked')],
           desc='Attacker: from the lock-up, snap the opponent\'s head down and wrap the right arm round it, left hand on the back of the neck. '
                'Start position for the vertical suplex and DDT.',
           tags=['grapple', 'facelock', 'attacker', 'setup'], start_state='lockup', end_state='facelock-hold', placement='center')
    PR.move('pair.front-facelock', 'Front facelock', 'grappling', 'grappling.front-facelock-attacker', 'grappling.front-facelock-defender',
            [ev2(0.2, 'attack_start', 'attacker'), ev2(0.25, 'grab', 'both'), ev2(0.35, 'grip_locked', 'both'), ev2(0.85, 'animation_complete', 'both')],
            'From the lock-up the attacker snaps the defender\'s head down into a front facelock.',
            contacts=[{'from': 0.25, 'to': 0.85, 'attacker': 'rightForearm+propLeftHand', 'defender': 'head'}], tags=['facelock', 'setup'])

    # ================================================================ waistlock (front body lock) from fighting stance
    DW = dframe(0.9)
    keys = [K(0, [0, 0, -0.9], 180, A.GUARD, feet=stand_feet([0, 0, -0.9], 180))]
    keys.append(K(0.35, [0, 0, -0.85], 180, A.STANCE, body(hy=-0.04, lean=10, neck=(-10, 0, 0)), ARMS_OUT, feet=stand_feet([0, 0, -0.85], 180)))
    def dwaist(t, sway=0.0):
        r_ = [0, 0, -0.82]
        return K(t, r_, 180, A.STANCE, body(hy=-0.04, lean=8, roll=sway * 20, neck=(-8, 0, 0)), {'rightUpperArm': r(60, 0, -40), 'leftUpperArm': r(60, 0, 40),
                 'rightForearm': r(60), 'leftForearm': r(60)}, feet=stand_feet(r_, 180))
    keys += [dwaist(0.6), dwaist(0.9)]
    L.clip('grappling.waistlock-defender', 'Caught in a body lock', 0.9, keys, DW,
           events=[ev(0.35, 'grab', attachment='hips'), ev(0.6, 'grip_locked')],
           desc='Defender: the attacker shoots in and locks both arms round the waist from the front; pushed upright, hands on the attacker\'s shoulders. '
                'Belly-to-belly and spinebuster set-up.',
           tags=['grapple', 'waistlock', 'defender', 'setup'], end_state='body-locked', placement='center', interrupt={'windows': []})
    wl = lambda t, s: PR.p('grappling.waistlock-defender', t, 'hips', (0.1 * s, 0.12, 0.14))
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(K(0.3, [0, 0, -0.25], 0, A.STANCE, body(hy=-0.25, lean=-28), ARMS_FWD, lfoot=plant(-0.13, -0.4), rfoot=plant(0.13, -0.05)))
    def awaist(t):
        r_ = [0, 0, -0.32]
        return K(t, r_, 0, A.STANCE, body(hy=-0.16, lean=-18, neck=(6, 30, 0)), lhand=wl(t, -1), rhand=wl(t, 1), feet=stag(r_, 0, lead=0.15))
    keys += [awaist(0.6), awaist(0.9)]
    L.clip('grappling.waistlock-attacker', 'Shoot in for a body lock', 0.9, keys, AT,
           events=[ev(0.15, 'attack_start'), ev(0.3, 'footstep'), ev(0.35, 'grab', attachment='leftHandGrip'), ev(0.6, 'grip_locked')],
           desc='Attacker: from fighting stance, duck in and lock both arms round the opponent\'s waist, head to the side of their chest.',
           tags=['grapple', 'waistlock', 'attacker', 'setup'], end_state='body-lock-hold', placement='center')
    PR.move('pair.waistlock', 'Body lock', 'grappling', 'grappling.waistlock-attacker', 'grappling.waistlock-defender',
            [ev2(0.15, 'attack_start', 'attacker'), ev2(0.35, 'grab', 'both'), ev2(0.6, 'grip_locked', 'both'), ev2(0.9, 'animation_complete', 'both')],
            'From fighting stance 0.9 m apart the attacker shoots in for a front body lock.',
            contacts=[{'from': 0.35, 'to': 0.9, 'attacker': 'propLeftHand+propRightHand', 'defender': 'hips'}], tags=['waistlock', 'setup'])

    # ================================================================ rear waistlock (attacker gets behind): German suplex set-up
    DR = dframe(0.9, yaw=0)            # defender with its back to the attacker
    keys = [K(0, [0, 0, -0.9], 0, A.GUARD, feet=stand_feet([0, 0, -0.9], 0))]
    keys.append(K(0.3, [0, 0, -0.9], 0, A.STANCE, body(hy=-0.04, lean=12, neck=(-14, 30, 0)), ARMS_OUT, feet=stand_feet([0, 0, -0.9], 0)))
    def drear(t, sway=0.0):
        r_ = [0, 0, -0.9]
        return K(t, r_, 0, A.STANCE, body(hy=-0.05, lean=6, roll=sway * 20, neck=(-6, 20, 0)), {'rightUpperArm': r(30, 0, -20), 'leftUpperArm': r(30, 0, 20),
                 'rightForearm': r(70), 'leftForearm': r(70)}, feet=stand_feet(r_, 0, width=0.15))
    keys += [drear(0.55), drear(0.8, 0.1), drear(1.0)]
    L.clip('grappling.rear-waistlock-defender', 'Grabbed from behind', 1.0, keys, DR,
           events=[ev(0.3, 'grab', attachment='hips'), ev(0.55, 'grip_locked')],
           desc='Defender: grabbed round the waist from behind; straightens up, hands clawing at the attacker\'s locked hands. German suplex set-up.',
           tags=['grapple', 'waistlock', 'defender', 'setup'], end_state='rear-locked', placement='center', interrupt={'windows': []})
    rw = lambda t, s: PR.p('grappling.rear-waistlock-defender', t, 'hips', (0.1 * s, 0.14, -0.13))
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(K(0.3, [0, 0, -0.3], 0, A.STANCE, body(hy=-0.08, lean=-12), ARMS_FWD, lfoot=plant(-0.13, -0.45), rfoot=plant(0.13, -0.15)))
    def arear(t):
        r_ = [0, 0, -0.48]
        return K(t, r_, 0, A.STANCE, body(hy=-0.12, lean=-10, neck=(4, 25, 0)), lhand=rw(t, -1), rhand=rw(t, 1), feet=stag(r_, 0, lead=0.12, back=0.2))
    keys += [arear(0.55), arear(0.8), arear(1.0)]
    L.clip('grappling.rear-waistlock-attacker', 'Rear waistlock', 1.0, keys, AT,
           events=[ev(0.15, 'attack_start'), ev(0.3, 'footstep'), ev(0.3, 'grab', attachment='leftHandGrip'), ev(0.55, 'grip_locked')],
           desc='Attacker: step in behind the opponent and lock the hands round their waist, chest to their back.',
           tags=['grapple', 'waistlock', 'attacker', 'setup'], end_state='rear-lock-hold', placement='center')
    PR.move('pair.rear-waistlock', 'Rear waistlock', 'grappling', 'grappling.rear-waistlock-attacker', 'grappling.rear-waistlock-defender',
            [ev2(0.15, 'attack_start', 'attacker'), ev2(0.3, 'grab', 'both'), ev2(0.55, 'grip_locked', 'both'), ev2(1.0, 'animation_complete', 'both')],
            'The attacker locks a waistlock from behind a defender who has their back turned (0.9 m apart).',
            contacts=[{'from': 0.3, 'to': 1.0, 'attacker': 'propLeftHand+propRightHand', 'defender': 'hips'}], tags=['waistlock', 'setup'])
