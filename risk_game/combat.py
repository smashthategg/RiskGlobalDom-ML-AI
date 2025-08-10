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

import random
import numpy as np


class TrueRandom():
    """
    Represents the True Random combat system in RISK.
    Simulation should be accurate. Probability engine will yield slightly different results from the game.

    Redefined methods:
        battle(attacker_troops, defender_troops) ...
        estimate_win_prob(attacker_troops, defender_troops, reps) ...
    """
    def __init__(self, seed=None):
        if seed: # for reproducibility
            random.seed(seed)


    def battle(self, a, d):
        """
        Simulates (blitzes) a full True Random battle, repeating a battle round (manual roll) until one side loses all its troops.

        Args:   
            a (int): Number of attackers
            d (int): Number of defenders

        Returns:   
            num_attackers (int), num_defenders (int): The total remaining troops on both sides.
        """
        while a > 0 and d > 0:
            atk_dice = min(3, a)
            def_dice = min(2, d)

            # Roll X dice
            att_rolls = np.random.randint(1, 7, size=atk_dice)
            def_rolls = np.random.randint(1, 7, size=def_dice)

            # Sort descending by manual max selection (no full sort)
            att_top = np.sort(att_rolls)[::-1]
            def_top = np.sort(def_rolls)[::-1]

            # Compare dice pairs
            for i in range(min(atk_dice, def_dice)):
                if att_top[i] > def_top[i]:
                    d -= 1
                else:
                    a -= 1

            return a, d
    
    def estimate_win_probability(self, a, d, n=1000):
        """
        Estimates the likelihood of winning an attack via Monte Carlo.

        Args:
            a (int): Number of attackers
            d (int): Number of defenders
            n (int): Number of repetitions
                
        Returns: 
            float: The percentage value estimated probability of winning.
        """
        wins = 0
        for _ in range(n):
            _, d = self.battle(a, d)
            if d == 0:
                wins += 1
        return round(wins / n * 100, 4)

    """
    The vectorized version tracks thousands of simulations at once with np arrays. 
    It is actually almost 100x slower than the simplified version but a useful demonstration nevertheless.
    
    def vector_estimate_win_prob(self, num_attackers, num_defenders, reps=1000):
        # Initialize arrays for attacker and defender troops across all simulations
        attackers = np.full(reps, num_attackers, dtype=np.int16)
        defenders = np.full(reps, num_defenders, dtype=np.int16)

        # Track which battles are still ongoing (both sides > 0)
        ongoing = (attackers > 0) & (defenders > 0)

        while np.any(ongoing):
            # For ongoing battles, determine dice counts
            atk_dice = np.minimum(3, attackers[ongoing])
            def_dice = np.minimum(2, defenders[ongoing])

            # Number of ongoing battles this round
            n_battles = atk_dice.size

            # Roll dice for attacker and defender in batch:
            # Create ragged arrays by rolling max dice and masking unused
            max_atk_dice = 3
            max_def_dice = 2

            # Roll attacker dice for all battles (shape: n_battles x max_atk_dice)
            att_rolls_all = np.random.randint(1, 7, size=(n_battles, max_atk_dice))
            # Mask rolls beyond atk_dice per battle by setting to zero
            for i, dice_count in enumerate(atk_dice):
                if dice_count < max_atk_dice:
                    att_rolls_all[i, dice_count:] = 0

            # Roll defender dice similarly
            def_rolls_all = np.random.randint(1, 7, size=(n_battles, max_def_dice))
            for i, dice_count in enumerate(def_dice):
                if dice_count < max_def_dice:
                    def_rolls_all[i, dice_count:] = 0

            # Extract only relevant dice per battle, sort descending ignoring zeros
            def sort_desc_ignore_zeros(arr, counts):
                # arr shape: (n_battles, max_dice)
                # counts: array of dice counts per battle
                sorted_arr = np.zeros_like(arr)
                for i in range(arr.shape[0]):
                    valid_rolls = arr[i, :counts[i]]
                    sorted_rolls = -np.sort(-valid_rolls)  # descending
                    sorted_arr[i, :counts[i]] = sorted_rolls
                return sorted_arr

            att_sorted = sort_desc_ignore_zeros(att_rolls_all, atk_dice)
            def_sorted = sort_desc_ignore_zeros(def_rolls_all, def_dice)

            # Compare dice pairs: min dice count per battle
            compare_counts = np.minimum(atk_dice, def_dice)

            # Compute losses per battle
            attacker_losses = np.zeros(n_battles, dtype=np.int16)
            defender_losses = np.zeros(n_battles, dtype=np.int16)

            for i in range(n_battles):
                for j in range(compare_counts[i]):
                    if att_sorted[i, j] > def_sorted[i, j]:
                        defender_losses[i] += 1
                    else:
                        attacker_losses[i] += 1

            # Update troop counts in original arrays
            attackers[ongoing] -= attacker_losses
            defenders[ongoing] -= defender_losses

            # Update ongoing mask
            ongoing = (attackers > 0) & (defenders > 0)

        # Count attacker wins where defender troops hit zero
        wins = np.sum(defenders == 0)

        return round(wins / reps * 100, 4)
    """

        

class BalancedBlitz(TrueRandom):
    """
    to be implemented
    """