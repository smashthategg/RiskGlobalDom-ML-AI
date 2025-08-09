"""
game.py

Core gameplay logic for a simplified RISK-style strategy game.

This module defines two main classes:

- GameState: A passive container holding the current state of the game,
  including territories, continents, players, round number, and game log.
  Think of it as a snapshot of all game data.

- Game: The active game engine responsible for enforcing game rules,
  managing turn order, handling territory assignments, drafting, and combat mechanics.
  Game owns a GameState instance, whereas GameState is unaware of Game.

This module assumes the existence of Player, Territory, and Continent classes
(defined in `structures.py`), as well as Combat classes (combat.py).

Usage:
    game_state = GameState(territories, continents, combat, players)
    game = Game(game_state)
    game.start()
"""

from structures import Card
import random

class GameState:
    """
    Holds the current state of the game, including all territories, continents, players,
    and game-related data such as the deck, discard pile, round number, and game log.

    Attributes:
        territories (list of Territory): All territories in the game map.
        continents (list of Continent): All continents in the game.
        players (list of Player): List of players currently in the game.
        round (int): Current round number.
        current_player_index (int): Index of the player whose turn it is.
        game_log (list of str): Chronological list of game event messages.
        game_log_index (int): Tracks how many log entries have been retrieved so far.
        combat (Combat): Combat mechanics handler (external class).
        deck (list of Card): Current deck of cards to draw from.
        discard (list of Card): Discard pile of used cards.
    """

    def __init__(self, territories, continents, combat, players=None):
        """
        Initializes the GameState with game map data, players, and combat system.

        Args:
            territories (list of Territory): List of Territory objects in the game.
            continents (list of Continent): List of Continent objects in the game.
            combat (Combat): An instance of the Combat class managing battles.
            players (list of Player, optional): List of Player objects participating.
                Defaults to an empty list if not provided.
        """
        self.territories = territories
        self.continents = continents
        self.players = players if players else []
        self.round = 0
        self.current_player_index = 0
        self.game_log = []
        self.game_log_index = 0
        self.combat = combat
        self.deck = []
        self.discard = []

    def log_event(self, event_str, doPrint=False):
        """
        Adds an event string to the game log. Optionally prints the updated log.

        Args:
            event_str (str): Description of the event to add to the log.
            doPrint (bool, optional): If True, prints all new log entries after adding this event.
                Defaults to False.
        """
        self.game_log.append(event_str)
        if doPrint:
            for line in self.get_log():
                print(line)

    def get_log(self, full=False):
        """
        Retrieves entries from the game log.

        Args:
            full (bool, optional): If True, returns the entire log.
                If False (default), returns only new entries since last retrieval.

        Returns:
            list of str: The requested log entries.
        """
        if full:
            self.game_log_index = len(self.game_log)
            return self.game_log
        else:
            out = self.game_log[self.game_log_index:]
            self.game_log_index = len(self.game_log)
            return out

    def current_player(self):
        """Returns the Player object whose turn it currently is."""
        return self.players[self.current_player_index]

    
class Game:
    """
    Main game container class.

    Attributes:
        state (GameState): Our passive container holding all the info
        running (bool): Our check if game is active or finished.
        
    Methods are listed as follows:
        def start(): # The main function
            def build_deck() # Set up the deck
            def assign_starting_territories() # Distribute territories among players
            def assign_starting_armies() # Distribute armies among territories 
            def next_round() ... # Start the next round (called indefinitely until game end)
                def start_turn() ... # Complete a player's turn (iterated through each player during round)
                    def trade_and_draft() ... # Helper function called during draft phase (& attack phase on kill)
                    def give_territory() ... # Transfer ownership of territory. Also used in assign_starting_territories() 
                    def eliminate_player ...  # Check if player has no territories, remove them if true.
                    def check_win_condition() ... # Check if anyone won, prepare to end game
                    def draw_card() ... # Get top card from deck
                    def reshuffle_deck() ... # Add discard pile and jokers when deck runs out.


    """
    def __init__(self, game_state):
        self.state = game_state
        self.running = True

    def start(self):
        """Begins the game by assigning territories and starting armies, (will implement the start of first turn)"""
        self.state.log_event("--- Game started. ---")
        self.build_deck()
        self.assign_starting_territories()
        self.assign_starting_armies()
        while self.running:
            self.next_round()
       
    def build_deck(self):
        """
        Builds a shuffled deck of cards of random types. One for each territory.
        Note: Jokers are only introduced on reshuffle_deck()
        """
        card_types = ["Infantry", "Cavalry", "Artillery"]
        cards = []
        for terr in self.state.territories:
            cards.append(Card(random.choice(card_types), terr))
        random.shuffle(cards)
        self.state.deck = cards

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
                self.state.log_event(f"[GAME] {player.name} received {territory.name}.")
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
            # Set all territories to 1 troop initially
            for terr in player.territories:
                terr.armies = 1
            
            # Calculate troops remaining after minimum one troop per territory
            remaining = start_army_count - len(player.territories)
            if remaining < 0:
                # Defensive: if territories > start armies, adjust (should never happen)
                remaining = 0

            # Distribute remaining troops randomly
            for _ in range(remaining):
                random.choice(player.territories).armies += 1

            player.update_army_count()

    def next_round(self):
        """Advances the game to the next round (iterate through each player's turn)."""
        info = [str(t) for t in self.state.territories] + [str(p) for p in self.state.players]
        info_str = '\n[INFO] ' + '\n[INFO] '.join(info)
        self.state.log_event(info_str, True)
        self.state.round += 1
        i = 0
        while self.running and i < len(self.state.players):
            self.state.current_player_index = i
            self.start_turn()
            i += 1

    def start_turn(self):
        """
        Completes a player's turn, including the draft, attack, and fortify phase.
        
        Returns True if game ended on this turn, False otherwise.
        """

        curr_player = self.state.current_player()
        self.state.log_event(f"\n--- Round {self.state.round}: {curr_player.name}'s turn ---")

        # Update current player's owned continents list
        owned_continents = []
        for continent in self.state.continents:
            if all(t.owner == curr_player for t in continent.territories):
                continent.owner = curr_player  # Update continent owner
                owned_continents.append(continent)
            else:
                # Remove owner if previously owned but lost
                if continent.owner == curr_player:
                    continent.owner = None

        curr_player.continents = owned_continents  # Update player's owned continents attribute
        
        # Draft phase
        self.state.log_event(f"[DRAFT] {curr_player.name} received {curr_player.update_aatd_count()} troops with {len(curr_player.territories)} territories.", True)
        self.trade_and_draft(curr_player)

        # Attack phase
        capture_success = False
        while True:
            try:
                attack_result = curr_player.attack()
                if attack_result is None:
                    self.state.log_event(f"[ATTACK] {curr_player.name} ended the attack phase.")
                    break

                atk_terr, def_terr, amount = attack_result
                self.state.log_event(f"[ATTACK] {curr_player.name} attacked {def_terr} from {atk_terr} with {amount} troops.")
                
                # Replace the territory army counts with the results of the battle.
                atk_res, def_res = self.state.combat.battle(amount, def_terr.armies)
                self.state.log_event(f"[ATTACK] Lost troops: {atk_terr.armies-atk_res-1} | {def_terr.armies-def_res}")
                self.state.log_event(f"[ATTACK] Remaining troops: {atk_res+1} | {def_res}", True)
                atk_terr.armies = atk_res+1
                def_terr.armies = def_res

                # If defender lost all troops, territory changes ownership
                if def_terr.armies == 0:
                    capture_success = True
                    def_player = def_terr.owner
                    self.give_territory(def_terr, curr_player)

                    # Eliminate defending player if they lost their last territory.
                    self.eliminate_player(player=def_player, winner=curr_player)
                    if self.check_win_condition(): return
                    
                    # On kill, player may now have 5+ cards. We force trade-ins here.
                    while len(curr_player.cards) >= 5:
                        self.trade_and_draft(curr_player)

                    # Move in troops.
                    amount = curr_player.fortify(from_territory = atk_terr, dest_territory = def_terr)
                    curr_player.move_troops(from_territory = atk_terr, dest_territory = def_terr, amt = amount)

                    self.state.log_event(f"[ATTACK] {curr_player.name} captured {def_terr.name} and moved in {amount} troops!")

            except Exception as e:
                self.state.log_event(f"[ERROR] {e}")
                break

        # Fortify phase
        while True:
            try:
                result = curr_player.fortify()
                if result is None:
                    self.state.log_event(f"[FORTIFY] {curr_player.name} skipped the fortify phase.")
                    break
                else:
                    from_terr, dest_terr, amount = result
                    curr_player.move_troops(from_terr, dest_terr, amount)
                    self.state.log_event(f"[FORTIFY] {curr_player.name} fortified {amount} troops from {from_terr} to {dest_terr}.")
                    break

            except Exception as e:
                self.state.log_event(f"[ERROR] {e}")
                break    

        # End turn
        curr_player.update_army_count()
        if capture_success:
            new_card = self.draw_card()
            curr_player.cards.append(new_card)
            self.state.log_event(f"[GAME] {curr_player.name} received a card: {new_card}.")
        self.state.log_event(f"[END] {curr_player}", True)

    def trade_and_draft(self, curr_player): 
        """Helper function for start_turn()."""
        chosen_set = curr_player.trade()
        if chosen_set: # On trade-in, discard cards and add bonus troops
            bonus = curr_player.trade_in_cards(chosen_set)
            self.state.discard.extend(chosen_set)
            self.state.log_event(f"[DRAFT] {curr_player.name} traded in cards for {bonus} bonus troops.", True)
        while curr_player.aatd > 0: # Draft all available troops
            terr, amt = curr_player.draft()
            terr.armies += amt
            curr_player.aatd -= amt
            self.state.log_event(f"[DRAFT] {curr_player.name} placed {amt} troops in {terr}.")

    def give_territory(self, territory, player):
        """
        Transfers ownership of a territory to a player.
        Used at start of game to distribute territories,
        and after a successful attack -> capture of territory.
        """
        if territory.owner: 
            territory.owner.territories.remove(territory)
        player.territories.append(territory)
        territory.owner = player
        territory.armies = 0

    def eliminate_player(self, player, winner):
        """
        Removes a player from the game when they have no territories left.
        Transfers that player's cards to winner, the player who killed them.
        """
        if player.territories == []:
            killed_index = self.state.players.index(player)
            num_cards = len(player.cards)
            winner.cards = winner.cards + player.cards
            player.cards = []

            self.state.log_event(f"[GAME] {winner.name} defeated {player.name}, gaining {num_cards} cards.", True)
            self.state.players.remove(player)

            # Adjust current player index if needed
            if killed_index < self.state.current_player_index:
                self.state.current_player_index -= 1

    def check_win_condition(self):
        """
        Checks if the game has been won. Updates game state to stop running.
        Returns True if game ends, False otherwise.
        """
        # Win condition #1, the standard for world domination gamemode. We may add more later.
        if len(self.state.players) == 1:
            self.state.log_event(f"[GAME] {self.state.players[0].name} wins the game!", True)
            self.running = False
            return True
        return False
                
    def draw_card(self):
        """
        Draws the top card from the deck. If deck is empty, reshuffles discard + jokers first.
        Returns the drawn card (to be added to player's hand by caller).
        """
        if not self.state.deck:
            self.reshuffle_deck()
        card = self.state.deck.pop(0)
        return card

    def reshuffle_deck(self):
        """
        Reshuffles the discard pile back into the deck and adds 2 jokers.
        Clears the discard pile after reshuffle.
        """
        jokers = [Card("Joker", None), Card("Joker", None)]
        self.state.deck = self.state.discard + jokers
        self.state.discard.clear()
        random.shuffle(self.state.deck)









