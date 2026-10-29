"""Template-based dialogue generator — no LLM dependency."""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding="utf-8")

import random
from typing import Dict, List
from .models import NPCPersona, WorldState, DialogueLine, EmotionalState, ConversationMemory

# ── Dialogue template bank (original, written for this project) ──────
TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    "innkeeper": {
        EmotionalState.NEUTRAL: [
            "Welcome to the {location}. What'll it be — ale, a room, or gossip?",
            "Aye, traveller. The fire's warm and the mead is cold. What do you need?",
            "Don't stand there gawkin'. Order something or move on.",
        ],
        EmotionalState.FRIENDLY: [
            "Ah, {player_name}! Grand to see you again. Your usual? First round's on me!",
            "Good to have a friend at the bar. The stew's fresh — best in {location}!",
            "You've got friends here, {player_name}. Anything you need, just say the word.",
        ],
        EmotionalState.HOSTILE: [
            "I've heard what you did. Take your coin elsewhere.",
            "Don't push your luck here, stranger. The door's behind you.",
            "My establishment doesn't serve troublemakers. Out!",
        ],
        EmotionalState.CURIOUS: [
            "You're not from around here, are you? What brings you to {location}?",
            "I've never seen your face before. Where do you hail from?",
            "Interesting… you carry yourself differently. Who trained you?",
        ],
        EmotionalState.FEARFUL: [
            "P-please, I want no trouble! I'll give you what I have!",
            "Just… just take what you want and leave us be…",
        ],
    },
    "blacksmith": {
        EmotionalState.NEUTRAL: [
            "Need a blade sharpened? My forge is the best in {location}.",
            "Steel doesn't lie. What can I make for you today?",
            "Don't touch the display pieces. They're not for handling.",
        ],
        EmotionalState.FRIENDLY: [
            "For you, {player_name}, I'll throw in a free sharpening. Good steel deserves care.",
            "Heard you've been helping folks around {location}. Take this — made it myself.",
            "You've proven yourself, {player_name}. I'll discount anything in the shop.",
        ],
        EmotionalState.HOSTILE: [
            "I don't deal with your kind. Get out of my forge.",
            "Every coin you spend here goes to trouble. I'll pass.",
            "Leave before I throw you out myself.",
        ],
        EmotionalState.CURIOUS: [
            "That weapon you carry — unusual craftsmanship. May I examine it?",
            "Where'd you find that armour? I've never seen that alloy before.",
            "You carry yourself like a fighter. What's your fighting style?",
        ],
        EmotionalState.FEARFUL: [
            "I — I'm just a blacksmith. I have nothing to do with the guild wars!",
            "Please don't burn the forge. I have a family to feed…",
        ],
    },
    "guard": {
        EmotionalState.NEUTRAL: [
            "Move along, citizen. Nothing to see here.",
            "Keep your weapons sheathed within town limits.",
            "The curfew starts at nightfall. Be inside by then.",
        ],
        EmotionalState.FRIENDLY: [
            "Ah, {player_name}. The captain speaks highly of you. Anything I can help with?",
            "Word travels fast — you did good out there. Safe travels.",
            "You've earned trust in {location}. I'll look the other way if you need to pass.",
        ],
        EmotionalState.HOSTILE: [
            "Halt! You're wanted for questioning. Surrender your weapons!",
            "I've got my eye on you, stranger. One wrong move…",
            "Criminals aren't welcome in {location}. I suggest you leave.",
        ],
        EmotionalState.CURIOUS: [
            "You seem capable. The captain is looking for recruits — interested?",
            "Strange times in {location}. Have you seen anything unusual on the road?",
            "That insignia on your cloak — which order do you represent?",
        ],
        EmotionalState.FEARFUL: [
            "The bandits are coming! Everyone get to the keep!",
            "Stay back — I'm warning you! I'll call the whole garrison!",
        ],
    },
}

DEFAULT_TEMPLATES = {
    EmotionalState.NEUTRAL: ["Hmm. What do you want?", "Speak your piece."],
    EmotionalState.FRIENDLY: ["Good to see you, {player_name}!", "Always a pleasure!"],
    EmotionalState.HOSTILE: ["Stay away from me!", "I have nothing to say to you."],
    EmotionalState.CURIOUS: ["Tell me more about yourself.", "That's… interesting."],
    EmotionalState.FEARFUL: ["Please, no trouble!", "I meant no harm!"],
}


def _fill_template(template: str, npc: NPCPersona, world: WorldState, player_name: str) -> str:
    return (template
            .replace("{location}", world.location.replace("_", " ").title())
            .replace("{player_name}", player_name)
            .replace("{npc_name}", npc.name)
            .replace("{faction}", npc.faction.value)
            .replace("{time}", world.time_of_day)
            )


def generate_line(
    npc: NPCPersona,
    world: WorldState,
    player_name: str = "Traveller",
    topic: str = "",
    memory: ConversationMemory = None,
) -> DialogueLine:
    role_templates = TEMPLATES.get(npc.role, DEFAULT_TEMPLATES)
    state_templates = role_templates.get(npc.emotional_state, DEFAULT_TEMPLATES.get(npc.emotional_state, ["..."]))

    # Memory influence: if we remember a positive interaction, prefer friendly lines
    if memory and npc.emotional_state == EmotionalState.NEUTRAL:
        recall = memory.recall(topic) if topic else None
        if recall and recall.sentiment == "positive" and EmotionalState.FRIENDLY in role_templates:
            state_templates = role_templates[EmotionalState.FRIENDLY]

    template = random.choice(state_templates)
    text = _fill_template(template, npc, world, player_name)
    return DialogueLine(
        npc_name=npc.name,
        text=text,
        emotional_state=npc.emotional_state,
        tags=[topic, npc.role] if topic else [npc.role]
    )

