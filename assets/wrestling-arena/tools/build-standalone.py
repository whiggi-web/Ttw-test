"""Bundle preview.html + arena-loader.js + all JSON into one self-contained page.

Usage: python tools/build-standalone.py  (run from the wrestling-arena folder)
Output: arena-standalone.html (opens straight from disk, no local server needed)
"""
import json, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
arena = json.loads((root / 'arena.json').read_text())
materials = json.loads((root / arena['materials']).read_text())
parts = {p['id']: json.loads((root / p['file']).read_text()) for p in arena['parts']}
bundle = json.dumps({'arena': arena, 'materials': materials, 'parts': parts}, separators=(',', ':'))

loader = (root / 'arena-loader.js').read_text()
loader = re.sub(r"^import \* as THREE from 'three';\s*$", '', loader, flags=re.M)
loader = re.sub(r'^export ', '', loader, flags=re.M)

page = (root / 'preview.html').read_text()
page = page.replace("import { loadArena, buildArena } from './arena-loader.js';", loader)
page = page.replace('<script type="importmap">', '<script>window.ARENA_BUNDLE = ' + bundle + ';</script>\n<script type="importmap">', 1)
(root / 'arena-standalone.html').write_text(page)
print('wrote', root / 'arena-standalone.html', len(page) // 1024, 'KB')
