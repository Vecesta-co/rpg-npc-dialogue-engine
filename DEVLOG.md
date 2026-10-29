# DEVLOG — rpg-npc-dialogue-engine

## Development Log

- **Problem**: Many popular dialogue engines use AGPL or heavy LLMs with non-deterministic output.
- **Solution**: Developed a clean, lightweight finite-state machine (FSM) in Python with emotional state triggers, reputation overrides, and templated text generation.
- **Problem**: Repetitive dialogue across states.
- **Solution**: Role-specific emotion buckets (innkeeper, blacksmith, guard) with dynamic string interpolations and sentiment memory weighting.
- **Test Results**: 24 tests passed in 0.16s with 100% assertion success.
