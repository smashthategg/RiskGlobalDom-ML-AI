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
        cards (list[Card]): Cards held by the player.
        armies (int): Total number of armies the player has.

    Methods:
        update_army_count(): Recalculates and updates the total army count based on territories.
    """

    def __init__(self, name):
        self.name = name
        self.territories = []
        self.cards = []
        self.armies = 0

    def update_army_count(self):
        """
        Recalculates the total number of armies by summing the armies in all owned territories.

        Returns:
            int: Updated total army count.
        """
        count = 0
        for territory in self.territories:
            count += territory.armies
        self.armies = count
        return count

    def __str__(self):
        return f"{self.name} has {self.armies} troops, {len(self.territories)} territories, and {len(self.cards)} cards."

    def __repr__(self):
        return self.__str__()

    