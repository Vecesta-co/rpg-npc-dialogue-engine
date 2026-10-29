"""HTTP REST server for RPG NPC dialogue engine."""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from .world import ALL_NPCS, DEFAULT_WORLD, ALL_QUESTS
from .emotion import apply_trigger
from .dialogue import generate_line
from .models import ConversationMemory

MEMORIES = {nid: ConversationMemory(npc_id=nid) for nid in ALL_NPCS}

class RPGServerHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _json(self, data, status=200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._json({"status": "ok", "npcs_count": len(ALL_NPCS)})
        elif parsed.path == "/npcs":
            self._json([npc.model_dump() for npc in ALL_NPCS.values()])
        elif parsed.path == "/quests":
            self._json([q.model_dump() for q in ALL_QUESTS.values()])
        elif parsed.path == "/world":
            self._json(DEFAULT_WORLD.model_dump())
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")

        if parsed.path == "/interact":
            npc_id = body.get("npc_id", "npc_innkeeper")
            npc = ALL_NPCS.get(npc_id)
            if not npc:
                self._json({"error": f"NPC {npc_id} not found"}, 404)
                return
            trigger = body.get("trigger")
            if trigger:
                apply_trigger(npc, trigger, DEFAULT_WORLD)
            player_name = body.get("player_name", "Traveller")
            topic = body.get("topic", "")
            mem = MEMORIES.get(npc_id)
            line = generate_line(npc, DEFAULT_WORLD, player_name=player_name, topic=topic, memory=mem)
            if mem:
                mem.add(topic or "greeting", line.text, "positive", len(mem.items) + 1)
            self._json({
                "npc": npc.name,
                "role": npc.role,
                "emotional_state": npc.emotional_state.value,
                "response": line.text,
                "tags": line.tags
            })
        else:
            self._json({"error": "not found"}, 404)

def run_server(host="0.0.0.0", port=8080):
    server = HTTPServer((host, port), RPGServerHandler)
    print(f"RPG dialogue server running on http://{host}:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
