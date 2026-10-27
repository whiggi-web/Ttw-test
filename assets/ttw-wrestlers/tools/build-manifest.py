"""Build manifest.json from the roster folder, the generated animation index and the planned list.

Usage (from assets/ttw-wrestlers):  python tools/build-manifest.py
Run build-roster.py and build-animations.py first.
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent

EVENTS = {
    "hit": "A strike reaches its target. Fields: attachment or bone (contact point), zone (head/body/legs), reach (metres in front of the attacker).",
    "hit_received": "Start of a damage reaction. Fields: zone.",
    "grab": "Hands close on the opponent. Fields: attachment.",
    "release": "The opponent or prop is let go, or a clip hands over to the next one. Fields: next (suggested follow-up animation id).",
    "rope_contact": "Body meets the ropes. Fields: attachment.",
    "rebound": "The ropes push the wrestler back out.",
    "jump": "Feet leave the mat.",
    "land": "Body or feet hit the mat. Fields: zone.",
    "recover": "From here the wrestler can be given new commands.",
    "weapon_impact": "A held prop hits something. Fields: attachment, prop.",
    "table_break": "The table should switch to its broken state.",
    "finished": "Emitted by the loader when a non-looping clip ends (not stored in the animation files)."
}

# Everything still to build, with the ids they will use. Status flips to "ready" as files land.
PLANNED = {
    "movement": ["idle-fight:Idle, fighting stance", "walk-cocky:Walk, cocky", "walk-injured:Walk, injured", "sprint:Sprint",
                 "backpedal:Backpedal", "sidestep-left:Sidestep left", "sidestep-right:Sidestep right", "turn-180:Turn around",
                 "stumble-forward:Stumble forward", "stumble-backward:Stumble backward", "stagger-move:Stagger while moving"],
    "striking": ["jab:Jab", "hook-left:Hook punch, left", "hook-right:Hook punch, right", "uppercut:Uppercut", "body-punch:Body punch",
                 "low-kick:Low kick", "roundhouse:Roundhouse kick", "knee:Knee strike", "elbow:Elbow strike",
                 "clothesline:Clothesline", "double-axe:Double axe handle"],
    "grappling": ["grab:Grab opponent", "grapple-idle:Grapple idle", "push:Push opponent", "break-grapple:Break grapple",
                  "spear:Spear tackle", "shoulder-charge:Shoulder charge", "body-slam:Body slam", "suplex:Suplex", "ddt:DDT",
                  "headlock:Headlock", "irish-whip:Irish whip", "throw-to-ropes:Throw opponent towards ropes"],
    "ropes": ["run-into-ropes:Run into ropes", "turn-from-ropes:Turn to face away from ropes", "rope-stretch:Rope stretch and recoil",
              "spring-forward:Spring forward from ropes", "bounce-running:Bounce off ropes while running", "jump-over-top:Jump over top rope",
              "climb-through:Climb through ropes", "slide-under:Slide under bottom rope", "enter-ring:Enter ring through ropes",
              "exit-ring:Exit ring through ropes", "tangled:Tangled in ropes"],
    "aerial": ["standing-jump:Standing jump", "running-jump:Running jump", "diving-attack:Diving attack", "swan-dive:Swan dive",
               "elbow-drop:Diving elbow drop", "body-splash:Diving body splash", "top-rope-jump:Top-rope jump",
               "land-on-opponent:Landing on opponent", "missed-dive:Missed dive and crash landing"],
    "reactions": ["hit-front-body:Hit from front, body", "hit-back-body:Hit from behind, body", "hit-left:Hit from left",
                  "hit-right:Hit from right", "hit-kick:Hit by kick", "hit-clothesline:Hit by clothesline", "hit-chair:Hit by chair",
                  "stunned:Stunned", "dizzy:Dizzy", "knocked-back:Knocked backwards", "stumble-recover:Stumble and recover"],
    "falls": ["fall-forward:Fall forwards", "fall-left:Fall sideways, left", "fall-right:Fall sideways, right",
              "collapse-knees:Collapse to knees", "fall-spear:Fall after spear", "fall-slam:Fall after body slam",
              "lie-back:Lie on back", "lie-front:Lie face down", "roll-to-back:Roll onto back", "roll-to-front:Roll onto stomach",
              "getup-front:Get up from stomach", "getup-injured:Get up slowly, injured", "quick-recovery:Quick recovery",
              "knockout:Knockout idle"],
    "taunts": ["raise-arms:Raise both arms", "flex:Flex muscles", "point:Point at opponent", "beckon:Beckon opponent",
               "crowd-hype:Crowd hype", "chest-beat:Chest beating", "victory:Victory celebration", "cocky-laugh:Cocky laugh",
               "angry-challenge:Angry challenge", "exhausted-celebration:Exhausted celebration"],
    "weapons": ["chair-pickup:Pick up folding chair", "chair-hold:Hold chair", "chair-swing-horizontal:Swing chair horizontally",
                "chair-swing-overhead:Swing chair overhead", "chair-hit-reaction:Chair hit reaction", "chair-drop:Drop chair",
                "table-pickup:Pick up table", "table-carry:Carry table", "table-setup:Set up table", "table-push:Push opponent onto table",
                "table-slam:Slam opponent through table", "table-break-reaction:Table-breaking reaction",
                "table-fall-through:Fall through broken table"],
}
PAIRED = {"body-slam", "suplex", "ddt", "headlock", "irish-whip", "throw-to-ropes", "spear", "grab", "push", "break-grapple",
          "table-push", "table-slam"}

def main():
    roster = []
    for f in sorted((ROOT / 'roster').glob('wrestler-*.json')):
        d = json.loads(f.read_text())
        roster.append({"id": d["id"], "displayName": d["displayName"], "gender": d["gender"], "file": f"roster/{f.name}",
                       "style": d.get("style", {}), "status": "ready"})
    for i in range(len(roster) + 1, 21):
        roster.append({"id": f"wrestler-{i:02d}", "file": f"roster/wrestler-{i:02d}.json", "status": "planned"})

    ready = json.loads((ROOT / 'tools' / 'animation-index.json').read_text())
    for a in ready: a["status"] = "ready"
    have = {a["id"] for a in ready}
    planned = []
    for cat, items in PLANNED.items():
        for item in items:
            slug, name = item.split(':', 1)
            cid = f"{cat}.{slug}"
            if cid in have: continue
            entry = {"id": cid, "name": name, "category": cat, "file": f"animations/{cat}/{slug}.json", "status": "planned"}
            if slug in PAIRED:
                entry["paired"] = True
                entry["roles"] = {"attacker": f"animations/{cat}/{slug}.attacker.json", "receiver": f"animations/{cat}/{slug}.receiver.json"}
                entry.pop("file")
            planned.append(entry)

    manifest = {
        "name": "TTW Universal Wrestler Pack",
        "version": "0.1.0",
        "threeVersion": "r160",
        "skeleton": "skeleton.json",
        "skeletonId": "ttw-humanoid",
        "loader": "loader.js",
        "conventions": {
            "units": "meters", "up": "+y", "forward": "-z", "feetAtY": 0, "heightMeters": 1.9,
            "rotations": "degrees, Euler XYZ, local to the bone, relative to the neutral pose",
            "positions": "offsets from the bone's rest position",
            "animationIds": "<category>.<name>",
            "ropes": "rope animations assume the ropes are behind the wrestler (+Z), top rope about 1.25 m up, about 0.4 m behind the feet",
        },
        "rootMotionModes": {
            "none": "Animation stays on the spot.",
            "inPlace": "Looping locomotion. The game moves the wrestler at 'speed' m/s along 'direction' (local).",
            "speedCurve": "One-shot movement. The game moves the wrestler using 'speedCurve' [[time, m/s], ...]. Wrestler.getRootSpeed() samples it.",
            "baked": "The hips travel inside the clip. When the next clip starts, the loader moves the wrestler by the hips' XZ offset ('endOffset' at the end of the clip).",
        },
        "events": EVENTS,
        "wrestlers": roster,
        "animations": ready + planned,
        "props": [
            {"id": "folding-chair", "file": "props/folding-chair.json", "status": "planned", "states": ["folded", "open"]},
            {"id": "wrestling-table", "file": "props/wrestling-table.json", "status": "planned", "states": ["intact", "damaged", "broken"]},
        ],
        "pairedMoveSchema": {
            "id": "grappling.body-slam",
            "duration": 1.6,
            "anchor": "attacker",
            "receiverOffset": {"position": [0, 0, -0.55], "rotationY": 180},
            "contacts": [{"time": 0.2, "attacker": "rightHandGrip", "receiver": "waist"}],
            "events": [{"time": 0.2, "name": "grab"}, {"time": 1.15, "name": "land", "role": "receiver"}, {"time": 1.3, "name": "release"}],
            "attacker": "animations/grappling/body-slam.attacker.json",
            "receiver": "animations/grappling/body-slam.receiver.json",
            "notes": "Both role files are normal animation files with the same duration. The receiver is placed at receiverOffset in the attacker's local frame and both clips start on the same frame. Receiver lift/throw travel is baked in its hips/root tracks."
        },
        "stats": {"wrestlersReady": sum(1 for w in roster if w["status"] == "ready"),
                  "animationsReady": len(ready), "animationsPlanned": len(planned)},
    }
    s = json.dumps(manifest, indent=2)
    s = re.sub(r'\[\s+(-?[\d.e-]+(?:,\s+-?[\d.e-]+)*)\s+\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', s)
    s = re.sub(r'\[\s+("[^"\n]*"(?:,\s+"[^"\n]*")*)\s+\]', lambda m: '[' + ', '.join(x.strip() for x in m.group(1).split(',')) + ']', s)
    (ROOT / 'manifest.json').write_text(s + '\n')
    print('manifest:', manifest['stats'])

if __name__ == '__main__':
    main()
