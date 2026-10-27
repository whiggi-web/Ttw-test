# TTW

Clean, standalone foundation for a player-controlled, livestream-friendly wrestling game.

## Start

```bash
python server.py
```

Visit http://localhost:8000. The level currently uses Three.js from a CDN, so internet access is needed.

## Level integration

`level.js` creates a scene, lighting, camera, temporary test floor, and `arenaMount` at world origin. When Claude supplies the arena model/loader, import it in `level.js` and call `attachArena(arenaObject)`. The test floor and grid are automatically hidden. Coordinate convention: Y up, ground at Y=0.

This is a scene test only. No wrestling gameplay, character controllers, or networking yet.

## Branch isolation

TTW uses `side-game`; Dark Arena remains on `development`. Reusable assets may be copied intentionally from the other branch without merging its game code.
