"""Write CATALOGUE.md from manifest-master.json: every clip that exists (with its states, placement and travel)
and, separately, everything still planned.

Usage (from assets/ttw-wrestlers):  python tools/build-catalogue.py
"""
import json, pathlib

PACK = pathlib.Path(__file__).resolve().parents[1]
m = json.loads((PACK / 'manifest-master.json').read_text())
anims = m['animations']
ready = [a for a in anims if a['status'] == 'ready']
planned = [a for a in anims if a['status'] == 'planned']

def src(a):
    return {'batch': f"batch {a.get('batch')}", 'ttw-props': 'props pack', 'library-v3': f"library v3, phase {a.get('phase')}"}.get(a.get('source'), '')

out = ['# TTW animation catalogue', '',
       f"Generated from `manifest-master.json`. **{len(ready)} clips exist as JSON files**, {len(m['paired'])} paired moves, "
       f"{len(planned)} entries are planned only (no file yet).", '',
       'Columns: id, length in seconds (L = loop), pose state at start and end, where it starts and ends, root motion mode, origin.', '']
cats = sorted({a['category'] for a in ready})
for c in cats:
    rows = sorted([a for a in ready if a['category'] == c], key=lambda a: a['id'])
    out += [f'## {c} ({len(rows)})', '', '| id | name | s | states | location | root | from |', '|---|---|---|---|---|---|---|']
    for a in rows:
        st = f"{a.get('startState', 'standing')} → {a.get('endState', 'standing')}"
        loc = f"{a.get('startLocation', 'ring')} → {a.get('endLocation', 'ring')}"
        out.append(f"| `{a['id']}` | {a['name']} | {a['duration']}{' L' if a.get('loop') else ''} | {st} | {loc} | {a.get('rootMotion', 'none')} | {src(a)} |")
    out.append('')
out += [f"## Paired moves ({len(m['paired'])})", '', '| id | name | s | attacker | defender |', '|---|---|---|---|---|']
for p in m['paired']:
    out.append(f"| `{p['id']}` | {p['name']} | {p['duration']} | `{p['attacker']}` | `{p['defender']}` |")
out.append('')
if m.get('superseded'):
    out += ['## Old planned ids now covered by new clips', '', '| planned id | covered by |', '|---|---|']
    out += [f"| `{s['id']}` | `{s['supersededBy']}` |" for s in m['superseded']]
    out.append('')
out += [f'## Planned, not built yet ({len(planned)})', '', 'Listed in the manifest with `"status": "planned"`. No JSON file exists for these.', '']
for c in sorted({a['category'] for a in planned}):
    out.append(f"- **{c}**: " + ', '.join(f"`{a['id']}`" for a in sorted(planned, key=lambda a: a['id']) if a['category'] == c))
out.append('')
(PACK / 'CATALOGUE.md').write_text('\n'.join(out))
print(len(ready), 'ready,', len(planned), 'planned')
