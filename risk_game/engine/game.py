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

from risk_game.engine.structures import Card
from risk_game.engine.combat import battle
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
        game_log (list of str): Chronological list of game event messages.
        game_log_index (int): Tracks how many log entries have been retrieved so far.
        current_player_index (int): Index of the player whose turn it is.
        phase_info (dict): Extra dynamic, one-time tracking player-specific info for UI rendering and logging.
        { 
            "phase": (str) The current phase of a turn.
            "draft_bonus": (int) The current Player's available armies to deploy (aatd)
            "card_bonus": (int) The trade-in value of the cards, if the current Player does trade a set.
            "selected": (dict) Tracks where the current Player drafts troops or attacks/fortifies from, if they do.
            {
                "territory": (str) Territory name
                "change": (int) Positive when drafting, negative when attacking (tracks losses) and fortifying (out)
            },
            "target": (dict) Tracks where the current Player attacks/fortifies to. 
            {
                "territory": (str) Territory name
                "change": (int) Negative when attacking (tracks defender losses), positive when fortifying (to)
            } 
        },

    """

    def __init__(self, territories, continents, players=None, custom_start_count=0):
        """
        Initializes the GameState with game map data, players, and combat system.

        Args:
            territories (list of Territory): List of Territory objects in the game.
            continents (list of Continent): List of Continent objects in the game.
            players (list of Player, optional): List of Player objects participating.
                Defaults to an empty list if not provided.
        """
        self.territories = territories
        self.continents = continents
        self.players = players if players else []
        self.round = 0
        self.game_log = []
        self.game_log_index = 0
        self.current_player_index = 0
        self.phase_info = {}
        self.custom_start_count = custom_start_count

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

    def serialize_ui_simulation(self):
        ui_state = {}
        ui_state["players"] = []
        ui_state["territories"] = {}
        ui_state["continent_ownership"] = {}
        for p in self.players:
            ui_state["players"].append({"name": p.name, "cards": len(p.cards), "armies": p.armies, "territories": len(p.territories)})
        for t in self.territories:
            if t.owner:
                ui_state["territories"][t.name] = {"owner_index": self.players.index(t.owner), "armies": t.armies}
        for c in self.continents:
            if c.owner:
                ui_state["continent_ownership"][c.name] = self.players.index(c.owner)
        ui_state["current_player_index"] = self.current_player_index
        ui_state["phase"] = self.phase_info.get("phase")
        ui_state["current_player_bonus"] = self.phase_info.get("draft_bonus")
        ui_state["card_bonus"] = self.phase_info.get("card_bonus")
        ui_state["highlights"] = {
            "selected": {
                "territory": self.phase_info.get("selected", {}).get("territory"),
                "owner_index": self.phase_info.get("selected", {}).get("owner_index"),
                "change": self.phase_info.get("selected", {}).get("change", 0)
            },
            "target": {
                "territory": self.phase_info.get("target", {}).get("territory"),
                "owner_index": self.phase_info.get("selected", {}).get("owner_index"),
                "change": self.phase_info.get("target", {}).get("change", 0)
            }
        }
        return ui_state
        
        
            
class Game:
    """
    Main game container class.

    Attributes:
        state (GameState): Our passive container holding all the info
        running (bool): Our check if game is active or finished.
        deck (list of Card): Current deck of cards to draw from.
        discard (list of Card): Discard pile of used cards.
        listeners (list of functions): UI modules insert functions here to track the Game
        
    Methods are listed as follows:
        def start(): # The main function
            def build_deck() # Set up the deck
            def assign_starting_territories() # Distribute territories among players
            def assign_starting_armies() # Distribute armies among territories 
            def next_round() # Start the next round (called indefinitely until game end)
                def start_turn() # Complete a player's turn (iterated through each player during round)
                    def trade_and_draft() # Helper function called during draft phase (& attack phase on kill)
                    def give_territory() # Transfer ownership of territory. Also used in assign_starting_territories() 
                    def eliminate_player  # Check if player has no territories, remove them if true.
                    def check_win_condition() # Check if anyone won, prepare to end game
                    def draw_card() # Get top card from deck
                    def reshuffle_deck() # Add discard pile and jokers when deck runs out.
        def add_listener(callback: Function) # Adds UI listener
        def notify_listeners() # Pings the UI listener
    

    """
    def __init__(self, game_state):
        self.state = game_state
        self.running = True
        self.deck = []
        self.discard = []
        self.listeners = []

    def start(self):
        """Begins the game by assigning territories and starting armies, (will implement the start of first turn)"""
        self.state.log_event("--- Game started. ---")
        self.build_deck()
        self.assign_starting_territories()
        self.assign_starting_armies()
        self.update_state("no-action")
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
        self.deck = cards

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
        if self.state.custom_start_count:
            start_army_count = self.state.custom_start_count
        else:
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
            curr_player = self.state.current_player()
            if curr_player.alive:
                self.start_turn(curr_player)
            i += 1

    def start_turn(self, curr_player):
        """
        Completes a player's turn, including the draft, attack, and fortify phase.
        
        Returns True if game ended on this turn, False otherwise.
        """
            
        self.state.log_event(f"\n--- Round {self.state.round}: {curr_player.name}'s turn ---")
        
        # Draft phase
        # Special first turn logic
        draft_bonus = 0
        if self.state.round == 1:
            i = 0
            extras = {
                6: [0,0,0,1,2,3],
                5: [0,0,0,1,2],
                4: [0,0,0,1],
                3: [0,0,1],
                2: [0,3]
            }
            num_players = len(self.state.players)
            i = self.state.players.index(curr_player)
            draft_bonus = curr_player.update_aatd_count(extras[num_players][i])
        else:
            draft_bonus = curr_player.update_aatd_count()
        self.state.log_event(f"[DRAFT] {curr_player.name} received {draft_bonus} troops with {len(curr_player.territories)} territories.", True)
        self.update_state("bonus", draft_bonus)
        self.trade_and_draft(curr_player)
        # Attack phase
        capture_success = False
        self.update_state("no-action")
        while True:
            try:
                attack_result = curr_player.attack()
                if attack_result is None:
                    self.state.log_event(f"[ATTACK] {curr_player.name} ended the attack phase.")
                    break

                atk_terr, def_terr, amount = attack_result
                self.state.log_event(f"[ATTACK] {curr_player.name} attacked {def_terr} from {atk_terr} with {amount} troops.")
                                
                # Replace the territory army counts with the results of the battle.
                atk_res, def_res = battle(amount, def_terr.armies)
                atk_res = atk_res + 1
                atk_loss, def_loss = atk_terr.armies - atk_res, def_terr.armies - def_res
                atk_terr.armies, def_terr.armies = atk_res, def_res

                self.state.log_event(f"[ATTACK] Lost troops: {atk_loss} | {def_loss}")
                self.state.log_event(f"[ATTACK] Remaining troops: {atk_res} | {def_res}", True)
                curr_player.update_army_count()
                def_terr.owner.update_army_count()
                self.update_state("attack", atk_terr.name, atk_loss*-1, def_terr, def_loss*-1)

                # If defender lost all troops, territory changes ownership
                if def_terr.armies == 0:
                    capture_success = True
                    def_player = def_terr.owner
                    self.give_territory(def_terr, curr_player)

                    # Eliminate defending player if they lost their last territory.
                    self.eliminate_player(player=def_player, winner=curr_player)
                    if self.check_win_condition(): 
                        self.update_state("no-action")
                        return
                    
                    # On kill, player may now have 5+ cards. We force trade-ins here.
                    while len(curr_player.cards) >= 5:
                        self.trade_and_draft(curr_player)

                    # Move in troops.
                    amount = curr_player.fortify(from_territory = atk_terr, dest_territory = def_terr)
                    curr_player.move_troops(from_territory = atk_terr, dest_territory = def_terr, amt = amount)

                    self.state.log_event(f"[ATTACK] {curr_player.name} captured {def_terr.name} and moved in {amount} troops!")
                    self.update_state("no-action")
            except Exception as e:
                self.state.log_event(f"[ERROR] {e}")
                break

        # Fortify phase
        self.update_state("no-action")
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
                    self.update_state("fortify", from_terr.name, amount*(-1), dest_terr.name, amount)
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
        self.update_state("no-action")

    def trade_and_draft(self, curr_player): 
        """Helper function for start_turn()."""
        chosen_set = curr_player.trade()
        if chosen_set: # On trade-in, discard cards and add bonus troops
            bonus = curr_player.trade_in_cards(chosen_set)
            self.discard.extend(chosen_set)
            self.state.log_event(f"[DRAFT] {curr_player.name} traded in cards for {bonus} bonus troops.", True)
            self.update_state("trade", bonus)
        while curr_player.aatd > 0: # Draft all available troops
            terr, amt = curr_player.draft()
            terr.armies += amt
            curr_player.aatd -= amt
            self.state.log_event(f"[DRAFT] {curr_player.name} placed {amt} troops in {terr}.")
            self.update_state("draft", terr.name, amt)

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

        # Update owner of any continent that includes this territory
        for continent in self.state.continents:
            if territory in continent.territories:
                owners = {t.owner for t in continent.territories}
                continent.owner = next(iter(owners)) if len(owners) == 1 and None not in owners else None

        # Update player's owned continents list
        for p in self.state.players:
            p.continents = [c for c in self.state.continents if c.owner == p]

    def eliminate_player(self, player, winner):
        """
        Removes a player from the game when they have no territories left.
        Transfers that player's cards to winner, the player who killed them.
        """
        if player.territories == []:
            player.alive = False
            player.armies = 0
            num_cards = len(player.cards)
            winner.cards = winner.cards + player.cards
            player.cards = []
            self.state.log_event(f"[GAME] {winner.name} defeated {player.name}, gaining {num_cards} cards.", True)

    def check_win_condition(self):
        """
        Checks if the game has been won. Updates game state to stop running.
        Returns True if game ends, False otherwise.
        """
        # Win condition #1, the standard for world domination gamemode. We may add more later.
        count = 0
        winner = None
        for player in self.state.players:
            if player.alive:
                count += 1
                winner = player
        if count == 1:
            self.state.log_event(f"[GAME] {winner.name} wins the game!", True)
            self.running = False
            return True
        return False
                
    def draw_card(self):
        """
        Draws the top card from the deck. If deck is empty, reshuffles discard + jokers first.
        Returns the drawn card (to be added to player's hand by caller).
        """
        if not self.deck:
            self.reshuffle_deck()
        card = self.deck.pop(0)
        return card

    def reshuffle_deck(self):
        """
        Reshuffles the discard pile back into the deck and adds 2 jokers.
        Clears the discard pile after reshuffle.
        """
        jokers = [Card("Joker", None), Card("Joker", None)]
        self.deck = self.discard + jokers
        self.discard.clear()
        random.shuffle(self.deck)

    def add_listener(self, callback):
        self.listeners.append(callback)

    def notify_listeners(self):
        state = self.state.serialize_ui_simulation()
        for cb in self.listeners:
            cb(state)  # call each function with the new state

    def update_state(self, phase, *args):
        self.state.phase_info = {}
        self.state.phase_info["phase"] = phase
        if phase == "no-action":
            pass
        elif phase == "bonus": 
            self.state.phase_info["draft_bonus"] = args[0]
        elif phase == "draft":
            self.state.phase_info["selected"] = {"territory": args[0], "owner_index": self.state.current_player_index, "change": args[1]}
        elif phase == "trade":
            self.state.phase_info["card_bonus"] = args[0]
        elif phase == "attack": 
            self.state.phase_info["selected"] = {"territory": args[0], "owner_index": self.state.current_player_index, "change": args[1]}
            self.state.phase_info["target"] = {"territory": args[2].name, "owner_index": self.state.players.index(args[2].owner), "change": args[3]}
        elif phase == "fortify": 
            self.state.phase_info["selected"] = {"territory": args[0], "owner_index": self.state.current_player_index, "change": args[1]}
            self.state.phase_info["target"] = {"territory": args[2], "owner_index": self.state.current_player_index, "change": args[3]}
        self.notify_listeners()





