# rpg-npc-dialogue-engine

> **Deterministic emotional state machine and template-based dialogue engine for RPG NPCs built from first principles. No AGPL code, no GPU/LLM dependencies.**

[![CI](https://github.com/Vecesta-co/rpg-npc-dialogue-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/Vecesta-co/rpg-npc-dialogue-engine/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)

```
$ python -m src.cli talk --npc npc_innkeeper --trigger greet --player Rowan
[Marta (innkeeper) - Mood: friendly]
"Ah, Rowan! Grand to see you again. Your usual? First round's on me!"

$ python -m src.cli talk --npc npc_guard --trigger threaten --player Rowan
[Ser Davan (guard) - Mood: hostile]
"Halt! You're wanted for questioning. Surrender your weapons!"
```

## Architecture

```
                  ┌──────────────────────┐
                  │      Player Input    │
                  └──────────┬───────────┘
                             │
                             ▼
┌──────────────────┐  Trigger Event   ┌──────────────────────┐
│   World State    ├─────────────────►│ Emotional State Mach │
│ (Reputation/Loc) │                  │  (Transitions Table) │
└────────┬─────────┘                  └──────────┬───────────┘
         │                                       │ Updated Emotion
         ▼                                       ▼
┌──────────────────┐                  ┌──────────────────────┐
│  Memory Stream   ├─────────────────►│  Dialogue Generator  │
│  (Recall Topics) │                  │ (Role/Mood Templates)│
└──────────────────┘                  └──────────┬───────────┘
                                                 │
                                                 ▼
                                      ┌──────────────────────┐
                                      │   Output Response    │
                                      └──────────────────────┘
```

## Comparison

| Feature | rpg-npc-dialogue-engine | LLM-based NPC systems |
|---|---|---|
| Latency | < 1 ms | 500 ms – 3 s |
| Offline / Air-gapped | 100% Offline | Requires GPU / API |
| Determinism | Provable state transitions | Non-deterministic |
| License | MIT (Permissive) | Often AGPL-3.0 or proprietary |
| Memory Footprint | < 15 MB RAM | 4 GB – 16 GB VRAM |

## Key Features

- **Emotional State Machine**: Explicit transitions between `neutral`, `friendly`, `hostile`, `fearful`, `curious`.
- **World & Reputation System**: Global reputation threshold overrides NPC sentiment.
- **Short-Term Memory Stream**: NPCs remember topics discussed and adjust future lines.
- **Ready-to-Play CLI & REST Server**: Complete interactive terminal RPG mode and HTTP API.

## Quick Start

```bash
git clone https://github.com/Vecesta-co/rpg-npc-dialogue-engine.git
cd rpg-npc-dialogue-engine
pip install pydantic pytest

# Interactive terminal RPG mode:
python -m src.cli play --player Rowan

# Or run REST server:
python -m src.server
```

## Difficulties & Solutions

- **First-Principles Design**: Many open-source RPG dialog frameworks rely on AGPL code (e.g. oobabooga). We designed the entire state transition matrix and dialogue templates from mathematical first principles under permissive MIT.
- **Dynamic Context Injection**: Implemented safe dictionary template interpolation with fallback to role-neutral lines without external templating engines.

---

**Built by Vecesta.co**
- Email: vecesta.co@gmail.com
- LinkedIn: https://www.linkedin.com/in/vansh-dhawan-2625v
- GitHub: https://github.com/Vecesta-co
- X: https://x.com/Vansh_Dhawann
- Hugging Face: https://huggingface.co/Vecesta
