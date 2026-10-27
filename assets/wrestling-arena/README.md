# Wrestling Arena (JSON scene)

Three.js r160. Ring centred on the origin, units in metres, Y up. Entrance runs down -Z: walkway, stage, screen, backstage.

## Files
- `arena.json` - manifest: parts, environment lighting, camera presets, entrance paths
- `materials.json` - named materials (colour, roughness, metalness, emissive)
- `parts/ring.json` - ring, ropes, turnbuckles, steps, barriers, announce table, lighting rig
- `parts/stadium.json` - floor seats, tiered stands with crowd, suites, outer walls, roof rig
- `parts/entrance.json` - walkway ramp, stage, main screen, side screens, curtain, truss
- `parts/backstage.json` - gorilla platform and ramp, two locker rooms, lounge, catering, road cases
- `arena-loader.js` - builds the scene from the JSON
- `preview.html` - viewer (needs a local server because it fetches the JSON)
- `arena-standalone.html` - same viewer with everything bundled, opens straight from disk
- `tools/build-standalone.py` - rebuilds the standalone file after editing JSON

## Use in game
```js
import { loadArena } from './assets/wrestling-arena/arena-loader.js';
const arena = await loadArena('./assets/wrestling-arena/arena.json');
scene.add(arena.group);
arena.applyEnvironment(scene);       // optional
arena.markers.ring_center;           // Vector3
arena.paths.entrance_red;            // Vector3[] locker room to ring centre
arena.colliders;                     // [{ id, tags, box: Box3 }]
arena.byTag('wall');                 // each wall is its own mesh with its own material (safe to fade)
arena.byId('stage_curtain');         // tagged "door"
arena.setScreen('screen_main', { text: 'NAME', sub: 'NOW ENTERING', colors: ['#3a0408', '#c4161c'] });
```

## Object schema
Common fields: `id`, `type`, `position`, `rotation` (degrees), `material`, `tags`, `collide`, `castShadow`.
- `mirror`: `"x"`, `"z"` or `"xz"` - adds mirrored copies with ids suffixed `_mx`, `_mz`, `_mxz`
- `array`: `{ count, step: [x,y,z] }` and `grid`: `{ counts: [nx,nz], step: [x,y,z] }` - become one InstancedMesh

Types: `box` (size), `cylinder` (radius, height), `rope` (from, to, radius), `ramp` (from, to, width, thickness, edgeMaterial, fill), `stairs` (width, steps, rise, run; climbs local +Z), `tiers` (length, rows, rise, depth, seatMaterial, seatSpacing, frontMaterial, crowd {density, seed, colors}; rises local +Z), `screen` (size [w,h], frameMaterial, content {text, sub, colors}), `light` (light: spot/point, color, intensity, distance, angle, penumbra, decay, target).

Markers live in each part's `markers` block and are referenced by name in `arena.json` paths.
