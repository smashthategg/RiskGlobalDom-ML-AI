from game import Game, GameState
from maploader import load_map
from structures import Player
import random

# Initialization settings, kinda
GAME_MAP_PATH = "map_data/classic.json"
players = [
    Player(name="P1"),
    Player(name="P2"),
    Player(name="P3"),
    Player(name="P4")
]


def play_game():
    random.shuffle(players)
    territories, continents = load_map(GAME_MAP_PATH)
    game_state = GameState(territories, continents, players)
    game = Game(game_state)
    game.start()
    print(game.state.get_log())
    

play_game()


