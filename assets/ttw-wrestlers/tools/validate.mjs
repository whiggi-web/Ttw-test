// Validate the TTW animation library from the command line.
//
//   node tools/validate.mjs                      (run from assets/ttw-wrestlers)
//   node tools/validate.mjs path/to/manifest.json
//
// Uses manifest-master.json by default (falls back to manifest-batch2.json, then manifest.json).
// Writes tools/validation-report.json and exits with code 1 if there are errors.

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { validateLibrary } from '../viewer/validate.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const base = path.resolve(here, '..');
const pick = process.argv[2] || ['manifest-master.json', 'manifest-batch2.json', 'manifest.json'].find((f) => fs.existsSync(path.join(base, f)));
const manifestPath = path.resolve(base, pick);
const mbase = path.dirname(manifestPath);
const read = (f) => JSON.parse(fs.readFileSync(path.resolve(mbase, f), 'utf8'));

const manifest = read(path.basename(manifestPath));
const skeleton = read(manifest.skeleton);
const animations = {};
for (const e of manifest.animations) {
  if (e.status && e.status !== 'ready') continue;
  try { animations[e.id] = read(e.file); } catch (err) { /* reported as missing */ }
}
const paired = {};
for (const p of manifest.paired || []) {
  if (p.status && p.status !== 'ready') continue;
  try { paired[p.id] = read(p.file); } catch (err) { console.error('missing paired file', p.file); }
}

const report = validateLibrary({ skeleton, entries: manifest.animations, animations, paired });
fs.writeFileSync(path.join(here, 'validation-report.json'), JSON.stringify({ manifest: pick, ...report }, null, 2));

console.log(`TTW validation: ${pick}`);
console.log(`  animations ${report.stats.animations} ready, ${report.stats.planned} planned, ${report.stats.missing} missing; paired ${report.stats.paired}`);
console.log(`  by category ${JSON.stringify(report.stats.byCategory)}`);
console.log(`  errors ${report.errors.length}, warnings ${report.warnings.length}`);
for (const e of report.errors.slice(0, 40)) console.log(`  ERROR   ${e.id}: ${e.msg}`);
for (const w of report.warnings.slice(0, 60)) console.log(`  warning ${w.id}: ${w.msg}`);
process.exit(report.ok ? 0 : 1);
