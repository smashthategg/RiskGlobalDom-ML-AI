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
        return f"{self.name} ({self.continent}) - Owner: {self.owner.name}, Armies: {self.armies}"

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
        while True:
            try:
                input_territory = input("Where will you draft? ")
                owned_territory_names = [t.name for t in self.territories]
                if input_territory not in owned_territory_names:
                    raise ValueError
                break
            except ValueError:
                print("You do not own a territory with this name. Please try again.")
        while True:
            try:
                amount = int(input("How many troops? "))
                if amount < 1 or amount > self.aatd:
                    raise ValueError
                break
            except ValueError:
                print(f"Invalid number of troops. Please pick a number between 1 and {self.aatd} (inclusive).")

        selected_territory = next(t for t in self.territories if t.name == input_territory)
        return selected_territory, amount




        
        


    def __str__(self):
        return f"{self.name} has {self.armies} troops, {len(self.territories)} territories, and {len(self.cards)} cards."

    def __repr__(self):
        return self.__str__()

    