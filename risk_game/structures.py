class Territory:
    def __init__(self, name, continent, neighbors):
        self.name = name
        self.continent = continent
        self.owner = None
        self.armies = 0
        self.neighbors = neighbors  # List of adjacent territory names
    
    def __str__(self):
        return f"{self.name} ({self.continent}) - Owner: {self.owner}, Armies: {self.armies}"

    def __repr__(self):
        return self.__str__()

class Continent:
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
    
class Player:
    def __init__(self, name):
        self.name = name
        self.territories = []
        self.cards = []
        self.armies = 0
    
    def update_army_count(self):
        count = 0
        for territory in self.territories:
            count += territory.armies
        self.armies = count
        return count
    
    def __str__(self):
        return f"{self.name} has {self.armies} troops, {len(self.territories)} territories, and {len(self.cards)} cards."
    
    def __repr__(self):
        return self.__str__()
    
    