"""Build Phase 4 (grappling): lock-ups and holds, throws and slams, submissions, ground work. Mostly paired moves.

Usage (from assets/ttw-wrestlers):  python tools/phase4/build-phase4.py [group ...]
Writes animations/<category>/*.json, paired/*.json, tools/phase4/index.json, paired-index.json, geometry-report.json
"""
import sys, json, pathlib
sys.dont_write_bytecode = True
P4 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P4)); sys.path.insert(0, str(P4.parent / 'phase2'))
from common import *
import pairs

PACK = P4.parents[1]
L = A.Library(PACK / 'animations', batch=3, index_path=P4 / 'index.json')
PR = pairs.PairBook(L, PACK / 'paired')
import importlib
groups = sys.argv[1:] or ['holds', 'throws', 'submissions', 'ground']
for g in groups:
    try:
        mod = importlib.import_module('group_' + g)
    except ModuleNotFoundError as e:
        if e.name == 'group_' + g: print('skip', g); continue
        raise
    mod.build(L, PR)
L.save_index()
PR.save(P4 / 'paired-index.json')
(P4 / 'geometry-report.json').write_text(json.dumps(L.reports, indent=2) + '\n')
for cid, rep in L.reports.items():
    flag = ' <<' if rep['floorPenetration'] > 0.06 else ''
    print(f"{cid:44} fix {rep['contactFixes']:2} floor {rep['floorPenetration']:.3f} @{rep['at']:<5} {rep['point']:12}{flag}")
print(len(L.index), 'animations,', len(PR.index), 'paired')
