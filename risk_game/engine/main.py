"""
main.py

Entry point for launching a game of RISK.

- Loads map data from a JSON file (maploader.py)
- Initializes players and game state (game.py), bots included (bots.py)
- Starts the game and prints the game log.
- On game end, writes full log to text file.

Intended as a script for testing or demo purposes.
"""

from risk_game.engine.game import Game, GameState
from risk_game.engine.maploader import load_map_json, build_map_objects
from risk_game.engine.bots import *
from datetime import datetime
import random, os


"""
Initialization settings:

Right now we only have the Classic map and True Random settings.

Feel free to edit players[]. Our options for Player classes are as follows:
 - Player: YOU get to play, interacting with user terminal.
 - Neutral_Bot: Bot that never attacks
 - Aggro1_Bot: Bot that puts up a fight (see bots.py for algorithm)
"""
GAME_MAP_PATH = "maps/map_data.json"
players = [
    Aggro1_Bot(name="P1"),
    Aggro1_Bot(name="P2"),
    Aggro1_Bot(name="P3"),
    Aggro1_Bot(name="P4"),
    Aggro1_Bot(name='P5'),
    Aggro1_Bot(name="P6")
]

def create_game(map=GAME_MAP_PATH, players=players, start_army=0):
    """
    Sets up a Game object.

    - Shuffles player order.
    - Loads map data.
    - Creates GameState and Game instances.
    """
    random.shuffle(players)
    territories, continents = build_map_objects(load_map_json(map))
    game_state = GameState(territories, continents, players, start_army)
    return Game(game_state)

def play_game(game):
    """
    - Runs the game startup (and completion) logic.
    - Writes the game log to txt file after initialization.
    """

    game.start()

    # Ensure game_logs directory exists
    os.makedirs("game_logs", exist_ok=True)

    now = datetime.now()
    filename = "RISK Simulation Log " + now.strftime("%Y-%m-%d_%H-%M-%S") + ".txt"


    log_path = os.path.join("game_logs", f"{filename}.txt")
    with open(log_path, "w", encoding="utf-8") as log_file:
        for line in game.state.get_log(full=True):
            log_file.write(line + "\n")

if __name__ == '__main__':
    g = create_game()
    play_game(g)