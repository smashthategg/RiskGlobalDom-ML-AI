"""
bots.py

Here is the playground to build various bots with different strategies. 
All will extend from the Player class (see structures.py), with strategies overwritten.
    
    Neutral_Bot has the simplest implementation. It drafts troops randomly, and never attack nor fortify its own troops.

"""

from structures import Player

class Neutral_Bot(Player):
    def __init__(self, name):
        super().__init__(self, name)
    
    