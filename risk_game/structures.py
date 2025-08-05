"""
structures.py

Contains the classes for the main game data structures. They are integral to the function of RISK: Global Domination.
    - Card 
    - Continent
    - Player
    - Territory
"""
import io

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
    def __init__(self, type, territory):
        self.type = type
        self.territory = territory

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
        
        


    def __str__(self):
        return f"{self.name} has {self.armies} troops, {len(self.territories)} territories, and {len(self.cards)} cards."

    def __repr__(self):
        return self.__str__()

    