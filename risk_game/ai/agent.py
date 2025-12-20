from risk_game.ai.encoder import *

class Agent():
    def __init__(self, name, index, state_encoder):
        self.name = name
        self.index = index
        self.state_encoder = state_encoder
        self.history = []

    def __call__(self, state):
        state_encoded = self.state_encoder.encode(state)
        if state["current_player_index"] == self.index: # if it's agent's turn
            print(f"{self.name}'s turn")
            print(state_encoded)
        self.history.append(state_encoded)
        

