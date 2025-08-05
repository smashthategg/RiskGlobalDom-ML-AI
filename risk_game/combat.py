"""
combat.py

Implementation for combat systems in RISK.

Note: Bulit from scratch, NOT fully accurate to real game's simulation rules. 
Probability calculations performed via Monte Carlo. # of simulations will be kept low (~10000) for performance.
Expected performance issues when calculating battles involving high amounts of troops (70+ troops?)

⚔️ RISK Combat Basics
    Dice Rules:
        Attacker can roll up to 3 dice, but only if they have at least 4 troops (must leave 1 behind).
        Defender can roll up to 2 dice, if they have 2 or more troops.

    Battle Round:
        Sort both dice rolls (attacker & defender) from highest to lowest.
        Compare the top dice: highest attacker die vs. highest defender die.
        If attacker > defender: defender loses 1 troop, else attacker loses 1 troop.
        Repeat for second dice (if both sides rolled ≥2 dice).
        Again, higher die wins; ties go to defender.
"""

import random

class TrueRandom():
    """
    Represents the True Random combat system in RISK.

    Simulation should be accurate. Probability engine will yield slightly different results from the game.

    Methods:
        roll_dice(num_dice) ...
        simulate_battle_round(attacker_troops, defender_troops) ...
        battle(attacker_troops, defender_troops) ...
        estimate_win_prob(attacker_troops, defender_troops) ...
    """
    def __init__(self, seed=None):
        if seed: # May want to set seed for reproducibility
            random.seed(seed)   

    def roll_dice(self, num_dice):
        """Returns a list (length num_dice) of random integers from 1 to 6, sorted by highest first."""
        return sorted([random.randint(1, 6) for _ in range(num_dice)], reverse=True)

    def simulate_battle_round(self, num_atk_dice, num_def_dice):
        """
        Simulates one `Battle Round` (see doc-level). Equivalent to a manual roll in RISK.
        
        Args:
            num_atk_dice (int): {1, 2, 3}
            num_def_dice (int): {1, 2}
        
        Returns:
            attacker_losses (int), defender_losses (int): Number of troops lost on either side.
        """

        attacker_roll = self.roll_dice(num_atk_dice)
        defender_roll = self.roll_dice(num_def_dice)

        attacker_losses = 0
        defender_losses = 0

        for a, d in zip(attacker_roll, defender_roll):
            if a > d:
                defender_losses += 1
            else:
                attacker_losses += 1

        return attacker_losses, defender_losses

    def battle(self, num_attackers, num_defenders):
        """
        Simulates a full True Random battle.

        Args:
            num_attackers (int): {x > 0}
            num_defenders (int): {x > 0}

        Returns:
            num_attackers (int), num_defenders (int): The total remaining troops on both sides.
        """
        while num_attackers > 0 and num_defenders > 0:
            atk_dice = min(3, num_attackers)
            def_dice = min(2, num_defenders)
            a_loss, d_loss = self.simulate_battle_round(atk_dice, def_dice)
            num_attackers -= a_loss
            num_defenders -= d_loss

        return num_attackers, num_defenders
