# ML/AI Project for RISK: Global Domination 

Trying to make a bot capable of playing the game of RISK: Global Domination at a satisfactory level. 

Currently building a simplified Python implementation of the game.

## Features

- Map loading from JSON (supports continents, territories, neighbor links)
- Player and territory modeling
- Randomized territory assignment
- Initial army distribution
- Full turn handling and draft/attack/fortify actions
- AFK bots to play with
- Event logging for game state transparency

> This project is a work-in-progress and currently does **not** include loser/winner checks, card trading, or user interface.

---

## Project Structure

```yaml
risk_game # Full python implementation of RISK
├── map_data/ # Map definitions (territories, continents, neighbors)
│ └── classic.json  # The classic RISK map, in JSON form.
├── bots.py # Bot classes that extend off of Player.
├── combat.py # Combat classes for battle mechanics/probability engine.
├── game.py # Game logic and game state definitions
├── main.py # Entry point for running the game
├── maploader.py # Loads map data from a JSON file
├── structures.py # Contains data classes: Player, Territory, Continent
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

✅ Player, Territory, and GameState structure

✅ Basic attack, draft, end turn logic

🔲 Full combat rules and Card system

🔲 AI bot(s) and training interface

🔲 GUI or CLI interface

## License

This project is open source and MIT-licensed. Feel free to fork, contribute, or build on top of it.

## Author

Johnny Lin (@smashthategg)