"""Phase 2 paired moves: definitions that bind an attacker clip and a defender clip to one shared timeline.

The two clips were authored together in the same ring frame, so the defender's start offset and facing are computed
from their placements rather than typed in. Format: see README-library.md, "Paired moves".
"""
import json, math
from common import *

def _offset(att, dfn):
    """defender start relative to the attacker start (attacker frame: x right, y up, -z forward) and relative facing"""
    a = att['placement']['frameStart']; d = dfn['placement']['frameStart']
    rel_world = np.array(d[:3], float) - np.array(a[:3], float)
    local = A.Ry(-a[3]) @ rel_world
    facing = (d[3] - a[3] + 540) % 360 - 180
    return [round(float(v), 4) for v in local], round(facing, 2)

def pair(L, out_dir, pid, name, category, attacker, defender, events, desc, *, contacts=(), phases=(), interrupt=None, tags=(), end_note='', start=None):
    da, dd = L.defs[attacker], L.defs[defender]
    assert abs(da['duration'] - dd['duration']) < 1e-6, f'{pid}: durations differ'
    off, facing = start if start else _offset(da, dd)      # shared-role moves (both play one clip) pass the start explicitly
    ra = da['rootMotion']; rd = dd['rootMotion']
    def end_of(d):
        rm = d['rootMotion']
        return {'offset': rm.get('endOffset', [0, 0, 0]), 'yaw': rm.get('endYaw', 0)} if rm['mode'] == 'curve' else {'offset': [0, 0, 0], 'yaw': 0}
    p = {
        'id': pid, 'name': name, 'category': category, 'description': desc, 'libraryVersion': 3,
        'skeleton': 'ttw-humanoid', 'duration': da['duration'],
        'attacker': {'animation': attacker, 'startState': da['startState'], 'endState': da['endState'],
                     'startLocation': da['startLocation'], 'endLocation': da['endLocation']},
        'defender': {'animation': defender, 'startState': dd['startState'], 'endState': dd['endState'],
                     'startLocation': dd['startLocation'], 'endLocation': dd['endLocation']},
        'anchor': 'attacker',
        'start': {'attackerOffset': [0, 0, 0], 'attackerFacing': 0, 'defenderOffset': off, 'defenderFacing': facing,
                  'note': "Defender start in the attacker's start frame (x right, y up, -z forward); facing in degrees relative to the attacker."},
        'end': {'attacker': end_of(da), 'defender': end_of(dd),
                'note': 'Where each wrestler ends, in its own start frame (from the clips\' root-motion curves). ' + end_note},
        'placement': {'frame': da['placement']['frame'], 'frameStart': da['placement']['frameStart'],
                      'attacker': da['placement']['start'], 'defender': dd['placement']['start']},
        'contacts': list(contacts),
        'events': sorted(events, key=lambda e: e['time']),
        'phases': [{'name': n, 'start': a, 'end': b} for n, a, b in phases],
        'interruptible': interrupt or {'windows': [], 'note': 'committed once started'},
        'multiplayer': {
            'sync': 'shared-clock',
            'authority': 'server picks the pair, the anchor transform and the start time; clients seek both clips to the same time',
            'lateJoin': 'PairedPlayer.start(elapsed) or seekAnimation on both clips with the recorded start transforms',
            'deterministic': True,
        },
        'tags': list(tags),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{pid.split('.', 1)[1]}.json"
    path.write_text(json.dumps(p, indent=1) + '\n')
    return {'id': pid, 'name': name, 'category': category, 'file': f'paired/{path.name}', 'duration': p['duration'],
            'attacker': attacker, 'defender': defender, 'tags': list(tags)}

def ev2(t, name, role, **kw):
    e = {'time': round(t, 3), 'name': name, 'role': role}; e.update(kw); return e

def build(L, out_dir, index_path):
    idx = []
    idx.append(pair(L, out_dir, 'pair.irish-whip-ropes', 'Irish whip into the ropes', 'ropes', 'ropes.irish-whip', 'ropes.whipped-into',
        [ev2(0.1, 'grab', 'attacker', attachment='leftHandGrip'), ev2(0.1, 'grab', 'defender', attachment='rightHand'),
         ev2(0.2, 'grip_locked', 'both'), ev2(0.3, 'attack_start', 'attacker'), ev2(0.42, 'release', 'both'),
         ev2(0.62, 'footstep', 'defender'), ev2(0.78, 'footstep', 'defender'), ev2(0.92, 'footstep', 'defender'),
         ev2(1.06, 'rope_contact', 'defender', attachment='back'), ev2(1.14, 'impact', 'defender', surface='ropes'),
         ev2(1.3, 'recover', 'attacker'), ev2(1.4, 'animation_complete', 'both')],
        'The attacker takes the defender\'s right wrist, slings them 2.5 m into the ropes and waits in guard. The defender ends in rope-lean, '
        'so the game can chain any rebound (ropes.rebound-sprint, -clothesline, -crossbody) while the attacker readies a counter.',
        contacts=[{'from': 0.1, 'to': 0.42, 'attacker': 'leftHandGrip', 'defender': 'rightHand'}],
        phases=[('contact', 0, 0.22), ('launch', 0.22, 0.42), ('traversal', 0.42, 1.06), ('recovery', 1.06, 1.4)],
        interrupt={'windows': [[0.9, 1.4]], 'note': 'attacker only, once the defender is on the way'},
        tags=['ropes', 'whip', 'setup'], end_note='Defender ends 2.58 m further along its facing, back to the ropes.'))

    idx.append(pair(L, out_dir, 'pair.push-against-ropes', 'Shove into the ropes', 'ropes', 'ropes.push-into-ropes', 'ropes.pushed-against',
        [ev2(0.16, 'attack_start', 'attacker'), ev2(0.28, 'hit', 'attacker', attachment='propRightHand', zone='body', reach=0.5),
         ev2(0.28, 'hit_received', 'defender', zone='body'), ev2(0.46, 'footstep', 'defender'),
         ev2(0.6, 'rope_contact', 'defender', attachment='back'), ev2(0.62, 'impact', 'defender', surface='ropes'),
         ev2(0.95, 'recover', 'attacker'), ev2(1.0, 'animation_complete', 'both')],
        'Two-handed shove to the chest: the defender back-pedals into the ropes and ends in rope-lean, the attacker stands in guard 0.94 m away.',
        contacts=[{'from': 0.26, 'to': 0.34, 'attacker': 'propLeftHand+propRightHand', 'defender': 'chest'}],
        phases=[('approach', 0, 0.16), ('contact', 0.16, 0.34), ('traversal', 0.34, 0.6), ('recovery', 0.6, 1.0)],
        interrupt={'windows': [[0.6, 1.0]], 'note': 'attacker only'},
        tags=['ropes', 'shove', 'setup']))

    idx.append(pair(L, out_dir, 'pair.pull-over-top-rope', 'Pull over the top rope to the floor', 'eliminations', 'ropes.pull-over-top', 'ropes.pulled-over-top',
        [ev2(0.1, 'grab', 'attacker', attachment='rightHandGrip'), ev2(0.1, 'grab', 'defender', attachment='head'),
         ev2(0.3, 'grip_locked', 'both'), ev2(0.35, 'attack_start', 'attacker'), ev2(0.55, 'rope_release', 'defender'),
         ev2(0.6, 'release', 'attacker'), ev2(0.8, 'footstep', 'attacker'), ev2(1.02, 'land', 'defender', zone='back', height=1.16),
         ev2(1.02, 'impact', 'defender', surface='floor'), ev2(1.3, 'recover', 'attacker'), ev2(1.4, 'animation_complete', 'both')],
        'The attacker, on the arena floor, grabs an opponent draped over the top rope (ropes.drape-over-top / hang-over-top) and drags them '
        'over head first; the defender flips and lands on the back on the floor while the attacker steps aside.',
        contacts=[{'from': 0.1, 'to': 0.6, 'attacker': 'propLeftHand+propRightHand', 'defender': 'head'}],
        phases=[('contact', 0, 0.3), ('launch', 0.3, 0.6), ('traversal', 0.6, 1.02), ('recovery', 1.02, 1.4)],
        tags=['ropes', 'elimination', 'to-floor'], end_note='Both end on the floor; the attacker 0.85 m to the side.'))
    index_path.write_text(json.dumps(idx, indent=2) + '\n')
