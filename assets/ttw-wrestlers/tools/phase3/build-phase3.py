"""Build Phase 3 (combat): strikes and damage reactions.

Usage (from assets/ttw-wrestlers):  python tools/phase3/build-phase3.py
Writes animations/striking|reactions/*.json, tools/phase3/index.json and tools/phase3/geometry-report.json
"""
import sys, json, pathlib
sys.dont_write_bytecode = True
P3 = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(P3)); sys.path.insert(0, str(P3.parent / 'phase2'))
from common import *
import group_strikes, group_reactions

PACK = P3.parents[1]
L = A.Library(PACK / 'animations', batch=3, index_path=P3 / 'index.json')
group_strikes.build(L)
group_reactions.build(L)
L.save_index()
(P3 / 'geometry-report.json').write_text(json.dumps(L.reports, indent=2) + '\n')
for cid, rep in L.reports.items():
    flag = ' <<' if rep['floorPenetration'] > 0.06 or rep['ropePush'] > 0.3 else ''
    print(f"{cid:40} fix {rep['contactFixes']:2} floor {rep['floorPenetration']:.3f} @{rep['at']:<5} {rep['point']:12}{flag}")
print(len(L.index), 'animations')
