"""
probability_table_generator.py

Generates and saves a probability lookup table for RISK battles.

- Uses Monte Carlo simulations (see ./notes/RISK_probability.ipynb for detailed explanation)
- Fills a 2D NumPy array with estimated win probabilities, indexed by attackers (rows) and defenders (columns).
- Saves table to disk after each new computation for resumable progress.
"""

import numpy as np
import os
from combat import battle

def estimate_win_probability(a, d, n):
    """
    Estimates the likelihood of winning an attack via Monte Carlo. Runs `battle()` for n repetitions, recording each simulated win.
    The probability estimate is equal to (# of wins / # of total reps).

    Args:
        a (int): Number of attackers
        d (int): Number of defenders
        n (int): Number of repetitions
            
    Returns: 
        float: The percentage value estimated probability of winning.
    """
    wins = 0
    for _ in range(n):
        _, defenders = battle(a, d)
        if defenders == 0:
            wins += 1
    return wins / n

def final_estimate_win_probability(a, d, verbose=False):
    p0 = estimate_win_probability(a, d, 400)
    if p0 < 0.48:
        p0 = p0 + 0.02
    elif p0 > 0.52:
        p0 = p0 - 0.02
    else:
        p0 = 0.5
    n = int(154000 * p0 * (1 - p0))
    if verbose:
        print(f"Pilot p estimate: {round(p0, 4)}, n = {n}")
    p = round(estimate_win_probability(a, d, n), 4)
    if verbose:
        print(f"0.5% error estimate for win probability: \nFor {a+1} attackers vs. {d} defenders: {p}%")
    return p

MAX_ATTACKERS = 1000
MAX_DEFENDERS = 1000
TABLE_FILE = "probability_table.npy"

def load_or_create_table():
    """
    Load an existing probability table from disk or create a new one.

    If `TABLE_FILE` exists, loads the NumPy array from disk.
    Otherwise, creates a new table filled with NaN to indicate 
    uncomputed entries.

    Returns:
        np.ndarray: 2D NumPy array of shape (MAX_ATTACKERS + 1, MAX_DEFENDERS + 1) with dtype float32.
                    Entries contain probabilities in percent, or NaN if not yet computed.
    """

    if os.path.exists(TABLE_FILE):
        table = np.load(TABLE_FILE)
        print("Loaded existing probability table.")
    else:
        # Use NaN to mark "uncomputed"
        table = np.full((MAX_ATTACKERS + 1, MAX_DEFENDERS + 1), np.nan, dtype=np.float32)
        print("Created new probability table.")
    return table

def save_table(table):
    """
    Save the probability table to disk as a `.npy` file.

    Args:
        table (np.ndarray): The probability table to save.
    """
    np.save(TABLE_FILE, table)
    print("Table saved.")

# ---- Main loop ----
table = load_or_create_table()

total_cells = MAX_ATTACKERS * MAX_DEFENDERS
cells_done = np.count_nonzero(~np.isnan(table))

for a in range(1, MAX_ATTACKERS + 1):
    for d in range(1, MAX_DEFENDERS + 1):
        if np.isnan(table[a, d]):  # Only compute missing entries
            p = final_estimate_win_probability(a, d)
            table[a, d] = p
            cells_done += 1
            progress = cells_done / total_cells * 100
            print(f"[{cells_done}/{total_cells} | {progress:.2f}%] "
                  f"Computed: attackers={a}, defenders={d}, win={p*100:.2f}%")
            save_table(table)  # Save after each computation

            # Optimization: if win% = 0, skip rest of row

            if p == 0.0:
                table[a, d+1:] = 0.0
                cells_done += (MAX_DEFENDERS - d)
                break


