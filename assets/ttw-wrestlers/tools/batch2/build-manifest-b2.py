"""Write manifest-batch2.json: the full pack index after Batch 2 (Batch 1 + Batch 2, plus what is still planned).

The Batch 1 manifest.json is left exactly as delivered. loadPack() accepts either file.

Usage (from assets/ttw-wrestlers):  python tools/batch2/build-manifest-b2.py
"""
import sys, json, pathlib, importlib.util, re
sys.dont_write_bytecode = True

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('manifest_b1', ROOT / 'tools' / 'build-manifest.py')
M1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M1)

LATER = {'ropes': 3, 'aerial': 3, 'taunts': 3, 'grappling': 4, 'weapons': 4}

def main():
    roster = []
    for f in sorted((ROOT / 'roster').glob('wrestler-*.json')):
        d = json.loads(f.read_text())
        roster.append({"id": d["id"], "displayName": d["displayName"], "gender": d["gender"], "file": f"roster/{f.name}",
                       "style": d.get("style", {}), "status": "ready", "batch": d.get("batch", 1)})

    b1 = json.loads((ROOT / 'tools' / 'animation-index.json').read_text())
    for a in b1: a.update(status="ready", batch=1)
    b2 = json.loads((ROOT / 'tools' / 'batch2' / 'animation-index-b2.json').read_text())
    for a in b2: a["status"] = "ready"
    ready = b1 + b2
    have = {a["id"] for a in ready}

    planned = []
    for cat, items in M1.PLANNED.items():
        for item in items:
            slug, name = item.split(':', 1)
            cid = f"{cat}.{slug}"
            if cid in have: continue
            e = {"id": cid, "name": name, "category": cat, "file": f"animations/{cat}/{slug}.json", "status": "planned", "batch": LATER.get(cat, 3)}
            if slug in M1.PAIRED:
                e["paired"] = True
                e["roles"] = {"attacker": f"animations/{cat}/{slug}.attacker.json", "receiver": f"animations/{cat}/{slug}.receiver.json"}
                e.pop("file")
            planned.append(e)

    b1m = json.loads((ROOT / 'manifest.json').read_text())
    manifest = {
        "name": b1m["name"],
        "version": "0.2.0",
        "threeVersion": b1m["threeVersion"],
        "skeleton": "skeleton.json",
        "skeletonId": b1m["skeletonId"],
        "loader": "loader.js",
        "extensions": ["loader-ext.js"],
        "conventions": b1m["conventions"],
        "rootMotionModes": dict(b1m["rootMotionModes"], baked=b1m["rootMotionModes"]["baked"] +
                                " Optional endRotationY (degrees) turns the wrestler when the next clip starts; applied by loader-ext.js."),
        "poseStates": {
            "standing": "default; any clip without a starts-* tag starts here",
            "lying-back": "flat on the back, head towards +Z (behind), feet towards the wrestler's origin",
            "lying-front": "face down, head towards -Z (in front)",
            "kneeling": "on both knees, sitting back on the heels",
            "rope-lean": "leaning back on the ropes (ropes behind, +Z)",
            "airborne-back": "held horizontal on the back at waist height (receiver of a slam)",
            "tags": "starts-<state> / ends-<state> on each animation; loader-ext.js exposes getStartState, getEndState, animationsFrom"
        },
        "events": M1.EVENTS,
        "wrestlers": roster,
        "animations": ready + planned,
        "props": [dict(p, batch=4) for p in b1m["props"]],
        "pairedMoveSchema": b1m["pairedMoveSchema"],
        "batches": {
            "1": "skeleton, wrestlers 01-02, 11 core animations, loader, viewer",
            "2": "wrestlers 03-20, movement, striking, damage reactions, falls and recovery, loader-ext.js",
            "3": "ropes, aerial, taunts (planned)",
            "4": "grappling paired moves, weapons, folding chair and table props (planned)"
        },
        "stats": {"wrestlersReady": len(roster), "male": sum(w["gender"] == "male" for w in roster),
                  "female": sum(w["gender"] == "female" for w in roster),
                  "animationsReady": len(ready), "animationsPlanned": len(planned)},
    }
    s = json.dumps(manifest, indent=2)
    s = re.sub(r'\[\s+(-?[\d.e-]+(?:,\s+-?[\d.e-]+)*)\s+\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', s)
    s = re.sub(r'\[\s+("[^"\n]*"(?:,\s+"[^"\n]*")*)\s+\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', s)
    (ROOT / 'manifest-batch2.json').write_text(s + '\n')
    print('manifest-batch2:', manifest['stats'])

if __name__ == '__main__':
    main()
