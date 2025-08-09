"""
main.py

Entry point for launching a game of RISK.

- Loads map data from a JSON file (maploader.py)
- Initializes players and game state (game.py), bots included (bots.py)
- Starts the game and prints the game log.
- On game end, writes full log to text file.

Intended as a script for testing or demo purposes.
"""

from game import Game, GameState
from maploader import load_map
from combat import TrueRandom
from bots import *
import random, os


"""
Initialization settings:

Right now we only have the Classic map and True Random settings.

Feel free to edit players[]. Our options for Player classes are as follows:
 - Player: YOU get to play, interacting with user terminal.
 - Neutral_Bot: Bot that never attacks
 - Aggro1_Bot: Bot that puts up a fight (see bots.py for algorithm)
"""
GAME_MAP_PATH = "map_data/classic.json"
combat_rules = TrueRandom()
players = [
    Aggro1_Bot(name="P1"),
    Aggro1_Bot(name="P2"),
    Aggro1_Bot(name="P3"),
    Aggro1_Bot(name="P5"),
    Aggro1_Bot(name='P5'),
    Aggro1_Bot(name="P6")
]

def play_game():
    """
    Sets up and starts a game of RISK.

    - Shuffles player order.
    - Loads map data.
    - Creates GameState and Game instances.
    - Runs the game startup (and completion) logic.
    - Writes the game log to txt file after initialization.
    """
    random.shuffle(players)
    territories, continents = load_map(GAME_MAP_PATH)
    game_state = GameState(territories, continents, combat_rules, players)
    game = Game(game_state)
    game.start()

    # Ensure game_logs directory exists
    os.makedirs("game_logs", exist_ok=True)

    # Find next available log filename
    existing_files = [f for f in os.listdir("game_logs") if f.endswith(".txt")]
    existing_numbers = []
    for f in existing_files:
        try:
            existing_numbers.append(int(os.path.splitext(f)[0]))
        except ValueError:
            pass
    next_num = max(existing_numbers) + 1 if existing_numbers else 1

    log_path = os.path.join("game_logs", f"{next_num}.txt")
    with open(log_path, "w", encoding="utf-8") as log_file:
        for line in game_state.get_log(full=True):
            log_file.write(line + "\n")

if __name__ == '__main__':
    play_game()