"""Batch 2 roster: wrestler-03 to wrestler-20.

Reuses the Batch 1 body template from tools/build-roster.py (imported, not modified) and adds
more hair, face, outfit and extra styles on top. Same skeleton, same joints, same part layout,
so every animation works on every wrestler.

Usage (from assets/ttw-wrestlers):  python tools/batch2/build-roster-b2.py
"""
import sys, copy, importlib.util, pathlib, json
sys.dont_write_bytecode = True

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('roster_b1', ROOT / 'tools' / 'build-roster.py')
B1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B1)
J, B = B1.J, B1.B

def P(skin, lower, top=None, belt='#f4f1ea', boot='#1c1d22', bootTrim=None, sole='#1c1d22', kneepad='#1c1d22',
      band=None, elbow=None, hair='#1f1410', facial=None, eye='#15100d', brow=None, lip=None, mask=None, mask2=None, accent=None):
    return {
        "skin": skin, "lower": lower, "top": top or skin, "belt": belt, "boot": boot,
        "bootTrim": bootTrim or belt, "sole": sole, "kneepad": kneepad, "band": band or belt,
        "elbow": elbow or kneepad, "hair": hair, "facial": facial or hair, "eye": eye, "brow": brow or facial or hair,
        "lip": lip or '#8a4a3a', "mask": mask or lower, "mask2": mask2 or belt, "accent": accent or belt,
    }

def build_(t=1.0, s=1.0, a=1.0, l=1.0, n=1.0):
    return {"torso": t, "shoulders": s, "arms": a, "legs": l, "neck": n}

ROSTER = [
    dict(id="wrestler-03", displayName="Marcus Vane", gender="male", bio="Bald brawler with a full beard, black tights and gold trim.",
         palette=P('#8d5a3b', '#16171c', belt='#f2b632', boot='#16171c', hair='#16100c'),
         build=build_(1.04, 1.04, 1.04, 1.0, 1.08), outfit="longtights", hair="bald", face="beard", extras=["armbands"]),
    dict(id="wrestler-04", displayName="Kenji Arata", gender="male", bio="Strong-style striker. Topknot, white trunks, red kneepads and boots.",
         palette=P('#e2b48c', '#f4f1ea', belt='#c41f2b', boot='#c41f2b', bootTrim='#f4f1ea', kneepad='#c41f2b', band='#c41f2b', hair='#121014'),
         build=build_(0.98, 1.0, 0.98, 1.0, 1.0), outfit="trunks", hair="topknot", face="clean", extras=[]),
    dict(id="wrestler-05", displayName="Diego Fuego", gender="male", bio="Masked high flyer in red and gold.",
         palette=P('#c68a5e', '#c41f2b', belt='#f2b632', boot='#f2b632', bootTrim='#c41f2b', kneepad='#c41f2b', hair='#1f1410',
                   mask='#c41f2b', mask2='#f2b632'),
         build=build_(0.94, 0.96, 0.92, 0.98, 0.94), outfit="longtights", hair="none", face="mask", extras=[]),
    dict(id="wrestler-06", displayName="Tank Okafor", gender="male", bio="Powerhouse. Buzz cut, moustache, blue fight shorts.",
         palette=P('#5a3a26', '#1d4fbf', belt='#f4f1ea', boot='#16171c', kneepad='#1d4fbf', hair='#0f0c0a'),
         build=build_(1.08, 1.08, 1.08, 1.04, 1.1), outfit="shorts", hair="buzz", face="moustache", extras=[]),
    dict(id="wrestler-07", displayName="Silas Crowe", gender="male", bio="Long black hair, white face paint, dark purple singlet.",
         palette=P('#e6c2a0', '#2b1a3a', top='#2b1a3a', belt='#8a8f9c', boot='#16171c', bootTrim='#8a8f9c', hair='#0c0b0e',
                   accent='#f4f1ea'),
         build=build_(0.96, 0.98, 0.96, 1.0, 0.96), outfit="singlet", hair="long", face="facepaint", extras=[]),
    dict(id="wrestler-08", displayName="Jett Lennox", gender="male", bio="Showboat. Spiky blond hair, shades, neon green trunks.",
         palette=P('#f0cfb0', '#3fd13a', belt='#16171c', boot='#3fd13a', bootTrim='#16171c', kneepad='#16171c', hair='#f2d36b',
                   accent='#16171c'),
         build=build_(0.96, 1.0, 0.96, 1.0, 0.98), outfit="trunks", hair="spiky", face="shades", extras=[]),
    dict(id="wrestler-09", displayName="Ivy Hart", gender="female", bio="Red bob, purple singlet, kneepads and boots.",
         palette=P('#f0cfb0', '#6b2fa8', top='#6b2fa8', belt='#f4f1ea', boot='#6b2fa8', bootTrim='#f4f1ea', kneepad='#16171c',
                   hair='#b0331e', lip='#a4524a'),
         build=build_(0.9, 0.9, 0.84, 0.93, 0.86), outfit="singlet-bare-legs", hair="bob", face="clean", extras=[]),
    dict(id="wrestler-10", displayName="Bruno Kael", gender="male", bio="Afro, goatee, orange tights.",
         palette=P('#6e4a32', '#f07a1a', belt='#16171c', boot='#16171c', bootTrim='#f07a1a', hair='#120d0a'),
         build=build_(1.02, 1.02, 1.0, 1.0, 1.02), outfit="longtights", hair="afro", face="goatee", extras=["elbowpads"]),
    dict(id="wrestler-11", displayName="Hollis Grant", gender="male", bio="Veteran. Slicked grey hair, horseshoe moustache, brown trunks, tan boots.",
         palette=P('#d9a27a', '#5a3a22', belt='#d8b07a', boot='#c49a64', bootTrim='#5a3a22', kneepad='#5a3a22', hair='#9a9aa0'),
         build=build_(1.04, 1.0, 1.0, 1.0, 1.04), outfit="trunks", hair="slick", face="horseshoe", extras=[]),
    dict(id="wrestler-12", displayName="Ravi Sen", gender="male", bio="Technician. Buzz cut, teal fight shorts, armbands.",
         palette=P('#9a6a48', '#0f8f8a', belt='#f4f1ea', boot='#16171c', kneepad='#0f8f8a', band='#f4f1ea', hair='#120d0a'),
         build=build_(0.96, 0.98, 0.96, 1.0, 0.96), outfit="shorts", hair="buzz", face="clean", extras=["armbands"]),
    dict(id="wrestler-13", displayName="Axel Storm", gender="male", bio="Long blond hair and beard, electric blue tights.",
         palette=P('#e6b896', '#1e66ff', belt='#f2d36b', boot='#1e66ff', bootTrim='#f2d36b', kneepad='#0d1a3a', hair='#e0bd62'),
         build=build_(1.02, 1.04, 1.02, 1.0, 1.02), outfit="longtights", hair="long", face="beard", extras=[]),
    dict(id="wrestler-14", displayName="Kai Moana", gender="male", bio="Long dark hair, clean shaven, green trunks.",
         palette=P('#a8714c', '#1f7a3a', belt='#f2b632', boot='#16171c', bootTrim='#1f7a3a', kneepad='#16171c', hair='#16100c'),
         build=build_(1.06, 1.04, 1.04, 1.02, 1.06), outfit="trunks", hair="long", face="clean", extras=[]),
    dict(id="wrestler-15", displayName="Zeke Malone", gender="male", bio="Blue mohawk, shades, black and blue tights.",
         palette=P('#e2b48c', '#101218', belt='#2f6bff', boot='#2f6bff', bootTrim='#101218', kneepad='#2f6bff', hair='#2f6bff',
                   accent='#101218'),
         build=build_(0.98, 1.0, 0.98, 1.0, 1.0), outfit="longtights", hair="mohawk", face="shades", extras=[]),
    dict(id="wrestler-16", displayName="Luna Vega", gender="female", bio="Two braids, star face paint, black and silver bodysuit.",
         palette=P('#c68a5e', '#16171c', top='#16171c', belt='#c9ccd6', boot='#c9ccd6', bootTrim='#16171c', kneepad='#c9ccd6',
                   hair='#1f1410', lip='#8a4a3a', accent='#c9ccd6'),
         build=build_(0.9, 0.9, 0.84, 0.93, 0.86), outfit="singlet", hair="braids", face="facepaint", extras=[]),
    dict(id="wrestler-17", displayName="Otis Brand", gender="male", bio="Old-school bruiser. Bald, moustache, red singlet.",
         palette=P('#d9a27a', '#b3121a', top='#b3121a', belt='#f4f1ea', boot='#16171c', kneepad='#16171c', hair='#3a2a1e'),
         build=build_(1.08, 1.06, 1.06, 1.04, 1.1), outfit="singlet", hair="bald", face="moustache", extras=[]),
    dict(id="wrestler-18", displayName="Felix Dorn", gender="male", bio="Showman. Slicked black hair, white tights with gold.",
         palette=P('#e6c2a0', '#f4f1ea', belt='#f2b632', boot='#f4f1ea', bootTrim='#f2b632', kneepad='#f2b632', hair='#0c0b0e'),
         build=build_(0.96, 1.0, 0.96, 1.0, 0.96), outfit="longtights", hair="slick", face="clean", extras=[]),
    dict(id="wrestler-19", displayName="Ox Barrow", gender="male", bio="Buzz cut, full beard, olive fight shorts.",
         palette=P('#c08a64', '#4b5a2a', belt='#16171c', boot='#3a2a1e', bootTrim='#4b5a2a', kneepad='#3a2a1e', hair='#2a1c12'),
         build=build_(1.06, 1.06, 1.06, 1.04, 1.08), outfit="shorts", hair="buzz", face="beard", extras=[]),
    dict(id="wrestler-20", displayName="Nico Strand", gender="male", bio="Spiky red hair, goatee, yellow trunks, elbow pads.",
         palette=P('#f0cfb0', '#f2c21a', belt='#16171c', boot='#16171c', bootTrim='#f2c21a', kneepad='#16171c', hair='#c4361c'),
         build=build_(0.96, 0.98, 0.96, 1.0, 0.96), outfit="trunks", hair="spiky", face="goatee", extras=["elbowpads"]),
]

# ---------------------------------------------------------------- outfit variants on top of the batch 1 body

def body_parts_v2(w):
    outfit = w["outfit"]
    base = dict(w)
    if outfit == "longtights":       # bare chest, tights to the boots: the batch 1 singlet body with top = skin
        base = dict(w, outfit="singlet", palette=dict(w["palette"], top=w["palette"]["skin"]))
        parts = B1.body_parts(base)
        for p in parts:
            if p["name"] == "trap": p["color"] = "skin"
        return parts
    if outfit == "singlet-bare-legs":  # singlet body, legs bare below the hem
        parts = B1.body_parts(dict(w, outfit="singlet"))
        for p in parts:
            if p["name"] == "leg":
                p["points"][1]["color"] = "skin"
                p["points"][4]["color"] = "skin"
        return parts
    if outfit == "shorts":            # fight shorts: trunks body, thighs covered to the kneepads
        parts = B1.body_parts(dict(w, outfit="trunks"))
        for p in parts:
            if p["name"] == "leg":
                p["points"][1]["color"] = "lower"
                p["points"][1]["r"] = round(p["points"][1]["r"] * 1.06, 4)
        return parts
    return B1.body_parts(base)

def extras_v2(w):
    out = []
    if "armbands" in w["extras"]:
        out.append({"name": "armband", "type": "tube", "radial": 10, "mirror": True, "points": [
            {"at": B("rightUpperArm", "rightForearm", 0.52), "r": round(0.092 * w["build"]["arms"], 4), "color": "band", "w": {"rightUpperArm": 1}, "steps": 1},
            {"at": B("rightUpperArm", "rightForearm", 0.62), "r": round(0.088 * w["build"]["arms"], 4), "color": "band", "w": {"rightUpperArm": 1}}]})
    return out

# ---------------------------------------------------------------- heads

def H(off): return J("head", off)
def E(name, at, radii, color, seg=(10, 8), rot=None, mirror=False):
    d = {"name": name, "type": "ellipsoid", "at": at, "radii": radii, "segments": list(seg), "color": color, "w": {"head": 1}}
    if rot: d["rotation"] = rot
    if mirror: d["mirror"] = True
    return d

def head_parts_v2(w):
    face, hair = w["face"], w["hair"]
    # Start from batch 1 head: base head, nose, eyes, ears (+ batch 1 face/hair when they match)
    b1 = dict(w, face=face if face in ("goatee", "clean") else "none", hair=hair if hair in ("mohawk", "ponytail") else "none")
    parts = B1.head_parts(b1)
    brow_m = E("brow", H([0, 0.135, -0.096]), [0.085, 0.018, 0.028], "brow", (10, 4))
    if face == "beard":
        parts += [brow_m,
                  E("beard", H([0, 0.03, -0.05]), [0.088, 0.07, 0.078], "facial", (12, 8)),
                  E("moustache", H([0, 0.058, -0.106]), [0.044, 0.013, 0.017], "facial", (8, 4))]
    elif face == "moustache":
        parts += [brow_m, E("moustache", H([0, 0.057, -0.108]), [0.05, 0.015, 0.018], "facial", (8, 4))]
    elif face == "horseshoe":
        parts += [brow_m,
                  E("moustache", H([0, 0.058, -0.106]), [0.046, 0.013, 0.017], "facial", (8, 4)),
                  {"name": "horseshoe", "type": "box", "mirror": True, "at": H([0.042, 0.03, -0.098]), "size": [0.016, 0.06, 0.016],
                   "color": "facial", "w": {"head": 1}}]
    elif face == "shades":
        parts += [brow_m,
                  {"name": "shades", "type": "box", "at": H([0, 0.112, -0.112]), "size": [0.17, 0.034, 0.016], "color": "accent", "w": {"head": 1}},
                  {"name": "shadesArm", "type": "box", "mirror": True, "at": H([0.09, 0.115, -0.05]), "size": [0.01, 0.012, 0.12], "color": "accent", "w": {"head": 1}}]
    elif face == "facepaint":
        parts += [{"name": "brow", "type": "ellipsoid", "mirror": True, "at": H([0.04, 0.136, -0.098]), "radii": [0.032, 0.009, 0.014],
                   "rotation": [0, 0, -6], "segments": [8, 4], "color": "brow", "w": {"head": 1}},
                  {"name": "paint", "type": "box", "mirror": True, "at": H([0.045, 0.085, -0.1]), "size": [0.016, 0.05, 0.012],
                   "rotation": [0, 18, 0], "color": "accent", "w": {"head": 1}},
                  {"name": "paintBrow", "type": "box", "at": H([0, 0.155, -0.1]), "size": [0.12, 0.012, 0.012], "color": "accent", "w": {"head": 1}}]
        if w["gender"] == "female":
            parts.append(E("lips", H([0, 0.045, -0.104]), [0.028, 0.01, 0.012], "lip", (8, 4)))
    elif face == "mask":
        # full hood over the batch 1 head shape; eye and mouth openings in the second colour
        parts += [E("mask", H([0, 0.105, -0.002]), [0.106, 0.128, 0.116], "mask", (14, 10)),
                  E("maskEye", H([0.04, 0.112, -0.1]), [0.034, 0.024, 0.02], "mask2", (8, 6), rot=[0, 0, -12], mirror=True),
                  E("maskEyeHole", H([0.04, 0.11, -0.112]), [0.02, 0.012, 0.01], "eye", (6, 4), mirror=True),
                  E("maskCrest", H([0, 0.17, -0.06]), [0.016, 0.05, 0.05], "mask2", (6, 6)),
                  E("maskMouth", H([0, 0.04, -0.108]), [0.03, 0.012, 0.01], "mask2", (8, 4))]

    if hair == "bald":
        pass
    elif hair == "buzz":
        parts.append(E("buzz", H([0, 0.13, 0.008]), [0.106, 0.1, 0.116], "hair", (14, 8)))
    elif hair == "slick":
        parts += [E("slick", H([0, 0.14, 0.014]), [0.108, 0.098, 0.12], "hair", (14, 8)),
                  E("slickBack", H([0, 0.1, 0.06]), [0.1, 0.09, 0.075], "hair", (12, 6)),
                  E("quiff", H([0, 0.205, -0.06]), [0.07, 0.035, 0.06], "hair", (10, 4), rot=[-14, 0, 0])]
    elif hair == "topknot":
        parts += [E("buzz", H([0, 0.13, 0.01]), [0.106, 0.1, 0.116], "hair", (14, 8)),
                  E("knot", H([0, 0.245, 0.03]), [0.04, 0.04, 0.04], "hair", (8, 6)),
                  E("knotTie", H([0, 0.215, 0.025]), [0.03, 0.012, 0.03], "band", (8, 4))]
    elif hair == "spiky":
        parts.append(E("buzz", H([0, 0.13, 0.008]), [0.106, 0.1, 0.116], "hair", (14, 8)))
        spikes = [([0, 0.235, -0.04], [0, 0, 0]), ([0.05, 0.225, 0.0], [0, 0, -28]), ([-0.05, 0.225, 0.0], [0, 0, 28]),
                  ([0, 0.225, 0.05], [30, 0, 0]), ([0.035, 0.215, -0.07], [-25, 0, -15]), ([-0.035, 0.215, -0.07], [-25, 0, 15]),
                  ([0.04, 0.2, 0.08], [35, 0, -20]), ([-0.04, 0.2, 0.08], [35, 0, 20])]
        for i, (pos, rot) in enumerate(spikes):
            parts.append(E(f"spike{i}", H(pos), [0.022, 0.06, 0.022], "hair", (6, 4), rot=rot))
    elif hair == "afro":
        parts.append(E("afro", H([0, 0.17, 0.02]), [0.16, 0.14, 0.16], "hair", (14, 10)))
    elif hair == "long":
        parts += [E("hairCap", H([0, 0.135, 0.014]), [0.11, 0.105, 0.12], "hair", (14, 8)),
                  E("hairBack", H([0, 0.06, 0.06]), [0.11, 0.12, 0.08], "hair", (12, 8)),
                  {"name": "hairFall", "type": "tube", "radial": 10, "caps": [False, True], "points": [
                      {"at": H([0, 0.06, 0.07]), "rx": 0.11, "rz": 0.07, "color": "hair", "w": {"head": 1}, "steps": 2},
                      {"at": H([0, -0.08, 0.075]), "rx": 0.12, "rz": 0.06, "color": "hair", "w": {"head": 0.6, "neck": 0.4}, "steps": 2},
                      {"at": H([0, -0.17, 0.08]), "rx": 0.13, "rz": 0.035, "color": "hair", "w": {"neck": 0.6, "chest": 0.4}}]},
                  {"name": "hairSide", "type": "ellipsoid", "mirror": True, "at": H([0.1, 0.04, 0.0]), "radii": [0.03, 0.1, 0.07],
                   "segments": [8, 6], "color": "hair", "w": {"head": 1}}]
    elif hair == "bob":
        parts += [E("hairCap", H([0, 0.13, 0.012]), [0.112, 0.108, 0.12], "hair", (14, 8)),
                  E("bob", H([0, 0.065, 0.03]), [0.125, 0.085, 0.11], "hair", (14, 8)),
                  E("fringe", H([0.0, 0.178, -0.072]), [0.09, 0.03, 0.05], "hair", (10, 4), rot=[-20, 0, 0])]
    elif hair == "braids":
        parts += [E("hairCap", H([0, 0.135, 0.012]), [0.108, 0.102, 0.118], "hair", (14, 8)),
                  E("fringe", H([0.0, 0.18, -0.07]), [0.085, 0.026, 0.045], "hair", (10, 4), rot=[-22, 0, 0])]
        parts.append({"name": "braid", "type": "tube", "radial": 8, "mirror": True, "caps": [False, True], "points": [
            {"at": H([0.07, 0.08, 0.08]), "r": 0.03, "color": "hair", "w": {"head": 1}, "steps": 2},
            {"at": H([0.08, -0.06, 0.09]), "r": 0.028, "color": "hair", "w": {"head": 0.7, "neck": 0.3}, "steps": 2},
            {"at": H([0.08, -0.17, 0.08]), "r": 0.022, "color": "hair", "w": {"neck": 0.6, "chest": 0.4}, "steps": 1},
            {"at": H([0.08, -0.2, 0.078]), "r": 0.024, "color": "accent", "w": {"neck": 0.5, "chest": 0.5}, "steps": 1},
            {"at": H([0.08, -0.24, 0.075]), "r": 0.01, "color": "accent", "w": {"neck": 0.5, "chest": 0.5}}]})
    return parts

def build(w):
    d = B1.build(dict(w, face="clean", hair="none"))   # metadata layout identical to batch 1
    d["style"] = {"outfit": w["outfit"], "hair": w["hair"], "face": w["face"], "extras": w["extras"]}
    d["batch"] = 2
    d["notes"] = ("Appearance only, generated by tools/batch2/build-roster-b2.py from the batch 1 body template. "
                  "All parts merge into ONE skinned mesh with ONE vertex-coloured material. Joints come from skeleton.json "
                  "and are never moved per wrestler.")
    d["parts"] = body_parts_v2(w) + extras_v2(w) + head_parts_v2(w)
    return d

if __name__ == '__main__':
    out = ROOT / 'roster'
    for w in ROSTER:
        path = out / f"{w['id']}.json"
        if path.exists() and json.loads(path.read_text()).get("batch") != 2:
            raise SystemExit(f"refusing to overwrite batch 1 file {path}")
        path.write_text(B1.dump(build(w)))
        print('wrote', w['id'], w['displayName'], w['gender'])
