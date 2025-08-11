"""
combat.py

Implementation for combat systems in RISK.

Note: Bulit from scratch, NOT fully accurate to real game's simulation rules. 
Probability calculations performed via Monte Carlo. # of simulations will be kept low (~10000) for performance.
Expected performance issues when calculating battles involving high amounts of troops (70+ troops?)

⚔️ RISK Combat Basics (the manual dice roll)
    - Attacker can roll up to 3 dice, but only if they have at least 4 troops (must leave 1 behind).
    - Defender can roll up to 2 dice, if they have 2 or more troops.
    - Sort both dice rolls (attacker & defender) from highest to lowest.
    - Compare the top dice: highest attacker die vs. highest defender die.
    - If attacker > defender: defender loses 1 troop, else attacker loses 1 troop.
    - Repeat for second dice (if both sides rolled ≥2 dice).
    - Again, higher die wins; ties go to defender.
"""


import numpy as np

def battle(a, d):
    """
    Simulates a full battle in according with RISK True Random settings.

    Args:
        a (int): Number of attackers
        d (int): Number of defenders
            
    Returns:    
        (int, int): The total remaining troops on both sides.
    """
    while a > 0 and d > 0:
        # Attacker rolls 3 dice (while they have 3+ troops)
        atk_dice = min(3, a) 
        # Defender rolls 2 dice (while they have 2+ troops)
        def_dice = min(2, d)

        att_rolls = np.random.randint(1, 7, size=atk_dice)
        def_rolls = np.random.randint(1, 7, size=def_dice)

        # Sort rolls by descending
        att_top = np.sort(att_rolls)[::-1]
        def_top = np.sort(def_rolls)[::-1]

        # Compare best dice pairs, lesser side loses one troop.
        for i in range(min(atk_dice, def_dice)):
            # If dice are a tie, defender wins.
            if att_top[i] > def_top[i]: 
                d -= 1
            else:
                a -= 1

    return a, d