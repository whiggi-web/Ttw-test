"""Phase 2, group C: the corners. Climbing the turnbuckles, perching on top, jumping and falling off, seated and
hanging positions, and getting whipped into the corner.

Corner frame: post at the origin, ropes along +x (z = 0) and +z (x = 0), ring at x > 0 and z > 0, mat y = 0.
Yaw 45 faces the post along the diagonal; yaw -135 has the post behind and faces the ring.
Facing the post, the wrestler's right hand side is the x-rope; facing the ring, the right side is the z-rope.
Turnbuckle pads cover the first ~0.3 m of every rope, so hands and feet go on the ropes 0.33 m or more from the post.
"""
from common import *

D_ = A.DROP
FC, FR = 45, -135                    # yaw: facing the corner / facing the ring
S2 = 0.70711

def diag(d, y=0.0): return [d * S2, y, d * S2]
def xr(h, a=0.36): return on_rope(a, h, 0.0)          # foot on the x-rope, a metres from the post
def zr(h, a=0.36): return on_rope(0.0, h, a)          # foot on the z-rope
def hx(h, a=0.38, up=0.055): return grip(a, h, 0.0, up)
def hz(h, a=0.38, up=0.055): return grip(0.0, h, a, up)
TOP = ROPE_TOP + RR
MID = ROPE_MID + RR
BOT = ROPE_BOT + RR

def facing(t, d, *parts, y=0.0, hands_h=None, feet=None, **kw):
    """facing the corner at diagonal distance d; hands on the given rope height (left on the z-rope, right on the x-rope)"""
    root = diag(d, y)
    hk = {}
    if hands_h is not None: hk = dict(lhand=hz(hands_h), rhand=hx(hands_h))
    if feet is None: kw.setdefault('feet', stand_feet(root, FC, width=0.13))
    else: kw['lfoot'], kw['rfoot'] = feet
    return K(t, root, FC, A.STANCE, *parts, **hk, **kw)

PERCH_CROUCH = {'hips': {'p': [0, -0.42, 0.06], 'r': [-22, 0, 0]}, 'spine': r(-10), 'chest': r(-4), 'neck': r(22),
                'rightUpperArm': r(30, 0, -40), 'leftUpperArm': r(30, 0, 40), 'rightForearm': r(40), 'leftForearm': r(40)}
PERCH_TALL = {'hips': {'p': [0, -0.06, 0], 'r': [-4, 0, 0]}, 'neck': r(4),
              'rightUpperArm': r(10, 0, -70), 'leftUpperArm': r(10, 0, 70), 'rightForearm': r(10), 'leftForearm': r(10)}
SEATED = {'hips': {'p': [0, -0.55, 0.12], 'r': [8, 0, 0]}, 'spine': r(-8), 'neck': r(18), 'head': r(8),
          'rightUpperLeg': r(80, 0, 14), 'leftUpperLeg': r(80, 0, -14), 'rightLowerLeg': r(-80), 'leftLowerLeg': r(-80),
          'rightUpperArm': r(-10, 0, -55), 'leftUpperArm': r(-10, 0, 55), 'rightForearm': r(20), 'leftForearm': r(20)}

def perch(t, *parts, tall=False, sway=0.0, dip=0.0):
    root = [0.19, TOP, 0.19]
    base = PERCH_TALL if tall else PERCH_CROUCH
    hy = (-0.06 if tall else -0.42) - dip
    return K(t, root, FR, A.STANCE, base, body(hy=hy, hz=0.0 if tall else 0.06, lean=-4 if tall else -22, roll=sway * 30,
             spine=(0 if tall else -10, 0, 0), neck=(4 if tall else 22, 0, 0)), *parts, lfoot=xr(ROPE_TOP, 0.34), rfoot=zr(ROPE_TOP, 0.34))

def on_mat_ring(t, d, yaw=FR, *parts, **kw):
    root = diag(d)
    return K(t, root, yaw, A.STANCE, *parts, feet=stand_feet(root, yaw), **kw)


def build(L):
    # ================================================================ approach and grab
    f = A.Frame('corner', diag(2.6) + [FC])
    keys = [stance_at(0, diag(2.6), FC)]
    keys.append(K(0.5, diag(2.0), FC, A.WC, body(hy=-0.03)))
    keys.append(K(1.0, diag(1.38), FC, A.WP, body(hy=-0.012)))
    keys.append(K(1.5, diag(0.8), FC, A.WC, body(hy=-0.03)))
    keys.append(stance_at(1.9, diag(0.62), FC))
    L.clip('turnbuckle.approach-corner', 'Walk to the corner', 1.9, keys, f,
           desc='Walk about 2 m to a corner and stop square to the turnbuckle, ready to climb or hit it.',
           events=steps(0.5, 1.0, 1.5, 1.85), tags=['turnbuckle', 'walk'], placement='inside-facing-corner')

    f = A.facing_corner(0.62)
    keys = [stance_at(0, diag(0.62), FC)]
    keys.append(facing(0.3, 0.52, body(hy=-0.03, lean=-6), {'rightUpperArm': r(80, 0, -30), 'leftUpperArm': r(80, 0, 30)},
                       feet=(plant(*diag(0.6)[0::2]), air(*diag(0.5, 0.08)))))
    keys.append(facing(0.55, 0.46, body(hy=-0.06, lean=-10), hands_h=ROPE_TOP))
    keys.append(facing(0.8, 0.46, body(hy=-0.04, lean=-8), hands_h=ROPE_TOP))
    L.clip('turnbuckle.grab-corner', 'Take hold of the corner', 0.8, keys, f,
           desc='Step in and grab the top rope on both sides of the turnbuckle. Ends holding the corner (start of every climb).',
           events=[ev(0.3, 'footstep'), ev(0.52, 'rope_contact', attachment='rightHandGrip'), ev(0.55, 'grip_locked')],
           tags=['turnbuckle', 'hold'], end_state='corner-hold', placement='inside-facing-corner')

    # ================================================================ climbing, one rope at a time
    f = A.facing_corner(0.46)
    keys = [facing(0, 0.46, body(hy=-0.04, lean=-8), hands_h=ROPE_TOP)]
    keys.append(facing(0.3, 0.46, body(hy=-0.08, lean=-10), hands_h=ROPE_TOP, feet=(plant(*diag(0.5)[0::2]), xr(ROPE_BOT))))
    keys.append(facing(0.6, 0.42, body(hy=-0.1, lean=-12), y=BOT, hands_h=ROPE_TOP, feet=(zr(ROPE_BOT), xr(ROPE_BOT))))
    keys.append(facing(0.85, 0.42, body(hy=-0.06, lean=-10), y=BOT, hands_h=ROPE_TOP, feet=(zr(ROPE_BOT), xr(ROPE_BOT))))
    L.clip('turnbuckle.climb-bottom', 'Climb onto the bottom rope', 0.85, keys, f,
           desc='Holding the corner: right foot onto the bottom rope (x side), then the left (z side). Ends standing on the bottom ropes facing the post.',
           events=[ev(0.3, 'footstep'), ev(0.6, 'footstep')], tags=['turnbuckle', 'climb'], start_state='corner-hold', end_state='corner-climb-1',
           placement='corner-climb')

    f = A.Frame('corner', diag(0.42, BOT) + [FC])
    keys = [facing(0, 0.42, body(hy=-0.06, lean=-10), y=BOT, hands_h=ROPE_TOP, feet=(zr(ROPE_BOT), xr(ROPE_BOT)))]
    keys.append(facing(0.3, 0.42, body(hy=-0.14, lean=-14), y=BOT, hands_h=ROPE_TOP, feet=(zr(ROPE_BOT), xr(ROPE_MID, 0.36))))
    keys.append(facing(0.62, 0.36, body(hy=-0.18, lean=-14), y=MID, lhand=hz(ROPE_TOP, 0.42, 0.06), rhand=hx(ROPE_TOP, 0.42, 0.06),
                       feet=(zr(ROPE_MID), xr(ROPE_MID))))
    keys.append(facing(0.9, 0.36, body(hy=-0.14, lean=-12), y=MID, lhand=hz(ROPE_TOP, 0.42, 0.06), rhand=hx(ROPE_TOP, 0.42, 0.06),
                       feet=(zr(ROPE_MID), xr(ROPE_MID))))
    L.clip('turnbuckle.climb-middle', 'Climb onto the middle rope', 0.9, keys, f,
           desc='From the bottom ropes: step up onto the middle ropes, hands sliding along the top rope. Ends on the middle ropes facing the post.',
           events=[ev(0.3, 'footstep'), ev(0.62, 'footstep')], tags=['turnbuckle', 'climb'], start_state='corner-climb-1', end_state='corner-climb-2',
           placement='corner-climb')

    # middle ropes facing the post -> hop-turn on the middle ropes -> step up to the top, facing the ring
    def turn_and_rise(keys, t0):
        keys.append(K(t0 + 0.25, diag(0.33, MID + 0.12), FC + 90, A.STANCE, body(hy=-0.3, lean=-10), lhand=hz(ROPE_TOP, 0.42, 0.06), rhand=hx(ROPE_TOP, 0.42, 0.06),
                      lfoot=air(0.04, MID + 0.22, 0.36), rfoot=air(0.36, MID + 0.22, 0.04)))
        keys.append(K(t0 + 0.45, diag(0.3, MID), FR, A.STANCE, body(hy=-0.2, lean=-6), lhand=hx(ROPE_TOP, 0.42, 0.06), rhand=hz(ROPE_TOP, 0.42, 0.06),
                      lfoot=xr(ROPE_MID), rfoot=zr(ROPE_MID)))
        keys.append(K(t0 + 0.8, [0.2, MID + 0.05, 0.2], FR, A.STANCE, body(hy=-0.32, lean=-16), lhand=hx(ROPE_TOP, 0.4, 0.04), rhand=hz(ROPE_TOP, 0.4, 0.04),
                      lfoot=xr(ROPE_TOP, 0.34), rfoot=zr(ROPE_MID)))
        keys.append(perch(t0 + 1.15, dip=0.06))
        keys.append(perch(t0 + 1.45))
    keys = [facing(0, 0.36, body(hy=-0.14, lean=-12), y=MID, lhand=hz(ROPE_TOP, 0.42, 0.06), rhand=hx(ROPE_TOP, 0.42, 0.06), feet=(zr(ROPE_MID), xr(ROPE_MID)))]
    turn_and_rise(keys, 0.0)
    f = A.Frame('corner', diag(0.36, MID) + [FC])
    L.clip('turnbuckle.climb-top', 'Turn and climb to the top', 1.45, keys, f,
           desc='From the middle ropes: hop round to put the back to the post, step up onto the top ropes and settle in a crouch facing the ring.',
           events=[ev(0.2, 'jump'), ev(0.45, 'footstep'), ev(0.8, 'footstep'), ev(1.15, 'footstep'), ev(1.4, 'recover')],
           tags=['turnbuckle', 'climb', 'aerial-setup'], start_state='corner-climb-2', end_state='perched', placement='corner-climb', end_placement='perched')

    f = A.facing_corner(0.46)
    keys = [facing(0, 0.46, body(hy=-0.04, lean=-8), hands_h=ROPE_TOP)]
    keys.append(facing(0.28, 0.44, body(hy=-0.1, lean=-12), hands_h=ROPE_TOP, feet=(plant(*diag(0.5)[0::2]), xr(ROPE_BOT))))
    keys.append(facing(0.55, 0.4, body(hy=-0.14, lean=-14), y=BOT, hands_h=ROPE_TOP, feet=(zr(ROPE_BOT), xr(ROPE_MID))))
    keys.append(facing(0.85, 0.36, body(hy=-0.16, lean=-14), y=MID, lhand=hz(ROPE_TOP, 0.42, 0.06), rhand=hx(ROPE_TOP, 0.42, 0.06), feet=(zr(ROPE_MID), xr(ROPE_MID))))
    turn_and_rise(keys, 0.85)
    L.clip('turnbuckle.climb-full', 'Climb the turnbuckle', 2.3, keys, f,
           desc='One smooth climb from holding the corner to crouching on the top turnbuckle facing the ring.',
           events=[ev(0.28, 'footstep'), ev(0.55, 'footstep'), ev(0.85, 'footstep'), ev(1.05, 'jump'), ev(1.3, 'footstep'), ev(1.65, 'footstep'), ev(2.0, 'footstep'), ev(2.25, 'recover')],
           tags=['turnbuckle', 'climb', 'aerial-setup'], start_state='corner-hold', end_state='perched', placement='corner-climb', end_placement='perched',
           phases=[('approach', 0, 0.28), ('traversal', 0.28, 2.0), ('recovery', 2.0, 2.3)])

    # top ropes facing the post (moonsault position)
    f = A.Frame('corner', diag(0.36, MID) + [FC])
    keys = [facing(0, 0.36, body(hy=-0.14, lean=-12), y=MID, lhand=hz(ROPE_TOP, 0.42, 0.06), rhand=hx(ROPE_TOP, 0.42, 0.06), feet=(zr(ROPE_MID), xr(ROPE_MID)))]
    keys.append(facing(0.35, 0.33, body(hy=-0.3, lean=-20), y=MID + 0.05, lhand=hz(ROPE_TOP, 0.4, 0.04), rhand=hx(ROPE_TOP, 0.4, 0.04), feet=(zr(ROPE_MID), xr(ROPE_TOP, 0.36))))
    keys.append(facing(0.7, 0.3, body(hy=-0.4, lean=-24, neck=(26, 0, 0)), {'rightUpperArm': r(40, 0, -50), 'leftUpperArm': r(40, 0, 50)}, y=TOP, feet=(zr(ROPE_TOP), xr(ROPE_TOP))))
    keys.append(facing(1.1, 0.3, body(hy=-0.08, lean=-4), ARMS_BALANCE, y=TOP, feet=(zr(ROPE_TOP), xr(ROPE_TOP))))
    keys.append(facing(1.4, 0.3, body(hy=-0.06, lean=-2), ARMS_BALANCE, y=TOP, feet=(zr(ROPE_TOP), xr(ROPE_TOP))))
    L.clip('turnbuckle.climb-top-facing-out', 'Stand on the top rope facing out', 1.4, keys, f,
           desc='From the middle ropes: step up and stand tall on the top ropes with the back to the ring (moonsault and backflip position).',
           events=[ev(0.35, 'footstep'), ev(0.7, 'footstep'), ev(1.3, 'recover')], tags=['turnbuckle', 'climb', 'aerial-setup'],
           start_state='corner-climb-2', end_state='corner-top-out', placement='corner-climb')

    # ================================================================ perched
    f = A.perched()
    keys = [perch(0), perch(0.6, sway=0.05, dip=0.02), perch(1.2, sway=-0.02, dip=-0.02), perch(1.8, sway=-0.05, dip=0.02), perch(2.4)]
    L.clip('turnbuckle.perched-idle', 'Perched on the top turnbuckle (loop)', 2.4, keys, f, loop=True,
           desc='Crouched on the top ropes, back to the post, balancing with small arm movements.',
           tags=['turnbuckle', 'perched', 'loop'], start_state='perched', end_state='perched', placement='perched')

    keys = [perch(0), perch(0.3, dip=0.06), perch(0.65, tall=True, dip=0.04), perch(0.8, ARMS_UP, tall=True, dip=-0.03), perch(1.0, ARMS_UP, tall=True)]
    L.clip('turnbuckle.prepare-jump', 'Rise up on the top turnbuckle', 1.0, keys, f,
           desc='From the crouch: stand up tall on the top ropes and raise the arms. Ends perched-ready, the take-off pose for every top-rope dive.',
           events=[ev(0.65, 'recover')], tags=['turnbuckle', 'perched', 'aerial-setup'], start_state='perched', end_state='perched-ready', placement='perched')

    keys = [perch(0, ARMS_UP, tall=True), perch(0.3, ARMS_BALANCE, tall=True, dip=0.06), perch(0.65, dip=0.04), perch(0.9)]
    L.clip('turnbuckle.crouch-top', 'Crouch back down on top', 0.9, keys, f,
           desc='From standing tall on the top ropes: bring the arms down and sink back into the balanced crouch.',
           tags=['turnbuckle', 'perched'], start_state='perched-ready', end_state='perched', placement='perched')

    pose_up = {'rightUpperArm': r(0, 0, 150), 'leftUpperArm': r(0, 0, -150), 'rightForearm': r(30), 'leftForearm': r(30), 'neck': r(-14), 'chest': r(-4)}
    keys = [perch(0), perch(0.35, dip=0.05), perch(0.75, pose_up, tall=True), perch(1.3, pose_up, {'rightForearm': r(80), 'leftForearm': r(80)}, tall=True, dip=-0.04),
            perch(1.8, pose_up, tall=True), perch(2.25, dip=0.05), perch(2.6)]
    L.clip('turnbuckle.taunt-top', 'Pose on the top turnbuckle', 2.6, keys, f,
           desc='Rise up on the top ropes, arms raised to the crowd, flex, then crouch back down.',
           events=[ev(1.3, 'apex')], tags=['turnbuckle', 'perched', 'taunt'], start_state='perched', end_state='perched', placement='perched')

    look = lambda a, b=0: {'neck': r(18, a * 0.5, 0), 'head': r(6, a * 0.5, 0), 'chest': r(0, a * 0.3, 0), 'rightUpperArm': r(30 + b, 0, -40)}
    keys = [perch(0), perch(0.6, look(-55)), perch(1.2, look(-50, 60), {'rightForearm': r(20)}), perch(1.9, look(50)), perch(2.5, look(55, 50)), perch(3.0)]
    L.clip('turnbuckle.look-crowd', 'Look round the crowd from the top', 3.0, keys, f,
           desc='Crouched on top: scan the crowd left, point, scan right, point.',
           tags=['turnbuckle', 'perched', 'taunt'], start_state='perched', end_state='perched', placement='perched')

    wobble = lambda a: {'rightUpperArm': r(40 + a, 0, -90), 'leftUpperArm': r(40 - a, 0, 90), 'rightForearm': r(10), 'leftForearm': r(10)}
    keys = [perch(0, tall=True), perch(0.2, wobble(60), tall=True, sway=0.25, dip=0.04), perch(0.45, wobble(-70), tall=True, sway=-0.3, dip=0.08),
            perch(0.7, wobble(50), sway=0.15, dip=0.1), perch(1.0, sway=-0.05, dip=0.04), perch(1.3)]
    L.clip('turnbuckle.recover-balance', 'Wobble and steady on top', 1.3, keys, f,
           desc='Standing on the top ropes: lose the balance, windmill the arms and drop into the crouch to steady.',
           tags=['turnbuckle', 'perched', 'balance'], start_state='perched-ready', end_state='perched', placement='perched')

    # ================================================================ getting down
    keys = [perch(0)]
    keys.append(K(0.3, [0.24, TOP, 0.24], FR, A.STANCE, PERCH_CROUCH, body(hy=-0.5, lean=-26), ARMS_FWD, lfoot=xr(ROPE_TOP, 0.34), rfoot=zr(ROPE_TOP, 0.34)))
    keys.append(K(0.5, diag(0.7, 0.75), FR, A.STANCE, body(hy=-0.16, lean=-6), ARMS_OUT, lfoot=air(*diag(0.75, 0.62)), rfoot=air(*diag(0.65, 0.62))))
    keys.append(K(0.72, diag(1.1, 0.0), FR, A.STANCE, body(hy=-0.36, lean=-14, spine=(-10, 0, 0)), ARMS_OUT, feet=stand_feet(diag(1.1), FR, width=0.16)))
    keys.append(on_mat_ring(1.05, 1.1))
    L.clip('turnbuckle.jump-down', 'Hop down into the ring', 1.05, keys, f,
           desc='From the crouch on top: push off gently and drop down into the ring, landing about 0.8 m out.',
           events=[ev(0.3, 'jump'), ev(0.72, 'land'), ev(1.0, 'recover')], tags=['turnbuckle', 'perched', 'dismount'], start_state='perched',
           placement='perched', end_placement='center')

    keys = [perch(0)]
    keys.append(K(0.35, [0.22, TOP, 0.22], FR + 90, A.STANCE, body(hy=-0.4, lean=-14), lhand=hx(ROPE_TOP, 0.42, 0.06), rhand=hz(ROPE_TOP, 0.42, 0.06),
                  lfoot=xr(ROPE_TOP, 0.34), rfoot=zr(ROPE_MID, 0.36)))
    keys.append(K(0.7, diag(0.32, MID), FC, A.STANCE, body(hy=-0.18, lean=-14), lhand=hz(ROPE_TOP, 0.42, 0.06), rhand=hx(ROPE_TOP, 0.42, 0.06),
                  lfoot=zr(ROPE_MID), rfoot=xr(ROPE_MID)))
    keys.append(facing(1.05, 0.42, body(hy=-0.1, lean=-12), y=BOT, hands_h=ROPE_TOP, feet=(zr(ROPE_BOT), xr(ROPE_BOT))))
    keys.append(facing(1.4, 0.5, body(hy=-0.06, lean=-8), hands_h=ROPE_TOP, feet=(plant(*diag(0.55)[0::2]), xr(ROPE_BOT))))
    keys.append(facing(1.7, 0.55, body(hy=-0.04, lean=-6), hands_h=ROPE_TOP))
    keys.append(stance_at(2.0, diag(0.7), FC))
    L.clip('turnbuckle.climb-down', 'Climb down from the top', 2.0, keys, f,
           desc='From the crouch on top: turn to face the post and climb back down the ropes into the ring.',
           events=[ev(0.35, 'footstep'), ev(0.7, 'footstep'), ev(1.05, 'footstep'), ev(1.4, 'footstep'), ev(1.75, 'rope_release'), ev(1.95, 'recover')],
           tags=['turnbuckle', 'perched', 'dismount'], start_state='perched', placement='perched', end_placement='inside-facing-corner')

    # ================================================================ jumps from perched-ready
    def take_off(keys):
        keys.append(perch(0.18, ARMS_FWD, tall=True, dip=0.2))
        keys.append(K(0.32, [0.26, TOP + 0.04, 0.26], FR, A.STANCE, body(hy=-0.04, lean=-10), ARMS_UP, lfoot=xr(ROPE_TOP, 0.34), rfoot=zr(ROPE_TOP, 0.34)))
    keys = [perch(0, ARMS_UP, tall=True)]
    take_off(keys)
    keys.append(K(0.6, diag(1.3, 0.85), FR, A.STANCE, body(hy=-0.1, lean=-6), ARMS_UP, lfoot=air(*diag(1.25, 0.72)), rfoot=air(*diag(1.15, 0.7))))
    keys.append(K(0.86, diag(2.2, 0.35), FR, A.STANCE, body(hy=-0.1), ARMS_OUT, lfoot=air(*diag(2.25, 0.3)), rfoot=air(*diag(2.15, 0.3))))
    keys.append(K(0.98, diag(2.45), FR, A.STANCE, body(hy=-0.45, lean=-18, spine=(-12, 0, 0)), ARMS_OUT, feet=stand_feet(diag(2.45), FR, width=0.17)))
    keys.append(on_mat_ring(1.35, 2.45))
    L.clip('turnbuckle.jump-forward', 'Leap forward off the top', 1.35, keys, f,
           desc='From standing tall on top: spring forward and land on the feet about 2 m out, absorbing a 1.3 m drop.',
           events=[ev(0.32, 'jump'), ev(0.6, 'apex'), ev(0.98, 'land'), ev(0.98, 'impact', surface='mat'), ev(1.3, 'recover')],
           tags=['turnbuckle', 'aerial', 'dismount'], start_state='perched-ready', placement='perched', end_placement='center',
           phases=[('launch', 0, 0.32), ('flight', 0.32, 0.98), ('landing', 0.98, 1.15), ('recovery', 1.15, 1.35)])

    keys = [perch(0, ARMS_UP, tall=True)]
    keys.append(perch(0.18, ARMS_OUT, tall=True, dip=0.2))
    side = lambda d, s: [d * S2 + s * 0.55, 0, d * S2 - s * 0.55]       # off the diagonal, towards the x-rope side
    keys.append(K(0.34, [0.3, TOP + 0.05, 0.22], FR + 30, A.STANCE, body(hy=-0.04, roll=-12), ARMS_OUT, lfoot=xr(ROPE_TOP, 0.34), rfoot=air(0.1, TOP + 0.2, 0.4)))
    p1 = side(1.0, 0.6); p1[1] = 0.8
    keys.append(K(0.62, p1, FR + 60, A.STANCE, body(hy=-0.1, roll=-10), ARMS_OUT, lfoot=air(p1[0] + 0.05, 0.65, p1[2] - 0.1), rfoot=air(p1[0] - 0.05, 0.65, p1[2] + 0.1)))
    p2 = side(1.6, 1.0)
    keys.append(K(0.92, p2, FR + 75, A.STANCE, body(hy=-0.44, lean=-16, spine=(-10, 0, 0)), ARMS_OUT, feet=stand_feet(p2, FR + 75, width=0.17)))
    keys.append(K(1.3, p2, FR + 75, A.STANCE, feet=stand_feet(p2, FR + 75)))
    L.clip('turnbuckle.jump-sideways', 'Leap sideways off the top', 1.3, keys, f,
           desc='From standing tall on top: jump out to the right side along the ropes, turning in the air, and land facing across the ring.',
           events=[ev(0.34, 'jump'), ev(0.62, 'apex'), ev(0.92, 'land'), ev(1.25, 'recover')], tags=['turnbuckle', 'aerial', 'dismount'],
           start_state='perched-ready', placement='perched', end_placement='center',
           phases=[('launch', 0, 0.34), ('flight', 0.34, 0.92), ('landing', 0.92, 1.1), ('recovery', 1.1, 1.3)])

    # backflip off the top (facing out) to the feet in the ring
    f = A.Frame('corner', diag(0.3, TOP) + [FC])
    keys = [facing(0, 0.3, body(hy=-0.06, lean=-2), ARMS_BALANCE, y=TOP, feet=(zr(ROPE_TOP), xr(ROPE_TOP)))]
    keys.append(facing(0.22, 0.3, body(hy=-0.32, lean=-16), {'rightUpperArm': r(-40, 0, -20), 'leftUpperArm': r(-40, 0, 20)}, y=TOP, feet=(zr(ROPE_TOP), xr(ROPE_TOP))))
    tuck = {'rightUpperLeg': r(110, 0, 8), 'leftUpperLeg': r(110, 0, -8), 'rightLowerLeg': r(-120), 'leftLowerLeg': r(-120),
            'rightUpperArm': r(60, 0, -20), 'leftUpperArm': r(60, 0, 20), 'rightForearm': r(70), 'leftForearm': r(70)}
    keys.append(K(0.42, diag(0.55, TOP + 0.45), FC, A.STANCE, body(hy=-0.1, lean=60), ARMS_UP))
    keys.append(K(0.62, diag(1.05, TOP + 0.35), FC, tuck, body(hy=-0.25, lean=180)))
    keys.append(K(0.82, diag(1.5, 0.55), FC, tuck, body(hy=-0.2, lean=300)))
    keys.append(K(0.98, diag(1.75), FC, A.STANCE, body(hy=-0.46, lean=342, spine=(-12, 0, 0)), ARMS_OUT, feet=stand_feet(diag(1.75), FC, width=0.17)))
    keys.append(K(1.4, diag(1.75), FC, A.STANCE, body(lean=360, hy=-0.02), feet=stand_feet(diag(1.75), FC)))
    L.clip('turnbuckle.jump-backward', 'Backflip off the top', 1.4, keys, f,
           desc='Standing on the top ropes facing out: dip, throw the arms and backflip into the ring, landing on the feet facing the post.',
           events=[ev(0.3, 'jump'), ev(0.62, 'apex'), ev(0.98, 'land'), ev(0.98, 'impact', surface='mat'), ev(1.35, 'recover')],
           tags=['turnbuckle', 'aerial', 'athletic', 'dismount'], start_state='corner-top-out', placement='corner-climb', end_placement='inside-facing-corner',
           phases=[('launch', 0, 0.3), ('flight', 0.3, 0.98), ('landing', 0.98, 1.15), ('recovery', 1.15, 1.4)])

    # ================================================================ coming off the top the wrong way
    f = A.perched()
    keys = [perch(0)]
    keys.append(perch(0.25, wobble(-60), sway=-0.2, dip=0.05))
    keys.append(K(0.5, [0.45, TOP - 0.05, 0.45], FR, A.STANCE, body(hy=-0.2, lean=-40), ARMS_FWD, lfoot=xr(ROPE_TOP, 0.34), rfoot=air(0.15, TOP + 0.1, 0.4)))
    keys.append(K(0.75, diag(1.3, 0.45), FR, A.STANCE, body(hy=-0.3, lean=-75), ARMS_FWD))
    keys.append(K(0.92, diag(1.75, 0.0), FR, A.LIE_FRONT, body(hy=-0.8, lean=-92), {'rightUpperArm': r(0, 0, 100), 'leftUpperArm': r(0, 0, -100), 'rightForearm': r(10), 'leftForearm': r(10)}))
    keys.append(K(1.1, diag(1.8), FR, A.LIE_FRONT))
    keys.append(K(1.5, diag(1.8), FR, A.LIE_FRONT))
    L.clip('turnbuckle.fall', 'Fall off the top', 1.5, keys, f,
           desc='Crouched on top: lose the footing, pitch forward and crash face first onto the mat.',
           events=[ev(0.5, 'jump'), ev(0.92, 'land', zone='front'), ev(0.92, 'impact', surface='mat'), ev(1.0, 'stun_start')],
           tags=['turnbuckle', 'fall'], start_state='perched', end_state='lying-front', placement='perched', end_placement='center',
           phases=[('contact', 0, 0.5), ('flight', 0.5, 0.92), ('landing', 0.92, 1.1), ('recovery', 1.1, 1.5)])

    # pushed off backwards to the floor outside the corner
    keys = [perch(0)]
    keys.append(K(0.15, [0.17, TOP, 0.17], FR, A.STANCE, PERCH_CROUCH, body(hy=-0.36, lean=10, neck=(-10, 0, 0)), ARMS_OUT, lfoot=xr(ROPE_TOP, 0.34), rfoot=zr(ROPE_TOP, 0.34)))
    keys.append(K(0.42, [-0.25, TOP + 0.35, -0.25], FR, A.STANCE, body(hy=-0.1, lean=60), ARMS_OUT, {'rightUpperLeg': r(70), 'leftUpperLeg': r(60)}))
    keys.append(K(0.72, [-0.85, 0.2, -0.85], FR, A.LIE_BACK, body(hy=-0.3, lean=80), ARMS_OUT))
    keys.append(K(0.92, [-1.15, D_, -1.15], FR, A.LIE_BACK))
    keys.append(K(1.4, [-1.2, D_, -1.2], FR, A.LIE_BACK))
    L.clip('turnbuckle.pushed-off', 'Shoved off the top to the floor', 1.4, keys, f,
           desc='Crouched on top: a shove to the chest sends them backwards over the corner, falling 2.4 m to land flat on the back on the floor outside.',
           events=[ev(0.15, 'hit_received', zone='body'), ev(0.42, 'apex'), ev(0.92, 'land', zone='back', height=2.4), ev(0.92, 'impact', surface='floor')],
           tags=['turnbuckle', 'fall', 'to-floor', 'elimination'], start_state='perched', end_state='lying-back', end_loc='floor', placement='perched',
           end_placement='floor-facing-ring', phases=[('contact', 0, 0.2), ('flight', 0.2, 0.92), ('landing', 0.92, 1.1), ('recovery', 1.1, 1.4)],
           interrupt={'windows': []})

    # thrown off into the ring, flipping onto the back
    keys = [perch(0)]
    keys.append(K(0.18, [0.26, TOP + 0.05, 0.26], FR, A.STANCE, PERCH_CROUCH, body(hy=-0.25, lean=-30), ARMS_FWD, lfoot=xr(ROPE_TOP, 0.34), rfoot=zr(ROPE_TOP, 0.34)))
    keys.append(K(0.45, diag(1.2, 0.95), FR, A.STANCE, body(hy=-0.1, lean=-110), ARMS_OUT, {'rightUpperLeg': r(-20), 'leftUpperLeg': r(-30)}))
    keys.append(K(0.7, diag(2.0, 0.5), FR, A.LIE_BACK, body(hy=-0.4, lean=-215), ARMS_OUT))
    keys.append(K(0.86, diag(2.35, 0.0), FR, A.LIE_BACK, body(hy=-0.83, lean=-270)))
    keys.append(K(1.3, diag(2.4), FR, A.LIE_BACK, body(hy=-0.83, lean=-270)))
    L.clip('turnbuckle.thrown-off', 'Thrown off the top', 1.3, keys, f,
           desc='Crouched on top: hurled forward into the ring, flipping over in the air and landing flat on the back about 2 m out.',
           events=[ev(0.18, 'grab'), ev(0.25, 'release'), ev(0.45, 'apex'), ev(0.86, 'land', zone='back', height=1.3), ev(0.86, 'impact', surface='mat')],
           tags=['turnbuckle', 'fall', 'thrown'], start_state='perched', end_state='lying-back', placement='perched', end_placement='center',
           phases=[('contact', 0, 0.25), ('flight', 0.25, 0.86), ('landing', 0.86, 1.0), ('recovery', 1.0, 1.3)], interrupt={'windows': []})

    # knocked off balance: drop onto the top turnbuckle, seated
    def seated(t, sway=0.0, sag=0.0, look=0):
        root = [0.22, TOP - 0.05, 0.22]
        # hips sit on the turnbuckle, thighs over the top ropes, shins hanging into the ring
        return K(t, root, FR, SEATED, body(hy=-0.84 - sag, hz=0.08, lean=8, roll=sway * 30, spine=(-8, 0, 0), neck=(18, look, 0)),
                 lhand=hx(ROPE_TOP, 0.45, 0.04), rhand=hz(ROPE_TOP, 0.45, 0.04),
                 lfoot=air(0.68, TOP - 0.42, 0.46), rfoot=air(0.46, TOP - 0.42, 0.68))
    keys = [perch(0, tall=True), perch(0.15, wobble(60), tall=True, sway=0.25, dip=0.04)]
    keys.append(K(0.35, [0.2, TOP - 0.02, 0.2], FR, A.STANCE, body(hy=-0.4, lean=10, neck=(-10, 0, 0)), ARMS_OUT, lfoot=air(0.5, TOP - 0.1, 0.25), rfoot=zr(ROPE_TOP, 0.34)))
    keys.append(seated(0.55, sag=0.06))
    keys.append(seated(0.85))
    L.clip('turnbuckle.knocked-off-balance', 'Knocked down onto the turnbuckle', 0.85, keys, f,
           desc='Standing on top: a hit to the legs drops them seated on the top turnbuckle, legs dangling into the ring, dazed (superplex position).',
           events=[ev(0.15, 'hit_received', zone='legs'), ev(0.55, 'impact', surface='turnbuckle'), ev(0.6, 'stun_start')],
           tags=['turnbuckle', 'seated', 'stunned'], start_state='perched-ready', end_state='corner-seated', placement='perched', interrupt={'windows': []})

    keys = [seated(0), seated(0.7, sway=0.12, sag=0.03, look=20), seated(1.4, sway=-0.05), seated(2.1, sway=-0.1, sag=0.03, look=-20), seated(2.8)]
    L.clip('turnbuckle.seated-dazed', 'Seated on the top turnbuckle (loop)', 2.8, keys, f, loop=True,
           desc='Sitting on the top turnbuckle facing the ring, legs dangling, swaying and dazed.',
           tags=['turnbuckle', 'seated', 'loop', 'stunned'], start_state='corner-seated', end_state='corner-seated', placement='perched')

    # tree of woe: slide back off the seat and hang upside down, legs hooked in the top ropes
    INV = {'hips': {'p': [0, -0.1, 0], 'r': [0, 0, 180]}, 'spine': r(6), 'chest': r(4), 'neck': r(10),
           'rightUpperArm': r(0, 0, 160), 'leftUpperArm': r(0, 0, -160), 'rightForearm': r(10), 'leftForearm': r(10)}
    def woe(t, sway=0.0, sag=0.0, roll_form=False):
        # Rx(186) Ry(180) == Rx(6) Rz(180): same orientation, two Euler forms. The roll form interpolates from upright
        # (the slide into the corner); the pitch form interpolates on into lying down (the drop out of it).
        root = [0.24, 0.0, 0.24]
        hr = [6, 0, 180 + sway * 20] if roll_form else [186, 180, sway * 20]
        return K(t, root, FR, INV, {'hips': {'p': [0, 0.2 - sag, 0.1], 'r': hr}, 'rightUpperArm': r(0, 0, 135), 'leftUpperArm': r(0, 0, -135)},
                 lfoot=air(0.52, ROPE_TOP - 0.02, -0.05, flat=False), rfoot=air(-0.05, ROPE_TOP - 0.02, 0.52, flat=False),
                 poles={'leftFoot': [0, -1, 1], 'rightFoot': [0, -1, 1]})
    keys = [seated(0), seated(0.25, sag=0.08)]
    keys.append(K(0.55, [0.24, 0.3, 0.24], FR, A.STANCE, {'hips': {'p': [0, -0.2, 0.1], 'r': [10, 0, 95]}}, ARMS_OUT,
                  lfoot=air(0.52, ROPE_TOP + 0.02, -0.04, flat=False), rfoot=air(-0.04, ROPE_TOP + 0.02, 0.52, flat=False)))
    keys.append(woe(0.85, sag=-0.05, roll_form=True))
    keys.append(woe(1.2, roll_form=True))
    L.clip('turnbuckle.hang-from-corner', 'Slip into the tree of woe', 1.2, keys, f,
           desc='Seated on top: slide back off the turnbuckle and end hanging upside down against the pad, legs hooked in the top ropes.',
           events=[ev(0.55, 'rope_contact', attachment='leftFoot'), ev(0.85, 'grip_locked'), ev(0.9, 'stun_start')],
           tags=['turnbuckle', 'hanging', 'tree-of-woe', 'stunned'], start_state='corner-seated', end_state='corner-hanging', placement='perched',
           interrupt={'windows': []})

    keys = [woe(0), woe(0.8, sway=0.15, sag=0.02), woe(1.6, sway=-0.1), woe(2.4, sway=0.05, sag=0.02), woe(3.2)]
    L.clip('turnbuckle.hanging-idle', 'Hanging in the corner (loop)', 3.2, keys, f, loop=True,
           desc='Hanging upside down in the corner, legs hooked in the top ropes, arms dangling to the mat.',
           tags=['turnbuckle', 'hanging', 'tree-of-woe', 'loop', 'stunned'], start_state='corner-hanging', end_state='corner-hanging', placement='perched')

    keys = [woe(0), woe(0.3, sag=-0.04)]
    # the head slides out towards the ring while the legs come down at the post: hips pitch on through 270 (Rx(x) Ry(180))
    keys.append(K(0.6, [0.55, 0, 0.55], FR, A.LIE_BACK, {'hips': {'p': [0, -0.3, 0], 'r': [225, 180, 0]}}, {'rightUpperLeg': r(-30), 'leftUpperLeg': r(-30)}))
    keys.append(K(0.9, diag(1.15), FR, A.LIE_BACK, {'hips': {'p': [0, -0.83, 0], 'r': [270, 180, 0]}}))
    keys.append(K(1.3, diag(1.15), FR, A.LIE_BACK, {'hips': {'p': [0, -0.83, 0], 'r': [270, 180, 0]}}))
    L.clip('turnbuckle.hanging-drop', 'Drop out of the tree of woe', 1.3, keys, f,
           desc='Unhook the legs and flop down out of the corner, ending flat on the back with the feet at the post and the head towards the ring.',
           events=[ev(0.3, 'rope_release'), ev(0.9, 'land', zone='back'), ev(0.9, 'impact', surface='mat')],
           tags=['turnbuckle', 'hanging', 'recover'], start_state='corner-hanging', end_state='lying-back', placement='perched', end_placement='center')

    # ================================================================ missed and botched dives
    f = A.perched()
    keys = [perch(0, ARMS_UP, tall=True)]
    take_off(keys)
    splash = {'rightUpperArm': r(0, 0, 100), 'leftUpperArm': r(0, 0, -100), 'rightForearm': r(10), 'leftForearm': r(10),
              'rightUpperLeg': r(-6, 0, 10), 'leftUpperLeg': r(-6, 0, -10)}
    keys.append(K(0.6, diag(1.3, 0.9), FR, A.STANCE, body(hy=-0.3, lean=-60), splash))
    keys.append(K(0.84, diag(2.1, 0.35), FR, A.STANCE, body(hy=-0.55, lean=-88), splash))
    keys.append(K(0.96, diag(2.35, 0.0), FR, A.LIE_FRONT, body(hy=-0.86, lean=-90), splash))
    keys.append(K(1.15, diag(2.4), FR, A.LIE_FRONT, {'rightUpperArm': r(0, 0, 90), 'leftUpperArm': r(0, 0, -90)}, body(hy=-0.82, lean=-90)))
    keys.append(K(1.5, diag(2.4), FR, A.LIE_FRONT, {'neck': r(-10, 0, 0), 'rightUpperArm': r(20, 0, 40), 'rightForearm': r(100)}))
    keys.append(K(2.0, diag(2.4), FR, A.LIE_FRONT))
    L.clip('turnbuckle.miss-aerial', 'Miss a dive from the top', 2.0, keys, f,
           desc='Diving splash from the top that hits nothing but canvas: belly-flop flat on the mat, then curl up clutching the ribs.',
           events=[ev(0.32, 'jump'), ev(0.6, 'apex'), ev(0.96, 'land', zone='front'), ev(0.96, 'impact', surface='mat'), ev(1.1, 'stun_start')],
           tags=['turnbuckle', 'aerial', 'miss'], start_state='perched-ready', end_state='lying-front', placement='perched', end_placement='center',
           phases=[('launch', 0, 0.32), ('flight', 0.32, 0.96), ('landing', 0.96, 1.15), ('recovery', 1.15, 2.0)], interrupt={'windows': []})

    keys = [perch(0, ARMS_UP, tall=True)]
    take_off(keys)
    keys.append(K(0.6, diag(1.3, 0.85), FR, A.STANCE, body(hy=-0.1, lean=-6), ARMS_UP, lfoot=air(*diag(1.25, 0.72)), rfoot=air(*diag(1.15, 0.7))))
    keys.append(K(0.86, diag(2.2, 0.32), FR, A.STANCE, body(hy=-0.1, roll=8), ARMS_OUT, lfoot=air(*diag(2.25, 0.28)), rfoot=air(*diag(2.15, 0.3))))
    keys.append(K(0.98, diag(2.42), FR, A.STANCE, body(hy=-0.4, lean=-14, roll=14), ARMS_OUT, lfoot=plant(*diag(2.5)[0::2]), rfoot=plant(*diag(2.35)[0::2], pitch=-20)))
    keys.append(K(1.15, diag(2.42), FR + 10, A.STANCE, KNEEL_R, body(hy=-0.5, roll=8)))
    keys.append(K(1.5, diag(2.42), FR + 10, SIT_INJ))
    keys.append(K(2.1, diag(2.42), FR + 10, SIT_INJ, {'neck': r(36, 0, 0)}))
    L.clip('turnbuckle.land-awkward', 'Land badly off the top', 2.1, keys, f,
           desc='Leap off the top, land with the right ankle rolling under, buckle to the knee and sit down clutching the leg.',
           events=[ev(0.32, 'jump'), ev(0.6, 'apex'), ev(0.98, 'land'), ev(0.98, 'impact', surface='mat'), ev(1.15, 'hit_received', zone='legs'), ev(1.5, 'stun_start')],
           tags=['turnbuckle', 'aerial', 'injury'], start_state='perched-ready', end_state='sitting', placement='perched', end_placement='center',
           phases=[('launch', 0, 0.32), ('flight', 0.32, 0.98), ('landing', 0.98, 1.2), ('recovery', 1.2, 2.1)], interrupt={'windows': []})

    # ================================================================ into the corner
    def corner_back(t, sag=0.0, sway=0.0, look=0):
        root = diag(0.48)
        return K(t, root, FR, A.LEAN, body(hy=-0.06 - sag, hz=0.14, lean=12, roll=sway * 30, neck=(-6, look, 0)),
                 lhand=hx(ROPE_TOP, 0.48, 0.0), rhand=hz(ROPE_TOP, 0.48, 0.0), feet=stand_feet(root, FR, width=0.15))
    f = A.Frame('corner', diag(3.2) + [FR])
    keys = [K(0, diag(3.2), FR + 180, A.GUARD, feet=stand_feet(diag(3.2), FR + 180))]
    keys.append(K(0.25, diag(3.0), FR + 180, run_pose(0.48), body(lean=-14)))
    keys.append(K(0.42, diag(2.3), FR + 180, run_pose(0.0), body(lean=-10)))
    keys.append(K(0.58, diag(1.65), FR + 180, run_pose(0.16), body(lean=-8)))
    keys.append(K(0.72, diag(1.1), FR + 90, run_pose(0.32), body(hy=-0.06, lean=-4)))
    keys.append(K(0.84, diag(0.6), FR, A.STRETCH, body(hz=0.3), feet=stand_feet(diag(0.6), FR)))
    keys.append(corner_back(0.94, sag=-0.02))
    keys.append(corner_back(1.3, sag=0.06))
    keys.append(corner_back(1.6))
    L.clip('turnbuckle.whipped-into-corner', 'Whipped into the corner', 1.6, keys, f,
           desc='Sent running into a corner from across the ring: spin at the last stride and crash back first into the turnbuckle. Ends leaning in the corner, arms over the ropes.',
           events=[ev(0.42, 'footstep'), ev(0.58, 'footstep'), ev(0.72, 'footstep'), ev(0.86, 'impact', surface='turnbuckle'), ev(0.88, 'rope_contact', attachment='back'), ev(1.0, 'stun_start')],
           tags=['turnbuckle', 'whip', 'defender', 'corner'], end_state='corner-back', placement='center', end_placement='inside-back-to-corner',
           phases=[('traversal', 0, 0.84), ('landing', 0.84, 1.0), ('recovery', 1.0, 1.6)], interrupt={'windows': []})

    f = A.Frame('corner', diag(0.48) + [FR])
    keys = [corner_back(0), corner_back(0.7, sag=0.04, sway=0.1, look=18), corner_back(1.4, sway=-0.04), corner_back(2.1, sag=0.04, sway=-0.1, look=-18), corner_back(2.8)]
    L.clip('turnbuckle.corner-back-idle', 'Propped in the corner (loop)', 2.8, keys, f, loop=True,
           desc='Back against the turnbuckle, arms draped over the top ropes, head lolling: the target for corner splashes and running attacks.',
           tags=['turnbuckle', 'corner', 'loop', 'stunned'], start_state='corner-back', end_state='corner-back', placement='inside-back-to-corner')

    SLUMP = {'hips': {'p': [0, -0.82, 0.18], 'r': [16, 0, 0]}, 'spine': r(-10), 'chest': r(-6), 'neck': r(30), 'head': r(10),
             'rightUpperLeg': r(70, 0, 16), 'leftUpperLeg': r(70, 0, -16), 'rightLowerLeg': r(-60), 'leftLowerLeg': r(-80),
             'rightUpperArm': r(0, 0, 70), 'leftUpperArm': r(0, 0, -70), 'rightForearm': r(30), 'leftForearm': r(30)}
    keys = [corner_back(0), corner_back(0.3, sag=0.1)]
    keys.append(K(0.65, diag(0.52), FR, A.LEAN, body(hy=-0.45, hz=0.1, lean=10), lhand=hx(ROPE_MID, 0.5), rhand=hz(ROPE_MID, 0.5), feet=stand_feet(diag(0.75), FR, width=0.16)))
    keys.append(K(0.95, diag(0.48), FR, SLUMP, lhand=hx(ROPE_BOT, 0.55), rhand=hz(ROPE_BOT, 0.55), feet=stand_feet(diag(1.05), FR, width=0.2)))
    keys.append(K(1.4, diag(0.48), FR, SLUMP, {'neck': r(40)}, lhand=hx(ROPE_BOT, 0.55), rhand=hz(ROPE_BOT, 0.55), feet=stand_feet(diag(1.05), FR, width=0.2)))
    L.clip('turnbuckle.corner-slump', 'Slump down in the corner', 1.4, keys, f,
           desc='From propped in the corner: legs give way and they slide down the turnbuckle to sit on the mat, arms on the bottom ropes.',
           events=[ev(0.95, 'impact', surface='mat'), ev(1.0, 'stun_start')],
           tags=['turnbuckle', 'corner', 'stunned'], start_state='corner-back', end_state='corner-slumped', placement='inside-back-to-corner')


KNEEL_R = {'hips': {'p': [0, -0.4, 0.04]}, 'spine': r(-14), 'rightUpperLeg': r(80, 0, 6), 'rightLowerLeg': r(-95), 'rightFoot': r(10),
           'leftUpperLeg': r(-5, 0, -6), 'leftLowerLeg': r(-100), 'leftFoot': r(-55),
           'rightUpperArm': r(30, 0, -20), 'rightForearm': r(70), 'leftUpperArm': r(40, 0, 20), 'leftForearm': r(60)}
SIT_INJ = {'hips': {'p': [0, -0.78, 0.1], 'r': [10, 0, 0]}, 'spine': r(-18), 'chest': r(-8), 'neck': r(20),
           'rightUpperLeg': r(70, 0, 8), 'rightLowerLeg': r(-100), 'leftUpperLeg': r(85, 0, -6), 'leftLowerLeg': r(-10), 'leftFoot': r(-20),
           'rightUpperArm': r(45, 0, -10), 'rightForearm': r(60), 'leftUpperArm': r(40, 0, 10), 'leftForearm': r(60)}
