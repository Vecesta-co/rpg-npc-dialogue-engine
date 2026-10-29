"""Pre-built NPC roster and quest data for the demo game."""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")

from .models import NPCPersona, Faction, EmotionalState, QuestData, WorldState

INNKEEPER = NPCPersona(
    id="npc_innkeeper",
    name="Marta",
    role="innkeeper",
    backstory="Marta has run The Rusty Flagon for 20 years. She knows every secret in Dawnhaven.",
    faction=Faction.TOWN,
    traits=["warm", "gossipy", "shrewd"],
    knowledge_base=["local rumors", "quest_lost_shipment", "bandit_camp_location"],
    reputation_threshold_hostile=-30,
    reputation_threshold_friendly=15,
)

BLACKSMITH = NPCPersona(
    id="npc_blacksmith",
    name="Aldric",
    role="blacksmith",
    backstory="Aldric forged blades for the King's Guard before retiring to Dawnhaven. He is the best smith in three counties.",
    faction=Faction.GUILD,
    traits=["proud", "professional", "taciturn"],
    knowledge_base=["weapons", "armour", "quest_forge_key"],
    reputation_threshold_hostile=-20,
    reputation_threshold_friendly=25,
)

GUARD = NPCPersona(
    id="npc_guard",
    name="Ser Davan",
    role="guard",
    backstory="A decorated soldier who survived the War of Ashes. He keeps the peace in Dawnhaven with an iron hand.",
    faction=Faction.ROYALS,
    traits=["stern", "dutiful", "honourable"],
    knowledge_base=["town_law", "bandit_threat", "quest_missing_merchant"],
    reputation_threshold_hostile=-10,
    reputation_threshold_friendly=20,
)

ALL_NPCS = {npc.id: npc for npc in [INNKEEPER, BLACKSMITH, GUARD]}

QUEST_MISSING_MERCHANT = QuestData(
    id="quest_missing_merchant",
    title="The Missing Merchant",
    description="Ser Davan asks you to find merchant Torben who vanished on the south road.",
    giver_npc_id="npc_guard",
    steps=["Talk to Marta about Torben", "Search the south road", "Find the abandoned cart", "Return to Ser Davan"],
)

ALL_QUESTS = {q.id: q for q in [QUEST_MISSING_MERCHANT]}

DEFAULT_WORLD = WorldState(
    time_of_day="day",
    location="dawnhaven",
    player_reputation=0,
    quest_flags={},
    weather="clear",
)

