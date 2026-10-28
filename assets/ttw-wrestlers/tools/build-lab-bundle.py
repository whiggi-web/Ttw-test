"""Bundle the Animation Lab into one self-contained HTML file (all clips, wrestlers and modules inlined; Three.js
from the CDN). Handy for sharing the lab without a web server.

Usage (from assets/ttw-wrestlers, with ../ttw-props installed):  python tools/build-lab-bundle.py [out.html]
"""
import json, pathlib, re, sys

PACK = pathlib.Path(__file__).resolve().parents[1]
out_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else PACK / 'viewer' / 'lab-bundled.html'

def module_body(path):
    """strip imports/exports from an ES module; returns (code, exported names)"""
    src = path.read_text()
    names = re.findall(r'^export\s+(?:async\s+)?(?:function|class|const|let)\s+([A-Za-z_$][\w$]*)', src, re.M)
    src = re.sub(r'^import[^\n]*\n', '', src, flags=re.M)
    src = re.sub(r'^export\s*\{[^}]*\};?\s*$', '', src, flags=re.M)
    src = re.sub(r'^export\s+', '', src, flags=re.M)
    return src, names

def iife(var, path, deps=''):
    code, names = module_body(path)
    return f"const {var} = (() => {{\n{deps}\n{code}\nreturn {{ {', '.join(names)} }};\n}})();\n"

loader, ext, rt, val = PACK / 'loader.js', PACK / 'loader-ext.js', PACK / 'ttw-anim-runtime.js', PACK / 'viewer' / 'validate.js'
lab_src = (PACK / 'viewer' / 'lab.js').read_text()
lab_src = re.sub(r'^import[^\n]*\n', '', lab_src, flags=re.M)

js = ["import * as THREE from 'three';", "import { OrbitControls } from 'three/addons/controls/OrbitControls.js';",
      iife('__WL', loader),
      iife('__EXT', ext, 'const { Wrestler, AnimationLibrary } = __WL;'),
      iife('__RT', rt, 'const { Wrestler } = __WL;'),
      iife('__V', val),
      'window.TTW_LAB_LIBS = { wrestler: __WL, runtime: __RT, validate: __V };',
      lab_src]

# data
m = json.loads((PACK / 'manifest-master.json').read_text())
m['__file'] = 'manifest-master.json (bundled)'
read = lambda f: json.loads((PACK / f).read_text())
data = {
    'manifest': m, 'skeleton': read(m['skeleton']), 'ring': read('viewer/ring-reference.json'),
    'wrestlers': {w['id']: read(w['file']) for w in m['wrestlers'] if w['status'] == 'ready'},
    'animations': {a['id']: read(a['file']) for a in m['animations'] if a['status'] == 'ready'},
    'paired': {p['id']: read(p['file']) for p in m.get('paired', []) if p.get('status', 'ready') == 'ready'},
}
html = (PACK / 'viewer' / 'index.html').read_text()
blob = json.dumps(data, separators=(',', ':')).replace('</', '<\\/')
bundle = f'<script>window.TTW_LAB_DATA = {blob};</script>\n<script type="module">\n' + '\n'.join(js).replace('</script', '<\\/script') + '\n</script>'
html = html.replace('<script type="module" src="./lab.js"></script>', bundle)
out_path.write_text(html)
print(out_path, round(out_path.stat().st_size / 1e6, 2), 'MB')
