"""Generate roster/wrestler-XX.json from one shared body template.

Every wrestler uses the same skeleton and the same body layout. Only colours, part sizes,
hair, face and outfit differ, so every animation works on every wrestler without retargeting.

Usage (from assets/ttw-wrestlers):  python tools/build-roster.py
Add the next 18 wrestlers to ROSTER below and run it again.
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- roster

ROSTER = [
    {
        "id": "wrestler-01", "displayName": "Rex Calloway", "gender": "male",
        "bio": "Brawler. Red mohawk, goatee, red trunks and white boots.",
        "palette": {
            "skin": "#d9a27a", "lower": "#c41f2b", "top": "#d9a27a", "belt": "#f4f1ea",
            "boot": "#f4f1ea", "bootTrim": "#c41f2b", "sole": "#1c1d22", "kneepad": "#1c1d22",
            "band": "#f4f1ea", "elbow": "#1c1d22", "hair": "#b0231e", "facial": "#5a2a18",
            "eye": "#15100d", "brow": "#5a2a18", "lip": "#b9785a"
        },
        "build": {"torso": 1.0, "shoulders": 1.0, "arms": 1.0, "legs": 1.0, "neck": 1.0},
        "outfit": "trunks", "hair": "mohawk", "face": "goatee", "extras": ["elbowpads"]
    },
    {
        "id": "wrestler-02", "displayName": "Nova Reyes", "gender": "female",
        "bio": "High flyer. Dark ponytail, teal singlet with gold trim, full-length tights.",
        "palette": {
            "skin": "#a8714c", "lower": "#0e2f3a", "top": "#12a39b", "belt": "#f2b632",
            "boot": "#12a39b", "bootTrim": "#f2b632", "sole": "#1c1d22", "kneepad": "#0e2f3a",
            "band": "#f2b632", "elbow": "#0e2f3a", "hair": "#1f1410", "facial": "#1f1410",
            "eye": "#15100d", "brow": "#1f1410", "lip": "#8a4a3a"
        },
        "build": {"torso": 0.9, "shoulders": 0.9, "arms": 0.84, "legs": 0.93, "neck": 0.86},
        "outfit": "singlet", "hair": "ponytail", "face": "clean", "extras": []
    }
]

# ---------------------------------------------------------------- body template

def J(joint, offset=None):
    d = {"joint": joint}
    if offset: d["offset"] = offset
    return d

def B(a, b, t, offset=None):
    d = {"between": [a, b], "t": t}
    if offset: d["offset"] = offset
    return d

def torso(w):
    s = w["build"]["torso"] * 1.0
    sh = w["build"]["shoulders"]
    singlet = w["outfit"] == "singlet"
    lower, belt = "lower", "belt"
    up = "top" if singlet else "skin"
    def ring(at, rx, rz, color, weights, steps=2):
        return {"at": at, "rx": round(rx, 4), "rz": round(rz, 4), "color": color, "w": weights, "steps": steps}
    pts = [
        ring(J("hips", [0, -0.13, 0.01]), 0.15 * s, 0.12 * s, lower, {"hips": 1}, 1),
        ring(J("hips", [0, -0.06, 0.01]), 0.182 * s, 0.138 * s, lower, {"hips": 1}),
        ring(J("hips", [0, 0.035, 0]), 0.178 * s, 0.135 * s, belt, {"hips": 1}, 1),
        ring(J("hips", [0, 0.07, 0]), 0.172 * s, 0.132 * s, up, {"hips": 0.75, "spine": 0.25}),
        ring(J("spine"), 0.165 * s, 0.128 * s, up, {"hips": 0.3, "spine": 0.7}),
        ring(J("spine", [0, 0.10, 0]), 0.178 * s, 0.135 * s, up, {"spine": 0.6, "chest": 0.4}),
        ring(J("chest", [0, 0, 0]), 0.195 * s, 0.142 * s, up, {"spine": 0.15, "chest": 0.85}),
        ring(J("chest", [0, 0.12, 0]), 0.212 * sh, 0.146 * s, up, {"chest": 1}),
        ring(J("chest", [0, 0.21, 0.005]), 0.218 * sh, 0.134 * s, up if singlet else "skin", {"chest": 1}, 1),
        ring(J("chest", [0, 0.27, 0.012]), 0.14 * sh, 0.105 * s, "skin", {"chest": 0.85, "neck": 0.15}),
    ]
    return {"name": "torso", "type": "tube", "radial": 14, "caps": [True, True], "points": pts}

def body_parts(w):
    b = w["build"]
    sh, ar, lg, nk = b["shoulders"], b["arms"], b["legs"], b["neck"]
    singlet = w["outfit"] == "singlet"
    legcolor_upper = "lower"
    legcolor_thigh = "lower" if singlet else "skin"
    parts = [torso(w)]
    # Shoulders and back: modest shapes only, no chest muscles
    parts += [
        {"name": "trap", "type": "ellipsoid", "mirror": True, "at": J("chest", [0.09, 0.222, 0.02]),
         "radii": [round(0.1 * sh, 4), 0.05, 0.075], "rotation": [0, 0, -18], "color": "top" if singlet else "skin",
         "w": {"chest": 0.75, "neck": 0.25}},
        {"name": "deltoid", "type": "ellipsoid", "mirror": True, "at": J("rightUpperArm", [0.008, -0.03, 0]),
         "radii": [round(0.088 * ar, 4), round(0.1 * ar, 4), round(0.088 * ar, 4)], "rotation": [0, 0, 25], "color": "skin",
         "w": {"chest": 0.35, "rightUpperArm": 0.65}},
        {"name": "glute", "type": "ellipsoid", "mirror": True, "at": J("hips", [0.08, -0.075, 0.065]),
         "radii": [0.095, 0.095, 0.08], "color": "lower", "w": {"hips": 0.8, "rightUpperLeg": 0.2}},
    ]
    # Neck
    parts.append({"name": "neck", "type": "tube", "radial": 10, "points": [
        {"at": J("chest", [0, 0.21, 0.015]), "r": round(0.084 * nk, 4), "color": "skin", "w": {"chest": 0.8, "neck": 0.2}, "steps": 1},
        {"at": J("neck"), "r": round(0.085 * nk, 4), "color": "skin", "w": {"neck": 1}, "steps": 2},
        {"at": J("head", [0, 0.05, 0.005]), "r": round(0.072 * nk, 4), "color": "skin", "w": {"neck": 0.25, "head": 0.75}},
    ]})
    # Arms
    def ap(at, r, color, wts, steps=2):
        return {"at": at, "r": round(r * ar, 4), "color": color, "w": wts, "steps": steps}
    parts.append({"name": "arm", "type": "tube", "radial": 10, "mirror": True, "caps": [False, True], "points": [
        ap(J("rightUpperArm", [-0.03, 0.02, 0]), 0.09, "skin", {"chest": 0.45, "rightUpperArm": 0.55}),
        ap(B("rightUpperArm", "rightForearm", 0.35), 0.094, "skin", {"rightUpperArm": 1}),
        ap(B("rightUpperArm", "rightForearm", 0.85), 0.076, "skin", {"rightUpperArm": 1}, 1),
        ap(J("rightForearm"), 0.07, "elbow" if "elbowpads" in w["extras"] else "skin", {"rightUpperArm": 0.5, "rightForearm": 0.5}, 1),
        ap(B("rightForearm", "rightHand", 0.25), 0.078, "skin", {"rightForearm": 1}),
        ap(B("rightForearm", "rightHand", 0.6), 0.068, "band", {"rightForearm": 1}),
        ap(J("rightHand"), 0.064, "band", {"rightForearm": 0.9, "rightHand": 0.1}),
    ]})
    if "elbowpads" in w["extras"]:
        parts.append({"name": "elbowpad", "type": "ellipsoid", "mirror": True, "at": J("rightForearm", [0.004, 0.0, 0.012]),
                      "radii": [round(0.08 * ar, 4), 0.07, round(0.08 * ar, 4)], "rotation": [0, 0, 25], "segments": [10, 6],
                      "color": "elbow", "w": {"rightUpperArm": 0.5, "rightForearm": 0.5}})
    parts += [
        {"name": "fist", "type": "ellipsoid", "mirror": True, "at": B("rightHand", "rightHand:tail", 0.42),
         "radii": [round(0.05 * ar, 4), 0.068, round(0.06 * ar, 4)], "rotation": [0, 0, 25], "segments": [10, 8], "color": "skin", "w": {"rightHand": 1}},
        {"name": "thumb", "type": "ellipsoid", "mirror": True, "at": B("rightHand", "rightHand:tail", 0.3, [-0.02, 0, -0.043]),
         "radii": [0.019, 0.033, 0.019], "rotation": [0, 0, 25], "segments": [6, 4], "color": "skin", "w": {"rightHand": 1}},
    ]
    # Legs
    def lp(at, r, color, wts, steps=2):
        return {"at": at, "r": round(r * lg, 4), "color": color, "w": wts, "steps": steps}
    parts.append({"name": "leg", "type": "tube", "radial": 12, "mirror": True, "caps": [False, True], "points": [
        lp(J("rightUpperLeg", [-0.012, 0.06, 0]), 0.132, legcolor_upper, {"hips": 0.55, "rightUpperLeg": 0.45}),
        lp(B("rightUpperLeg", "rightLowerLeg", 0.3), 0.125, legcolor_thigh, {"rightUpperLeg": 1}, 3),
        lp(B("rightUpperLeg", "rightLowerLeg", 0.8), 0.098, "kneepad", {"rightUpperLeg": 1}, 1),
        lp(J("rightLowerLeg", [0, 0, -0.008]), 0.102, "kneepad", {"rightUpperLeg": 0.5, "rightLowerLeg": 0.5}, 1),
        lp(B("rightLowerLeg", "rightFoot", 0.17), 0.093, "lower" if singlet else "skin", {"rightLowerLeg": 1}),
        lp(B("rightLowerLeg", "rightFoot", 0.32 if singlet else 0.4, [0, 0, 0.008]), 0.097, "bootTrim", {"rightLowerLeg": 1}, 1),
        lp(B("rightLowerLeg", "rightFoot", 0.38 if singlet else 0.46, [0, 0, 0.008]), 0.095, "boot", {"rightLowerLeg": 1}, 3),
        lp(J("rightFoot"), 0.073, "boot", {"rightLowerLeg": 0.6, "rightFoot": 0.4}),
    ]})
    parts += [
        {"name": "boot", "type": "ellipsoid", "mirror": True, "at": J("rightFoot", [0, -0.03, -0.055]),
         "radii": [0.066, 0.058, 0.132], "segments": [10, 8], "color": "boot", "w": {"rightFoot": 0.85, "rightLowerLeg": 0.15}},
        {"name": "sole", "type": "box", "mirror": True, "at": J("rightFoot", [0, -0.075, -0.055]),
         "size": [0.12, 0.03, 0.265], "color": "sole", "w": {"rightFoot": 1}},
    ]
    return parts

def head_parts(w):
    H = lambda off: J("head", off)
    parts = [
        {"name": "head", "type": "ellipsoid", "at": H([0, 0.10, -0.005]), "radii": [0.102, 0.122, 0.112], "segments": [14, 10], "color": "skin", "w": {"head": 1}},
        {"name": "nose", "type": "ellipsoid", "at": H([0, 0.085, -0.115]), "radii": [0.018, 0.03, 0.024], "segments": [6, 4], "color": "skin", "w": {"head": 1}},
        {"name": "eye", "type": "ellipsoid", "mirror": True, "at": H([0.04, 0.11, -0.104]), "radii": [0.02, 0.012, 0.012], "segments": [6, 4], "color": "eye", "w": {"head": 1}},
        {"name": "ear", "type": "ellipsoid", "mirror": True, "at": H([0.101, 0.1, 0.005]), "radii": [0.019, 0.034, 0.025], "segments": [6, 4], "color": "skin", "w": {"head": 1}},
    ]
    face = w["face"]
    if face == "goatee":
        parts += [
            {"name": "brow", "type": "ellipsoid", "at": H([0, 0.135, -0.096]), "radii": [0.085, 0.018, 0.028], "segments": [10, 4], "color": "brow", "w": {"head": 1}},
            {"name": "goatee", "type": "ellipsoid", "at": H([0, 0.02, -0.09]), "radii": [0.04, 0.05, 0.035], "segments": [8, 6], "color": "facial", "w": {"head": 1}},
            {"name": "moustache", "type": "ellipsoid", "at": H([0, 0.058, -0.106]), "radii": [0.042, 0.012, 0.016], "segments": [8, 4], "color": "facial", "w": {"head": 1}},
        ]
    elif face == "clean":
        parts += [
            {"name": "brow", "type": "ellipsoid", "mirror": True, "at": H([0.04, 0.136, -0.098]), "radii": [0.032, 0.009, 0.014], "rotation": [0, 0, -6], "segments": [8, 4], "color": "brow", "w": {"head": 1}},
            {"name": "lips", "type": "ellipsoid", "at": H([0, 0.045, -0.104]), "radii": [0.028, 0.01, 0.012], "segments": [8, 4], "color": "lip", "w": {"head": 1}},
        ]
    hair = w["hair"]
    if hair == "mohawk":
        parts += [
            {"name": "mohawk", "type": "ellipsoid", "at": H([0, 0.2, 0.0]), "radii": [0.032, 0.065, 0.13], "rotation": [-8, 0, 0], "segments": [8, 8], "color": "hair", "w": {"head": 1}},
        ]
    elif hair == "ponytail":
        parts += [
            {"name": "hairCap", "type": "ellipsoid", "at": H([0, 0.13, 0.014]), "radii": [0.108, 0.104, 0.118], "segments": [14, 8], "color": "hair", "w": {"head": 1}},
            {"name": "hairBack", "type": "ellipsoid", "at": H([0, 0.09, 0.05]), "radii": [0.1, 0.09, 0.08], "segments": [12, 6], "color": "hair", "w": {"head": 1}},
            {"name": "fringe", "type": "ellipsoid", "at": H([0.025, 0.178, -0.072]), "radii": [0.085, 0.032, 0.05], "rotation": [-20, 0, -12], "segments": [10, 4], "color": "hair", "w": {"head": 1}},
            {"name": "tie", "type": "ellipsoid", "at": H([0, 0.15, 0.125]), "radii": [0.032, 0.032, 0.022], "segments": [8, 4], "color": "band", "w": {"head": 1}},
            {"name": "ponytail", "type": "tube", "radial": 8, "caps": [False, True], "points": [
                {"at": H([0, 0.15, 0.13]), "r": 0.036, "color": "hair", "w": {"head": 1}, "steps": 2},
                {"at": H([0, 0.06, 0.175]), "r": 0.042, "color": "hair", "w": {"head": 1}, "steps": 2},
                {"at": H([0, -0.08, 0.17]), "r": 0.03, "color": "hair", "w": {"head": 0.8, "neck": 0.2}, "steps": 2},
                {"at": H([0, -0.16, 0.15]), "r": 0.012, "color": "hair", "w": {"head": 0.6, "neck": 0.4}},
            ]},
        ]
    return parts

def build(w):
    return {
        "id": w["id"],
        "displayName": w["displayName"],
        "gender": w["gender"],
        "bio": w["bio"],
        "version": 1,
        "skeleton": "../skeleton.json",
        "skeletonId": "ttw-humanoid",
        "heightMeters": 1.9,
        "material": {"type": "standard", "roughness": 0.62, "metalness": 0.0},
        "palette": w["palette"],
        "build": w["build"],
        "style": {"outfit": w["outfit"], "hair": w["hair"], "face": w["face"], "extras": w["extras"]},
        "notes": "Appearance only, generated by tools/build-roster.py. All parts merge into ONE skinned mesh with ONE vertex-coloured material. Joints come from skeleton.json and are never moved per wrestler; body shape changes live in part sizes.",
        "parts": body_parts(w) + head_parts(w),
    }

def dump(obj):
    s = json.dumps(obj, indent=2)
    # keep short numeric arrays on one line
    s = re.sub(r'\[\s+(-?[\d.e-]+(?:,\s+-?[\d.e-]+)*)\s+\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', s)
    s = re.sub(r'\[\s+("[^"\n]*"(?:,\s+"[^"\n]*")*)\s+\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', s)
    return s + '\n'

if __name__ == '__main__':
    out = ROOT / 'roster'
    out.mkdir(exist_ok=True)
    for w in ROSTER:
        (out / f"{w['id']}.json").write_text(dump(build(w)))
        print('wrote', w['id'], w['displayName'])
