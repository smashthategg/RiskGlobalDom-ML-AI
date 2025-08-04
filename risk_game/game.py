from maploader import load_map
from structures import Territory, Continent
import random

'''
class GameState: Passive container that holds all the current data (players, map, turn info, game log).
class Game: Active logic engine that enforces rules, handles turn progression, attacks, reinforcements, etc.

Game owns a GameState instance.
GameState doesn't know about Game. It's just a structured data snapshot.
'''

class GameState:
    def __init__(self, territories, continents, players=None):
        self.territories = territories  # list of Territory objects
        self.continents = continents    # list of Continent objects 
        self.players = players if players else []  # list of Player objects
        self.turn = 0
        self.current_player_index = 0
        self.game_log = []  # List of strings describing game events

    def log_event(self, event_str):
        """Add a new event to the game log."""
        self.game_log.append(event_str)

    def get_log(self, last_n=None):
        """Get the full log or last n entries."""
        if last_n is None:
            return self.game_log
        return self.game_log[-last_n:]

    def current_player(self):
        """Return the Player whose turn it is."""
        return self.players[self.current_player_index]
    
class Game:
    def __init__(self, game_state):
        self.state = game_state

    def assign_starting_armies(self):
        num_players = len(self.state.players)
        counts = [0,0,40,35,30,25,20] # 2 player game -> each player starts with 40 troops. 6 player game -> 20 troops each.
        start_army_count = counts[num_players]
        for player in self.state.players:
            player.update_army_count()
            for _ in range(start_army_count - player.armies):
                random.choice(player.territories).armies += 1
            player.update_army_count()
            self.state.log_event(str(player))
            for t in player.territories:
                print(f"{t.name} has {t.armies} troops.")

    def assign_starting_territories(self):
        all_territories = self.state.territories.copy()
        random.shuffle(all_territories)

        players = self.state.players
        num_players = len(players)
        territories_per_player = len(all_territories) // num_players
        remainder = len(all_territories) % num_players  # e.g., 42 % 5 = 2

        assignment_counts = [territories_per_player] * num_players
        for i in range(remainder):
            assignment_counts[i] += 1  # First N players get 1 extra

        idx = 0
        for player_index, count in enumerate(assignment_counts):
            for _ in range(count):
                territory = all_territories[idx]
                player = players[player_index]
                self.give_territory(territory, player)
                self.state.log_event(f"{player.name} received {territory.name}.")
                idx += 1 

    def attack(self, attacker, from_territory, to_territory, num_armies):
        # TODO: Implement real combat logic
        if from_territory.owner != attacker:
            self.state.log_event(f"{attacker.name} cannot attack from {from_territory.name} they don't control.")
            return False
        if to_territory.owner == attacker:
            self.state.log_event(f"{attacker.name} cannot attack their own territory.")
            return False
        self.state.log_event(f"{attacker.name} attacked {to_territory.name} from {from_territory.name} with {num_armies} armies.")
        return True

    def give_territory(self, territory, player):
        if territory.owner: 
            territory.owner.territories.remove(territory)
        player.territories.append(territory)
        territory.owner = player
        territory.armies = 1

    def draft(self, player, territory, armies):
        if territory.owner != player:
            self.state.log_event(f"{player.name} tried to reinforce {territory.name}, but doesn't own it.")
            return False
        territory.armies += armies
        self.state.log_event(f"{player.name} reinforced {territory.name} with {armies} armies.")
        return True   
                 
    def end_turn(self):
        self.state.current_player_index = (self.state.current_player_index + 1) % len(self.state.players)
        self.state.turn += 1
        self.state.log_event(f"Turn {self.state.turn}: Now it's {self.state.current_player().name}'s turn.")

    def start(self):
        self.state.log_event("Game started.")
        self.assign_starting_territories()
        self.assign_starting_armies()
        self.state.log_event(f"{self.state.current_player().name}'s turn begins.")









