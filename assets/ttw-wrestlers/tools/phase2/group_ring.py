"""Phase 2, group A: entering and leaving the ring, apron movement, falls from the ring to the floor."""
from common import *

def gap_heights(gap):
    return (ROPE_MID, ROPE_TOP) if gap == 'top' else (ROPE_BOT, ROPE_MID)

# ------------------------------------------------------------------ step through the ropes, side-on
def step_through(L, cid, name, s, gap, desc, tags=()):
    lo, hi = gap_heights(gap)
    if s > 0: frame, zs, ze, loc = A.apron_facing_ring(0.3), -0.3, 0.55, ('apron', 'ring')
    else:     frame, zs, ze, loc = A.inside_facing_ropes(0.55), 0.55, -0.3, ('ring', 'apron')
    yf = 180 if s > 0 else 0
    ys = yf + 90                                    # right side leads through the ropes
    low = gap == 'bottom'
    T = [0, 0.32, 0.64, 1.0, 1.36, 1.68, 2.0] if not low else [0, 0.34, 0.7, 1.12, 1.52, 1.86, 2.2]
    step_y = lo + RR + ANKLE + 0.06
    zl, zr = zs - s * 0.1, zs + s * 0.12
    def hgrips(root):
        a = rel(root, ys, 0, 0, -0.26); b = rel(root, ys, 0, 0, 0.16)
        return grip(b[0], hi, 0), grip(a[0], hi, 0)        # left hand behind, right hand ahead
    keys = [stance_at(T[0], [0, 0, zs], yf)]
    r1 = [0, 0, zs + s * 0.05]
    keys.append(K(T[1], r1, ys, A.STANCE, body(hy=-0.04 if not low else -0.12, spine=(-4, 0, 0)), hands=hgrips(r1),
                  lfoot=plant(0.03, zl, yaw=ys), rfoot=plant(-0.03, zr, yaw=ys)))
    r2 = [0, 0, zs + s * 0.12]
    keys.append(K(T[2], r2, ys, A.STANCE, body(hy=0.0 if not low else -0.22, roll=-10, spine=(-6, 0, -8)), hands=hgrips(r2),
                  lfoot=plant(0.03, zl, yaw=ys), rfoot=air(0.05, step_y, s * 0.06, pitch=10)))
    r3 = [0, 0, 0.0]
    keys.append(K(T[3], r3, ys, A.STANCE,
                  body(hy=-0.03 if not low else -0.38, roll=-48 if not low else -70, spine=(0, 0, -22), chest=(0, 0, -10), neck=(0, 0, 30), head=(0, 0, 12)),
                  hands=hgrips(r3), lfoot=plant(0.0, -s * 0.25, yaw=ys), rfoot=plant(0.05, s * 0.27, yaw=ys)))
    r4 = [0, 0, s * 0.2]
    keys.append(K(T[4], r4, ys, A.STANCE, body(hy=-0.02 if not low else -0.18, roll=-14, spine=(0, 0, -10), neck=(0, 0, 10)),
                  rhand=grip(rel(r4, ys, 0, 0, -0.26)[0], hi, 0),
                  lfoot=air(-0.04, step_y, s * 0.05, pitch=10), rfoot=plant(0.05, s * 0.27, yaw=ys)))
    r5 = [0, 0, s * 0.36]
    keys.append(K(T[5], r5, (ys + yf) / 2 if s > 0 else ys - 45, A.STANCE, body(hy=-0.06), ARMS_DOWN,
                  lfoot=plant(-0.1, s * 0.46), rfoot=plant(0.08, s * 0.3)))
    keys.append(stance_at(T[6], [0, 0, ze], yf if s > 0 else 0))
    ph = [('approach', 0, T[1]), ('contact', T[1], T[2]), ('traversal', T[2], T[4]), ('landing', T[4], T[5]), ('recovery', T[5], T[6])]
    evs = [ev(T[1], 'rope_contact', attachment='rightHandGrip'), ev(T[3] - 0.02, 'footstep'), ev(T[4] + 0.02, 'rope_release'),
           ev(T[5] - 0.02, 'footstep'), ev(T[6] - 0.05, 'recover')]
    L.clip(cid, name, T[6], keys, frame, events=evs, desc=desc, tags=['ring-entry' if s > 0 else 'ring-exit'] + list(tags),
           start_loc=loc[0], end_loc=loc[1], placement='apron-facing-ring' if s > 0 else 'inside-facing-ropes',
           end_placement='inside-facing-ropes' if s > 0 else 'apron-facing-out', phases=ph)

# ------------------------------------------------------------------ duck through, facing the way of travel
def duck_through(L, cid, name, s, desc):
    lo, hi = ROPE_MID, ROPE_TOP
    if s > 0: frame, zs, ze, loc = A.apron_facing_ring(0.3), -0.3, 0.6, ('apron', 'ring')
    else:     frame, zs, ze, loc = A.inside_facing_ropes(0.5), 0.5, -0.3, ('ring', 'apron')
    yf = 180 if s > 0 else 0
    T = [0, 0.26, 0.52, 0.84, 1.12, 1.5]
    def tg(root, side):  # hands push the top rope up, either side
        p = rel(root, yf, side * 0.28, 0, -0.1); return grip(p[0], hi, 0, up=0.07)
    keys = [stance_at(T[0], [0, 0, zs], yf)]
    r1 = [0, 0, zs + s * 0.05]
    keys.append(K(T[1], r1, yf, A.STANCE, body(hy=-0.1, lean=-12, spine=(-10, 0, 0)), hands=(tg(r1, -1), tg(r1, 1)),
                  feet=stand_feet(r1, yf, width=0.13)))
    r2 = [0, 0, zs + s * 0.1]
    lf, rf = stand_feet(r2, yf, width=0.13)
    keys.append(K(T[2], r2, yf, A.STANCE, body(hy=-0.02, lean=-24, spine=(-18, 0, 0), neck=(20, 0, 0)), hands=(tg(r2, -1), tg(r2, 1)),
                  lfoot=lf, rfoot=air(rel(r2, yf, 0.12)[0], lo + RR + ANKLE + 0.06, s * 0.06, pitch=12)))
    r3 = [0, 0, s * 0.02]
    keys.append(K(T[3], r3, yf, A.STANCE, body(hy=-0.06, lean=-58, spine=(-14, 0, 0), chest=(-6, 0, 0), neck=(48, 0, 0)), hands=(tg(r3, -1), tg(r3, 1)),
                  lfoot=plant(rel(r3, yf, -0.12)[0], -s * 0.24), rfoot=plant(rel(r3, yf, 0.12)[0], s * 0.3)))
    r4 = [0, 0, s * 0.28]
    keys.append(K(T[4], r4, yf, A.STANCE, body(hy=-0.04, lean=-26, spine=(-8, 0, 0), neck=(22, 0, 0)), ARMS_DOWN,
                  lfoot=air(rel(r4, yf, -0.12)[0], lo + RR + ANKLE + 0.06, s * 0.04, pitch=10), rfoot=plant(rel(r4, yf, 0.12)[0], s * 0.36)))
    keys.append(stance_at(T[5], [0, 0, ze], yf))
    L.clip(cid, name, T[5], keys, frame, desc=desc, tags=['ring-entry' if s > 0 else 'ring-exit', 'fast'],
           events=[ev(T[1], 'rope_contact', attachment='rightHandGrip'), ev(T[3], 'footstep'), ev(T[4], 'rope_release'), ev(T[4] + 0.12, 'footstep'), ev(T[5] - 0.05, 'recover')],
           start_loc=loc[0], end_loc=loc[1], placement='apron-facing-ring' if s > 0 else 'inside-facing-ropes',
           end_placement='inside-facing-ropes' if s > 0 else 'apron-facing-out',
           phases=[('approach', 0, T[1]), ('contact', T[1], T[2]), ('traversal', T[2], T[4]), ('recovery', T[4], T[5])])

# ------------------------------------------------------------------ over the top rope
def climb_over_top(L, cid, name, s, desc):
    """hold the top rope, both feet up onto the middle rope, swing one leg then the other over, hop down"""
    if s > 0: frame, zs, ze, loc = A.apron_facing_ring(0.3), -0.3, 0.6, ('apron', 'ring')
    else:     frame, zs, ze, loc = A.inside_facing_ropes(0.5), 0.5, -0.3, ('ring', 'apron')
    yf = 180 if s > 0 else 0
    hm = ROPE_MID + RR
    T = [0, 0.4, 0.82, 1.2, 1.55, 1.95, 2.3, 2.6, 2.95]
    def hands(root, w=0.3, z=0.0):
        a = rel(root, yf, -w, 0, 0); b = rel(root, yf, w, 0, 0)
        return grip(a[0], ROPE_TOP, z), grip(b[0], ROPE_TOP, z)
    keys = [stance_at(T[0], [0, 0, zs], yf)]
    r1 = [0, 0, zs + s * 0.08]
    lf, _ = stand_feet(r1, yf)
    keys.append(K(T[1], r1, yf, A.STANCE, body(hy=-0.06, lean=-8), hands=hands(r1), lfoot=lf,
                  rfoot=on_rope(rel(r1, yf, 0.13)[0], ROPE_MID, -s * 0.06)))
    r2 = [0, hm, -s * 0.07]
    keys.append(K(T[2], r2, yf, A.STANCE, body(hy=-0.16, lean=-14, spine=(-10, 0, 0)), hands=hands(r2, z=s * 0.02),
                  lfoot=on_rope(rel(r2, yf, -0.13)[0], ROPE_MID, -s * 0.06), rfoot=on_rope(rel(r2, yf, 0.13)[0], ROPE_MID, -s * 0.06)))
    r3 = [0, hm, -s * 0.04]
    keys.append(K(T[3], r3, yf, A.STANCE, body(hy=-0.12, lean=-10, roll=8, spine=(-6, 0, 6)), hands=hands(r3, z=s * 0.02),
                  lfoot=on_rope(rel(r3, yf, -0.13)[0], ROPE_MID, -s * 0.05), rfoot=air(rel(r3, yf, 0.2)[0], ROPE_TOP + 0.33, s * 0.05, pitch=10)))
    r4 = [0, hm, 0.0]
    keys.append(K(T[4], r4, yf, A.STANCE, body(hy=-0.24, lean=-4), hands=hands(r4, z=0),
                  lfoot=on_rope(rel(r4, yf, -0.14)[0], ROPE_MID, -s * 0.05), rfoot=on_rope(rel(r4, yf, 0.16)[0], ROPE_MID, s * 0.06)))
    r5 = [0, hm, s * 0.03]
    keys.append(K(T[5], r5, yf, A.STANCE, body(hy=-0.12, lean=-10, roll=-8, spine=(-6, 0, -6)), hands=hands(r5, z=0),
                  lfoot=air(rel(r5, yf, -0.2)[0], ROPE_TOP + 0.33, s * 0.0, pitch=10), rfoot=on_rope(rel(r5, yf, 0.16)[0], ROPE_MID, s * 0.06)))
    r6 = [0, hm, s * 0.07]
    keys.append(K(T[6], r6, yf, A.STANCE, body(hy=-0.18, lean=-6), hands=hands(r6, z=-s * 0.02),
                  lfoot=on_rope(rel(r6, yf, -0.13)[0], ROPE_MID, s * 0.06), rfoot=on_rope(rel(r6, yf, 0.13)[0], ROPE_MID, s * 0.06)))
    r7 = [0, 0, ze]
    keys.append(K(T[7], r7, yf, A.STANCE, body(hy=-0.32, lean=-12, spine=(-8, 0, 0)), ARMS_OUT, feet=stand_feet(r7, yf, width=0.15)))
    keys.append(stance_at(T[8], [0, 0, ze], yf))
    L.clip(cid, name, T[8], keys, frame, desc=desc, tags=['ring-entry' if s > 0 else 'ring-exit', 'slow'],
           events=[ev(T[1], 'rope_contact', attachment='rightHandGrip'), ev(T[2], 'footstep'), ev(T[4], 'footstep'), ev(T[6], 'footstep'),
                   ev(T[6] + 0.06, 'rope_release'), ev(T[6] + 0.1, 'jump'), ev(T[7], 'land'), ev(T[8] - 0.05, 'recover')],
           start_loc=loc[0], end_loc=loc[1], placement='apron-facing-ring' if s > 0 else 'inside-facing-ropes',
           end_placement='inside-facing-ropes' if s > 0 else 'apron-facing-out',
           phases=[('approach', 0, T[1]), ('contact', T[1], T[2]), ('traversal', T[2], T[6]), ('landing', T[6], T[7]), ('recovery', T[7], T[8])])

def build(L):
    step_through(L, 'ropes.enter-between-ropes', 'Enter between middle and top ropes', 1, 'top',
                 'From the apron: turn side-on, hold the top rope, step over the middle rope and slip the body between middle and top ropes.')
    step_through(L, 'ropes.enter-over-bottom', 'Enter over the bottom rope', 1, 'bottom',
                 'From the apron: crouch low, step over the bottom rope and fold the body under the middle rope.', ['low'])
    duck_through(L, 'ropes.enter-duck-top', 'Duck under the top rope', 1,
                 'From the apron: push the top rope up with both hands, step over the middle rope and duck straight through, facing in.')
    climb_over_top(L, 'ropes.enter-climb-over-top', 'Climb over the top rope', 1,
                   'From the apron: stand on the middle rope, swing each leg over the top rope, hop down into the ring.')
    step_through(L, 'ropes.exit-between-ropes', 'Exit between middle and top ropes', -1, 'top',
                 'From inside: side-on through the gap between middle and top ropes onto the apron. Ends on the apron facing out.')
    duck_through(L, 'ropes.exit-duck-through', 'Duck out through the ropes', -1,
                 'From inside: push the top rope up and duck out onto the apron, facing out.')
    climb_over_top(L, 'ropes.exit-climb-over-top', 'Climb out over the top rope', -1,
                   'From inside: up onto the middle rope, legs over the top rope, hop down onto the apron.')
    step_through(L, 'ropes.exit-under-middle', 'Exit between bottom and middle ropes', -1, 'bottom',
                 'From inside: crouch and step out between the bottom and middle ropes onto the apron.', ['low'])

    # ---------------- jump over the top rope (in from the apron)
    f = A.apron_facing_ring(0.3)
    T = [0, 0.3, 0.5, 0.64, 0.8, 1.0, 1.4]
    keys = [stance_at(0, [0, 0, -0.3], 180)]
    r1 = [0, 0, -0.26]
    keys.append(K(T[1], r1, 180, A.STANCE, body(hy=-0.3, lean=-14, spine=(-10, 0, 0)), hands=(grip(0.28, ROPE_TOP, 0), grip(-0.28, ROPE_TOP, 0)),
                  feet=stand_feet(r1, 180, width=0.14)))
    r2 = [0, 0.35, -0.16]
    keys.append(K(T[2], r2, 180, A.STANCE, body(hy=-0.15, lean=-8), hands=(grip(0.28, ROPE_TOP, 0), grip(-0.28, ROPE_TOP, 0)),
                  lfoot=air(0.13, 0.55, -0.22, pitch=-20), rfoot=air(-0.13, 0.55, -0.22, pitch=-20)))
    r3 = [0, 0.72, 0.02]
    keys.append(K(T[3], r3, 180, A.STANCE, body(hy=-0.32, lean=-6), hands=(grip(0.3, ROPE_TOP, 0.0), grip(-0.3, ROPE_TOP, 0.0)),
                  lfoot=air(0.14, 1.42, 0.2), rfoot=air(-0.14, 1.42, 0.2)))
    r4 = [0, 0.45, 0.32]
    keys.append(K(T[4], r4, 180, A.STANCE, body(hy=-0.2, lean=4), ARMS_OUT, lfoot=air(0.15, 0.6, 0.42), rfoot=air(-0.15, 0.6, 0.42)))
    r5 = [0, 0, 0.62]
    keys.append(K(T[5], r5, 180, A.STANCE, body(hy=-0.36, lean=-14, spine=(-10, 0, 0)), ARMS_OUT, feet=stand_feet(r5, 180, width=0.16)))
    keys.append(stance_at(T[6], [0, 0, 0.62], 180))
    L.clip('ropes.enter-jump-over-top', 'Jump over the top rope', T[6], keys, f,
           desc='From the apron: grab the top rope, spring up and tuck both legs over it, land crouched inside.',
           events=[ev(T[1], 'rope_contact', attachment='rightHandGrip'), ev(0.45, 'jump'), ev(T[3], 'apex'), ev(0.7, 'rope_release'), ev(T[5], 'land'), ev(T[6] - 0.05, 'recover')],
           tags=['ring-entry', 'athletic'], start_loc='apron', end_loc='ring', placement='apron-facing-ring', end_placement='inside-facing-ropes',
           phases=[('approach', 0, T[1]), ('contact', T[1], T[2]), ('traversal', T[2], T[4]), ('landing', T[4], T[5]), ('recovery', T[5], T[6])])

    # ---------------- vault over the top rope to the floor (out)
    f = A.inside_facing_ropes(0.5)
    T = [0, 0.32, 0.52, 0.66, 0.84, 1.08, 1.5]
    keys = [stance_at(0, [0, 0, 0.5], 0)]
    r1 = [0, 0, 0.42]
    keys.append(K(T[1], r1, 0, A.STANCE, body(hy=-0.3, lean=-14, spine=(-10, 0, 0)), hands=(grip(-0.28, ROPE_TOP, 0), grip(0.28, ROPE_TOP, 0)), feet=stand_feet(r1, 0, width=0.14)))
    r2 = [0, 0.4, 0.18]
    keys.append(K(T[2], r2, 0, A.STANCE, body(hy=-0.15, lean=-8), hands=(grip(-0.28, ROPE_TOP, 0), grip(0.28, ROPE_TOP, 0)),
                  lfoot=air(-0.13, 0.6, 0.24, pitch=-20), rfoot=air(0.13, 0.6, 0.24, pitch=-20)))
    r3 = [0, 0.75, -0.05]
    keys.append(K(T[3], r3, 0, A.STANCE, body(hy=-0.32, lean=-6), hands=(grip(-0.3, ROPE_TOP, 0), grip(0.3, ROPE_TOP, 0)),
                  lfoot=air(-0.14, 1.45, -0.22), rfoot=air(0.14, 1.45, -0.22)))
    r4 = [0, -0.25, -0.8]
    keys.append(K(T[4], r4, 0, A.STANCE, body(hy=-0.1, lean=6), ARMS_OUT, lfoot=air(-0.15, -0.65, -0.9), rfoot=air(0.15, -0.65, -0.9)))
    r5 = [0, A.DROP, -1.05]
    keys.append(K(T[5], r5, 0, A.STANCE, body(hy=-0.42, lean=-18, spine=(-12, 0, 0)), ARMS_OUT, feet=stand_feet(r5, 0, width=0.17)))
    keys.append(stance_at(T[6], [0, A.DROP, -1.05], 0))
    L.clip('ropes.exit-jump-over-top', 'Vault over the top rope to the floor', T[6], keys, f,
           desc='From inside: hands on the top rope, vault both legs over it, clear the apron and drop 1.16 m to land on the arena floor.',
           events=[ev(T[1], 'rope_contact', attachment='rightHandGrip'), ev(0.48, 'jump'), ev(T[3], 'apex'), ev(0.72, 'rope_release'), ev(T[5], 'land', height=1.16), ev(T[6] - 0.05, 'recover')],
           tags=['ring-exit', 'athletic', 'to-floor'], start_loc='ring', end_loc='floor', placement='inside-facing-ropes', end_placement='floor-facing-out',
           phases=[('approach', 0, T[1]), ('contact', T[1], T[2]), ('traversal', T[2], T[4]), ('landing', T[4], T[5]), ('recovery', T[5], T[6])])

    # ---------------- slide in under the bottom rope from the floor
    f = A.floor_facing_ring(0.35)
    D_ = A.DROP
    GF1 = {'hips': {'p': [0, -0.7, 0.08], 'r': [-78, 0, 0]}, 'neck': r(30), 'rightUpperArm': r(78, 0, -6), 'leftUpperArm': r(78, 0, 6),
           'rightForearm': r(8), 'leftForearm': r(8), 'rightFoot': r(-50), 'leftFoot': r(-50)}
    GF2 = {'hips': {'p': [0, -0.5, 0.3], 'r': [-75, 0, 0]}, 'neck': r(40), 'rightUpperLeg': r(75, 0, 4), 'leftUpperLeg': r(75, 0, -4),
           'rightLowerLeg': r(-90), 'leftLowerLeg': r(-90), 'rightFoot': r(-40), 'leftFoot': r(-40), 'rightUpperArm': r(75, 0, -6), 'leftUpperArm': r(75, 0, 6)}
    GF3 = {'hips': {'p': [0, -0.45, 0.12], 'r': [-15, 0, 0]}, 'spine': r(-10), 'neck': r(10),
           'rightUpperLeg': r(95, 0, 6), 'rightLowerLeg': r(-80), 'rightFoot': r(0), 'leftUpperLeg': r(15, 0, -4), 'leftLowerLeg': r(-90), 'leftFoot': r(-40),
           'rightUpperArm': r(40, 0, -10), 'rightForearm': r(40), 'leftUpperArm': r(30, 0, 10), 'leftForearm': r(30)}
    SLIDE = A.merge(A.LIE_FRONT, {'neck': r(30, 0, 0), 'head': r(10, 0, 0), 'rightUpperArm': r(0, 0, 150), 'leftUpperArm': r(0, 0, -150),
                                  'rightForearm': r(0, 0, 10), 'leftForearm': r(0, 0, -10)})
    T = [0, 0.3, 0.55, 0.78, 1.05, 1.3, 1.62, 1.95, 2.3, 2.7]
    keys = [stance_at(0, [0, D_, -0.95], 180)]
    r1 = [0, D_, -0.86]
    keys.append(K(T[1], r1, 180, A.STANCE, body(hy=-0.12, lean=-30, spine=(-14, 0, 0)), hands=(grip(0.22, 0.0, -0.48, up=0.05), grip(-0.22, 0.0, -0.48, up=0.05)),
                  feet=stand_feet(r1, 180, width=0.14)))
    r2 = [0, -0.55, -0.7]
    keys.append(K(T[2], r2, 180, A.LIE_FRONT, body(hy=-0.55, lean=-62, neck=(40, 0, 0)), hands=(grip(0.22, 0.0, -0.3, up=0.05), grip(-0.22, 0.0, -0.3, up=0.05))))
    r3 = [0, 0, -0.46]
    reach = lambda rt: (air(0.2, 0.06, rt[2] + 1.0), air(-0.2, 0.06, rt[2] + 1.0))
    keys.append(K(T[3], r3, 180, SLIDE, body(hy=-0.78, lean=-88, neck=(34, 0, 0)), hands=reach(r3)))
    r4 = [0, 0, 0.12]
    keys.append(K(T[4], r4, 180, SLIDE, body(hy=-0.8, lean=-90, neck=(30, 0, 0)), hands=reach(r4)))
    r5 = [0, 0, 0.5]
    keys.append(K(T[5], r5, 180, A.LIE_FRONT, body(hy=-0.84, lean=-90)))
    keys.append(on_support(T[6], r5, 180, GF1))
    keys.append(K(T[7], r5, 180, GF2))
    keys.append(K(T[8], r5, 180, GF3, rfoot=plant(-0.12, 0.92), lfoot={'at': [0.12, 0.13, 0.12], 'pitch': -60}))
    keys.append(stance_at(T[9], [0, 0, 0.7], 180))
    L.clip('ropes.enter-slide-under', 'Slide in under the bottom rope', T[9], keys, f,
           desc='From the arena floor: hands on the apron, spring up onto the belly, slide in under the bottom rope, push up to the feet inside.',
           events=[ev(T[1], 'grab', attachment='rightHandGrip'), ev(0.45, 'jump'), ev(T[3], 'land', zone='front'), ev(T[5], 'rope_release'),
                   ev(T[8], 'footstep'), ev(T[9] - 0.1, 'recover')],
           tags=['ring-entry', 'from-floor'], start_loc='floor', end_loc='ring', placement='floor-facing-ring', end_placement='inside-facing-ropes',
           phases=[('approach', 0, T[1]), ('contact', T[1], T[3]), ('traversal', T[3], T[5]), ('recovery', T[5], T[9])])

    # ---------------- dive in under the bottom rope from a run on the floor
    f = A.floor_facing_ring(1.4)
    T = [0, 0.18, 0.34, 0.5, 0.68, 0.9, 1.15]
    keys = [K(0, [0, D_, -2.0], 180, A.RC)]
    keys.append(K(T[1], [0, D_, -1.6], 180, A.RF))
    keys.append(K(T[2], [0, D_, -1.25], 180, A.RC, body(hy=-0.12, lean=-20, spine=(-14, 0, 0)), ARMS_SUPERMAN))
    keys.append(K(T[3], [0, -0.45, -0.8], 180, SLIDE, body(hy=-0.55, lean=-70, neck=(40, 0, 0))))
    keys.append(K(T[4], [0, 0, -0.32], 180, SLIDE, body(hy=-0.78, lean=-88, neck=(34, 0, 0))))
    keys.append(K(T[5], [0, 0, 0.36], 180, SLIDE, body(hy=-0.8, lean=-90, neck=(28, 0, 0))))
    keys.append(K(T[6], [0, 0, 0.62], 180, A.LIE_FRONT))
    L.clip('ropes.enter-dive-under', 'Dive in under the bottom rope', T[6], keys, f,
           desc='From a run on the floor: dive head-first onto the apron and slide under the bottom rope, ending face down inside (chain getup-front).',
           events=steps(0.08, 0.26) + [ev(0.4, 'jump'), ev(T[4], 'land', zone='front'), ev(T[6] - 0.05, 'animation_complete')][:-1],
           tags=['ring-entry', 'from-floor', 'fast'], start_loc='floor', end_loc='ring', end_state='lying-front',
           placement='floor-facing-ring', end_placement='inside-lying',
           phases=[('approach', 0, T[2]), ('launch', T[2], T[3]), ('traversal', T[3], T[5]), ('landing', T[5], T[6])])

    # ---------------- enter at the corner (from the apron beside the post)
    f = A.Frame('corner', [0.35, 0, -0.32, 180])
    T = [0, 0.35, 0.7, 1.05, 1.4, 1.75, 2.1]
    hm = ROPE_MID + RR
    keys = [stance_at(0, [0.35, 0, -0.32], 180)]
    keys.append(K(T[1], [0.3, 0, -0.26], 180, A.STANCE, body(hy=-0.05, lean=-6), hands=(grip(0.55, ROPE_TOP, 0), grip(0.02, ROPE_TOP + 0.12, -0.02)),
                  feet=stand_feet([0.3, 0, -0.26], 180)))
    keys.append(K(T[2], [0.24, hm, -0.08], 180, A.STANCE, body(hy=-0.18, lean=-12, roll=-6), hands=(grip(0.5, ROPE_TOP, 0), grip(0.02, ROPE_TOP + 0.12, 0.02)),
                  lfoot=on_rope(0.36, ROPE_MID, 0.0), rfoot=on_rope(0.12, ROPE_MID, 0.0)))
    keys.append(K(T[3], [0.26, hm, 0.0], 200, A.STANCE, body(hy=-0.12, lean=-8, roll=8), hands=(grip(0.48, ROPE_TOP, 0), grip(0.02, ROPE_TOP + 0.12, 0.08)),
                  lfoot=on_rope(0.38, ROPE_MID, 0.0), rfoot=air(0.12, ROPE_TOP + 0.36, 0.22, pitch=10)))
    keys.append(K(T[4], [0.34, 0.3, 0.3], 215, A.STANCE, body(hy=-0.4, lean=-6), hands=(grip(0.48, ROPE_TOP, 0), grip(0.02, ROPE_TOP + 0.12, 0.1)),
                  lfoot=air(0.36, ROPE_TOP + 0.33, 0.06, pitch=10), rfoot=plant(0.24, 0.42)))
    keys.append(K(T[5], [0.5, 0, 0.55], 225, A.STANCE, body(hy=-0.24, lean=-10), ARMS_DOWN, lfoot=plant(0.62, 0.48), rfoot=plant(0.4, 0.62)))
    keys.append(stance_at(T[6], [0.72, 0, 0.72], 225))
    L.clip('ropes.enter-from-corner', 'Enter at the corner', T[6], keys, f,
           desc='From the apron beside the corner post: hand on the post, step onto the middle rope, swing over the top rope by the turnbuckle and step down facing the ring centre.',
           events=[ev(T[1], 'grab', attachment='rightHandGrip'), ev(T[2], 'footstep'), ev(T[4], 'footstep'), ev(T[4] + 0.1, 'rope_release'), ev(T[5], 'footstep'), ev(T[6] - 0.05, 'recover')],
           tags=['ring-entry', 'corner'], start_loc='apron', end_loc='ring', placement='apron-beside-corner', end_placement='inside-facing-centre',
           phases=[('approach', 0, T[1]), ('contact', T[1], T[2]), ('traversal', T[2], T[4]), ('landing', T[4], T[5]), ('recovery', T[5], T[6])])

    # ---------------- enter injured: drop to the knees on the apron, crawl under the bottom rope, slow getup
    f = A.apron_facing_ring(0.3)
    KNEEL = {'hips': {'p': [0, -0.515, 0.04]}, 'spine': r(-14), 'neck': r(-6),
             'rightUpperLeg': r(10, 0, 4), 'leftUpperLeg': r(10, 0, -4), 'rightLowerLeg': r(-100), 'leftLowerLeg': r(-100), 'rightFoot': r(-55), 'leftFoot': r(-55)}
    CRAWL = merge_crawl = A.merge(GF2, {'hips': {'p': [0, -0.57, 0.3], 'r': [-82, 0, 0]}, 'rightFoot': r(-72), 'leftFoot': r(-72), 'neck': r(30), 'rightUpperArm': r(95, 0, -10), 'leftUpperArm': r(95, 0, 10),
                                        'rightForearm': r(42), 'leftForearm': r(42), 'rightUpperLeg': r(82, 0, 6), 'leftUpperLeg': r(82, 0, -6)})
    T = [0, 0.7, 1.3, 1.9, 2.5, 3.1, 3.6, 4.2, 4.8, 5.4]
    keys = [K(0, [0, 0, -0.3], 180, A.STANCE, HUNCH, body(hy=-0.04, spine=(-14, 0, 4)), feet=stand_feet([0, 0, -0.3], 180))]
    keys.append(K(T[1], [0, 0, -0.3], 180, KNEEL, HUNCH, body(hy=-0.515, hz=0.04, spine=(-14, 0, 4))))
    keys.append(K(T[2], [0, 0, -0.2], 180, CRAWL))
    keys.append(K(T[3], [0, 0, -0.05], 180, SLIDE, body(hy=-0.8, lean=-90, neck=(28, 0, 0))))
    keys.append(K(T[4], [0, 0, 0.3], 180, A.LIE_FRONT, body(hy=-0.84, lean=-90), {'rightUpperArm': r(150, 0, -30), 'rightForearm': r(70)}))
    keys.append(K(T[5], [0, 0, 0.5], 180, A.LIE_FRONT))
    keys.append(on_support(T[6], [0, 0, 0.5], 180, GF1, {'rightUpperArm': r(20, 0, -30), 'rightForearm': r(110)}, skip=('rightHand',)))
    keys.append(K(T[7], [0, 0, 0.5], 180, GF2))
    keys.append(K(T[8], [0, 0, 0.5], 180, GF3, {'spine': r(-20), 'rightUpperArm': r(22, 0, -30), 'rightForearm': r(112)},
                  rfoot=plant(-0.12, 0.92), lfoot={'at': [0.12, 0.13, 0.12], 'pitch': -60}))
    keys.append(K(T[9], [0, 0, 0.7], 180, A.STANCE, HUNCH, body(hy=-0.05, spine=(-14, 0, 4)), feet=stand_feet([0, 0, 0.7], 180)))
    L.clip('ropes.enter-injured', 'Enter the ring injured', T[9], keys, f,
           desc='From the apron, hurt: sink to the knees, crawl under the bottom rope holding the ribs, struggle up inside.',
           events=[ev(T[1], 'land', zone='knees'), ev(T[3], 'rope_contact'), ev(T[5], 'rope_release'), ev(T[9] - 0.2, 'recover')],
           tags=['ring-entry', 'injured', 'slow'], start_loc='apron', end_loc='ring', placement='apron-facing-ring', end_placement='inside-facing-ropes',
           phases=[('approach', 0, T[1]), ('traversal', T[1], T[5]), ('recovery', T[5], T[9])])

    # ---------------- slide out under the bottom rope to the floor, feet first
    f = A.inside_facing_ropes(0.6)
    SIT = {'hips': {'p': [0, -0.76, 0], 'r': [18, 0, 0]}, 'spine': r(-14), 'neck': r(-4),
           'rightUpperLeg': r(76, 0, 6), 'leftUpperLeg': r(76, 0, -6), 'rightLowerLeg': r(-30), 'leftLowerLeg': r(-30),
           'rightUpperArm': r(-30, 0, 16), 'leftUpperArm': r(-30, 0, -16), 'rightForearm': r(10), 'leftForearm': r(10)}
    LAYB = A.merge(SIT, {'hips': {'p': [0, -0.8, 0], 'r': [62, 0, 0]}, 'spine': r(-4), 'neck': r(-26),
                         'rightUpperLeg': r(28, 0, 6), 'leftUpperLeg': r(28, 0, -6), 'rightLowerLeg': r(-6), 'leftLowerLeg': r(-6)})
    T = [0, 0.4, 0.72, 1.0, 1.3, 1.52, 1.95]
    keys = [stance_at(0, [0, 0, 0.6], 0)]
    keys.append(K(T[1], [0, 0, 0.52], 0, SIT, lfoot=plant(-0.15, 0.0, pitch=-20), rfoot=plant(0.15, 0.0, pitch=-20)))
    keys.append(K(T[2], [0, 0, 0.24], 0, LAYB, lfoot=air(-0.15, 0.1, -0.5, flat=False), rfoot=air(0.15, 0.1, -0.5, flat=False)))
    keys.append(K(T[3], [0, 0, -0.32], 0, LAYB, {'hips': {'p': [0, -0.8, 0], 'r': [40, 0, 0]}, 'rightUpperLeg': r(46, 0, 6), 'leftUpperLeg': r(46, 0, -6),
                                                  'rightLowerLeg': r(-40), 'leftLowerLeg': r(-40)}))
    keys.append(K(T[4], [0, -0.55, -0.82], 0, A.STANCE, body(hy=-0.28, lean=-10), ARMS_OUT, lfoot=air(-0.15, -0.95, -0.95), rfoot=air(0.15, -0.95, -0.95)))
    keys.append(K(T[5], [0, D_, -1.05], 0, A.STANCE, body(hy=-0.42, lean=-18, spine=(-10, 0, 0)), ARMS_OUT, feet=stand_feet([0, D_, -1.05], 0, width=0.16)))
    keys.append(stance_at(T[6], [0, D_, -1.1], 0))
    L.clip('ropes.exit-slide-under', 'Slide out under the bottom rope', T[6], keys, f,
           desc='From inside: sit down, slide feet first under the bottom rope across the apron and drop onto the feet on the arena floor.',
           events=[ev(T[1], 'land', zone='seat'), ev(T[3], 'rope_release'), ev(T[5], 'land', height=1.16), ev(T[6] - 0.05, 'recover')],
           tags=['ring-exit', 'to-floor'], start_loc='ring', end_loc='floor', placement='inside-facing-ropes', end_placement='floor-facing-out',
           phases=[('approach', 0, T[1]), ('traversal', T[1], T[3]), ('landing', T[3], T[5]), ('recovery', T[5], T[6])])

    # ---------------- roll out under the bottom rope
    f = A.inside_facing_ropes(0.7)
    T = [0, 0.38, 0.72, 1.0, 1.28, 1.56, 1.9, 2.15]
    LB = A.LIE_BACK
    keys = [stance_at(0, [0, 0, 0.7], 0)]
    keys.append(K(T[1], [0, 0, 0.66], 45, A.merge(SIT, {'hips': {'p': [0, -0.7, 0], 'r': [10, 0, 0]}})))
    keys.append(K(T[2], [0, 0, 0.58], 90, LB, {'hips': {'p': [0, -0.83, 0], 'r': [90, 0, 0]}, 'rightUpperArm': r(0, 0, 160), 'leftUpperArm': r(0, 0, -160)}))
    keys.append(K(T[3], [0, 0, 0.32], 90, LB, {'hips': {'p': [0, -0.81, 0], 'r': [90, -90, 0]}, 'rightUpperArm': r(0, 0, 160), 'leftUpperArm': r(0, 0, -160)}))
    keys.append(K(T[4], [0, 0, 0.05], 90, LB, {'hips': {'p': [0, -0.83, 0], 'r': [90, -180, 0]}, 'rightUpperArm': r(0, 0, 160), 'leftUpperArm': r(0, 0, -160)}))
    keys.append(K(T[5], [0, 0, -0.3], 90, LB, {'hips': {'p': [0, -0.83, 0], 'r': [90, -360, 0]}, 'rightUpperArm': r(0, 0, 160), 'leftUpperArm': r(0, 0, -160)}))
    EDGE = A.merge(SIT, {'hips': {'p': [0, -0.72, 0], 'r': [-6, -360, 0]}, 'spine': r(-12), 'neck': r(6),
                         'rightUpperArm': r(-20, 0, 20), 'leftUpperArm': r(-20, 0, -20)})
    keys.append(K(T[6], [0, 0, -0.5], 0, EDGE, lfoot=air(-0.14, -0.5, -0.86), rfoot=air(0.14, -0.5, -0.86)))
    keys.append(K(T[7], [0, -0.45, -0.88], 0, A.STANCE, body(hy=-0.2, lean=-8, turn=-360), ARMS_OUT, lfoot=air(-0.15, -0.92, -0.95), rfoot=air(0.15, -0.92, -0.95)))
    keys.append(K(T[7] + 0.18, [0, D_, -1.0], 0, A.STANCE, body(hy=-0.4, lean=-16, turn=-360, spine=(-10, 0, 0)), ARMS_OUT, feet=stand_feet([0, D_, -1.0], 0, width=0.16)))
    keys.append(K(T[7] + 0.55, [0, D_, -1.0], 0, A.STANCE, body(hy=-0.02, turn=-360), feet=stand_feet([0, D_, -1.0], 0)))
    L.clip('ropes.exit-roll-under', 'Roll out under the bottom rope', T[7] + 0.55, keys, f,
           desc='From inside: drop to the mat, roll sideways under the bottom rope and across the apron, swing the legs down and land on the floor.',
           events=[ev(T[2], 'land', zone='back'), ev(T[4], 'rope_release'), ev(T[6] + 0.05, 'jump'), ev(T[7] + 0.18, 'land', height=1.16), ev(T[7] + 0.5, 'recover')],
           tags=['ring-exit', 'to-floor', 'roll'], start_loc='ring', end_loc='floor', placement='inside-facing-ropes', end_placement='floor-facing-out',
           phases=[('approach', 0, T[2]), ('traversal', T[2], T[6]), ('landing', T[6], T[7] + 0.18), ('recovery', T[7] + 0.18, T[7] + 0.55)])

    # ---------------- crawl out of the ring, slump down to the floor
    f = A.inside_facing_ropes(0.75)
    T = [0, 0.6, 1.2, 1.8, 2.4, 3.0, 3.5, 4.0, 4.6]
    keys = [K(0, [0, 0, 0.75], 0, A.STANCE, HUNCH, body(hy=-0.04, spine=(-14, 0, 4)), feet=stand_feet([0, 0, 0.75], 0))]
    keys.append(K(T[1], [0, 0, 0.72], 0, KNEEL, HUNCH))
    keys.append(K(T[2], [0, 0, 0.5], 0, CRAWL))
    keys.append(K(T[3], [0, 0, 0.18], 0, SLIDE, body(hy=-0.8, lean=-90, neck=(28, 0, 0))))
    keys.append(K(T[4], [0, 0, -0.22], 0, SLIDE, body(hy=-0.8, lean=-90, neck=(28, 0, 0))))
    # slither head first off the apron: hands reach for the floor, knees bend so the feet stay clear, land on hands and knees
    LEGS_UP = {'rightUpperLeg': r(-8, 0, 4), 'leftUpperLeg': r(-8, 0, -4), 'rightLowerLeg': r(-105), 'leftLowerLeg': r(-105)}
    keys.append(K(2.8, [0, 0, -0.42], 0, SLIDE, body(hy=-0.78, lean=-118, neck=(32, 0, 0)), LEGS_UP,
                  hands=(air(-0.24, -0.6, -1.15), air(0.24, -0.6, -1.15))))
    keys.append(K(3.2, [0, -0.25, -0.62], 0, SLIDE, body(hy=-0.78, lean=-140, neck=(38, 0, 0)), LEGS_UP,
                  lhand=[-0.24, D_ + 0.06, -1.3], rhand=[0.24, D_ + 0.06, -1.3]))
    keys.append(K(3.45, [0, -0.7, -1.45], 0, CRAWL, {'hips': {'p': [0, -0.55, 0.3], 'r': [-110, 0, 0]}}, LEGS_UP,
                  lhand=[-0.24, D_ + 0.06, -1.75], rhand=[0.24, D_ + 0.06, -1.75]))
    keys.append(K(3.75, [0, D_, -1.75], 0, CRAWL))
    keys.append(K(T[7] + 0.15, [0, D_, -1.75], 0, A.STANCE, KNEEL, HUNCH))
    keys.append(K(T[8] + 0.15, [0, D_, -1.8], 0, A.STANCE, HUNCH, body(hy=-0.06, spine=(-16, 0, 4)), feet=stand_feet([0, D_, -1.8], 0)))
    T[7] += 0.15; T[8] += 0.15
    L.clip('ropes.exit-crawl-out', 'Crawl out of the ring', T[8], keys, f,
           desc='Hurt: sink to the knees, crawl under the bottom rope onto the apron, slither off onto the floor and stand up holding the ribs.',
           events=[ev(T[1], 'land', zone='knees'), ev(T[3], 'rope_contact'), ev(T[4], 'rope_release'), ev(T[7], 'land', zone='knees', height=1.16), ev(T[8] - 0.2, 'recover')],
           tags=['ring-exit', 'to-floor', 'injured', 'slow'], start_loc='ring', end_loc='floor', placement='inside-facing-ropes', end_placement='floor-facing-out',
           phases=[('approach', 0, T[2]), ('traversal', T[2], T[5]), ('landing', T[5], T[7]), ('recovery', T[7], T[8])])

    # ---------------- apron: climb up from the floor
    f = A.floor_facing_ring(0.45)
    T = [0, 0.3, 0.72, 1.0, 1.35, 1.7]
    keys = [stance_at(0, [0, D_, -1.05], 180)]
    keys.append(K(T[1], [0, D_, -1.0], 180, A.STANCE, body(hy=-0.18, lean=-24, spine=(-12, 0, 0)), hands=(grip(0.24, 0, -0.5), grip(-0.24, 0, -0.5)),
                  feet=stand_feet([0, D_, -1.0], 180, width=0.15)))
    # right knee comes up high first, foot clears the apron edge, then it plants on the apron
    keys.append(K(0.44, [0, -0.95, -0.95], 180, A.STANCE, body(hy=-0.16, lean=-26, spine=(-12, 0, 0)), hands=(grip(0.24, 0, -0.48), grip(-0.24, 0, -0.48)),
                  lfoot=plant(0.12, -1.04, D_), rfoot=air(-0.14, -0.55, -0.86, pitch=-15)))
    keys.append(K(0.58, [0, -0.74, -0.92], 180, A.STANCE, body(hy=-0.14, lean=-28, spine=(-13, 0, 0)), hands=(grip(0.24, 0, -0.46), grip(-0.24, 0, -0.46)),
                  lfoot=plant(0.12, -1.04, D_), rfoot=air(-0.14, 0.22, -0.8, pitch=-10)))
    keys.append(K(T[2], [0, -0.5, -0.68], 180, A.STANCE, body(hy=-0.1, lean=-30, spine=(-14, 0, 0)), hands=(grip(0.24, 0, -0.44), grip(-0.24, 0, -0.44)),
                  lfoot=air(0.12, -0.8, -0.98, pitch=-30), rfoot=plant(-0.14, -0.44, y=0.02)))
    keys.append(K(T[3], [0, 0, -0.42], 180, KNEEL, {'hips': {'p': [0, -0.45, 0.0], 'r': [-16, 0, 0]}, 'spine': r(-10), 'rightFoot': r(-80), 'leftFoot': r(-80)}, hands=(grip(0.24, 0, -0.2), grip(-0.24, 0, -0.2))))
    keys.append(K(T[4], [0, 0, -0.36], 180, A.STANCE, body(hy=-0.32, lean=-12), ARMS_DOWN, lfoot=plant(0.13, -0.42), rfoot=plant(-0.13, -0.3)))
    keys.append(K(T[5], [0, 0, -0.32], 180, A.STANCE, body(hy=-0.03), hands=(grip(0.3, ROPE_TOP, 0), grip(-0.3, ROPE_TOP, 0)), feet=stand_feet([0, 0, -0.32], 180)))
    L.clip('ropes.apron-climb-up', 'Climb onto the apron', T[5], keys, f,
           desc='From the arena floor: hands on the apron, hop a knee up onto it, stand and take hold of the top rope.',
           events=[ev(T[1], 'grab'), ev(0.5, 'jump'), ev(T[3], 'land', zone='knees'), ev(T[4], 'footstep'), ev(T[5], 'rope_contact'), ev(T[5] - 0.02, 'recover')],
           tags=['apron', 'from-floor'], start_loc='floor', end_loc='apron', end_state='apron-hold', placement='floor-facing-ring', end_placement='apron-facing-ring',
           phases=[('approach', 0, T[1]), ('contact', T[1], T[2]), ('traversal', T[2], T[4]), ('recovery', T[4], T[5])])

    # ---------------- apron: drop down to the floor
    f = A.apron_facing_ring(0.32)
    T = [0, 0.35, 0.62, 0.86, 1.12, 1.5]
    keys = [K(0, [0, 0, -0.32], 180, A.STANCE, body(hy=-0.03), hands=(grip(0.3, ROPE_TOP, 0), grip(-0.3, ROPE_TOP, 0)), feet=stand_feet([0, 0, -0.32], 180))]
    keys.append(K(T[1], [0, 0, -0.36], 90, A.STANCE, body(hy=-0.04), {'leftUpperArm': r(10, 0, -10)}, rhand=grip(-0.1, ROPE_TOP, 0), feet=stand_feet([0, 0, -0.36], 90)))
    keys.append(K(T[2], [0, 0, -0.46], 0, A.STANCE, body(hy=-0.2, lean=-8), ARMS_DOWN, feet=stand_feet([0, 0, -0.46], 0, width=0.14)))
    keys.append(K(0.74, [0, 0.12, -0.68], 0, A.STANCE, body(hy=-0.1), ARMS_OUT, lfoot=air(-0.15, 0.2, -0.72), rfoot=air(0.15, 0.2, -0.72)))
    keys.append(K(0.92, [0, -0.5, -0.9], 0, A.STANCE, body(hy=-0.16), ARMS_OUT, lfoot=air(-0.15, -0.85, -0.95), rfoot=air(0.15, -0.85, -0.95)))
    keys.append(K(T[4], [0, D_, -1.02], 0, A.STANCE, body(hy=-0.38, lean=-16, spine=(-10, 0, 0)), ARMS_OUT, feet=stand_feet([0, D_, -1.02], 0, width=0.16)))
    keys.append(stance_at(T[5], [0, D_, -1.02], 0))
    L.clip('ropes.apron-drop-down', 'Drop down from the apron', T[5], keys, f,
           desc='From the apron: let go of the rope, turn to face out, hop down onto the arena floor.',
           events=[ev(T[1], 'rope_release'), ev(0.7, 'jump'), ev(T[4], 'land', height=1.16), ev(T[5] - 0.05, 'recover')],
           tags=['apron', 'to-floor'], start_loc='apron', end_loc='floor', start_state='apron-hold', placement='apron-facing-ring', end_placement='floor-facing-out',
           phases=[('approach', 0, T[2]), ('traversal', T[2], T[4]), ('landing', T[3], T[4]), ('recovery', T[4], T[5])])

    # ---------------- apron: idle holding the top rope, shuffle left/right, hang on
    f = A.apron_facing_ring(0.32)
    root = [0, 0, -0.32]
    def apron_hold(t, hy=-0.03, lean=0, look=0, shift=0.0):
        return K(t, root, 180, A.STANCE, body(hy=hy, lean=lean, hx=shift, neck=(0, look, 0)), hands=(grip(0.3, ROPE_TOP, 0), grip(-0.3, ROPE_TOP, 0)),
                 feet=stand_feet(root, 180))
    L.clip('ropes.apron-idle', 'Apron idle', 2.4, [apron_hold(0), apron_hold(0.8, hy=-0.05, look=20, shift=0.02), apron_hold(1.6, hy=-0.04, look=-18, shift=-0.02), apron_hold(2.4)], f,
           loop=True, desc='Standing on the apron holding the top rope, breathing and glancing around. Loop.',
           tags=['apron', 'loop', 'idle'], start_loc='apron', end_loc='apron', start_state='apron-hold', end_state='apron-hold', placement='apron-facing-ring')

    def shuffle(cid, name, dirx):
        # in place; gameplay slides the wrestler along the apron (dirx in the wrestler's local x)
        ks = []
        for i, t in enumerate([0, 0.25, 0.5, 0.75, 1.0]):
            ph = i % 4
            wide = ph in (1,)
            narrow = ph in (3,)
            lx = 0.12 + (0.06 if wide else (-0.04 if narrow else 0))
            lead = -dirx  # frame x of the leading side (wrestler faces +Z, his right is -X)
            lf = plant(lx if ph != 1 else lx + 0.03 * lead, -0.32, yaw=180)
            rf = plant(-lx if ph != 3 else -lx + 0.03 * lead, -0.32, yaw=180)
            if ph == 1: rf = air(-lx, 0.12, -0.32)
            if ph == 3: lf = air(lx, 0.12, -0.32)
            ks.append(K(t, root, 180, A.STANCE, body(hy=-0.06 if ph in (1, 3) else -0.04, roll=3 * (1 if ph == 1 else -1 if ph == 3 else 0)),
                        hands=(grip(0.3, ROPE_TOP, 0), grip(-0.3, ROPE_TOP, 0)), lfoot=lf, rfoot=rf))
        L.clip(cid, name, 1.0, ks, f, loop=True, events=steps(0.33, 0.83),
               desc='Side-step along the apron holding the top rope. In place: gameplay moves the wrestler along the apron at rootMotion.speed.',
               tags=['apron', 'loop', 'locomotion'], start_loc='apron', end_loc='apron', start_state='apron-hold', end_state='apron-hold',
               placement='apron-facing-ring', gameplay={'inPlace': {'speed': 0.8, 'direction': [dirx, 0, 0]}})
    shuffle('ropes.apron-shuffle-left', 'Apron shuffle left', -1)
    shuffle('ropes.apron-shuffle-right', 'Apron shuffle right', 1)

    def hang(t, lean=-28, look=0, sway=0.0):
        rt = [0, 0, -0.52]
        return K(t, rt, 180, A.STANCE, body(hy=-0.14, hz=0.0, lean=lean, roll=sway, neck=(-lean * 0.6, look, 0)),
                 hands=(grip(0.28, ROPE_MID, 0.0), grip(-0.28, ROPE_MID, 0.0)), lfoot=plant(0.12, -0.56, pitch=-12), rfoot=plant(-0.12, -0.56, pitch=-12))
    L.clip('ropes.apron-hang-on', 'Hang on at the apron edge', 2.0, [hang(0), hang(0.5, lean=-34, sway=4), hang(1.0, lean=-26, look=25), hang(1.5, lean=-32, sway=-4), hang(2.0)],
           A.apron_facing_ring(0.52), loop=True,
           desc='Heels at the edge of the apron, leaning back out over the floor and clinging to the middle rope to stay up. Loop.',
           tags=['apron', 'loop', 'elimination-risk'], start_loc='apron', end_loc='apron', start_state='apron-teeter', end_state='apron-teeter',
           placement='apron-edge-facing-ring')

    # ---------------- falls from the apron to the floor
    f = A.apron_facing_ring(0.35)
    T = [0, 0.12, 0.36, 0.6, 0.78, 0.9, 1.4]
    keys = [K(0, [0, 0, -0.35], 180, A.STANCE, body(hy=-0.03), feet=stand_feet([0, 0, -0.35], 180))]
    keys.append(K(T[1], [0, 0, -0.42], 180, A.STANCE, body(hy=-0.05, lean=12, neck=(24, 0, 0)), {'rightUpperArm': r(40, 0, 40), 'leftUpperArm': r(40, 0, -40)},
                  feet=stand_feet([0, 0, -0.42], 180)))
    keys.append(K(T[2], [0, 0, -0.62], 180, A.STANCE, body(hy=-0.2, lean=38, neck=(-10, 0, 0)), {'rightUpperArm': r(90, 0, 40), 'leftUpperArm': r(90, 0, -40)},
                  lfoot=plant(0.12, -0.5, pitch=-25), rfoot=plant(-0.12, -0.5, pitch=-25)))
    keys.append(K(T[3], [0, -0.55, -1.25], 180, A.STANCE, body(hy=-0.45, lean=78, neck=(-24, 0, 0)), {'rightUpperArm': r(40, 0, 60), 'leftUpperArm': r(40, 0, -60)},
                  lfoot=air(0.12, 0.25, -0.62, flat=False), rfoot=air(-0.12, 0.3, -0.62, flat=False)))
    keys.append(K(T[4], [0, D_, -1.6], 180, A.F3))
    keys.append(K(T[5], [0, D_, -1.62], 180, A.F4))
    keys.append(K(T[6], [0, D_, -1.64], 180, A.LIE_BACK))
    L.clip('eliminations.apron-fall-back', 'Fall backwards off the apron', T[6], keys, f,
           desc='Hit on the apron: arms windmill, heels go over the edge and the wrestler drops 1.16 m flat on the back on the arena floor.',
           events=[ev(0.02, 'stun_start'), ev(T[3], 'jump'), ev(T[4], 'land', zone='back', height=1.16), ev(T[4], 'impact')],
           tags=['elimination', 'to-floor', 'fall'], start_loc='apron', end_loc='floor', end_state='lying-back', placement='apron-facing-ring', end_placement='floor-lying',
           phases=[('contact', 0, T[1]), ('traversal', T[1], T[4]), ('landing', T[4], T[6])])

    f = A.Frame('rope', [0, 0, -0.35, 0])
    LF2 = A.merge(A.LIE_FRONT, {'neck': r(30, 30, 0)})
    keys = [K(0, [0, 0, -0.35], 0, A.STANCE, body(hy=-0.03), feet=stand_feet([0, 0, -0.35], 0))]
    keys.append(K(0.14, [0, 0, -0.42], 0, A.STANCE, body(hy=-0.06, lean=-14, neck=(-10, 0, 0)), {'rightUpperArm': r(-30, 0, 30), 'leftUpperArm': r(-30, 0, -30)}, feet=stand_feet([0, 0, -0.42], 0)))
    keys.append(K(0.38, [0, -0.05, -0.72], 0, A.STANCE, body(hy=-0.2, lean=-40), ARMS_FWD, lfoot=plant(-0.12, -0.5, pitch=30), rfoot=air(0.12, 0.3, -0.5)))
    keys.append(K(0.6, [0, -0.7, -1.4], 0, A.STANCE, body(hy=-0.4, lean=-80, neck=(30, 0, 0)), {'rightUpperArm': r(150, 0, -20), 'leftUpperArm': r(150, 0, 20)},
                  lfoot=air(-0.12, 0.25, -0.6, flat=False), rfoot=air(0.12, 0.3, -0.6, flat=False)))
    keys.append(K(0.78, [0, D_, -1.75], 0, LF2, body(hy=-0.8, lean=-86, neck=(24, 30, 0))))
    keys.append(K(0.9, [0, D_, -1.8], 0, LF2, body(hy=-0.81, lean=-88, neck=(30, 30, 0))))
    keys.append(K(1.4, [0, D_, -1.82], 0, A.LIE_FRONT))
    L.clip('eliminations.apron-fall-forward', 'Fall forwards off the apron', 1.4, keys, f,
           desc='Shoved from behind on the apron while facing out: stumble off the edge and crash face down on the arena floor.',
           events=[ev(0.02, 'stun_start'), ev(0.4, 'jump'), ev(0.78, 'land', zone='front', height=1.16), ev(0.78, 'impact')],
           tags=['elimination', 'to-floor', 'fall'], start_loc='apron', end_loc='floor', end_state='lying-front', placement='apron-facing-out', end_placement='floor-lying',
           phases=[('contact', 0, 0.14), ('traversal', 0.14, 0.78), ('landing', 0.78, 1.4)])

    # ---------------- falling / being sent through and over the ropes (receiver side, usable solo)
    f = A.inside_facing_ropes(0.9)
    T = [0, 0.18, 0.38, 0.58, 0.76, 0.98, 1.16, 1.3, 1.8]
    keys = [K(0, [0, 0, 0.9], 0, A.STANCE, body(hy=-0.04, lean=-6), feet=stand_feet([0, 0, 0.9], 0))]
    keys.append(K(T[1], [0, 0, 0.62], 0, A.STANCE, body(hy=-0.08, lean=-20, spine=(-10, 0, 0)), {'rightUpperArm': r(50, 0, 30), 'leftUpperArm': r(50, 0, -30)},
                  lfoot=plant(-0.12, 0.72), rfoot=air(0.12, 0.2, 0.5)))
    keys.append(K(T[2], [0, 0, 0.32], 0, A.STANCE, body(hy=-0.1, lean=-36, spine=(-14, 0, 0)), ARMS_FWD, lfoot=air(-0.12, 0.25, 0.48), rfoot=plant(0.12, 0.3)))
    keys.append(K(T[3], [0, 0, 0.12], 0, A.STANCE, body(hy=-0.06, lean=-70, spine=(-12, 0, 0), neck=(50, 0, 0)), {'rightUpperArm': r(120, 0, 10), 'leftUpperArm': r(120, 0, -10)},
                  lfoot=plant(-0.12, 0.22, pitch=40), rfoot=plant(0.12, 0.26, pitch=40)))
    keys.append(K(T[4], [0, 0.1, -0.2], 0, A.STANCE, body(hy=-0.1, lean=-95, neck=(60, 0, 0)), {'rightUpperArm': r(150, 0, 10), 'leftUpperArm': r(150, 0, -10)},
                  lfoot=air(-0.12, 0.35, 0.3, flat=False), rfoot=air(0.12, 0.4, 0.32, flat=False)))
    keys.append(K(T[5], [0, -0.45, -0.85], 0, A.STANCE, body(hy=-0.25, lean=-130, neck=(50, 0, 0)), {'rightUpperArm': r(160, 0, 20), 'leftUpperArm': r(160, 0, -20)},
                  lfoot=air(-0.12, 0.5, -0.2, flat=False), rfoot=air(0.12, 0.55, -0.2, flat=False)))
    keys.append(K(T[6], [0, -0.8, -1.3], 0, A.merge(A.LIE_BACK, {'hips': {'p': [0, -0.35, 0], 'r': [-185, 0, 0]}, 'rightUpperArm': r(120, 0, 30), 'leftUpperArm': r(120, 0, -30)})))
    keys.append(K(T[7], [0, D_, -1.48], 0, A.merge(A.F3, {'hips': {'p': [0, -0.8, 0], 'r': [-262, 0, 0]}})))
    keys.append(K(T[8], [0, D_, -1.56], 0, A.merge(A.LIE_BACK, {'hips': {'p': [0, -0.83, 0], 'r': [-270, 0, 0]}})))
    L.clip('eliminations.fall-through-ropes', 'Stumble through the ropes to the floor', T[8], keys, f,
           desc='Staggering forward into the ropes, the wrestler pitches head first between the middle and top ropes, tumbles off the apron and lands on the back on the floor.',
           events=[ev(0.02, 'stun_start')] + steps(T[1], T[2]) + [ev(T[3], 'rope_contact'), ev(T[5], 'rope_release'), ev(T[7], 'land', zone='back', height=1.16), ev(T[7], 'impact')],
           tags=['elimination', 'to-floor', 'fall', 'stumble'], start_loc='ring', end_loc='floor', end_state='lying-back', placement='inside-facing-ropes', end_placement='floor-lying',
           phases=[('approach', 0, T[3]), ('contact', T[3], T[4]), ('traversal', T[4], T[6]), ('landing', T[6], T[8])])

    f = A.back_to_ropes(0.45)
    T = [0, 0.1, 0.3, 0.5, 0.72, 0.92, 1.08, 1.6]
    keys = [K(0, [0, 0, 0.45], 180, A.STANCE, body(hy=-0.03), feet=stand_feet([0, 0, 0.45], 180))]
    keys.append(K(T[1], [0, 0, 0.36], 180, A.STANCE, body(hy=-0.05, lean=14, neck=(26, 0, 0)), {'rightUpperArm': r(40, 0, 30), 'leftUpperArm': r(40, 0, -30)}, feet=stand_feet([0, 0, 0.36], 180)))
    keys.append(K(T[2], [0, 0, 0.18], 180, A.STANCE, body(hy=-0.08, lean=40, neck=(10, 0, 0)), {'rightUpperArm': r(80, 0, 50), 'leftUpperArm': r(80, 0, -50)},
                  lfoot=plant(0.12, 0.28), rfoot=plant(-0.12, 0.28)))
    keys.append(K(T[3], [0, 0.02, -0.12], 180, A.STANCE, body(hy=-0.04, lean=82, neck=(-14, 0, 0)), {'rightUpperArm': r(100, 0, 60), 'leftUpperArm': r(100, 0, -60)},
                  lfoot=air(0.12, 0.3, 0.3, flat=False), rfoot=air(-0.12, 0.3, 0.3, flat=False)))
    keys.append(K(T[4], [0, -0.1, -0.55], 180, A.merge(A.LIE_BACK, {'hips': {'p': [0, -0.25, 0], 'r': [100, 0, 0]}}),
                  lfoot=air(0.12, 0.62, 0.05, flat=False), rfoot=air(-0.12, 0.6, 0.05, flat=False)))
    keys.append(K(T[5], [0, -0.75, -1.2], 180, A.merge(A.LIE_BACK, {'hips': {'p': [0, -0.4, 0], 'r': [125, 0, 0]}}), lfoot=air(0.12, 0.15, -0.45, flat=False), rfoot=air(-0.12, 0.15, -0.45, flat=False)))
    keys.append(K(T[6], [0, D_, -1.6], 180, A.F3))
    keys.append(K(T[7], [0, D_, -1.63], 180, A.LIE_BACK))
    L.clip('eliminations.knocked-through-ropes', 'Knocked backwards through the ropes', T[7], keys, f,
           desc='Hit with the back to the ropes: folds backwards between the middle and top ropes, slides off the apron and lands flat on the back on the floor.',
           events=[ev(0.02, 'stun_start'), ev(T[2], 'rope_contact'), ev(T[4], 'rope_release'), ev(T[6], 'land', zone='back', height=1.16), ev(T[6], 'impact')],
           tags=['elimination', 'to-floor', 'fall', 'reaction'], start_loc='ring', end_loc='floor', end_state='lying-back', placement='inside-back-to-ropes', end_placement='floor-lying',
           phases=[('contact', 0, T[2]), ('traversal', T[2], T[5]), ('landing', T[5], T[7])])

    f = A.back_to_ropes(0.42)
    T = [0, 0.14, 0.32, 0.5, 0.68, 0.86, 1.02, 1.16, 1.7]
    keys = [K(0, [0, 0, 0.42], 180, A.STANCE, body(hy=-0.03), feet=stand_feet([0, 0, 0.42], 180))]
    keys.append(K(T[1], [0, 0, 0.32], 180, A.STANCE, body(hy=-0.12, lean=20), {'rightUpperArm': r(60, 0, 40), 'leftUpperArm': r(60, 0, -40)}, feet=stand_feet([0, 0, 0.32], 180)))
    keys.append(K(T[2], [0, 0.42, 0.12], 180, A.STANCE, body(hy=-0.05, lean=70, neck=(-10, 0, 0)), {'rightUpperArm': r(120, 0, 50), 'leftUpperArm': r(120, 0, -50)},
                  lfoot=air(0.13, 0.75, 0.42, flat=False), rfoot=air(-0.13, 0.8, 0.44, flat=False)))
    keys.append(K(T[3], [0, 0.6, -0.12], 180, A.merge(A.LIE_BACK, {'hips': {'p': [0, -0.2, 0], 'r': [130, 0, 0]}, 'rightUpperArm': r(60, 0, 60), 'leftUpperArm': r(60, 0, -60)})))
    keys.append(K(T[4], [0, 0.3, -0.72], 180, A.merge(A.LIE_BACK, {'hips': {'p': [0, -0.2, 0], 'r': [185, 0, 0]}, 'rightUpperArm': r(30, 0, 70), 'leftUpperArm': r(30, 0, -70)})))
    keys.append(K(T[5], [0, -0.42, -1.42], 180, A.merge(A.LIE_BACK, {'hips': {'p': [0, -0.35, 0], 'r': [230, 0, 0]}})))
    keys.append(K(T[6], [0, D_, -1.6], 180, A.merge(A.LIE_FRONT, {'hips': {'p': [0, -0.82, 0], 'r': [272, 0, 0]}})))
    keys.append(K(T[7], [0, D_, -1.64], 180, A.merge(A.LIE_FRONT, {'hips': {'p': [0, -0.78, 0], 'r': [266, 0, 0]}})))
    keys.append(K(T[8], [0, D_, -1.66], 180, A.merge(A.LIE_FRONT, {'hips': {'p': [0, -0.84, 0], 'r': [270, 0, 0]}})))
    L.clip('eliminations.thrown-over-top', 'Thrown over the top rope', T[8], keys, f,
           desc='Heaved up and backwards: the legs go over the top rope, the wrestler flips backwards past the apron and crashes face down on the floor (elimination).',
           events=[ev(0.02, 'stun_start'), ev(T[2], 'rope_contact'), ev(T[3], 'apex'), ev(T[4], 'rope_release'), ev(T[6], 'land', zone='front', height=1.16), ev(T[6], 'impact')],
           tags=['elimination', 'to-floor', 'fall', 'over-top-rope'], start_loc='ring', end_loc='floor', end_state='lying-front', placement='inside-back-to-ropes', end_placement='floor-lying',
           phases=[('contact', 0, T[2]), ('traversal', T[2], T[5]), ('landing', T[5], T[8])])

    f = A.inside_facing_ropes(1.2)
    T = [0, 0.14, 0.3, 0.46, 0.62, 0.8, 0.94, 1.5]
    SUP = A.merge(A.LIE_FRONT, {'hips': {'p': [0, 0, 0], 'r': [-90, 0, 0]}, 'neck': r(36, 0, 0), 'rightUpperArm': r(160, 0, -16), 'leftUpperArm': r(160, 0, 16),
                                 'rightForearm': r(10, 0, 0), 'leftForearm': r(10, 0, 0), 'rightUpperLeg': r(0, 0, 4), 'leftUpperLeg': r(0, 0, -4)})
    keys = [K(0, [0, 0, 1.2], 0, A.STANCE, body(hy=-0.04, lean=10), feet=stand_feet([0, 0, 1.2], 0))]
    keys.append(K(T[1], [0, 0, 0.92], 0, A.RC, body(hy=-0.08, lean=-24, spine=(-12, 0, 0)), {'rightUpperArm': r(-40, 0, 20), 'leftUpperArm': r(-40, 0, -20)}))
    keys.append(K(T[2], [0, 0, 0.6], 0, A.RF, body(hy=-0.1, lean=-40, spine=(-14, 0, 0)), ARMS_FWD))
    keys.append(K(T[3], [0, 0.0, 0.3], 0, SUP, body(hy=-0.0, lean=-70, neck=(40, 0, 0)), lfoot=air(-0.12, 0.4, 0.62, flat=False), rfoot=air(0.12, 0.35, 0.6, flat=False)))
    keys.append(K(T[4], [0, 0.0, -0.25], 0, SUP, body(hy=0.06, lean=-90)))
    keys.append(K(T[5], [0, -0.3, -1.32], 0, SUP, body(hy=-0.2, lean=-96, neck=(30, 0, 0))))
    keys.append(K(T[6], [0, D_, -1.82], 0, A.merge(A.LIE_FRONT, {'hips': {'p': [0, -0.78, 0], 'r': [-86, 0, 0]}})))
    keys.append(K(T[7], [0, D_, -1.9], 0, A.LIE_FRONT))
    L.clip('eliminations.thrown-through-middle', 'Thrown through the middle ropes', T[7], keys, f,
           desc='Propelled head first: two driven steps, launched flat between the middle and top ropes, over the apron and face first onto the floor.',
           events=[ev(0.02, 'stun_start'), ev(T[1], 'footstep'), ev(T[2], 'jump'), ev(T[3], 'rope_contact'), ev(T[5], 'rope_release'), ev(T[6], 'land', zone='front', height=1.16), ev(T[6], 'impact')],
           tags=['elimination', 'to-floor', 'fall', 'through-ropes'], start_loc='ring', end_loc='floor', end_state='lying-front', placement='inside-facing-ropes', end_placement='floor-lying',
           phases=[('approach', 0, T[2]), ('traversal', T[2], T[6]), ('landing', T[6], T[7])])
