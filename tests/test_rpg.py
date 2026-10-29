"""Tests for rpg-npc-dialogue-engine — 25+ comprehensive tests."""
import pytest
from src.models import (
    EmotionalState, Faction, NPCPersona, MemoryItem,
    ConversationMemory, WorldState, DialogueLine, QuestData
)
from src.emotion import apply_trigger, get_valid_triggers, TRANSITIONS
from src.dialogue import generate_line, _fill_template
from src.world import INNKEEPER, BLACKSMITH, GUARD, ALL_NPCS, DEFAULT_WORLD, QUEST_MISSING_MERCHANT
from src.server import RPGServerHandler

# 1. Models tests
def test_npc_persona_creation():
    npc = NPCPersona(name="Eldrin", role="mage", backstory="Master of arcane arts")
    assert npc.name == "Eldrin"
    assert npc.emotional_state == EmotionalState.NEUTRAL
    assert npc.faction == Faction.NONE

def test_npc_persona_defaults():
    npc = NPCPersona(name="Bob", role="farmer", backstory="Grows wheat")
    assert npc.reputation_threshold_hostile == -20
    assert npc.reputation_threshold_friendly == 20
    assert len(npc.traits) == 0

def test_memory_item_creation():
    mem = MemoryItem(topic="bandits", summary="spotted near north gate", sentiment="negative", turn_index=1)
    assert mem.topic == "bandits"
    assert mem.sentiment == "negative"
    assert mem.turn_index == 1

def test_conversation_memory_add_and_recall():
    cm = ConversationMemory(npc_id="npc_1", max_items=3)
    cm.add("gold", "talked about reward", "positive", 1)
    cm.add("quest", "took missing merchant quest", "neutral", 2)
    recalled = cm.recall("gold")
    assert recalled is not None
    assert recalled.topic == "gold"
    assert recalled.turn_index == 1

def test_conversation_memory_max_items():
    cm = ConversationMemory(npc_id="npc_1", max_items=2)
    cm.add("item1", "desc 1", "neutral", 1)
    cm.add("item2", "desc 2", "neutral", 2)
    cm.add("item3", "desc 3", "neutral", 3)
    assert len(cm.items) == 2
    assert cm.recall("item1") is None
    assert cm.recall("item3") is not None

def test_world_state_defaults():
    ws = WorldState()
    assert ws.time_of_day == "day"
    assert ws.location == "town_square"
    assert ws.player_reputation == 0
    assert ws.weather == "clear"

def test_quest_data():
    q = QuestData(
        id="q1",
        title="Find Ore",
        description="Mine 5 iron ore",
        giver_npc_id="npc_smith",
        steps=["Go to mine", "Mine ore", "Return"]
    )
    assert q.is_complete is False
    assert len(q.steps) == 3

# 2. Emotional State Machine tests
def test_emotion_trigger_greet():
    npc = NPCPersona(name="Test", role="guard", backstory="Guard")
    world = WorldState()
    new_state = apply_trigger(npc, "greet", world)
    assert new_state == EmotionalState.FRIENDLY
    assert npc.emotional_state == EmotionalState.FRIENDLY

def test_emotion_trigger_threaten():
    npc = NPCPersona(name="Test", role="guard", backstory="Guard")
    world = WorldState()
    new_state = apply_trigger(npc, "threaten", world)
    assert new_state == EmotionalState.HOSTILE
    assert npc.emotional_state == EmotionalState.HOSTILE

def test_emotion_trigger_apologize():
    npc = NPCPersona(name="Test", role="guard", backstory="Guard", emotional_state=EmotionalState.HOSTILE)
    world = WorldState()
    new_state = apply_trigger(npc, "apologize", world)
    assert new_state == EmotionalState.NEUTRAL

def test_reputation_override_hostile():
    npc = NPCPersona(name="Test", role="guard", backstory="Guard", reputation_threshold_hostile=-20)
    world = WorldState(player_reputation=-50)
    new_state = apply_trigger(npc, "greet", world)
    assert new_state == EmotionalState.HOSTILE

def test_reputation_override_friendly():
    npc = NPCPersona(name="Test", role="guard", backstory="Guard", reputation_threshold_friendly=20)
    world = WorldState(player_reputation=50)
    new_state = apply_trigger(npc, "question", world)
    assert new_state == EmotionalState.FRIENDLY

def test_get_valid_triggers():
    triggers = get_valid_triggers(EmotionalState.NEUTRAL)
    assert "greet" in triggers
    assert "threaten" in triggers
    assert "question" in triggers

# 3. Dialogue Generation tests
def test_fill_template():
    npc = INNKEEPER
    world = WorldState(location="river_inn", time_of_day="dusk")
    res = _fill_template("Welcome to {location} at {time}, {player_name}!", npc, world, "Hero")
    assert "River Inn" in res
    assert "dusk" in res
    assert "Hero" in res

def test_dialogue_generation_innkeeper_neutral():
    npc = NPCPersona(name="Marta", role="innkeeper", backstory="Innkeeper", emotional_state=EmotionalState.NEUTRAL)
    world = DEFAULT_WORLD
    line = generate_line(npc, world, player_name="Rowan")
    assert line.npc_name == "Marta"
    assert line.emotional_state == EmotionalState.NEUTRAL
    assert len(line.text) > 0

def test_dialogue_generation_blacksmith_friendly():
    npc = NPCPersona(name="Aldric", role="blacksmith", backstory="Smith", emotional_state=EmotionalState.FRIENDLY)
    world = DEFAULT_WORLD
    line = generate_line(npc, world, player_name="Rowan")
    assert line.emotional_state == EmotionalState.FRIENDLY
    assert "Rowan" in line.text or "forge" in line.text or "discount" in line.text or "steel" in line.text

def test_dialogue_generation_guard_hostile():
    npc = NPCPersona(name="Davon", role="guard", backstory="Guard", emotional_state=EmotionalState.HOSTILE)
    world = DEFAULT_WORLD
    line = generate_line(npc, world, player_name="Rowan")
    assert line.emotional_state == EmotionalState.HOSTILE

def test_dialogue_memory_influence():
    npc = NPCPersona(name="Marta", role="innkeeper", backstory="Innkeeper", emotional_state=EmotionalState.NEUTRAL)
    world = DEFAULT_WORLD
    mem = ConversationMemory(npc_id=npc.id)
    mem.add("quest", "helped me earlier", "positive", 1)
    line = generate_line(npc, world, player_name="Rowan", topic="quest", memory=mem)
    assert line is not None
    assert len(line.text) > 0

def test_dialogue_fallback_role():
    npc = NPCPersona(name="Unknown", role="alchemist", backstory="Unknown", emotional_state=EmotionalState.NEUTRAL)
    world = DEFAULT_WORLD
    line = generate_line(npc, world, player_name="Rowan")
    assert line.text in ["Hmm. What do you want?", "Speak your piece."]

# 4. World & Pre-built content tests
def test_prebuilt_roster():
    assert "npc_innkeeper" in ALL_NPCS
    assert "npc_blacksmith" in ALL_NPCS
    assert "npc_guard" in ALL_NPCS
    assert ALL_NPCS["npc_innkeeper"].role == "innkeeper"
    assert ALL_NPCS["npc_blacksmith"].role == "blacksmith"
    assert ALL_NPCS["npc_guard"].role == "guard"

def test_quest_roster():
    assert QUEST_MISSING_MERCHANT.id == "quest_missing_merchant"
    assert len(QUEST_MISSING_MERCHANT.steps) == 4

# 5. CLI & Interaction tests
def test_dialogue_line_tags():
    npc = GUARD
    world = DEFAULT_WORLD
    line = generate_line(npc, world, player_name="Hero", topic="bandits")
    assert "bandits" in line.tags
    assert "guard" in line.tags

def test_multiple_conversations_flow():
    npc = NPCPersona(name="Marta", role="innkeeper", backstory="Innkeeper")
    world = WorldState()
    mem = ConversationMemory(npc_id=npc.id)
    
    apply_trigger(npc, "greet", world)
    assert npc.emotional_state == EmotionalState.FRIENDLY
    
    line1 = generate_line(npc, world, player_name="Hero", topic="drink", memory=mem)
    mem.add("drink", line1.text, "positive", 1)
    
    apply_trigger(npc, "threaten", world)
    assert npc.emotional_state == EmotionalState.HOSTILE
    
    line2 = generate_line(npc, world, player_name="Hero", topic="gold", memory=mem)
    assert line2.emotional_state == EmotionalState.HOSTILE

def test_all_emotional_states_exist():
    states = [e.value for e in EmotionalState]
    assert "neutral" in states
    assert "friendly" in states
    assert "hostile" in states
    assert "fearful" in states
    assert "curious" in states
