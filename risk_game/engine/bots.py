"""
bots.py

Here is the playground to build various bots with different strategies. 
All will extend from the Player class (see structures.py), with strategies overwritten.
    
    Neutral_Bot has the simplest implementation. It drafts troops randomly, and will never attack nor fortify its own troops.
    Aggro1_Bot:
        DRAFT: into the territory with the most troops and able to attack. 
        ATTACK: Full send A* -> B*, where:
                    - A* is the strongest territory that can attack (A*.troops > 2)
                    - B* is the weakest territory able to be attacked by A*. (B*.troops < A*.troops - 1)
                If captures, move all A* troops into B* and repeat until no territory meets the criteria A* or B*.
        FORTIFY: Full send C* -> D*, where:
                    C* is strongest territory that has no attackable neighobrs, and
                    D* is strongest territory that can attack.
                If no territory meets the criteria for C*, skip this phase.
        TRADE: the highest value set whenever possible.

"""

from structures import Player
import random

class Neutral_Bot(Player):
    def __init__(self, name):
        super().__init__(name)

    def draft(self):
        """
        Returns:
            tuple: (territory, amount)
                territory (Territory): The territory to draft troops to.
                amount (int): Number of troops to draft (typically all available).
        """
        return random.choice(self.territories), self.aatd
    
    def attack(self): # Because bot never attacks, it will never get cards and never trade!
        return None
    
    def fortify(self):
        return None
    
    
    
class Aggro1_Bot(Player):
    def __init__(self, name):
        super().__init__(name)

    def draft(self):
        """
        Returns:
            tuple: (territory, amount)
                territory (Territory): The territory to draft troops to.
                amount (int): Number of troops to draft (typically all available).
        """
        # Territory with most troops AND can attack (troops > 1 and enemy neighbor)
        candidates = [
            t for t in self.territories if t.armies > 1 and any(n.owner != self for n in t.neighbors)
        ]
        if not candidates:
            # fallback: draft to territory with most troops
            terr = max(self.territories, key=lambda t: t.armies)
        else:
            terr = max(candidates, key=lambda t: t.armies)
        return terr, self.aatd  # draft all troops here

    def attack(self):
        """
        Returns:
            tuple or None:
                If attacking, returns (from_territory, to_territory, attack_armies)
                - from_territory (Territory): Attacking territory.
                - to_territory (Territory): Defending territory to attack.
                - attack_armies (int): Number of troops to use in the attack.
                Returns None if no valid attack is possible.
        """
        # Find strongest territory with troops > 2 that can attack
        attackers = [
            t for t in self.territories if t.armies > 2 and any(n.owner != self for n in t.neighbors)
        ]
        if not attackers:
            return None

        A_star = max(attackers, key=lambda t: t.armies)

        # Weakest neighbor that can be attacked: troops < A_star.armies - 1
        targets = [
            n for n in A_star.neighbors if n.owner != self and n.armies < A_star.armies - 1
        ]
        if not targets:
            return None

        B_star = min(targets, key=lambda t: t.armies)
        amount = A_star.armies - 1
        # Return the attack from A* to B*
        return A_star, B_star, amount

    def fortify(self, from_territory=None, dest_territory=None):
        """
        Args:
            from_territory (Territory, optional): Territory to move troops from.
            dest_territory (Territory, optional): Territory to move troops to.

        Returns:
            tuple or int or None:
                - If no arguments, returns (from_territory, dest_territory, move_amount) tuple to initiate fortify.
                - If from_territory and dest_territory are given, returns int of troops to move.
                - Returns None if no fortify action is desired.
        """
        if from_territory:
            return from_territory.armies - 1
        # C*: strongest territory with no attackable neighbors
        candidates_C = [
            t for t in self.territories if not any(n.owner != self for n in t.neighbors)
        ]
        if not candidates_C:
            return None  # skip fortify

        C_star = max(candidates_C, key=lambda t: t.armies)

        # D*: strongest territory that can attack
        candidates_D = [
            t for t in self.territories if any(n.owner != self for n in t.neighbors)
        ]
        if not candidates_D:
            return None

        D_star = max(candidates_D, key=lambda t: t.armies)

        if C_star == D_star or C_star.armies <= 1:
            return None  # no meaningful fortify move

        move_amount = C_star.armies - 1
        return C_star, D_star, move_amount
    
    def trade(self):
        """
        AggroBot's automated card trade logic.
        Returns:
            list[Card] or None: The chosen set of cards to trade in, or None if no valid set.
        """
        from collections import Counter
        
        cards = self.cards
        n = len(cards)
        if n < 3:
            return None
        
        # Helper to get card types except jokers
        def card_type(card):
            return card.type
        
        # Find all 3-card subsets (since max 5 cards, 3-card combos are manageable)
        subsets = []
        # Manually enumerate 3-card combos without itertools:
        for i in range(n-2):
            for j in range(i+1, n-1):
                for k in range(j+1, n):
                    subsets.append([cards[i], cards[j], cards[k]])

        best_set = None
        best_value = -1

        # Card values by type sets
        value_map = {
            "3 Infantry": 4,
            "3 Cavalry": 6,
            "3 Artillery": 8,
            "1 Infantry + 1 Cavalry + 1 Artillery": 10
        }

        for subset in subsets:
            types = [c.type for c in subset if c.type != "Joker"]
            jokers = sum(1 for c in subset if c.type == "Joker")
            unique_types = set(types)

            # Check for 3 of a kind
            if len(unique_types) == 1:
                card_type_name = unique_types.pop()
                # Adjust for jokers
                count_needed = 3 - jokers
                # We already have count_needed cards of this type because they form the subset
                key = f"3 {card_type_name}"
                val = value_map.get(key, 0)
                if val > best_value:
                    best_value = val
                    best_set = subset

            # Check for one of each type
            needed_types = {"Infantry", "Cavalry", "Artillery"}
            if len(unique_types) + jokers == 3 and unique_types.issubset(needed_types):
                val = value_map["1 Infantry + 1 Cavalry + 1 Artillery"]
                if val > best_value:
                    best_value = val
                    best_set = subset

        return best_set


    

    
    