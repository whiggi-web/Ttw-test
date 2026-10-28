"""Build manifest-master.json: every TTW animation in one place.

Usage (from assets/ttw-wrestlers):  python tools/build-master-manifest.py

Reads (never writes) manifest-batch2.json and ../ttw-props/manifest.json, then adds every library v3 clip
from tools/phase*/index.json, paired moves from tools/phase*/paired-index.json and the planned catalogue in
tools/planned-library.json. Old 'planned' entries that a delivered clip now covers are marked 'superseded' with
'supersededBy', so nothing is listed twice.
"""
import json, pathlib, glob

PACK = pathlib.Path(__file__).resolve().parents[1]
b2 = json.loads((PACK / 'manifest-batch2.json').read_text())
props_path = PACK.parent / 'ttw-props' / 'manifest.json'
props = json.loads(props_path.read_text()) if props_path.exists() else None

SUPERSEDE = {
    'ropes.enter-ring': 'ropes.enter-between-ropes',
    'ropes.exit-ring': 'ropes.exit-between-ropes',
    'ropes.slide-under': 'ropes.enter-slide-under',
    'ropes.climb-through': 'ropes.enter-duck-top',
    'ropes.jump-over-top': 'ropes.enter-jump-over-top',
    'ropes.run-into-ropes': 'ropes.run-into',
    'ropes.bounce-running': 'ropes.bounce-running',
    'ropes.rope-stretch': 'ropes.stretch',
    'ropes.spring-forward': 'ropes.rebound-sprint',
    'ropes.turn-from-ropes': 'ropes.turn-from-ropes',
    'ropes.tangled': 'ropes.get-tangled',
    'grappling.irish-whip': 'ropes.irish-whip',
    'grappling.throw-to-ropes': 'ropes.push-into-ropes',
    'aerial.top-rope-jump': 'turnbuckle.jump-forward',
    'aerial.missed-dive': 'turnbuckle.miss-aerial',
}

v3 = []
for f in sorted(glob.glob(str(PACK / 'tools' / 'phase*' / 'index.json'))):
    phase = int(pathlib.Path(f).parent.name.replace('phase', ''))
    for e in json.loads(pathlib.Path(f).read_text()):
        e = dict(e, status='ready', phase=phase)
        v3.append(e)
ids_v3 = {e['id'] for e in v3}

paired = []
for f in sorted(glob.glob(str(PACK / 'tools' / 'phase*' / 'paired-index.json'))):
    phase = int(pathlib.Path(f).parent.name.replace('phase', ''))
    paired += [dict(e, status='ready', phase=phase) for e in json.loads(pathlib.Path(f).read_text())]

animations, ready = [], set()
for a in b2['animations']:
    if a['status'] == 'ready':
        animations.append(dict(a, source='batch'))
        ready.add(a['id'])
prop_ids = set()
if props:
    for a in props['wrestlerAnimations']:
        animations.append(dict(a, file='../ttw-props/' + a['file'], status='ready', batch='props', source='ttw-props',
                               rootMotion=a.get('rootMotion', 'none')))
        ready.add(a['id']); prop_ids.add(a['id'])
for e in v3:
    if e['id'] in ready:
        raise SystemExit(f'duplicate id {e["id"]}')
    animations.append(dict(e, source='library-v3'))
    ready.add(e['id'])

planned_path = PACK / 'tools' / 'planned-library.json'
planned_new = json.loads(planned_path.read_text()) if planned_path.exists() else []
superseded = 0
superseded_list = []    # kept out of `animations`: loader.js fetches every entry that is not 'planned'
for a in b2['animations']:
    if a['status'] == 'ready':
        continue
    target = SUPERSEDE.get(a['id'])
    if a['id'] in prop_ids:
        continue  # delivered by the props pack under the same id
    if target and target in ready:
        superseded_list.append({'id': a['id'], 'name': a['name'], 'supersededBy': target}); superseded += 1
    else:
        animations.append(dict(a, status='planned'))
known = {a['id'] for a in animations}
for p in planned_new:
    if p['id'] not in known:
        animations.append(dict(p, status='planned')); known.add(p['id'])

events = dict(b2['events'])
events.update({
    'attack_start': 'An attack begins (its committed part). Fields: role.',
    'grip_locked': 'A hold is secure: from here the defender follows the attacker.',
    'lift_start': 'The defender leaves the ground.',
    'lift_complete': 'The lift reaches its top position.',
    'impact': 'A body lands hard on a surface (mat, apron, floor, turnbuckle). Fields: surface.',
    'rope_release': 'Hands or body leave the ropes.',
    'footstep': 'A foot plants. Fields: foot (left/right).',
    'jump': 'Feet leave the surface.',
    'apex': 'Top of a jump or flight.',
    'stun_start': 'A dazed state begins (stun loop can follow).',
    'animation_complete': 'Last frame of a one-shot clip (always present on library v3 clips).',
})

poses = dict(b2['poseStates'])
poses.update({
    'apron': 'standing on the apron outside the ropes, facing the ring',
    'apron-hanging': 'outside the ropes, holding the top rope, feet on the apron edge',
    'rope-lean': 'leaning back on the ropes (ropes behind, +Z)',
    'rope-draped': 'folded over the top rope',
    'rope-tangled': 'arms caught between the top and middle rope',
    'corner-perched': 'standing on the top turnbuckle, facing the ring',
    'corner-seated': 'sitting on the top turnbuckle, facing the ring',
    'corner-slumped': 'seated against the corner post on the mat',
    'floor': 'standing on the arena floor at ringside',
})

wrestlers = b2['wrestlers']
counts = {}
for a in animations:
    counts.setdefault(a['status'], 0); counts[a['status']] += 1
by_cat = {}
for a in animations:
    if a['status'] == 'ready':
        by_cat[a['category']] = by_cat.get(a['category'], 0) + 1

out = {
    'name': 'TTW Wrestling Animation Library',
    'version': '0.3.0',
    'libraryVersion': 3,
    'threeVersion': b2['threeVersion'],
    'skeleton': b2['skeleton'],
    'skeletonId': b2['skeletonId'],
    'loader': b2['loader'],
    'extensions': ['loader-ext.js', 'ttw-anim-runtime.js'],
    'compatibleWith': ['manifest.json', 'manifest-batch2.json'],
    'conventions': dict(b2['conventions'], **{
        'rootMotionCurve': 'library v3: rootMotion.mode "curve", keys [t, x, y, z, yawDeg] in the start frame (x right, y up, -z forward); policy "gameplay" keeps the root bone at the object, see README-library.md',
        'placement': 'library v3: placement.frame "rope" (rope line z=0, ring z>0, mat y=0) or "corner" (post at origin, ring x>0 z>0); placement.frameStart [x, y, z, yawDeg] in that frame',
        'ring': 'viewer/ring-reference.json',
    }),
    'rootMotionModes': dict(b2['rootMotionModes'], curve='Library v3. Declared travel curve in the start frame; ttw-anim-runtime.js samples it (RootMotion.targetAt) and never accumulates anything undeclared.'),
    'poseStates': poses,
    'locations': ['ring', 'apron', 'floor', 'corner', 'top-rope'],
    'events': events,
    'wrestlers': wrestlers,
    'animations': animations,
    'paired': paired,
    'superseded': superseded_list,
    'props': props['props'] if props else [],
    'propsManifest': '../ttw-props/manifest.json',
    'stats': {
        'wrestlersReady': sum(1 for w in wrestlers if w['status'] == 'ready'),
        'animationsReady': counts.get('ready', 0),
        'animationsPlanned': counts.get('planned', 0),
        'plannedIdsCoveredByNewClips': len(superseded_list),
        'pairedReady': len(paired),
        'readyByCategory': dict(sorted(by_cat.items())),
    },
}
(PACK / 'manifest-master.json').write_text(json.dumps(out, indent=1) + '\n')
print(json.dumps(out['stats'], indent=1))
