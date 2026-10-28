"""Phase 4, throws and slams (paired). The thrown body is keyed by world orientation (head and chest directions)
and hips position; the thrower's hands are pinned to points on the thrown body at the same key times.

Pair frame: attacker at the origin facing -z (+x is the attacker's right). Moves from a set-up (front facelock,
body lock, rear waistlock, side headlock, bent over) start exactly where the set-up clips end.
"""
from common import *
from pairs import *
from throws_lib import *

UP, DOWN = [0, 1, 0], [0, -1, 0]
PX, NX, PZ, NZ = [1, 0, 0], [-1, 0, 0], [0, 0, 1], [0, 0, -1]

def lie_back_key(B, t, hips_xz, head, *parts):
    y = yaw_for_lying_back(head)
    return B.pose(t, [hips_xz[0], 0, hips_xz[1]], y, A.LIE_BACK, *parts)

def lie_front_key(B, t, hips_xz, head, *parts):
    y = yaw_for_lying_front(head)
    return B.pose(t, [hips_xz[0], 0, hips_xz[1]], y, A.LIE_FRONT, *parts)

def stand(t, root, yaw, *parts, w=0.14, **kw):
    return K(t, list(root), yaw, A.STANCE, *parts, feet=stand_feet(list(root), yaw, width=w), **kw)


def build(L, PR):
    P = PR.p

    # ================================================================ body slam (from fighting stance, 0.62 m apart)
    d_id, a_id = 'throws.body-slam-defender', 'throws.body-slam-attacker'
    B = Body(180)
    keys = [B.pose(0, [0, 0, -0.62], 180, A.GUARD, feet=stand_feet([0, 0, -0.62], 180))]
    keys.append(B.key(0.3, [0, 0.98, -0.6], UP, PZ, A.STANCE, TUCK, feet=stand_feet([0, 0, -0.6], 180)))
    keys.append(B.key(0.5, [-0.05, 1.25, -0.42], [-0.7, 0.7, 0], PZ, TUCK))
    keys.append(B.key(0.8, [-0.02, 1.45, -0.32], [-1, -0.15, 0], [0, 0.25, 1], TUCK))              # across the chest, head low on the left
    keys.append(B.key(0.92, [-0.02, 0.9, -0.6], NX, [0, 0.8, 0.6], FLAIL))
    keys.append(lie_back_key(B, 1.02, [-0.05, -0.82], NX, {'neck': r(20)}))                        # flat on the back
    keys.append(lie_back_key(B, 1.3, [-0.05, -0.82], NX, {'neck': r(-10)}))
    keys.append(lie_back_key(B, 1.8, [-0.05, -0.82], NX))
    L.clip(d_id, 'Body slammed', 1.8, keys, dframe(0.62),
           events=[ev(0.3, 'grab'), ev(0.45, 'lift_start'), ev(0.8, 'lift_complete'), ev(1.02, 'land', zone='back'), ev(1.02, 'impact', surface='mat'), ev(1.05, 'stun_start')],
           desc='Defender: scooped up, turned upside down across the attacker\'s chest and slammed flat on the back.', tags=['throw', 'slam', 'defender'],
           end_state='lying-back', placement='center', interrupt={'windows': []})
    crotch = lambda t: P(d_id, t, 'hips', (0.0, -0.12, 0.0))
    upper = lambda t: P(d_id, t, 'chest', (0.0, 0.05, 0.14))
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(stand(0.3, [0, 0, -0.1], 0, body(hy=-0.3, lean=-22, spine=(-10, 0, 0)), rhand=crotch(0.3), lhand=upper(0.3)))
    keys.append(stand(0.5, [0, 0, -0.1], 0, body(hy=-0.16, lean=-6), rhand=crotch(0.5), lhand=upper(0.5)))
    keys.append(stand(0.8, [0, 0, -0.1], 0, body(hy=-0.04, lean=6), rhand=crotch(0.8), lhand=upper(0.8)))
    keys.append(stand(0.92, [0, 0, -0.12], 0, body(hy=-0.2, lean=-24), rhand=crotch(0.92), lhand=upper(0.92)))
    keys.append(stand(1.02, [0, 0, -0.12], 0, body(hy=-0.32, lean=-36, spine=(-10, 0, 0)), {'rightUpperArm': r(70, 0, -10), 'leftUpperArm': r(70, 0, 10)}))
    keys.append(stand(1.35, [0, 0, -0.1], 0, body(hy=-0.08, lean=-8)))
    keys.append(K(1.8, [0, 0, -0.1], 0, A.GUARD, feet=stand_feet([0, 0, -0.1], 0)))
    L.clip(a_id, 'Body slam', 1.8, keys, AT,
           events=[ev(0.2, 'attack_start'), ev(0.3, 'grab', attachment='rightHandGrip'), ev(0.35, 'grip_locked'), ev(0.45, 'lift_start'), ev(0.8, 'lift_complete'),
                   ev(0.95, 'release'), ev(1.02, 'impact', surface='mat'), ev(1.75, 'recover')],
           desc='Attacker: right arm between the legs, left hand on the upper back; lift, turn them upside down across the chest and slam them down in front.',
           tags=['throw', 'slam', 'attacker'], placement='center')
    PR.move('pair.body-slam', 'Body slam', 'throws', a_id, d_id,
            [ev2(0.2, 'attack_start', 'attacker'), ev2(0.3, 'grab', 'both'), ev2(0.45, 'lift_start', 'both'), ev2(0.8, 'lift_complete', 'both'),
             ev2(0.95, 'release', 'attacker'), ev2(1.02, 'land', 'defender', zone='back'), ev2(1.02, 'impact', 'defender', surface='mat'),
             ev2(1.75, 'recover', 'attacker'), ev2(1.8, 'animation_complete', 'both')],
            'Classic body slam from fighting stance. The defender ends flat on the back in front of the attacker, head to the attacker\'s left.',
            contacts=[{'from': 0.3, 'to': 0.95, 'attacker': 'propRightHand->crotch,propLeftHand->upperBack', 'defender': 'hips+chest'}],
            phases=[('contact', 0, 0.45), ('launch', 0.45, 0.8), ('flight', 0.8, 1.02), ('landing', 1.02, 1.2), ('recovery', 1.2, 1.8)], tags=['slam'])

    # ================================================================ suplexes, DDT, neckbreaker (from the front facelock)
    def from_facelock():
        fa, ra, ya, pa = from_setup(L, 'grappling.front-facelock-attacker')
        fd, rd, yd, pd = from_setup(L, 'grappling.front-facelock-defender')
        return fa, ra, ya, pa, fd, rd, yd, pd
    fa, ra, ya, pa, fd, rd, yd, pd = from_facelock()
    def def_start_hips(t=0):
        W = A.fk(dict(pd)); fr = A.Frame('mat', [rd[0], 0, rd[2], yd])
        return list(fr.to_frame(W['hips'][1]))

    def suplex(name, title, dur, T, hang, desc):
        d_id, a_id = f'throws.{name}-defender', f'throws.{name}-attacker'
        B = Body(yd)
        h0 = def_start_hips()
        t_lift, t_vert, t_drop, t_land = T
        keys = [B.pose(0, rd, yd, pd)]
        keys.append(B.key(t_lift, [0.12, 1.45, rd[2] + 0.3], [0, 0.2, 1], DOWN, TUCK))                  # hips up, head under the arm
        keys.append(B.key(t_vert, [0.16, 2.0, rd[2] + 0.55], DOWN, NZ, A.only(A.LIE_BACK, A.LEGS), {'rightUpperArm': r(0, 0, -60), 'leftUpperArm': r(0, 0, 60)}))
        if hang: keys.append(B.key(t_vert + hang, [0.16, 2.02, rd[2] + 0.56], DOWN, NZ, A.only(A.LIE_BACK, A.LEGS), {'rightUpperArm': r(0, 0, -60), 'leftUpperArm': r(0, 0, 60)}))
        keys.append(B.key(t_drop, [0.14, 1.25, 0.75], [0, -0.6, -0.8], [0, 0.8, -0.6], FLAIL))
        keys.append(lie_back_key(B, t_land, [0.12, 1.4], NZ, {'neck': r(25)}))
        keys.append(lie_back_key(B, dur, [0.12, 1.4], NZ))
        L.clip(d_id, f'{title} (taken)', dur, keys, fd,
               events=[ev(0.1, 'grab'), ev(t_lift - 0.15, 'lift_start'), ev(t_vert, 'lift_complete'), ev(t_land, 'land', zone='back'), ev(t_land, 'impact', surface='mat'), ev(t_land + 0.05, 'stun_start')],
               desc=f'Defender: {desc}', tags=['throw', 'suplex', 'defender'], start_state='facelocked', end_state='lying-back', placement='center', interrupt={'windows': []})
        neck = lambda t: P(d_id, t, 'neck', (0.0, 0.0, 0.0))
        belt = lambda t: P(d_id, t, 'hips', (0.0, 0.08, 0.14))
        a0 = [ra[0], 0, ra[2]]
        keys = [K(0, a0, ya, pa, feet=stand_feet(a0, ya, width=0.16))]
        keys.append(stand(t_lift, a0, ya, body(hy=-0.22, lean=-4), rhand=neck(t_lift), lhand=belt(t_lift), w=0.17))
        keys.append(stand(t_vert, a0, ya, body(hy=-0.06, lean=10, neck=(-10, 0, 0)), rhand=neck(t_vert), lhand=belt(t_vert), w=0.17))
        if hang: keys.append(stand(t_vert + hang, a0, ya, body(hy=-0.05, lean=12, neck=(-14, 0, 0)), rhand=neck(t_vert + hang), lhand=belt(t_vert + hang), w=0.17))
        keys.append(K(t_drop, [a0[0], -0.35, a0[2] + 0.18], ya, A.STANCE, body(hy=-0.1, lean=55), rhand=neck(t_drop), lhand=belt(t_drop),
                      lfoot=plant(a0[0] - 0.15, a0[2] - 0.12), rfoot=plant(a0[0] + 0.15, a0[2] - 0.12)))
        keys.append(K(t_land, [a0[0], 0, a0[2] + 0.2], ya, A.LIE_BACK, {'rightUpperArm': r(0, 0, 70), 'leftUpperArm': r(0, 0, -70)}))
        keys.append(K(dur, [a0[0], 0, a0[2] + 0.2], ya, A.LIE_BACK))
        L.clip(a_id, title, dur, keys, fa,
               events=[ev(0.05, 'attack_start'), ev(0.1, 'grip_locked'), ev(t_lift - 0.15, 'lift_start'), ev(t_vert, 'lift_complete'), ev(t_drop, 'release'),
                       ev(t_land, 'land', zone='back'), ev(t_land, 'impact', surface='mat')],
               desc=f'Attacker: from the front facelock, {desc.split(": ", 1)[-1]}', tags=['throw', 'suplex', 'attacker'],
               start_state='facelock-hold', end_state='lying-back', placement='center')
        PR.move(f'pair.{name}', title, 'throws', a_id, d_id,
                [ev2(0.05, 'attack_start', 'attacker'), ev2(0.1, 'grip_locked', 'both'), ev2(t_lift - 0.15, 'lift_start', 'both'), ev2(t_vert, 'lift_complete', 'both'),
                 ev2(t_drop, 'release', 'attacker'), ev2(t_land, 'land', 'both', zone='back'), ev2(t_land, 'impact', 'defender', surface='mat'), ev2(dur, 'animation_complete', 'both')],
                f'From the front facelock. {desc} Both end lying on the back.',
                contacts=[{'from': 0, 'to': t_drop, 'attacker': 'rightForearm->neck,propLeftHand->waistband', 'defender': 'neck+hips'}],
                phases=[('contact', 0, t_lift), ('launch', t_lift, t_vert), ('hold', t_vert, t_vert + hang), ('flight', t_vert + hang, t_land), ('landing', t_land, t_land + 0.2), ('recovery', t_land + 0.2, dur)],
                tags=['suplex'])
    suplex('vertical-suplex', 'Vertical suplex', 2.4, (0.45, 0.85, 1.7, 1.88), 0.6,
           'hoisted straight up and held upside down for a long beat, then dropped backwards over the attacker onto the back.')
    suplex('snap-suplex', 'Snap suplex', 1.5, (0.3, 0.55, 0.78, 0.92), 0.0,
           'hoisted up and snapped straight over the attacker onto the back in one fast motion.')

    # ---------------------------------------------------------------- DDT
    d_id, a_id = 'throws.ddt-defender', 'throws.ddt-attacker'
    B = Body(yd)
    keys = [B.pose(0, rd, yd, pd)]
    keys.append(B.key(0.25, [0, 0.9, rd[2] + 0.02], [0, -0.3, 1], [0, -1, 0.3], A.only(A.STANCE, A.LEGS), {'rightUpperArm': r(-20, 0, -30), 'leftUpperArm': r(-20, 0, 30)}))
    keys.append(B.key(0.42, [0, 0.72, rd[2] - 0.05], [0, -0.7, 0.7], [0, -0.7, -0.7], A.only(A.LIE_FRONT, A.LEGS), ARMS_OUT))       # head spiked
    keys.append(lie_front_key(B, 0.6, [0, rd[2] - 0.12], PZ))
    keys.append(lie_front_key(B, 1.5, [0, rd[2] - 0.12], PZ, {'neck': r(0, 0, 0)}))
    L.clip(d_id, 'Spiked with a DDT', 1.5, keys, fd,
           events=[ev(0.42, 'impact', surface='mat', zone='head'), ev(0.6, 'land', zone='front'), ev(0.65, 'stun_start')],
           desc='Defender: still in the front facelock as the attacker falls back; driven head first into the mat and flopped face down.',
           tags=['throw', 'ddt', 'defender'], start_state='facelocked', end_state='lying-front', placement='center', interrupt={'windows': []})
    headp = lambda t: P(d_id, t, 'head', (0.12, -0.05, -0.12))
    nk = lambda t: P(d_id, t, 'neck', (-0.08, 0.05, 0.05))
    a0 = [ra[0], 0, ra[2]]
    keys = [K(0, a0, ya, pa, feet=stand_feet(a0, ya, width=0.16))]
    keys.append(stand(0.12, a0, ya, body(hy=-0.08, lean=-6), rhand=headp(0.12), lhand=nk(0.12), w=0.16))
    keys.append(K(0.25, [a0[0], 0.05, a0[2] + 0.1], ya, A.STANCE, body(hy=-0.25, lean=40), rhand=headp(0.25), lhand=nk(0.25), lfoot=air(a0[0] - 0.14, 0.25, a0[2] - 0.15), rfoot=air(a0[0] + 0.14, 0.25, a0[2] - 0.15)))
    keys.append(K(0.42, [a0[0], 0, a0[2] + 0.25], ya, A.LIE_BACK, body(hy=-0.6, lean=75), rhand=headp(0.42), lhand=nk(0.42)))
    keys.append(K(0.6, [a0[0], 0, a0[2] + 0.3], ya, A.LIE_BACK))
    keys.append(K(1.5, [a0[0], 0, a0[2] + 0.3], ya, A.LIE_BACK))
    L.clip(a_id, 'DDT', 1.5, keys, fa,
           events=[ev(0.1, 'attack_start'), ev(0.2, 'jump'), ev(0.42, 'impact', surface='mat'), ev(0.42, 'land', zone='back'), ev(0.5, 'release')],
           desc='Attacker: from the front facelock, kick the legs out and fall straight back, spiking the opponent\'s head into the mat.',
           tags=['throw', 'ddt', 'attacker', 'finisher'], start_state='facelock-hold', end_state='lying-back', placement='center')
    PR.move('pair.ddt', 'DDT', 'throws', a_id, d_id,
            [ev2(0.1, 'attack_start', 'attacker'), ev2(0.2, 'jump', 'attacker'), ev2(0.42, 'impact', 'both', surface='mat'), ev2(0.42, 'land', 'attacker', zone='back'),
             ev2(0.5, 'release', 'attacker'), ev2(0.6, 'land', 'defender', zone='front'), ev2(1.5, 'animation_complete', 'both')],
            'From the front facelock: the attacker falls back and drives the defender\'s head into the mat. Attacker ends on the back, defender face down.',
            contacts=[{'from': 0, 'to': 0.5, 'attacker': 'rightForearm->head', 'defender': 'head'}], tags=['ddt', 'finisher'])

    # ---------------------------------------------------------------- neckbreaker
    d_id, a_id = 'throws.neckbreaker-defender', 'throws.neckbreaker-attacker'
    B = Body(yd)
    keys = [B.pose(0, rd, yd, pd)]
    keys.append(B.key(0.3, [0.05, 0.95, rd[2] + 0.1], [0.3, 0.2, 0.93], [0.3, -0.9, 0], A.only(A.STANCE, A.LEGS), ARMS_OUT))
    keys.append(B.key(0.5, [0.15, 0.6, rd[2] + 0.05], [0.5, 0, 0.86], [0, 0.3, -0.1], FLAIL))
    keys.append(lie_back_key(B, 0.62, [0.1, rd[2] - 0.1], [0.35, 0, 0.94], {'neck': r(30)}))
    keys.append(lie_back_key(B, 1.5, [0.1, rd[2] - 0.1], [0.35, 0, 0.94]))
    L.clip(d_id, 'Neckbreakered', 1.5, keys, fd,
           events=[ev(0.62, 'land', zone='back'), ev(0.62, 'impact', surface='mat', zone='neck'), ev(0.7, 'stun_start')],
           desc='Defender: head kept under the attacker\'s arm while the attacker turns and drops; flipped over and snapped down onto the back of the neck.',
           tags=['throw', 'neckbreaker', 'defender'], start_state='facelocked', end_state='lying-back', placement='center', interrupt={'windows': []})
    headp = lambda t: P(d_id, t, 'head', (0.0, -0.06, -0.1))
    keys = [K(0, a0, ya, pa, feet=stand_feet(a0, ya, width=0.16))]
    keys.append(stand(0.2, [a0[0] + 0.05, 0, a0[2] - 0.05], ya - 90, body(hy=-0.08, lean=-4), rhand=headp(0.2), w=0.16))
    keys.append(K(0.42, [a0[0] + 0.15, -0.35, a0[2] - 0.05], ya - 170, A.STANCE, body(hy=-0.2, lean=35), rhand=headp(0.42),
                  lfoot=plant(a0[0] + 0.0, a0[2] - 0.45), rfoot=plant(a0[0] + 0.3, a0[2] - 0.45)))
    SIT = {'hips': {'p': [0, -0.8, 0.05], 'r': [20, 0, 0]}, 'spine': r(-10), 'neck': r(14),
           'rightUpperLeg': r(80, 0, 10), 'leftUpperLeg': r(80, 0, -10), 'rightLowerLeg': r(-20), 'leftLowerLeg': r(-20), 'leftUpperArm': r(-20, 0, 30)}
    keys.append(K(0.62, [a0[0] + 0.15, 0, a0[2] - 0.05], ya - 180, SIT, rhand=headp(0.62)))
    keys.append(K(1.5, [a0[0] + 0.15, 0, a0[2] - 0.05], ya - 180, SIT))
    L.clip(a_id, 'Neckbreaker', 1.5, keys, fa,
           events=[ev(0.1, 'attack_start'), ev(0.62, 'impact', surface='mat'), ev(0.62, 'land', zone='seat'), ev(0.7, 'release')],
           desc='Attacker: from the front facelock, pivot to stand back to back with the head still trapped, and sit down hard, snapping the opponent\'s neck to the mat.',
           tags=['throw', 'neckbreaker', 'attacker'], start_state='facelock-hold', end_state='sitting', placement='center')
    PR.move('pair.neckbreaker', 'Neckbreaker', 'throws', a_id, d_id,
            [ev2(0.1, 'attack_start', 'attacker'), ev2(0.62, 'impact', 'both', surface='mat'), ev2(0.62, 'land', 'both'), ev2(0.7, 'release', 'attacker'), ev2(1.5, 'animation_complete', 'both')],
            'From the front facelock: the attacker pivots and sits out, snapping the defender down onto the back of the neck. Attacker ends sitting, defender on the back.',
            contacts=[{'from': 0, 'to': 0.7, 'attacker': 'rightForearm->head', 'defender': 'head'}], tags=['neckbreaker'])

    # ================================================================ from the front body lock: belly-to-belly, spinebuster
    fa, ra, ya, pa = from_setup(L, 'grappling.waistlock-attacker')
    fd, rd, yd, pd = from_setup(L, 'grappling.waistlock-defender')
    a0 = [ra[0], 0, ra[2]]
    d_id, a_id = 'throws.belly-to-belly-defender', 'throws.belly-to-belly-attacker'
    B = Body(yd)
    keys = [B.pose(0, rd, yd, pd)]
    keys.append(B.key(0.35, [0, 1.3, rd[2] + 0.1], [0, 0.95, 0.3], [0, 0.3, -0.95], TUCK))
    keys.append(B.key(0.6, [0, 1.7, a0[2] + 0.1], PZ, DOWN, FLAIL))                       # over the top
    keys.append(B.key(0.78, [0, 1.2, a0[2] + 0.9], [0, -0.7, 0.7], [0, -0.7, -0.7], FLAIL))
    keys.append(B.key(0.86, [0, 0.88, a0[2] + 1.2], [0, -0.85, -0.5], [0, 0.5, -0.85], FLAIL))
    keys.append(lie_back_key(B, 0.95, [0, a0[2] + 1.45], NZ, {'neck': r(25)}))
    keys.append(lie_back_key(B, 1.08, [0, a0[2] + 1.45], NZ, {'neck': r(15)}))
    keys.append(lie_back_key(B, 1.6, [0, a0[2] + 1.45], NZ))
    L.clip(d_id, 'Belly-to-belly suplexed', 1.6, keys, fd,
           events=[ev(0.2, 'lift_start'), ev(0.6, 'apex'), ev(0.95, 'land', zone='back'), ev(0.95, 'impact', surface='mat'), ev(1.0, 'stun_start')],
           desc='Defender: hugged chest to chest, lifted and launched backwards over the attacker\'s head, landing flat on the back behind them.',
           tags=['throw', 'suplex', 'defender'], start_state='body-locked', end_state='lying-back', placement='center', interrupt={'windows': []})
    hold = lambda t, s: P(d_id, t, 'hips', (0.12 * s, 0.15, 0.13))
    keys = [K(0, a0, ya, pa, feet=stand_feet(a0, ya, width=0.17))]
    keys.append(stand(0.2, a0, ya, body(hy=-0.3, lean=-8), lhand=hold(0.2, -1), rhand=hold(0.2, 1), w=0.18))
    keys.append(stand(0.35, a0, ya, body(hy=-0.08, lean=20, neck=(-20, 0, 0)), lhand=hold(0.35, -1), rhand=hold(0.35, 1), w=0.18))
    keys.append(K(0.6, [a0[0], -0.25, a0[2] + 0.15], ya, A.STANCE, body(hy=-0.1, lean=60, neck=(-30, 0, 0)), lhand=hold(0.6, -1), rhand=hold(0.6, 1),
                  lfoot=plant(-0.16, a0[2] - 0.1), rfoot=plant(0.16, a0[2] - 0.1)))
    keys.append(K(0.78, [a0[0], 0, a0[2] + 0.25], ya, A.LIE_BACK, body(hy=-0.6, lean=80), ARMS_UP))
    keys.append(K(0.92, [a0[0], 0, a0[2] + 0.3], ya, A.LIE_BACK))
    keys.append(K(1.6, [a0[0], 0, a0[2] + 0.3], ya, A.LIE_BACK))
    L.clip(a_id, 'Belly-to-belly suplex', 1.6, keys, fa,
           events=[ev(0.1, 'attack_start'), ev(0.2, 'lift_start'), ev(0.5, 'release'), ev(0.78, 'land', zone='back'), ev(0.92, 'impact', surface='mat')],
           desc='Attacker: from the front body lock, dip, explode upwards and arch back, releasing the opponent over the head.',
           tags=['throw', 'suplex', 'attacker'], start_state='body-lock-hold', end_state='lying-back', placement='center')
    PR.move('pair.belly-to-belly', 'Belly-to-belly suplex', 'throws', a_id, d_id,
            [ev2(0.1, 'attack_start', 'attacker'), ev2(0.2, 'lift_start', 'both'), ev2(0.5, 'release', 'attacker'), ev2(0.6, 'apex', 'defender'),
             ev2(0.78, 'land', 'attacker', zone='back'), ev2(0.92, 'land', 'defender', zone='back'), ev2(0.92, 'impact', 'defender', surface='mat'), ev2(1.6, 'animation_complete', 'both')],
            'From the front body lock: the defender is launched backwards over the attacker. Both end on the back, head to head.',
            contacts=[{'from': 0, 'to': 0.5, 'attacker': 'propLeftHand+propRightHand', 'defender': 'hips'}], tags=['suplex'])

    d_id, a_id = 'throws.spinebuster-defender', 'throws.spinebuster-attacker'
    B = Body(yd)
    keys = [B.pose(0, rd, yd, pd)]
    keys.append(B.key(0.35, [0.0, 1.35, rd[2] + 0.05], UP, PZ, TUCK, yaw=yd))
    keys.append(B.key(0.6, [-0.25, 1.4, a0[2] - 0.15], UP, [-0.7, 0, -0.7], TUCK, yaw=yd + 90))                 # carried round a half turn
    keys.append(B.key(0.78, [0.0, 0.8, a0[2] + 0.45], [0, 0.5, 0.85], [0, 0.85, -0.5], FLAIL, yaw=yd + 180))
    keys.append(lie_back_key(B, 0.9, [0, a0[2] + 0.65], PZ, {'neck': r(25)}))
    keys.append(lie_back_key(B, 1.7, [0, a0[2] + 0.65], PZ))
    L.clip(d_id, 'Spinebustered', 1.7, keys, fd,
           events=[ev(0.2, 'lift_start'), ev(0.9, 'land', zone='back'), ev(0.9, 'impact', surface='mat'), ev(0.95, 'stun_start')],
           desc='Defender: lifted in the body lock, swung round and driven down flat on the back with the attacker on top.',
           tags=['throw', 'slam', 'defender'], start_state='body-locked', end_state='lying-back', placement='center', interrupt={'windows': []})
    hold = lambda t, s: P(d_id, t, 'hips', (0.12 * s, 0.15, 0.13))
    keys = [K(0, a0, ya, pa, feet=stand_feet(a0, ya, width=0.17))]
    keys.append(stand(0.35, a0, ya, body(hy=-0.1, lean=10), lhand=hold(0.35, -1), rhand=hold(0.35, 1), w=0.18))
    keys.append(stand(0.6, [a0[0], 0, a0[2] + 0.05], ya + 90, body(hy=-0.1, lean=6), lhand=hold(0.6, -1), rhand=hold(0.6, 1), w=0.18))
    keys.append(K(0.78, [a0[0], 0, a0[2] + 0.2], ya + 180, A.STANCE, body(hy=-0.45, lean=-45), lhand=hold(0.78, -1), rhand=hold(0.78, 1),
                  lfoot=plant(a0[0] - 0.15, a0[2] + 0.05), rfoot=plant(a0[0] + 0.15, a0[2] + 0.0)))
    KNEEL_OVER = {'hips': {'p': [0, -0.55, 0.05], 'r': [-40, 0, 0]}, 'spine': r(-20), 'neck': r(20),
                  'rightUpperLeg': r(60, 0, 8), 'leftUpperLeg': r(60, 0, -8), 'rightLowerLeg': r(-110), 'leftLowerLeg': r(-110), 'rightFoot': r(-55), 'leftFoot': r(-55)}
    keys.append(K(0.9, [a0[0], 0, a0[2] + 0.25], ya + 180, KNEEL_OVER, lhand=hold(0.9, -1), rhand=hold(0.9, 1)))
    keys.append(K(1.3, [a0[0], 0, a0[2] + 0.25], ya + 180, KNEEL_OVER, {'hips': {'p': [0, -0.5, 0.0], 'r': [-25, 0, 0]}}))
    keys.append(K(1.7, [a0[0], 0, a0[2] + 0.25], ya + 180, A.STANCE, body(hy=-0.35, lean=-20), feet=stand_feet([a0[0], 0, a0[2] + 0.25], ya + 180, width=0.18)))
    L.clip(a_id, 'Spinebuster', 1.7, keys, fa,
           events=[ev(0.1, 'attack_start'), ev(0.2, 'lift_start'), ev(0.6, 'lift_complete'), ev(0.9, 'impact', surface='mat'), ev(0.9, 'land', zone='knees'), ev(1.0, 'release')],
           desc='Attacker: from the front body lock, lift, swing a half turn and drive the opponent down onto the back, landing on the knees over them.',
           tags=['throw', 'slam', 'attacker', 'power'], start_state='body-lock-hold', end_state='crouching', placement='center')
    PR.move('pair.spinebuster', 'Spinebuster', 'throws', a_id, d_id,
            [ev2(0.1, 'attack_start', 'attacker'), ev2(0.2, 'lift_start', 'both'), ev2(0.9, 'impact', 'both', surface='mat'), ev2(0.9, 'land', 'defender', zone='back'),
             ev2(1.0, 'release', 'attacker'), ev2(1.7, 'animation_complete', 'both')],
            'From the front body lock: the attacker spins a half turn and slams the defender down, ending crouched over them.',
            contacts=[{'from': 0, 'to': 1.0, 'attacker': 'propLeftHand+propRightHand', 'defender': 'hips'}], tags=['slam', 'power'])

    # ================================================================ German suplex (from the rear waistlock)
    fa, ra, ya, pa = from_setup(L, 'grappling.rear-waistlock-attacker')
    fd, rd, yd, pd = from_setup(L, 'grappling.rear-waistlock-defender')
    a0 = [ra[0], 0, ra[2]]
    d_id, a_id = 'throws.german-suplex-defender', 'throws.german-suplex-attacker'
    B = Body(yd)
    keys = [B.pose(0, rd, yd, pd)]
    keys.append(B.key(0.3, [0, 1.25, rd[2] + 0.1], [0, 0.95, 0.3], [0, -0.3, -0.95], FLAIL))
    keys.append(B.key(0.52, [0, 1.65, a0[2] + 0.05], PZ, UP, FLAIL))                                   # horizontal over the attacker
    keys.append(B.key(0.7, [0, 1.35, a0[2] + 0.75], [0, -0.85, 0.5], [0, 0.5, 0.85], FLAIL))             # coming down on the shoulders
    keys.append(B.key(0.82, [0, 0.97, a0[2] + 1.05], DOWN, PZ, FLAIL))                                   # neck and shoulders on the mat
    keys.append(B.key(0.96, [0, 0.85, a0[2] + 1.35], [0, -0.71, -0.71], [0, -0.71, 0.71], FLAIL))                   # legs flop over
    keys.append(lie_front_key(B, 1.1, [0, a0[2] + 1.65], NZ))
    keys.append(lie_front_key(B, 1.25, [0, a0[2] + 1.65], NZ, {'neck': r(10, 20, 0)}))
    keys.append(lie_front_key(B, 1.8, [0, a0[2] + 1.65], NZ, {'neck': r(10, 30, 0)}))
    L.clip(d_id, 'German suplexed', 1.8, keys, fd,
           events=[ev(0.15, 'lift_start'), ev(0.52, 'apex'), ev(0.82, 'impact', surface='mat', zone='neck'), ev(1.1, 'land', zone='front'), ev(1.15, 'stun_start')],
           desc='Defender: grabbed from behind, lifted and arched backwards over the attacker; lands on the neck and shoulders and the legs flop over, ending face down.',
           tags=['throw', 'suplex', 'defender'], start_state='rear-locked', end_state='lying-front', placement='center', interrupt={'windows': []})
    hold = lambda t, s: P(d_id, t, 'hips', (0.12 * s, 0.15, -0.13))
    BR = Body(ya)
    keys = [BR.pose(0, a0, ya, pa, feet=stand_feet(a0, ya, width=0.17))]
    keys.append(BR.pose(0.3, a0, ya, A.STANCE, body(hy=-0.15, lean=20), lhand=hold(0.3, -1), rhand=hold(0.3, 1), feet=stand_feet(a0, ya, width=0.18)))
    BRIDGE = {'spine': r(30), 'chest': r(20), 'neck': r(-40), 'rightUpperLeg': r(-30, 0, 8), 'leftUpperLeg': r(-30, 0, -8), 'rightLowerLeg': r(-110), 'leftLowerLeg': r(-110)}
    keys.append(BR.pose(0.52, [a0[0], -0.25, a0[2] + 0.1], ya, A.STANCE, BRIDGE, body(hy=-0.2, lean=70, spine=(30, 0, 0), chest=(20, 0, 0), neck=(-40, 0, 0)),
                        lhand=hold(0.52, -1), rhand=hold(0.52, 1), lfoot=plant(-0.16, a0[2] - 0.05), rfoot=plant(0.16, a0[2] - 0.05)))
    keys.append(BR.pose(0.82, [a0[0], -0.2, a0[2] + 0.2], ya, A.STANCE, BRIDGE, body(hy=-0.25, lean=110, spine=(30, 0, 0), chest=(20, 0, 0), neck=(-50, 0, 0)),
                        lhand=hold(0.82, -1), rhand=hold(0.82, 1), lfoot=plant(-0.16, a0[2] - 0.05), rfoot=plant(0.16, a0[2] - 0.05)))       # bridge
    keys.append(BR.pose(1.2, [a0[0], -0.2, a0[2] + 0.2], ya, A.STANCE, BRIDGE, body(hy=-0.25, lean=110, spine=(30, 0, 0), chest=(20, 0, 0), neck=(-50, 0, 0)),
                        ARMS_OUT, lfoot=plant(-0.16, a0[2] - 0.05), rfoot=plant(0.16, a0[2] - 0.05)))
    keys.append(BR.pose(1.45, [a0[0], 0, a0[2] + 0.2], ya, A.LIE_BACK, body(hy=-0.8, lean=95)))
    keys.append(BR.pose(1.8, [a0[0], 0, a0[2] + 0.25], ya, A.LIE_BACK))
    L.clip(a_id, 'German suplex', 1.8, keys, fa,
           events=[ev(0.1, 'attack_start'), ev(0.15, 'lift_start'), ev(0.82, 'impact', surface='mat'), ev(0.9, 'release'), ev(1.45, 'land', zone='back')],
           desc='Attacker: from the rear waistlock, lift and arch all the way back into a bridge, dumping the opponent on the neck and shoulders. Holds the bridge, then lies back.',
           tags=['throw', 'suplex', 'attacker', 'finisher'], start_state='rear-lock-hold', end_state='lying-back', placement='center')
    PR.move('pair.german-suplex', 'German suplex', 'throws', a_id, d_id,
            [ev2(0.1, 'attack_start', 'attacker'), ev2(0.15, 'lift_start', 'both'), ev2(0.52, 'apex', 'defender'), ev2(0.82, 'impact', 'defender', surface='mat', zone='neck'),
             ev2(0.9, 'release', 'attacker'), ev2(1.1, 'land', 'defender', zone='front'), ev2(1.45, 'land', 'attacker', zone='back'), ev2(1.8, 'animation_complete', 'both')],
            'From the rear waistlock: bridging German suplex. Defender ends face down, attacker on the back.',
            contacts=[{'from': 0, 'to': 0.9, 'attacker': 'propLeftHand+propRightHand', 'defender': 'hips'}], tags=['suplex', 'finisher'])

    # ================================================================ hip toss and arm drag (from the lock-up)
    LOCK = end_pose(L, 'grappling.lockup')
    DF = dframe(0.61)
    def hip_toss(name, title, mirror_dir, attack_desc, def_desc):
        d_id, a_id = f'throws.{name}-defender', f'throws.{name}-attacker'
        B = Body(180)
        s = mirror_dir                      # +1 throws to the attacker's left (-x)
        keys = [B.pose(0, [0, 0, -0.61], 180, LOCK, feet=stand_feet([0, 0, -0.61], 180, width=0.15))]
        keys.append(B.key(0.3, [-0.05 * s, 1.05, -0.45], [-0.2 * s, 0.98, 0], PZ, FLAIL))
        keys.append(B.key(0.5, [-0.25 * s, 1.55, -0.3], [-1 * s, 0, 0], [0, 0.4, 0.9], FLAIL))           # over the hip, horizontal
        keys.append(B.key(0.68, [-0.65 * s, 0.85, -0.35], [-0.6 * s, -0.8, 0], [0, 0.7, 0.7], FLAIL))
        keys.append(lie_back_key(B, 0.8, [-0.95 * s, -0.4], [1 * s, 0, 0], {'neck': r(20)}))             # flat on the back, head towards the attacker
        keys.append(lie_back_key(B, 0.95, [-0.95 * s, -0.4], [1 * s, 0, 0], {'neck': r(10)}))
        keys.append(lie_back_key(B, 1.4, [-0.95 * s, -0.4], [1 * s, 0, 0]))
        L.clip(d_id, f'{title} (taken)', 1.4, keys, DF,
               events=[ev(0.2, 'lift_start'), ev(0.5, 'apex'), ev(0.8, 'land', zone='back'), ev(0.8, 'impact', surface='mat')],
               desc=f'Defender: {def_desc}', tags=['throw', 'defender', name], start_state='lockup', end_state='lying-back', placement='center', interrupt={'windows': []})
        arm = lambda t: P(d_id, t, 'rightForearm', (0, -0.05, 0))
        waist = lambda t: P(d_id, t, 'hips', (0.0, 0.12, 0.14))
        keys = [K(0, [0, 0, 0], 0, LOCK, feet=stand_feet([0, 0, 0], 0, width=0.15))]
        keys.append(stand(0.2, [-0.05 * s, 0, -0.18], 70 * s, body(hy=-0.2, lean=-8), lhand=waist(0.2), rhand=arm(0.2)))
        keys.append(stand(0.4, [-0.08 * s, 0, -0.22], 85 * s, body(hy=-0.3, lean=-25, roll=10 * s), lhand=waist(0.4), rhand=arm(0.4)))
        keys.append(stand(0.6, [-0.1 * s, 0, -0.22], 85 * s, body(hy=-0.3, lean=-35, roll=10 * s), rhand=arm(0.6)))
        keys.append(stand(0.85, [-0.1 * s, 0, -0.22], 85 * s, body(hy=-0.2, lean=-15)))
        keys.append(K(1.4, [-0.1 * s, 0, -0.22], 85 * s, A.GUARD, feet=stand_feet([-0.1 * s, 0, -0.22], 85 * s)))
        L.clip(a_id, title, 1.4, keys, AT,
               events=[ev(0.1, 'attack_start'), ev(0.2, 'grab', attachment='leftHandGrip'), ev(0.2, 'lift_start'), ev(0.6, 'release'), ev(1.35, 'recover')],
               desc=f'Attacker: {attack_desc}', tags=['throw', 'attacker', name], start_state='lockup', placement='center')
        PR.move(f'pair.{name}', title, 'throws', a_id, d_id,
                [ev2(0.1, 'attack_start', 'attacker'), ev2(0.2, 'grab', 'both'), ev2(0.2, 'lift_start', 'both'), ev2(0.5, 'apex', 'defender'),
                 ev2(0.6, 'release', 'attacker'), ev2(0.8, 'land', 'defender', zone='back'), ev2(0.8, 'impact', 'defender', surface='mat'), ev2(1.4, 'animation_complete', 'both')],
                f'From the lock-up. {def_desc}', contacts=[{'from': 0.2, 'to': 0.6, 'attacker': 'propLeftHand->waist,propRightHand->arm', 'defender': 'hips+rightForearm'}],
                tags=[name])
    hip_toss('hip-toss', 'Hip toss', 1,
             'from the lock-up, turn in, hook the waist with the left arm and pull the opponent over the left hip.',
             'turned into, hooked round the waist and thrown over the attacker\'s hip in a high arc, landing flat on the back.')
    # arm drag: opposite direction, arm-led, faster
    d_id, a_id = 'throws.arm-drag-defender', 'throws.arm-drag-attacker'
    B = Body(180)
    keys = [B.pose(0, [0, 0, -0.61], 180, LOCK, feet=stand_feet([0, 0, -0.61], 180, width=0.15))]
    keys.append(B.key(0.22, [0.1, 1.0, -0.42], [0.35, 0.93, 0.1], PZ, A.only(A.STANCE, A.LEGS), {'leftUpperArm': r(90, 0, 30)}))
    keys.append(B.key(0.42, [0.45, 1.25, -0.3], [0.2, -0.3, 0.93], [0.9, 0.3, 0], FLAIL))                # cartwheels over the arm
    keys.append(B.key(0.58, [0.85, 0.6, -0.15], [-0.6, -0.6, 0.5], [0.2, 0.8, 0.5], FLAIL))
    keys.append(lie_back_key(B, 0.7, [1.05, 0.0], NX, {'neck': r(20)}))
    keys.append(lie_back_key(B, 1.2, [1.05, 0.0], NX))
    L.clip(d_id, 'Arm-dragged', 1.2, keys, DF,
           events=[ev(0.15, 'grab', attachment='leftHand'), ev(0.42, 'apex'), ev(0.7, 'land', zone='back'), ev(0.7, 'impact', surface='mat')],
           desc='Defender: the left arm is trapped and yanked; cartwheels over it and lands on the back off to the attacker\'s right.',
           tags=['throw', 'arm-drag', 'defender'], start_state='lockup', end_state='lying-back', placement='center', interrupt={'windows': []})
    arm = lambda t: P(d_id, t, 'leftForearm', (0, -0.08, 0))
    keys = [K(0, [0, 0, 0], 0, LOCK, feet=stand_feet([0, 0, 0], 0, width=0.15))]
    keys.append(stand(0.15, [0.0, 0, -0.08], -20, body(hy=-0.12, lean=-8), lhand=arm(0.15), rhand=arm(0.15)))
    keys.append(stand(0.35, [0.05, 0, -0.05], -70, body(hy=-0.35, lean=-20, roll=-12), lhand=arm(0.35), rhand=arm(0.35), w=0.18))
    keys.append(K(0.55, [0.1, 0, 0.0], -110, A.STANCE, {'hips': {'p': [0, -0.45, 0.04]}, 'rightUpperLeg': r(80, 0, 6), 'rightLowerLeg': r(-95),
                  'leftUpperLeg': r(-5, 0, -6), 'leftLowerLeg': r(-100), 'leftFoot': r(-55)}, body(hy=-0.45, lean=-12), ARMS_OUT))
    keys.append(K(0.9, [0.1, 0, 0.0], -110, A.STANCE, body(hy=-0.15, lean=-6), A.GUARD, feet=stand_feet([0.1, 0, 0.0], -110)))
    keys.append(K(1.2, [0.1, 0, 0.0], -110, A.GUARD, feet=stand_feet([0.1, 0, 0.0], -110)))
    L.clip(a_id, 'Arm drag', 1.2, keys, AT,
           events=[ev(0.1, 'attack_start'), ev(0.15, 'grab', attachment='propLeftHand'), ev(0.42, 'release'), ev(0.55, 'land', zone='knees'), ev(1.15, 'recover')],
           desc='Attacker: from the lock-up, trap the opponent\'s left arm, drop to one knee turning away and drag them over in a cartwheel; pop back up.',
           tags=['throw', 'arm-drag', 'attacker'], start_state='lockup', placement='center')
    PR.move('pair.arm-drag', 'Arm drag', 'throws', a_id, d_id,
            [ev2(0.1, 'attack_start', 'attacker'), ev2(0.15, 'grab', 'both'), ev2(0.42, 'release', 'attacker'), ev2(0.42, 'apex', 'defender'),
             ev2(0.7, 'land', 'defender', zone='back'), ev2(0.7, 'impact', 'defender', surface='mat'), ev2(1.2, 'animation_complete', 'both')],
            'From the lock-up: the attacker drops and drags the defender over by the arm; the defender cartwheels and lands on the back.',
            contacts=[{'from': 0.15, 'to': 0.42, 'attacker': 'propLeftHand+propRightHand', 'defender': 'leftForearm'}], tags=['arm-drag'])

    build_power(L, PR)


def build_power(L, PR):
    """power moves: powerbomb, chokeslam, powerslam, backbreaker, fireman's carry slam, bulldog"""
    P = PR.p

    # ================================================================ powerbomb (defender bent over in front, 0.55 m)
    fd = dframe(0.55)
    d_id, a_id = 'throws.powerbomb-defender', 'throws.powerbomb-attacker'
    B = Body(180)
    BENTP = {'hips': {'p': [0, -0.1, 0.12], 'r': [-12, 0, 0]}, 'spine': r(-38), 'chest': r(-18), 'neck': r(30), 'head': r(6),
             'rightUpperArm': r(30, 0, -10), 'leftUpperArm': r(30, 0, 10), 'rightForearm': r(100), 'leftForearm': r(100)}
    SITTING_UP = {'rightUpperLeg': r(80, 0, 20), 'leftUpperLeg': r(80, 0, -20), 'rightLowerLeg': r(-90), 'leftLowerLeg': r(-90),
                  'rightUpperArm': r(40, 0, -30), 'leftUpperArm': r(40, 0, 30), 'rightForearm': r(60), 'leftForearm': r(60), 'spine': r(-10)}
    keys = [B.pose(0, [0, 0, -0.55], 180, A.STANCE, BENTP, feet=stand_feet([0, 0, -0.55], 180, width=0.15))]
    keys.append(B.pose(0.3, [0, 0, -0.45], 180, A.STANCE, BENTP, {'hips': {'p': [0, -0.08, 0.12], 'r': [-30, 0, 0]}}, feet=stand_feet([0, 0, -0.45], 180, width=0.15)))
    keys.append(B.key(0.6, [0, 1.35, -0.3], [0, -0.4, 0.92], [0, -0.92, -0.4], SITTING_UP))                   # hoisted, upside down over the back
    keys.append(B.key(0.95, [0, 2.0, -0.12], [0, 0.98, -0.2], [0, 0.2, 0.98], SITTING_UP))                   # sitting up on the shoulders
    keys.append(B.key(1.25, [0, 2.0, -0.15], [0, 0.98, -0.15], [0, 0.15, 0.98], SITTING_UP, {'spine': r(-20), 'neck': r(20)}))
    keys.append(B.key(1.45, [0, 1.1, -0.85], [0, 0.4, 0.92], [0, 0.92, -0.4], FLAIL))
    keys.append(lie_back_key(B, 1.55, [0, -0.95], PZ, {'neck': r(30)}))
    keys.append(lie_back_key(B, 1.7, [0, -0.95], PZ, {'neck': r(15)}))
    keys.append(lie_back_key(B, 2.3, [0, -0.95], PZ))
    L.clip(d_id, 'Powerbombed', 2.3, keys, fd,
           events=[ev(0.3, 'grab'), ev(0.4, 'lift_start'), ev(0.95, 'lift_complete'), ev(1.55, 'land', zone='back'), ev(1.55, 'impact', surface='mat'), ev(1.6, 'stun_start')],
           desc='Defender: bent over, head trapped between the attacker\'s legs; hoisted up to sit on the attacker\'s shoulders, then driven down flat on the back.',
           tags=['throw', 'powerbomb', 'defender'], start_state='bent-over', end_state='lying-back', placement='center', interrupt={'windows': []})
    waist = lambda t, s: P(d_id, t, 'hips', (0.15 * s, 0.1, 0.0))
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(stand(0.3, [0, 0, -0.15], 0, body(hy=-0.3, lean=-35, spine=(-10, 0, 0)), lhand=waist(0.3, -1), rhand=waist(0.3, 1), w=0.22))
    keys.append(stand(0.6, [0, 0, -0.15], 0, body(hy=-0.25, lean=-10), lhand=waist(0.6, -1), rhand=waist(0.6, 1), w=0.22))
    keys.append(stand(0.95, [0, 0, -0.15], 0, body(hy=-0.04, lean=0), lhand=waist(0.95, -1), rhand=waist(0.95, 1), w=0.2))
    keys.append(stand(1.25, [0, 0, -0.15], 0, body(hy=-0.03, lean=2), lhand=waist(1.25, -1), rhand=waist(1.25, 1), w=0.2))
    keys.append(stand(1.45, [0, 0, -0.18], 0, body(hy=-0.35, lean=-35), lhand=waist(1.45, -1), rhand=waist(1.45, 1), w=0.24))
    keys.append(stand(1.55, [0, 0, -0.2], 0, body(hy=-0.45, lean=-45, spine=(-10, 0, 0)), lhand=waist(1.55, -1), rhand=waist(1.55, 1), w=0.26))
    keys.append(stand(1.9, [0, 0, -0.2], 0, body(hy=-0.2, lean=-15)))
    keys.append(K(2.3, [0, 0, -0.2], 0, A.GUARD, feet=stand_feet([0, 0, -0.2], 0)))
    L.clip(a_id, 'Powerbomb', 2.3, keys, AT,
           events=[ev(0.2, 'attack_start'), ev(0.3, 'grab', attachment='leftHandGrip'), ev(0.35, 'grip_locked'), ev(0.4, 'lift_start'), ev(0.95, 'lift_complete'),
                   ev(1.55, 'impact', surface='mat'), ev(1.6, 'release'), ev(2.25, 'recover')],
           desc='Attacker: tuck the bent-over opponent\'s head between the thighs, hook the waist, hoist them up onto the shoulders, pause, and drive them down.',
           tags=['throw', 'powerbomb', 'attacker', 'finisher', 'power'], placement='center')
    PR.move('pair.powerbomb', 'Powerbomb', 'throws', a_id, d_id,
            [ev2(0.2, 'attack_start', 'attacker'), ev2(0.3, 'grab', 'both'), ev2(0.4, 'lift_start', 'both'), ev2(0.95, 'lift_complete', 'both'),
             ev2(1.55, 'impact', 'defender', surface='mat'), ev2(1.55, 'land', 'defender', zone='back'), ev2(1.6, 'release', 'attacker'),
             ev2(2.25, 'recover', 'attacker'), ev2(2.3, 'animation_complete', 'both')],
            'Defender bent over in front (reactions.doubled-over / bent-over-idle): hoisted onto the shoulders and powerbombed flat on the back.',
            contacts=[{'from': 0.3, 'to': 1.6, 'attacker': 'propLeftHand+propRightHand', 'defender': 'hips'}],
            phases=[('contact', 0, 0.4), ('launch', 0.4, 0.95), ('hold', 0.95, 1.25), ('flight', 1.25, 1.55), ('landing', 1.55, 1.7), ('recovery', 1.7, 2.3)],
            tags=['powerbomb', 'finisher'])

    # ================================================================ chokeslam (standing, 0.6 m)
    fd = dframe(0.6)
    d_id, a_id = 'throws.chokeslam-defender', 'throws.chokeslam-attacker'
    B = Body(180)
    keys = [B.pose(0, [0, 0, -0.6], 180, A.GUARD, feet=stand_feet([0, 0, -0.6], 180))]
    keys.append(B.pose(0.25, [0, 0, -0.6], 180, A.STANCE, body(hy=0.0, lean=8, neck=(-20, 0, 0)), {'rightUpperArm': r(70, 0, 10), 'leftUpperArm': r(70, 0, -10), 'rightForearm': r(80), 'leftForearm': r(80)},
                    feet=stand_feet([0, 0, -0.6], 180)))
    keys.append(B.key(0.7, [0, 1.75, -0.55], UP, PZ, A.only(A.STANCE, A.LEGS), {'rightUpperArm': r(70, 0, 10), 'leftUpperArm': r(70, 0, -10), 'rightForearm': r(80), 'leftForearm': r(80),
                      'rightLowerLeg': r(-20), 'leftLowerLeg': r(-30)}))                                          # hoisted high by the throat
    keys.append(B.key(0.95, [0, 1.85, -0.6], [0, 0.95, -0.3], [0, 0.3, 0.95], FLAIL))
    keys.append(B.key(1.1, [0, 0.9, -0.85], [0, 0.3, -0.95], [0, 0.95, 0.3], FLAIL))
    keys.append(lie_back_key(B, 1.18, [0, -0.95], NZ, {'neck': r(30)}))
    keys.append(lie_back_key(B, 1.35, [0, -0.95], NZ, {'neck': r(10)}))
    keys.append(lie_back_key(B, 1.9, [0, -0.95], NZ))
    L.clip(d_id, 'Chokeslammed', 1.9, keys, fd,
           events=[ev(0.15, 'grab', attachment='neck'), ev(0.35, 'lift_start'), ev(0.95, 'lift_complete'), ev(1.18, 'land', zone='back'), ev(1.18, 'impact', surface='mat'), ev(1.25, 'stun_start')],
           desc='Defender: grabbed by the throat, hoisted high, then thrown straight down onto the back.', tags=['throw', 'slam', 'defender'],
           end_state='lying-back', placement='center', interrupt={'windows': []})
    throat = lambda t: P(d_id, t, 'neck', (0, 0.02, -0.07))
    belt = lambda t: P(d_id, t, 'hips', (-0.1, 0.1, 0.0))
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(stand(0.15, [0, 0, -0.05], 0, body(hy=-0.04), rhand=throat(0.15)))
    keys.append(stand(0.35, [0, 0, -0.05], 0, body(hy=-0.2, lean=-10), rhand=throat(0.35), lhand=belt(0.35), w=0.18))
    keys.append(stand(0.7, [0, 0, -0.05], 0, body(hy=-0.02, lean=4), rhand=throat(0.7), lhand=belt(0.7), w=0.18))
    keys.append(stand(0.95, [0, 0, -0.05], 0, body(hy=0.0, lean=6, neck=(-10, 0, 0)), rhand=throat(0.95), w=0.18))
    keys.append(stand(1.12, [0, 0, -0.08], 0, body(hy=-0.3, lean=-35), rhand=throat(1.12), w=0.2))
    keys.append(stand(1.45, [0, 0, -0.08], 0, body(hy=-0.1, lean=-10)))
    keys.append(K(1.9, [0, 0, -0.08], 0, A.GUARD, feet=stand_feet([0, 0, -0.08], 0)))
    L.clip(a_id, 'Chokeslam', 1.9, keys, AT,
           events=[ev(0.1, 'attack_start'), ev(0.15, 'grab', attachment='rightHandGrip'), ev(0.35, 'lift_start'), ev(0.95, 'lift_complete'), ev(1.12, 'release'),
                   ev(1.18, 'impact', surface='mat'), ev(1.85, 'recover')],
           desc='Attacker: right hand to the throat, left hand on the belt; hoist them high and slam them down.', tags=['throw', 'slam', 'attacker', 'finisher', 'power'],
           placement='center')
    PR.move('pair.chokeslam', 'Chokeslam', 'throws', a_id, d_id,
            [ev2(0.1, 'attack_start', 'attacker'), ev2(0.15, 'grab', 'both'), ev2(0.35, 'lift_start', 'both'), ev2(0.95, 'lift_complete', 'both'),
             ev2(1.12, 'release', 'attacker'), ev2(1.18, 'land', 'defender', zone='back'), ev2(1.18, 'impact', 'defender', surface='mat'), ev2(1.9, 'animation_complete', 'both')],
            'From fighting stance 0.6 m apart: chokeslam. Defender ends flat on the back in front of the attacker.',
            contacts=[{'from': 0.15, 'to': 1.12, 'attacker': 'propRightHand->throat', 'defender': 'neck'}], tags=['slam', 'finisher'])

    # ================================================================ scoop powerslam and backbreaker (standing, 0.62 m)
    def scoop(t_keys, d_id, B):
        keys = [B.pose(0, [0, 0, -0.62], 180, A.GUARD, feet=stand_feet([0, 0, -0.62], 180))]
        keys.append(B.key(t_keys[0], [0, 0.98, -0.58], UP, PZ, A.STANCE, TUCK, feet=stand_feet([0, 0, -0.58], 180)))
        keys.append(B.key(t_keys[1], [0.05, 1.45, -0.3], [-1, 0.1, 0], [0, -0.3, 0.95], TUCK))               # draped across the chest, face down
        return keys
    fd = dframe(0.62)
    d_id, a_id = 'throws.powerslam-defender', 'throws.powerslam-attacker'
    B = Body(180)
    keys = scoop((0.3, 0.65), d_id, B)
    keys.append(B.key(0.9, [0.0, 1.2, -0.75], [-1, 0, 0], [0, 0.3, 0.95], TUCK))
    keys.append(B.key(1.05, [0.0, 0.55, -0.95], NX, [0, 0.9, 0.4], FLAIL))
    keys.append(lie_back_key(B, 1.12, [0.0, -0.95], NX, {'neck': r(25)}))
    keys.append(lie_back_key(B, 1.3, [0.0, -0.95], NX))
    keys.append(lie_back_key(B, 2.0, [0.0, -0.95], NX))
    L.clip(d_id, 'Powerslammed', 2.0, keys, fd,
           events=[ev(0.3, 'grab'), ev(0.35, 'lift_start'), ev(0.65, 'lift_complete'), ev(1.12, 'land', zone='back'), ev(1.12, 'impact', surface='mat'), ev(1.2, 'stun_start')],
           desc='Defender: scooped up across the attacker\'s chest and crushed flat on the back as the attacker falls on top.',
           tags=['throw', 'slam', 'defender'], end_state='lying-back', placement='center', interrupt={'windows': []})
    crotch = lambda t: P(d_id, t, 'hips', (0.0, -0.12, 0.0))
    upper = lambda t: P(d_id, t, 'chest', (0.0, 0.05, 0.14))
    COVER = {'hips': {'p': [0, -0.68, 0], 'r': [-80, 0, 0]}, 'spine': r(-6), 'neck': r(30),
             'rightUpperLeg': r(40, 0, 20), 'leftUpperLeg': r(10, 0, -20), 'rightLowerLeg': r(-90), 'leftLowerLeg': r(-60), 'rightFoot': r(-50), 'leftFoot': r(-50)}
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(stand(0.3, [0, 0, -0.1], 0, body(hy=-0.3, lean=-22), rhand=crotch(0.3), lhand=upper(0.3)))
    keys.append(stand(0.65, [0, 0, -0.1], 0, body(hy=-0.05, lean=4), rhand=crotch(0.65), lhand=upper(0.65)))
    keys.append(stand(0.9, [0, 0, -0.3], 0, body(hy=-0.15, lean=-20), rhand=crotch(0.9), lhand=upper(0.9), w=0.18))
    keys.append(K(1.12, [0, 0, -0.75], 0, COVER, lhand=crotch(1.12), rhand=upper(1.12)))
    keys.append(K(1.5, [0, 0, -0.75], 0, COVER))
    keys.append(K(2.0, [0, 0, -0.75], 0, COVER, {'neck': r(40)}))
    L.clip(a_id, 'Scoop powerslam', 2.0, keys, AT,
           events=[ev(0.2, 'attack_start'), ev(0.3, 'grab', attachment='rightHandGrip'), ev(0.35, 'lift_start'), ev(0.65, 'lift_complete'), ev(1.12, 'impact', surface='mat')],
           desc='Attacker: scoop the opponent across the chest, run a step and fall forward on top of them, ending in a cover.',
           tags=['throw', 'slam', 'attacker', 'power'], end_state='covering', placement='center')
    PR.move('pair.powerslam', 'Scoop powerslam', 'throws', a_id, d_id,
            [ev2(0.2, 'attack_start', 'attacker'), ev2(0.3, 'grab', 'both'), ev2(0.35, 'lift_start', 'both'), ev2(0.65, 'lift_complete', 'both'),
             ev2(1.12, 'impact', 'both', surface='mat'), ev2(1.12, 'land', 'defender', zone='back'), ev2(2.0, 'animation_complete', 'both')],
            'From fighting stance: the attacker scoops the defender and falls on top of them. Ends with the attacker lying across the defender (covering).',
            contacts=[{'from': 0.3, 'to': 1.12, 'attacker': 'propRightHand->crotch,propLeftHand->upperBack', 'defender': 'hips+chest'}], tags=['slam', 'power'])

    d_id, a_id = 'throws.backbreaker-defender', 'throws.backbreaker-attacker'
    B = Body(180)
    keys = scoop((0.3, 0.65), d_id, B)
    keys.append(B.key(0.85, [0.0, 1.0, -0.2], [-1, 0.1, 0], [0, 0.95, 0.2], TUCK))
    keys.append(B.key(0.95, [-0.05, 0.75, -0.05], [-1, -0.25, 0], [0, 0.97, 0.1], FLAIL))                # back across the knee, bent
    keys.append(B.key(1.3, [-0.05, 0.72, -0.05], [-1, -0.35, 0], [0, 0.93, 0.1], FLAIL, {'neck': r(-20)}))
    keys.append(B.key(1.6, [-0.1, 0.4, -0.5], [-1, -0.1, 0], [0, 0.6, 0.8], FLAIL))
    keys.append(lie_back_key(B, 1.75, [-0.1, -0.65], NX, {'neck': r(20)}))
    keys.append(lie_back_key(B, 2.3, [-0.1, -0.65], NX))
    L.clip(d_id, 'Backbreakered', 2.3, keys, fd,
           events=[ev(0.3, 'grab'), ev(0.35, 'lift_start'), ev(0.95, 'impact', surface='knee', zone='back'), ev(1.0, 'stun_start'), ev(1.75, 'land', zone='back')],
           desc='Defender: scooped up and dropped back first across the attacker\'s knee, held there bent, then rolled off onto the mat.',
           tags=['throw', 'backbreaker', 'defender'], end_state='lying-back', placement='center', interrupt={'windows': []})
    crotch = lambda t: P(d_id, t, 'hips', (0.0, -0.12, 0.0))
    upper = lambda t: P(d_id, t, 'chest', (0.0, 0.05, 0.14))
    KNEE = {'hips': {'p': [0, -0.48, 0.05]}, 'spine': r(-6),
            'leftUpperLeg': r(90, 0, -6), 'leftLowerLeg': r(-90), 'leftFoot': r(0),
            'rightUpperLeg': r(-10, 0, 6), 'rightLowerLeg': r(-100), 'rightFoot': r(-55)}
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(stand(0.3, [0, 0, -0.1], 0, body(hy=-0.3, lean=-22), rhand=crotch(0.3), lhand=upper(0.3)))
    keys.append(stand(0.65, [0, 0, -0.1], 0, body(hy=-0.05, lean=4), rhand=crotch(0.65), lhand=upper(0.65)))
    keys.append(K(0.95, [0, 0, -0.1], 0, KNEE, rhand=crotch(0.95), lhand=upper(0.95)))
    keys.append(K(1.3, [0, 0, -0.1], 0, KNEE, rhand=crotch(1.3), lhand=upper(1.3)))
    keys.append(K(1.6, [0, 0, -0.1], 0, KNEE, ARMS_OUT, {'hips': {'p': [0, -0.4, 0.05]}}))
    keys.append(stand(1.95, [0, 0, -0.1], 0, body(hy=-0.06)))
    keys.append(K(2.3, [0, 0, -0.1], 0, A.GUARD, feet=stand_feet([0, 0, -0.1], 0)))
    L.clip(a_id, 'Backbreaker', 2.3, keys, AT,
           events=[ev(0.2, 'attack_start'), ev(0.3, 'grab', attachment='rightHandGrip'), ev(0.35, 'lift_start'), ev(0.95, 'impact', surface='knee'), ev(0.95, 'land', zone='knees'),
                   ev(1.5, 'release'), ev(2.25, 'recover')],
           desc='Attacker: scoop the opponent up, drop to one knee and bring their back down across the raised knee, hold, then shove them off.',
           tags=['throw', 'backbreaker', 'attacker'], placement='center')
    PR.move('pair.backbreaker', 'Backbreaker', 'throws', a_id, d_id,
            [ev2(0.2, 'attack_start', 'attacker'), ev2(0.3, 'grab', 'both'), ev2(0.35, 'lift_start', 'both'), ev2(0.95, 'impact', 'defender', surface='knee', zone='back'),
             ev2(1.5, 'release', 'attacker'), ev2(1.75, 'land', 'defender', zone='back'), ev2(2.3, 'animation_complete', 'both')],
            'From fighting stance: backbreaker over the knee; the defender rolls off onto the back.',
            contacts=[{'from': 0.3, 'to': 1.5, 'attacker': 'propRightHand->crotch,propLeftHand->upperBack', 'defender': 'hips+chest'}], tags=['backbreaker'])

    # ================================================================ fireman's carry slam (defender bent over, 0.55 m)
    fd = dframe(0.55)
    d_id, a_id = 'throws.fireman-carry-defender', 'throws.fireman-carry-attacker'
    B = Body(180)
    keys = [B.pose(0, [0, 0, -0.55], 180, A.STANCE, BENTP, feet=stand_feet([0, 0, -0.55], 180, width=0.15))]
    keys.append(B.key(0.4, [0.0, 1.35, -0.25], [0.95, -0.2, 0], [0, -0.98, 0.1], FLAIL))                     # draped over the shoulders
    keys.append(B.key(0.9, [0.0, 1.62, -0.05], [1, -0.05, 0], [0, -0.99, 0.1], FLAIL))
    keys.append(B.key(1.4, [0.0, 1.64, -0.05], [1, -0.05, 0], [0, -0.99, 0.1], FLAIL))
    keys.append(B.key(1.65, [0.0, 1.45, -0.45], [0.7, 0.5, -0.5], [0, 0.6, 0.8], FLAIL))                       # rolled forward off the shoulders
    keys.append(B.key(1.82, [0.0, 0.6, -0.8], [0.1, 0.2, -0.97], [0, 0.97, 0.2], FLAIL))
    keys.append(lie_back_key(B, 1.92, [0.0, -1.05], NZ, {'neck': r(25)}))
    keys.append(lie_back_key(B, 2.6, [0.0, -1.05], NZ))
    L.clip(d_id, 'Fireman\'s carry slam (taken)', 2.6, keys, fd,
           events=[ev(0.2, 'grab'), ev(0.25, 'lift_start'), ev(0.9, 'lift_complete'), ev(1.92, 'land', zone='back'), ev(1.92, 'impact', surface='mat'), ev(2.0, 'stun_start')],
           desc='Defender: hoisted across the attacker\'s shoulders in a fireman\'s carry, carried for a beat, then rolled off forward and slammed onto the back.',
           tags=['throw', 'carry', 'defender'], start_state='bent-over', end_state='lying-back', placement='center', interrupt={'windows': []})
    leg = lambda t: P(d_id, t, 'rightUpperLeg', (0, -0.2, 0))
    arm = lambda t: P(d_id, t, 'leftForearm', (0, 0, 0))
    keys = [K(0, [0, 0, 0], 0, A.GUARD, feet=stand_feet([0, 0, 0], 0))]
    keys.append(stand(0.2, [0, 0, -0.2], 0, body(hy=-0.45, lean=-30), lhand=arm(0.2), rhand=leg(0.2), w=0.22))
    keys.append(stand(0.4, [0, 0, -0.2], 0, body(hy=-0.4, lean=-15), lhand=arm(0.4), rhand=leg(0.4), w=0.22))
    keys.append(stand(0.9, [0, 0, -0.2], 0, body(hy=-0.03, lean=0), lhand=arm(0.9), rhand=leg(0.9), w=0.2))
    keys.append(stand(1.4, [0, 0, -0.25], 0, body(hy=-0.04, lean=-2), lhand=arm(1.4), rhand=leg(1.4), w=0.2))
    keys.append(stand(1.65, [0, 0, -0.3], 0, body(hy=-0.25, lean=-30), lhand=arm(1.65), rhand=leg(1.65), w=0.22))
    keys.append(stand(1.92, [0, 0, -0.32], 0, body(hy=-0.4, lean=-35)))
    keys.append(stand(2.25, [0, 0, -0.32], 0, body(hy=-0.08, lean=-8)))
    keys.append(K(2.6, [0, 0, -0.32], 0, A.GUARD, feet=stand_feet([0, 0, -0.32], 0)))
    L.clip(a_id, 'Fireman\'s carry slam', 2.6, keys, AT,
           events=[ev(0.1, 'attack_start'), ev(0.2, 'grab', attachment='rightHandGrip'), ev(0.25, 'lift_start'), ev(0.9, 'lift_complete'), ev(1.7, 'release'),
                   ev(1.92, 'impact', surface='mat'), ev(2.55, 'recover')],
           desc='Attacker: duck under the bent-over opponent, hook an arm and a leg and stand up with them across the shoulders, then roll them off forward into a slam.',
           tags=['throw', 'carry', 'attacker', 'power'], placement='center')
    PR.move('pair.fireman-carry', 'Fireman\'s carry slam', 'throws', a_id, d_id,
            [ev2(0.1, 'attack_start', 'attacker'), ev2(0.2, 'grab', 'both'), ev2(0.25, 'lift_start', 'both'), ev2(0.9, 'lift_complete', 'both'),
             ev2(1.7, 'release', 'attacker'), ev2(1.92, 'land', 'defender', zone='back'), ev2(1.92, 'impact', 'defender', surface='mat'), ev2(2.6, 'animation_complete', 'both')],
            'Defender bent over in front: fireman\'s carry, then rolled off the shoulders into a slam.',
            contacts=[{'from': 0.2, 'to': 1.7, 'attacker': 'propLeftHand->arm,propRightHand->leg', 'defender': 'leftForearm+rightUpperLeg'}], tags=['carry', 'power'])

    # ================================================================ bulldog (from the side headlock)
    fa, ra, ya, pa = from_setup(L, 'grappling.side-headlock-attacker')
    fd, rd, yd, pd = from_setup(L, 'grappling.side-headlock-defender')
    a0 = [ra[0], 0, ra[2]]
    d_id, a_id = 'throws.bulldog-defender', 'throws.bulldog-attacker'
    B = Body(yd)
    keys = [B.pose(0, rd, yd, pd)]
    keys.append(B.key(0.25, [rd[0], 0.95, rd[2] + 0.15], [0, 0.0, 1], DOWN, A.only(A.STANCE, A.LEGS), ARMS_FWD))
    keys.append(B.key(0.45, [rd[0], 0.55, rd[2] + 0.45], [0, -0.45, 0.89], [0, -0.89, -0.45], A.only(A.LIE_FRONT, A.LEGS), ARMS_OUT))      # face planted
    keys.append(lie_front_key(B, 0.6, [rd[0], rd[2] + 0.35], PZ))
    keys.append(lie_front_key(B, 1.4, [rd[0], rd[2] + 0.35], PZ))
    L.clip(d_id, 'Bulldogged', 1.4, keys, fd,
           events=[ev(0.45, 'impact', surface='mat', zone='head'), ev(0.6, 'land', zone='front'), ev(0.65, 'stun_start')],
           desc='Defender: headlocked as the attacker leaps forward; the face is driven into the mat and they flop flat on the front.',
           tags=['throw', 'bulldog', 'defender'], start_state='headlocked', end_state='lying-front', placement='center', interrupt={'windows': []})
    head = lambda t: P(d_id, t, 'head', (0.0, -0.06, -0.14))
    keys = [K(0, a0, ya, pa, feet=stand_feet(a0, ya, width=0.17))]
    keys.append(K(0.25, [a0[0], 0.2, a0[2] + 0.25], ya, A.STANCE, body(hy=-0.1, lean=-30), rhand=head(0.25), lfoot=air(a0[0] + 0.15, 0.3, a0[2] + 0.1), rfoot=air(a0[0] - 0.15, 0.3, a0[2] + 0.1)))
    SIT = {'hips': {'p': [0, -0.8, 0.05], 'r': [15, 0, 0]}, 'spine': r(-14), 'neck': r(12),
           'rightUpperLeg': r(80, 0, 10), 'leftUpperLeg': r(80, 0, -10), 'rightLowerLeg': r(-20), 'leftLowerLeg': r(-30), 'leftUpperArm': r(-30, 0, 30)}
    keys.append(K(0.45, [a0[0], 0, a0[2] + 0.35], ya, SIT, rhand=head(0.45)))
    keys.append(K(0.6, [a0[0], 0, a0[2] + 0.35], ya, SIT))
    keys.append(K(1.4, [a0[0], 0, a0[2] + 0.35], ya, SIT, {'neck': r(20)}))
    L.clip(a_id, 'Bulldog', 1.4, keys, fa,
           events=[ev(0.1, 'attack_start'), ev(0.15, 'jump'), ev(0.45, 'impact', surface='mat'), ev(0.45, 'land', zone='seat'), ev(0.5, 'release')],
           desc='Attacker: from the side headlock, leap forward and sit down, driving the opponent\'s face into the mat.',
           tags=['throw', 'bulldog', 'attacker'], start_state='headlock-hold', end_state='sitting', placement='center')
    PR.move('pair.bulldog', 'Bulldog', 'throws', a_id, d_id,
            [ev2(0.1, 'attack_start', 'attacker'), ev2(0.15, 'jump', 'attacker'), ev2(0.45, 'impact', 'both', surface='mat'), ev2(0.5, 'release', 'attacker'),
             ev2(0.6, 'land', 'defender', zone='front'), ev2(1.4, 'animation_complete', 'both')],
            'From the side headlock: bulldog. Attacker ends sitting, defender face down.',
            contacts=[{'from': 0, 'to': 0.5, 'attacker': 'rightForearm->head', 'defender': 'head'}], tags=['bulldog'])
