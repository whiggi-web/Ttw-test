"""python tools/lib/diag.py <clip.json> [t0 t1]: per-frame worst probe vs surface, in frame coords"""
import sys, json, pathlib
sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import ttwanim as A
d = json.loads(pathlib.Path(sys.argv[1]).read_text())
pl = d['placement']; fs = pl['frameStart']
frame = A.Frame(pl['frame'], fs)
t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0; t1 = float(sys.argv[3]) if len(sys.argv) > 3 else d['duration']
i = 0
while i / 30 <= d['duration'] + 1e-6:
    t = i / 30; i += 1
    if t < t0 or t > t1: continue
    W = A.fk(A.sample_pose(d, t)); P = A.probe_points(W)
    worst = max(((frame.surface(*(lambda q: (q[0], q[2]))(frame.to_frame(p))) - frame.to_frame(p)[1], n, frame.to_frame(p)) for n, p in P.items()), key=lambda x: x[0])
    print(f'{t:.2f} {worst[1]:12} pen {worst[0]:+.3f} at {[round(v, 2) for v in worst[2]]}')
