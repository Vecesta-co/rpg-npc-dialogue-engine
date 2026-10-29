"""Data models: NPC, WorldState, DialogueLine, Memory."""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import uuid
from enum import Enum


class EmotionalState(str, Enum):
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    HOSTILE = "hostile"
    FEARFUL = "fearful"
    CURIOUS = "curious"


class Faction(str, Enum):
    TOWN = "town"
    GUILD = "guild"
    BANDITS = "bandits"
    ROYALS = "royals"
    NONE = "none"


class NPCPersona(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    role: str                             # innkeeper, blacksmith, guard, etc.
    backstory: str
    faction: Faction = Faction.NONE
    traits: List[str] = Field(default_factory=list)  # friendly, cautious, gruff, etc.
    knowledge_base: List[str] = Field(default_factory=list)  # topics NPC knows about
    emotional_state: EmotionalState = EmotionalState.NEUTRAL
    reputation_threshold_hostile: int = -20  # player rep below this → NPC hostile
    reputation_threshold_friendly: int = 20   # player rep above this → NPC friendly


class MemoryItem(BaseModel):
    topic: str
    summary: str
    sentiment: str = "neutral"  # positive, negative, neutral
    turn_index: int = 0


class ConversationMemory(BaseModel):
    npc_id: str
    items: List[MemoryItem] = Field(default_factory=list)
    max_items: int = 10

    def add(self, topic: str, summary: str, sentiment: str, turn: int):
        self.items.append(MemoryItem(topic=topic, summary=summary, sentiment=sentiment, turn_index=turn))
        if len(self.items) > self.max_items:
            self.items.pop(0)

    def recall(self, topic: str) -> Optional[MemoryItem]:
        for item in reversed(self.items):
            if topic.lower() in item.topic.lower():
                return item
        return None


class WorldState(BaseModel):
    time_of_day: str = "day"           # morning, day, evening, night
    location: str = "town_square"
    player_reputation: int = 0         # -100 to 100
    quest_flags: Dict[str, bool] = Field(default_factory=dict)
    weather: str = "clear"


class DialogueLine(BaseModel):
    npc_name: str
    text: str
    emotional_state: EmotionalState
    tags: List[str] = Field(default_factory=list)


class QuestData(BaseModel):
    id: str
    title: str
    description: str
    giver_npc_id: str
    is_complete: bool = False
    steps: List[str] = Field(default_factory=list)

