# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python implementation of the Regicide card game - a cooperative deck-building game where players use a standard deck of cards to defeat 12 enemies (4 Jacks, 4 Queens, 4 Kings). The game features a GUI built with Pygame and implements the complete Regicide ruleset including suit abilities, combo mechanics, and the "animal companion" system.

## Running the Game

### Primary entry points:
```bash
python start.py          # Simple launcher with English interface
python main.py           # Full launcher (may have mixed language output)
python regicide_fixed.py # Direct launch of fixed version (recommended)
```

### Dependencies:
- Python 3.x
- Pygame (`pip install pygame`)

## Architecture Overview

### Core Components

- **regicide_fixed.py** - Main game implementation with fixed UI and English interface (recommended version)
- **game_engine.py** - Core game logic, battle system, and state management
- **card.py** - Card system with Suit/Rank enums and card mechanics
- **enemy.py** - Enemy system with health, attack, and special abilities
- **start.py/main.py** - Game launchers with dependency checking

### Key Classes

- `RegicideGame` (game_engine.py) - Main game state manager
- `Card` (card.py) - Individual card representation with suit abilities
- `Deck` (card.py) - Card deck management and shuffling
- `Enemy` (enemy.py) - Enemy entities with health/attack properties
- `EnemyQueue` (enemy.py) - Manages sequence of 12 enemies to defeat

### Game Architecture

The game follows an object-oriented design with clear separation of concerns:

1. **Game Engine** - Handles state transitions, turn management, battle calculations
2. **Card System** - Manages deck, hands, discard pile, and suit abilities
3. **Enemy System** - Controls enemy behavior, health, and attack patterns
4. **GUI Layer** - Pygame-based interface with card rendering and user input

## Game Mechanics Implementation

### Suit Abilities
- **Hearts (H)**: Healing - recover cards from discard pile to hand
- **Diamonds (D)**: Draw cards from deck
- **Spades (S)**: Weaken enemies (reduce attack permanently)
- **Clubs (C)**: Double damage dealt

### Combo System
- Players can play 1-4 cards of the same rank
- Combo bonus: `cards_played * (cards_played - 1)`
- Animal companions (Aces) can combine with any rank

### Battle System
- Player attacks deal damage based on card values + combo bonuses
- Enemies counter-attack, forcing discard equal to their attack value
- Game ends when all 12 enemies defeated or deck/hand exhausted

## Development Notes

- The codebase uses UTF-8 encoding with mixed English/Chinese comments
- **regicide_fixed.py** is the stable version with English UI and ASCII suit symbols
- Main game logic is centralized in `game_engine.py` with clear state management
- Pygame is used for rendering with custom card drawing and UI layout
- No formal testing framework - manual testing through game play

## File Structure Guidance

When modifying the game:
- Core logic changes go in `game_engine.py`
- Card-related mechanics belong in `card.py`
- Enemy behavior modifications go in `enemy.py`
- UI/rendering changes should be made in `regicide_fixed.py`
- Keep launchers (`start.py`, `main.py`) minimal and focused on startup