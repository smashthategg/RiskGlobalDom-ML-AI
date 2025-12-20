# ML/AI Project for RISK: Global Domination 

Trying to make a bot capable of playing the game of RISK: Global Domination at a satisfactory level. 

More or less finished building a simplified Python implementation of the game.

To do:
- (structures.py) Integrate probability engines into attack prompts for users.
- Continue the reinforcement learning implementation (action encoder)
- 
## Features

- Map loading from JSON (supports continents, territories, neighbor links)
- Player and territory modeling
- Randomized territory assignment
- Initial army distribution
- Full turn handling and trade/draft/attack/fortify/end actions
- Card system with trading rules (highest-value set prioritization for bots)
- Continents recognition and ownership bonus tracking
- Combat system with true random dice rolls (Risk rules)
- Event logging for game state transparency
- Basic "Aggro" and "Neutral" bots to play with
- Modular design for adding new bot strategies

> This project is a work-in-progress and currently does **not** include user interface or ML/AI.

---

## How the Bots Work

The game supports automated players (“bots”) with different strategies.  
All bots inherit from the base `Player` class but override key decision-making functions.

### Core Bot Functions

A bot can override any of these methods to customize its playstyle:

| Method | Purpose |
|--------|---------|
| `trade_in_cards()` | Decide whether to trade cards. Bots can evaluate hand value and return the chosen set. |
| `draft_phase()` | Decide where and how to place available armies. |
| `attack_phase()` | Determine which territories to attack and with how many armies. |
| `fortify_phase()` | Decide troop movement between owned territories at the end of the turn. |

Bots receive full access to `self.territories (neighbors included)`, `self.cards`, `self.armies`, and `self.continents` to make decisions. In the future, I will add a **lot** of metrics for AI to learn off of.

---

### Example: Aggressive Bot (“Aggro1_Bot”)

The **Aggro1_Bot** class focuses on rapid expansion:  
- **Card Trading:** Always trades the **highest-value** set whenever possible.  
- **Draft:** Puts all available armies into the **strongest territory with at least one enemy neighbor**.  
- **Attack:** Attacks as long as a win is likely (e.g., attacker has ≥ 2 more armies than defender).  
- **Fortify:** Moves armies toward the front lines to prepare for more attacks next

## Project Structure

```yaml
game_logs # Directory for game logs
└──X.txt # Complete log of one game instance
risk_game # Full python implementation of RISK
├── map_data/ # Map definitions (territories, continents, neighbors)
│ └── classic.json  # The classic RISK map, in JSON form.
├── bots.py # Bot classes that extend off of Player.
├── combat.py # Combat classes for battle mechanics/probability engine.
├── game.py # Game logic and game state definitions
├── main.py # Entry point for running the game
├── maploader.py # Loads map data from a JSON file
└── structures.py # Contains data classes: Player, Territory, Continent
.gitignore # unshared files (mostly cache)
README.md # You are here
```

---

## Quick Start

Make sure you have Python 3.7+ installed.

1. Clone the repository:
   ```bash
   git clone https://github.com/smashthategg/RiskGlobalDom-ML-AI.git
   cd RiskGlobalDom-ML-AI
   ```

Run risk_game/main.py, and you should see a log of turns printed out.

## Map Format

Maps are defined in JSON and must include:

"territories": each with continent, neighbors (by name)

"continents": each with a bonus and list of territory names

Example snippet:

```json
{
    "territories": {
        "Alaska": {
            "continent": "North America",
            "neighbors": ["Northwest Territory", "Alberta"]
        }
    },
    "continents": {
        "North America": {
            "bonus": 5,
            "territories": ["Alaska", "Northwest Territory", "Alberta"]
        },
    }
}
```

## Future Plans

✅ Card, Player, Territory, Continent, GameState, Game structures

✅ Full draft, attack, fortify, end turn, and card logic

✅ Complete detailed logging of full games

✅ True Random combat on Classic map + Map loader

✅ Basic bots.

🔲 More modes and maps!

🔲 Advanced ML/RL bot(s) and training interface

🔲 GUI or CLI interface (help appreciated!!)

## License

This project is open source and MIT-licensed. Feel free to fork, contribute, or build on top of it.

## Author

Johnny (@smashthategg)