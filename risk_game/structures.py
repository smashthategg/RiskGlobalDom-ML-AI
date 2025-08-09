"""
structures.py

Contains the classes for the main game data structures. They are integral to the function of RISK: Global Domination.
    - Card 
    - Continent
    - Player
    - Territory
"""

class Card:
    """
    Represents the card, which is traded in sets of 3 for bonus troops.

    Attributes:
        type (str): 3 types: "Infantry", "Cavalry", "Artillery". There is also the "Joker" which acts as a wildcard for any type.
            Trading in a set of 3 Infantry cards gives 4 additional troops.
            Trading in a set of 3 Cavalry cards gives 6 additional troops.
            Trading in a set of 3 Artillery cards gives 8 additional troops.
            Trading in a set of 3 cards containing one of each type gives 10 additional troops.
        territory (Territory): Each card has an associated territory.
            Technically, players choose the order of cards in a traded 3-card set. 
            The first card in this order whose associated territory is also owned by the player also grants 2 additional troops
            which are automatically drafted to that territory.
    """
    def __init__(self, type, territory=None):
        self.type = type
        self.territory = territory

    def __repr__(self):
        if self.territory:
            return f"Card(type={self.type}, territory={self.territory.name})"
        else:
            return f"Card(type={self.type})"


class Continent:
    """
    Represents a specific collection of territories. If a player owns all the territories in a Continent during draft phase,
    they receive additional troops equal to the Continent's bonus.

    Attributes:
        name (str): Name of the continent.
        bonus (int): Size of the bonus armies
        territories (list[Territory]): Territories that make up the continent.
        owner (Player or None): Player who currently owns it.
    """
    def __init__(self, name, bonus, territories):
        self.name = name
        self.bonus = bonus
        self.territories = territories
        self.owner = None
    
    def __str__(self):
        territory_names = ', '.join([t.name for t in self.territories])
        return f"{self.name} (Bonus: {self.bonus}) - Territories: {territory_names}"

    def __repr__(self):
        return self.__str__()
    
class Territory:
    """
    Represents a territory in the RISK game.

    Attributes:
        name (str): Name of the territory.
        continent (str): Name of the continent it belongs to. Just for user clarification so can encode as String.
        owner (Player or None): Player who currently owns it.
        armies (int): Number of armies stationed. In practice, this number is always 1 or greater.
        neighbors (list[Territory]): Adjacent territories that can be attacked/fortified through.
    """
    def __init__(self, name, continent, neighbors):
        self.name = name
        self.continent = continent
        self.owner = None
        self.armies = 0
        self.neighbors = neighbors  # List of adjacent territory names

    def get_connected_territories(self):
        """
        Gets a list of Territories connected to this Territory through neighbors 
        that share the same owner. Does NOT include self in the result.

        Returns:
            connected (list[Territory]): Territories connected to this territory 
                                        via same-owner paths. Can be empty.
        """
        connected = []
        visited = {self}  # Set to avoid repeats
        queue = [self]

        while queue:
            current = queue.pop(0)
            for neighbor in current.neighbors:
                if neighbor.owner == self.owner and neighbor not in visited:
                    visited.add(neighbor)
                    connected.append(neighbor)
                    queue.append(neighbor)

        return connected


    
    def __str__(self):
        return f"{self.name} ({self.owner.name}, {self.armies} armies)"

    def __repr__(self):
        return self.__str__()
    
class Player:
    """
    Represents a player in the RISK game.

    Attributes:
        name (str): Name of the player.
        territories (list[Territory]): Territories owned by the player.
        continents (list[Continent]): Continents owned by the player.
        cards (list[Card]): Cards held by the player.
        armies (int): Total number of armies the player has, including income at the start of draft phase.
        aatd (int): Armies Available to Draft. Total number of armies the player is allowed to deploy during draft phase.

    Methods:
        update_army_count(): Recalculates and updates the total army count based on territories.
        update_aatd_count(): Recalculates and updates total income based on held continents and # territories owned.
        trade_in_cards(list[Card]): Trades in a chosen set of 3 cards
    
    Interactive methods prompt the user to make moves via std I/O:
        draft(): User chooses a territory to add troops in and how much.
        attack(): User chooses a territory to attack and how hard.
        fortify(): User chooses a territory to fortify troops from and to, and how much.
        trade(): User chooses cards to trade in.
    """

    def __init__(self, name):
        self.name = name
        self.territories = []
        self.continents = []
        self.cards = []
        self.armies = 0
        self.aatd = 3

    def update_army_count(self):
        """
        Recalculates the total number of armies by summing the armies in all owned territories.
        Also reevaluates continent ownership
        Player.armies is set to this value.

        Returns:
            int: Updated total army count.
        """
        count = 0
        for territory in self.territories:
            count += territory.armies
        self.armies = count

        return count

    def update_aatd_count(self):
        """
        Recalculates and updates total income based on held continents and # territories owned.
        Player.aatd is set to this value.

        Algorithm: Sum all continent bonuses and add `max(3, floor(# territories owned / 3))`.

        Returns:
            Updated aatd value (int).
        """
        count = max(3, (len(self.territories) // 3))
        for c in self.continents:
            count += c.bonus
        self.aatd = count
        return count
    
    def trade_in_cards(self, chosen_set):
        """
        Trade in a chosen set of 3 cards.

        Args:
            chosen_set (list of Card): Exactly 3 cards forming a valid set.

        Updates:
            self.cards: removes the traded cards
            self.aatd: increments by total troop bonus
            Territory.armies: adds +2 bonus troops to first owned card territory, if any
        
        Returns:
            int: number of bonus troops gained.
        """
        # Remove cards from player's hand
        for card in chosen_set:
            self.cards.remove(card)

        # Count card types, ignoring jokers
        types = [card.type for card in chosen_set if card.type != "Joker"]
        jokers = sum(1 for card in chosen_set if card.type == "Joker")
        unique_types = set(types)

        bonus = 0
        if len(unique_types) + jokers == 3:
            bonus = 10
        elif len(unique_types) == 1:
            card_type = unique_types.pop()
            if card_type == "Infantry":
                bonus = 4
            elif card_type == "Cavalry":
                bonus = 6
            elif card_type == "Artillery":
                bonus = 8
        else: # This should never be called if our logic is coded properly
            raise ValueError("[ERROR] Invalid card set traded in.")

        # Find first card territory owned by player, add 2 to it.
        for card in chosen_set:
            if card.territory in self.territories:
                card.territory.armies += 2
                break
        
        self.aatd += bonus
        return bonus

    def validate_card_set(self, chosen_set):
        """
        Validates whether the chosen set of cards (3 or more) contains at least one valid 3-card trade-in set.

        Args:
            chosen_set (list[Card]):

        Returns:
            bool: True if there exists a 3-card subset forming a valid set, False otherwise.
        """
        n = len(chosen_set)
        if n < 3:
            return False
        if n >= 5:
            # Guaranteed at least one valid set
            return True

        # For 3 or 4 cards, manually check all 3-card subsets
        subsets = []
        if n == 3:
            subsets = [chosen_set]
        elif n == 4:
            # 4 choose 3 = 4 subsets
            subsets = [
                [chosen_set[0], chosen_set[1], chosen_set[2]],
                [chosen_set[0], chosen_set[1], chosen_set[3]],
                [chosen_set[0], chosen_set[2], chosen_set[3]],
                [chosen_set[1], chosen_set[2], chosen_set[3]],
            ]

        for subset in subsets:
            types = [card.type for card in subset if card.type != "Joker"]
            jokers = sum(1 for card in subset if card.type == "Joker")
            unique_types = set(types)

            # Three of a kind
            if len(unique_types) == 1 or len(unique_types) + jokers == 3:
                return True

        return False



    def draft(self):
        """
        User chooses territory to add troops in and how much. 
        This function keeps getting called until there are no more troops to draft.

        Output: 
            tuple: (selected_territory, amount): Territory object and the corresponding amount of troops to add (int >= 1).
        """

        step = 0
        selected_territory = None

        while True:
            if step == 0:
                input_territory = input("[PROMPT] Where will you draft? ")
                if input_territory.lower() == "back":
                    print("[ERROR] You are already at the first step.")
                    continue
                owned_territory_names = [t.name for t in self.territories]
                if input_territory not in owned_territory_names:
                    print("[ERROR] You do not own a territory with this name. Please try again.")
                    continue
                selected_territory = next(t for t in self.territories if t.name == input_territory)
                step = 1

            elif step == 1:
                response = input(f"[PROMPT] How many troops? (1–{self.aatd}): (Type 'back' to reselect a territory.) ")
                if response.lower() == "back":
                    step = 0
                    continue
                try:
                    amount = int(response)
                    if amount < 1 or amount > self.aatd:
                        raise ValueError
                    return selected_territory, amount
                except ValueError:
                    print(f"[ERROR] Invalid number of troops. Please pick a number between 1 and {self.aatd} (inclusive).")


    def attack(self):
        """
        User chooses a territory to attack from, a neighboring enemy territory to attack,
        and how many troops to use in the attack.

        Returns:
            tuple: (from_territory, dest_territory, amount) or None if player skips attack
        """
        print("Type 'skip' at any prompt to end your attack phase. Type 'back' to go back one step.")

        step = 0
        from_territory = None
        dest_territory = None
        amount = None

        while True:
            if step == 0:
                from_name = input("[PROMPT] Attack from which territory? ")
                if from_name.lower() in {"skip", "end"}:
                    return None
                try:
                    from_territory = next(t for t in self.territories if t.name == from_name)
                    if from_territory.armies < 2:
                        print("[ERROR] You need at least 2 troops to attack from this territory.")
                        continue
                    if not any(n.owner != self for n in from_territory.neighbors):
                        print("[ERROR] This territory has no enemy neighbors to attack.")
                        continue
                    step = 1
                except StopIteration:
                    print("[ERROR] You do not own a territory with this name. Please try again.")

            elif step == 1:
                enemy_neighbors = [n for n in from_territory.neighbors if n.owner != self]
                options = "\n".join([str(n) for n in enemy_neighbors])
                dest_name = input(f"[PROMPT] Which enemy territory do you want to attack? Options: \n{options}\n")
                if dest_name.lower() in {"skip", "end"}:
                    return None
                elif dest_name.lower() == "back":
                    step = 0
                    continue
                try:
                    dest_territory = next(n for n in enemy_neighbors if n.name == dest_name)
                    step = 2
                except StopIteration:
                    print("[ERROR] Invalid target. Please pick a valid enemy neighbor.")

            elif step == 2:
                response = input(f"[PROMPT] How many troops to attack with? (1–{from_territory.armies-1}): ")
                if response.lower() in {"skip", "end"}:
                    return None
                elif response.lower() == "back":
                    step = 1
                    continue
                try:
                    amount = int(response)
                    if amount < 1 or amount > from_territory.armies-1:
                        raise ValueError
                    return from_territory, dest_territory, amount
                except ValueError:
                    print(f"[ERROR] Invalid input. You must choose between 1 and {from_territory.armies-1}.")
    
    def move_troops(self, from_territory, dest_territory, amt):
        """
        Helper function to move troops from one territory to another
        Used after an attack, or during fortify phase.
        Note: no error checks within this function, should be done before function is called.

        Args:
            from_territory (Territory): Starting territory
            dest_territory (Territory): Ending territory
            amt (int): Number of troops to be moved
        """
        from_territory.armies -= amt
        dest_territory.armies += amt

    def fortify(self, from_territory=None, dest_territory=None):
        """
        User chooses a territory to fortify from, a connected territory to fortify to,
        and how many troops to move. This function also doubles to be flexible with post-attack troop movement.

        Args default to none but are given when moving troops in after a successful attack:
            from_territory (Territory):
            dest_territory (Territory): 

        Returns:
            tuple: (from_territory, dest_territory, amount) or None if player skips foritfy
            OR
            int: if from_territory and dest_territory are already given, and we just want the # troops for post-attack phase.
        """
        attack = True if from_territory and dest_territory else False
        step = 2 if attack else 0
        while True:
            if step == 0:
                print("[INFO] Type 'skip' at any prompt to end your fortify phase. Type 'back' to go back one step.")
                from_name = input("[PROMPT] Fortify from which territory? ")
                if from_name.lower() in {"skip", "end"}:
                    return None
                try:
                    from_territory = next(t for t in self.territories if t.name == from_name)
                    if from_territory.armies < 2:
                        print("[INFO] You need at least 2 troops to fortify from this territory.")
                        continue
                    connected_owned = from_territory.get_connected_territories()
                    if not connected_owned:
                        print("[INFO] No connected territories you own to fortify to.")
                        continue
                    step = 1
                except StopIteration:
                    print("[ERROR] You do not own a territory with this name. Please try again.")

            elif step == 1:
                options = "\n".join([str(t) for t in connected_owned])
                dest_name = input(f"[PROMPT] Fortify to which connected territory? Options:\n{options}\n")
                if dest_name.lower() in {"skip", "end"}:
                    return None
                elif dest_name.lower() == "back":
                    step = 0
                    continue
                try:
                    dest_territory = next(t for t in connected_owned if t.name == dest_name)
                    step = 2
                except StopIteration:
                    print("[ERROR] Invalid target. Please choose a valid connected owned territory.")

            elif step == 2:
                max_movable = from_territory.armies - 1
                if attack:
                    # You must move at least 3 troops into a captured territory, when possible.
                    # If you can only move 3 or less, then they automatically get moved.
                    if max_movable <= 3: 
                        return max_movable
                    else:
                        min_movable = 3
                else:
                    min_movable = 1
                response = input(f"[PROMPT] How many troops to move? ({min_movable}–{max_movable}): ")
                if response.lower() in {"skip", "end"}:
                    if attack:
                        print("[INFO] Skip failed. You must choose troops to move after an attack.")
                        continue
                    else:
                        return None
                elif response.lower() == "back":
                    if attack:
                        print("[INFO] Back failed. You must choose troops to move after an attack.")
                    else:
                        step = 1
                    continue
                try:
                    amount = int(response)
                    if amount < min_movable or amount > max_movable:
                        raise ValueError
                    if attack:
                        return amount
                    return from_territory, dest_territory, amount
                except ValueError:
                    print(f"[ERROR] Invalid input. You must choose between {min_movable} and {max_movable}.")

    def trade(self):
        """
        User-interactive function to trade in cards.

        Repeatedly prompts user to select 3 cards to trade in until a valid set is chosen
        or user opts to skip trading (can't skip if user has 5+ cards.)

        Returns:
            list[Card]: the chosen set of cards (to be passed through trade_in_cards())
        """
        # Skip this function if user can't trade.
        if not self.validate_card_set(self.cards):
            return None

        print("[INFO] You can trade cards! Listed below: ")
        for idx, card in enumerate(self.cards):
            print(f"{idx}: {card}")

        while True:
            user_input = input("Enter three card indices to trade separated by spaces, or 'skip' to skip trading: ").strip()
            if user_input.lower() == "skip":
                if len(self.cards) >= 5:
                    print("[INFO] Skip failed. You must trade on 5+ cards.")
                    continue
                else:
                    return None

            try:
                indices = list(map(int, user_input.split()))
                if len(indices) != 3:
                    print("[ERROR] Please enter exactly 3 indices.")
                    continue
                chosen_set = [self.cards[i] for i in indices]
            except (ValueError, IndexError):
                print("[ERROR] Invalid input. Please enter valid card indices separated by spaces.")
                continue

            if not self.is_valid_set(chosen_set):
                print("[INFO] Chosen cards do not form a valid set. Try again.")
                continue
            else:
                return chosen_set


    def __str__(self):
        return f"{self.name} has {self.armies} troops, {len(self.territories)} territories, and {len(self.cards)} cards."

    def __repr__(self):
        return self.__str__()

    