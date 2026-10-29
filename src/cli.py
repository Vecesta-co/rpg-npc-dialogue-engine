"""CLI for rpg-npc-dialogue-engine."""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")

import argparse
import json
from .models import WorldState, EmotionalState, ConversationMemory
from .world import ALL_NPCS, DEFAULT_WORLD
from .emotion import apply_trigger, get_valid_triggers
from .dialogue import generate_line

def cmd_list(args):
    print("Available NPCs in Dawnhaven:")
    for npc_id, npc in ALL_NPCS.items():
        print(f"  • {npc.name} ({npc.role}) - Faction: {npc.faction.value} - State: {npc.emotional_state.value}")
        print(f"    Backstory: {npc.backstory}")
        print(f"    Knowledge: {', '.join(npc.knowledge_base)}")

def cmd_talk(args):
    npc = ALL_NPCS.get(args.npc)
    if not npc:
        print(f"NPC '{args.npc}' not found. Available: {list(ALL_NPCS.keys())}")
        return
    world = DEFAULT_WORLD
    if args.trigger:
        apply_trigger(npc, args.trigger, world)
    line = generate_line(npc, world, player_name=args.player, topic=args.topic or "")
    print(f"\n[{npc.name} ({npc.role}) - Mood: {npc.emotional_state.value}]")
    print(f"\"{line.text}\"")

def cmd_play(args):
    world = DEFAULT_WORLD
    player_name = args.player or "Adventurer"
    memories = {nid: ConversationMemory(npc_id=nid) for nid in ALL_NPCS}
    print("==================================================")
    print(" Welcome to Dawnhaven RPG Dialogue Engine")
    print(" Type 'help' for commands, 'exit' to quit.")
    print("==================================================")
    current_npc_id = "npc_innkeeper"
    turn = 0
    while True:
        try:
            cmd = input(f"[{world.location} | talking to: {ALL_NPCS[current_npc_id].name}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not cmd:
            continue
        if cmd.lower() in ("exit", "quit"):
            break
        elif cmd.lower() == "help":
            print("Commands:")
            print("  switch <npc_id>   - Switch target NPC (npc_innkeeper, npc_blacksmith, npc_guard)")
            print("  trigger <action>  - Trigger emotion (greet, threaten, question, apologize, etc.)")
            print("  say <text>        - Say something to current NPC")
            print("  status            - Show world and NPC status")
        elif cmd.lower().startswith("switch "):
            nid = cmd.split(maxsplit=1)[1].strip()
            if nid in ALL_NPCS:
                current_npc_id = nid
                print(f"Now talking to {ALL_NPCS[current_npc_id].name}.")
            else:
                print(f"Unknown NPC. Choose: {list(ALL_NPCS.keys())}")
        elif cmd.lower().startswith("trigger "):
            trig = cmd.split(maxsplit=1)[1].strip()
            apply_trigger(ALL_NPCS[current_npc_id], trig, world)
            print(f"{ALL_NPCS[current_npc_id].name}'s mood is now {ALL_NPCS[current_npc_id].emotional_state.value}.")
        elif cmd.lower().startswith("say ") or cmd:
            text = cmd[4:].strip() if cmd.lower().startswith("say ") else cmd
            turn += 1
            npc = ALL_NPCS[current_npc_id]
            line = generate_line(npc, world, player_name=player_name, topic=text, memory=memories[current_npc_id])
            print(f"[{npc.name}]: \"{line.text}\"")
            memories[current_npc_id].add(text, line.text, "positive", turn)

def main():
    parser = argparse.ArgumentParser(prog="rpg-npc", description="RPG NPC Dialogue Engine CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all NPCs")

    p_talk = sub.add_parser("talk", help="Talk to an NPC once")
    p_talk.add_argument("--npc", default="npc_innkeeper", help="NPC ID")
    p_talk.add_argument("--player", default="Traveller", help="Player name")
    p_talk.add_argument("--topic", default="", help="Conversation topic")
    p_talk.add_argument("--trigger", default="", help="Emotional trigger (greet, threaten, etc.)")

    p_play = sub.add_parser("play", help="Start interactive RPG session")
    p_play.add_argument("--player", default="Adventurer", help="Player name")

    args = parser.parse_args()
    if args.command == "list":
        cmd_list(args)
    elif args.command == "talk":
        cmd_talk(args)
    elif args.command == "play":
        cmd_play(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
