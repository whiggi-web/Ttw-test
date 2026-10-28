"""Build all Phase 2 animations (ring, ropes, apron, turnbuckle, ring-to-floor) and the Phase 2 paired moves.

Usage (from assets/ttw-wrestlers):  python tools/phase2/build-phase2.py [group ...]
Writes animations/<category>/*.json, paired/*.json, tools/phase2/index.json and tools/phase2/geometry-report.json
"""
import sys, json, pathlib
sys.dont_write_bytecode = True
P2 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P2))
from common import *
import group_ring

PACK = P2.parents[1]
L = A.Library(PACK / 'animations', batch=3, index_path=P2 / 'index.json')
groups = sys.argv[1:] or ['ring', 'ropes', 'turnbuckle', 'paired']
mods = {'ring': group_ring}
try:
    import group_ropes; mods['ropes'] = group_ropes
except ImportError: pass
try:
    import group_turnbuckle; mods['turnbuckle'] = group_turnbuckle
except ImportError: pass
for g in groups:
    if g in mods: mods[g].build(L)
if 'paired' in groups:
    try:
        import group_paired; group_paired.build(L, PACK / 'paired', P2 / 'paired-index.json')
    except ImportError: pass
L.save_index()
(P2 / 'geometry-report.json').write_text(json.dumps(L.reports, indent=2) + '\n')
for cid, rep in L.reports.items():
    flag = ' <<' if rep['floorPenetration'] > 0.06 or rep['ropePush'] > 0.3 else ''
    print(f"{cid:40} fix {rep['contactFixes']:2} floor {rep['floorPenetration']:.3f} @{rep['at']:<5} {rep['point']:12} ropePush {rep['ropePush']:.3f}{flag}")
print(len(L.index), 'animations')
