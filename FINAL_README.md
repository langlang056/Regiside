# Regicide Card Game - Final Version

A cooperative deck-building card game implementation using Python and Pygame, featuring high-quality poker card images with authentic graphically-drawn suit symbols (♠♥♦♣).

## How to Play

```bash
python regicide_fixed.py    # Start the main game
python start.py            # Alternative launcher
```

## Game Features

- **Complete Regicide Rules**: Battle through 12 enemies (4 Jacks, 4 Queens, 4 Kings)
- **Image-Based Cards**: Professional poker card graphics with proper suit symbols
- **Suit Abilities**:
  - ♥ Hearts: Healing (recover cards from discard)
  - ♦ Diamonds: Draw additional cards
  - ♠ Spades: Weaken enemies (reduce attack)
  - ♣ Clubs: Double damage
- **Combo System**: Play multiple cards of same rank for bonus damage
- **Animal Companions**: Aces can combine with any rank

## Project Structure

### Core Game Files
- `regicide_fixed.py` - Main game with image-based card rendering
- `game_engine.py` - Core game logic and battle system
- `card.py` - Card system with suits, ranks, and abilities
- `enemy.py` - Enemy system with health and attack mechanics
- `image_card_renderer.py` - Image-based card rendering system

### Launchers
- `start.py` - Simple game launcher
- `main.py` - Alternative launcher

### Assets
- `assets/images/cards/` - 40 poker card images (A-10 all suits)
- `assets/images/enemies/` - 12 enemy cards (J,Q,K all suits)
- `assets/images/backs/` - Card back image

## Requirements

- Python 3.x
- Pygame (`pip install pygame`)

## Controls

- **Mouse**: Click cards to select/deselect
- **Attack Button**: Play selected cards to attack enemy
- **Space**: Quick play single card
- **ESC**: Exit game

The game features professional poker card graphics with authentic graphically-drawn suit symbols, providing an immersive and visually appealing card game experience. All suit symbols are drawn using vector graphics to ensure perfect display regardless of font support.