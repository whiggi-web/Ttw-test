"""TTW local two-player WebSocket relay. Install: pip install websockets
Run alongside the existing HTTP server: python multiplayer_server.py
For internet play, deploy behind HTTPS/WSS and configure ?server=wss://HOST.
"""
import asyncio
import json
import math
import time
from websockets.asyncio.server import serve

players = {}
last_hit = {}
last_position = {}
knockout_tasks = {}

async def recover_player(ws):
    try:
        await asyncio.sleep(10)
        if ws not in players or players[ws]['hp'] != 0:
            return
        players[ws]['hp'] = 100
        for client in list(players):
            other = next((p for w, p in players.items() if w != client), None)
            await send(client, {'type': 'health', 'self': players[client]['hp'], 'other': other['hp'] if other else 100, 'hit': None})
    except asyncio.CancelledError:
        pass
    finally:
        knockout_tasks.pop(ws, None)

async def send(ws, payload):
    await ws.send(json.dumps(payload))

async def broadcast(payload, exclude=None):
    for ws in list(players):
        if ws != exclude:
            try:
                await send(ws, payload)
            except Exception:
                pass

async def handler(ws):
    slot = None
    try:
        async for raw in ws:
            try:
                data = json.loads(raw)
            except (ValueError, TypeError):
                continue
            if not isinstance(data, dict):
                continue
            kind = data.get("type")
            if slot is None:
                if kind != "join":
                    continue
                if len(players) >= 2:
                    await send(ws, {"type": "full"})
                    await ws.close()
                    return
                slot = 1 if 1 not in [p["slot"] for p in players.values()] else 2
                players[ws] = {"slot": slot, "hp": 100, "name": str(data.get("name", "Wrestler"))[:20]}
                last_position[ws] = {"x": -1.4 if slot == 1 else 1.4, "y": 1.2, "z": 0}
                await send(ws, {"type": "welcome", "slot": slot, "hp": 100})
                if len(players) == 2:
                    for client in list(players):
                        other = next(p for w, p in players.items() if w != client)
                        await send(client, {"type": "joined", "hp": other["hp"], "name": other["name"]})
                else:
                    await send(ws, {"type": "waiting"})
                continue
            if kind == "state":
                p = data.get("position")
                rotation = data.get("rotation")
                if not isinstance(p, dict) or not isinstance(rotation, (float, int)):
                    continue
                try:
                    x, y, z = [float(p[k]) for k in ("x", "y", "z")]
                except (KeyError, ValueError, TypeError):
                    continue
                if not all(math.isfinite(v) for v in (x, y, z, rotation)):
                    continue
                if not (-4.1 <= x <= 4.1 and -4.1 <= z <= 4.1 and 0 <= y <= 3):
                    continue
                last_position[ws] = {"x": x, "y": y, "z": z}
                animation = data.get("animation")
                if animation not in ("idle", "run", "punch", "jab", "hook", "uppercut", "kick", "clothesline", "fall"):
                    animation = "idle"
                await broadcast({"type": "state", "slot": slot, "position": last_position[ws],
                                 "rotation": rotation, "animation": animation}, exclude=ws)
            elif kind == "punch" and len(players) == 2:
                now = time.monotonic()
                move = data.get("move", "punch")
                attacks = {"punch": (11, .7, "reactions.hit-front"), "jab": (7, .48, "reactions.hit-front"), "hook": (13, .8, "reactions.hit-left"), "uppercut": (16, .95, "reactions.knocked-back"), "kick": (15, 1.0, "reactions.hit-kick"), "clothesline": (18, 1.1, "reactions.hit-clothesline")}
                if move not in attacks:
                    continue
                base_damage, cooldown, reaction = attacks[move]
                if now - last_hit.get(ws, 0) < cooldown or players[ws]["hp"] <= 0:
                    continue
                last_hit[ws] = now
                other_ws = next(w for w in players if w != ws)
                other = players[other_ws]
                if other["hp"] <= 0:
                    continue
                a, b = last_position[ws], last_position[other_ws]
                if math.hypot(a["x"] - b["x"], a["z"] - b["z"]) > 2.2:
                    continue
                try:
                    momentum = float(data.get("momentum", 1))
                except (ValueError, TypeError):
                    momentum = 1
                if not math.isfinite(momentum):
                    momentum = 1
                damage = round(base_damage * max(1, min(1.3, momentum)))
                other["hp"] = max(0, other["hp"] - damage)
                if other["hp"] == 0 and other_ws not in knockout_tasks:
                    knockout_tasks[other_ws] = asyncio.create_task(recover_player(other_ws))
                await send(ws, {"type": "health", "self": players[ws]["hp"], "other": other["hp"], "hit": "other", "damage": damage, "reaction": reaction, "move": move})
                await send(other_ws, {"type": "health", "self": other["hp"], "other": players[ws]["hp"], "hit": "self", "damage": damage, "reaction": reaction, "move": move})
    finally:
        if ws in players:
            del players[ws]
            last_hit.pop(ws, None)
            last_position.pop(ws, None)
            task = knockout_tasks.pop(ws, None)
            if task:
                task.cancel()
            await broadcast({"type": "peer_left"})

async def main():
    async with serve(handler, "0.0.0.0", 8765):
        print("TTW multiplayer server listening on port 8765")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
