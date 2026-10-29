"""Emotional state machine for NPCs."""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")

from .models import EmotionalState, NPCPersona, WorldState

# Transition rules: (current_state, trigger) -> new_state
TRANSITIONS = {
    (EmotionalState.NEUTRAL,  "greet"):    EmotionalState.FRIENDLY,
    (EmotionalState.NEUTRAL,  "threaten"): EmotionalState.HOSTILE,
    (EmotionalState.NEUTRAL,  "question"): EmotionalState.CURIOUS,
    (EmotionalState.FRIENDLY, "threaten"): EmotionalState.HOSTILE,
    (EmotionalState.FRIENDLY, "leave"):    EmotionalState.NEUTRAL,
    (EmotionalState.HOSTILE,  "apologize"):EmotionalState.NEUTRAL,
    (EmotionalState.HOSTILE,  "greet"):    EmotionalState.HOSTILE,  # stays hostile
    (EmotionalState.CURIOUS,  "answer"):   EmotionalState.FRIENDLY,
    (EmotionalState.CURIOUS,  "ignore"):   EmotionalState.NEUTRAL,
    (EmotionalState.FEARFUL,  "reassure"): EmotionalState.NEUTRAL,
    (EmotionalState.FEARFUL,  "threaten"): EmotionalState.HOSTILE,
}


def apply_trigger(npc: NPCPersona, trigger: str, world: WorldState) -> EmotionalState:
    """Apply a player trigger and return the new emotional state."""
    key = (npc.emotional_state, trigger)
    new_state = TRANSITIONS.get(key, npc.emotional_state)

    # Reputation override
    if world.player_reputation <= npc.reputation_threshold_hostile:
        new_state = EmotionalState.HOSTILE
    elif world.player_reputation >= npc.reputation_threshold_friendly:
        if new_state not in (EmotionalState.HOSTILE,):
            new_state = EmotionalState.FRIENDLY

    npc.emotional_state = new_state
    return new_state


def get_valid_triggers(state: EmotionalState) -> list:
    return list({t for (s, t) in TRANSITIONS if s == state})

