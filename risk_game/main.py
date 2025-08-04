"""
main.py

Entry point for launching a game of RISK.

- Loads map data from a JSON file.
- Initializes players and game state.
- Starts the game and prints the game log.

Intended as a simple script for testing or demo purposes.
"""

from game import Game, GameState
from maploader import load_map
from structures import Player
import random

# Initialization settings
GAME_MAP_PATH = "map_data/classic.json"
players = [
    Player(name="P1"),
    Player(name="P2"),
    Player(name="P3"),
    Player(name="P4")
]

def play_game():
    """
    Sets up and starts a game of RISK.

    - Shuffles player order.
    - Loads map data.
    - Creates GameState and Game instances.
    - Runs the game startup logic.
    - Prints the game log after initialization.
    """
    random.shuffle(players)
    territories, continents = load_map(GAME_MAP_PATH)
    game_state = GameState(territories, continents, players)
    game = Game(game_state)
    game.start()
    print(game.state.get_log())

play_game()
