"""
game.py

Core gameplay logic for a simplified RISK-style strategy game.

This module defines two main classes:

    - GameState: A passive container that holds the current state of the game,
    including territories, continents, players, turn number, and game log. It's like a snapshot of the data.

    - Game: The active game engine responsible for enforcing game rules,
    managing turn order, handling territory assignments, drafting, and combat mechanics.
    Game owns a GameState instance, while GameState doesn't know about Game.

This module assumes the existence of Player, Territory, and Continent classes
(defined in `structures.py`).

Usage:
    game_state = GameState(territories, continents, players)
    game = Game(game_state)
    game.start()
"""

from structures import Territory, Continent
import random

class GameState:
    """See above for a basic rundown."""
    def __init__(self, territories, continents, players=None):
        self.territories = territories  # list of Territory objects
        self.continents = continents    # list of Continent objects 
        self.players = players if players else []  # list of Player objects
        self.round = 0
        self.current_player_index = 0
        self.game_log = []  # List of strings describing game events
        self.game_log_index = 0 # Index to track most recent printed log line. Will be useful for printing only new entries.

    def log_event(self, event_str, doPrint=False):
        """Add a new event to the game log. If doPrint=True then also print out recent log entries."""
        self.game_log.append(event_str)
        if doPrint:
           for line in self.get_log():
               print(line)

    def get_log(self, full=False):
        """
        By default, gets the most recent log entries that have not yet been retrieved by this method.
        Setting full=True retrieves the full log.
        """
        if full:
            self.game_log_index = len(self.game_log)
            return self.game_log
        else:
            out = self.game_log[self.game_log_index:]
            self.game_log_index = len(self.game_log)
            return out

    def current_player(self):
        """Return the Player whose turn it is."""
        return self.players[self.current_player_index]
    
class Game:
    """
    See the top of page for a basic rundown. 
    
    Methods are listed in order of logical importance:
        Setup methods:
            def start() ...
            def assign_starting_territories() ...
            def assign_starting_armies() ...
        
        Turn-related methods: 
            def next_turn() ... in progress
            def kill_player() ... not started
            def end_game() ... not started
        
        Helper, utility, internal methods:
            def give_territory() ...
            def check_for_winner() ... not started
            def check_for_dead() ... not started
    """
    def __init__(self, game_state):
        self.state = game_state

    def start(self):
        """Begins the game by assigning territories and starting armies, (will implement the start of first turn)"""
        self.state.log_event("Game started.")
        self.assign_starting_territories()
        self.assign_starting_armies()
        self.next_round()
       

    def assign_starting_territories(self):
        """
        Randomly assigns all territories evenly among players.
        
        Each player gets # of territories X equal to (total # of territories // # of players).
        For Y remainder territories, the first Y players get 1 additional territory, for a total of (X+1) territories.
        """
        all_territories = self.state.territories.copy()
        random.shuffle(all_territories)

        players = self.state.players
        num_players = len(players)
        territories_per_player = len(all_territories) // num_players
        remainder = len(all_territories) % num_players

        assignment_counts = [territories_per_player] * num_players
        for i in range(remainder):
            assignment_counts[i] += 1 

        idx = 0
        for player_index, count in enumerate(assignment_counts):
            for _ in range(count):
                territory = all_territories[idx]
                player = players[player_index]
                self.give_territory(territory, player)
                self.state.log_event(f"{player.name} received {territory.name}.")
                idx += 1 

    def assign_starting_armies(self):
        """
        Distributes starting armies randomly across each player's territories.
        
        The number of troops each player gets at the start depends on the number of players in the game:
            2 players -> 40 troops
            3 players -> 35 troops
            4 players -> 30 troops
            5 players -> 25 troops
            6 players -> 20 troops

        Note that each terrority must contain at least 1 troop, which we account for in give_territory()
        """
        num_players = len(self.state.players)
        counts = [0,0,40,35,30,25,20]
        start_army_count = counts[num_players]
        for player in self.state.players:
            player.update_army_count()
            for _ in range(start_army_count - player.armies):
                random.choice(player.territories).armies += 1
            player.update_army_count()
            self.state.log_event(str(player))

    def next_round(self):
        """Advances the game to the next round (iterate through each player's turn)."""
        self.state.round += 1
        for i in range(len(self.state.players)):
            self.state.current_player_index = i
            self.start_turn()

    def start_turn(self):
        """Completes a player's turn, including the draft, attack, and fortify phase."""

        curr_player = self.state.current_player()
        self.state.log_event(f"\n--- Round {self.state.round}: {curr_player.name}'s turn ---")
        
        # Draft phase
        self.state.log_event(f"[DRAFT] Received {curr_player.update_aatd_count()} troops ({len(curr_player.territories)})", True)
        while curr_player.aatd > 0:
            terr, amt = curr_player.draft()
            terr.armies += amt
            curr_player.aatd -= amt
            self.state.log_event(f"Placed {amt} troops in {terr}.")

        # Attack phase - in progress

        # Fortify phase - in progress

        # End turn
        self.state.log_event(f"Ends with {curr_player.update_army_count()} troops", True)



    def give_territory(self, territory, player):
        """Transfers ownership of a territory to a player."""
        if territory.owner: 
            territory.owner.territories.remove(territory)
        player.territories.append(territory)
        territory.owner = player
        territory.armies = 1










