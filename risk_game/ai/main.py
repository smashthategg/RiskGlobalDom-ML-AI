from risk_game.engine.main import *
from risk_game.ai.encoder import *
from risk_game.ai.agent import *

players = [
    Aggro1_Bot(name="P1"),
    Aggro1_Bot(name="P2"),
    Aggro1_Bot(name="P3")
]
game_map_filepath = "maps/small.json"
start_army = 10




if __name__ == '__main__':
    map_data = load_map_json(game_map_filepath)
    g = create_game(game_map_filepath, players, 10)

    e = StateEncoder(GameSchema(map_data))
    agents = []
    for i, player in enumerate(g.state.players):
        if isinstance(player, (Aggro1_Bot, Neutral_Bot)):
            agents.append(Agent(player.name, i, e))
    for agent in agents:
        g.add_listener(agent)
    play_game(g)

    for s in agents[0].history:
        print(s)