"""
bots.py

Here is the playground to build various bots with different strategies. 
All will extend from the Player class (see structures.py), with strategies overwritten.
    
    Neutral_Bot has the simplest implementation. It drafts troops randomly, and will never attack nor fortify its own troops.

"""

from structures import Player
import random

class Neutral_Bot(Player):
    def __init__(self, name):
        super().__init__(name)

    def draft(self):
        return random.choice(self.territories), self.aatd
    
    def attack(self):
        return None
    
    def fortify(self):
        return None
    

    
    