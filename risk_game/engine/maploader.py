"""
maploader.py

Module responsible for loading the map data for a RISK game from a JSON file.

Functions:
    load_map(path): Loads and returns dictionary from the given JSON file.
    build_map_objects(territory_data, continent_data): Converts raw dictionary (String) to Territory/Continent objects
"""

import json, os
from risk_game.engine.structures import Territory, Continent

def load_map_json(path):
    """
    Loads JSON map data and returns raw dictionaries for territories and continents.

    Args:
        path (str): File path relative to this script.

    Returns:
        map_data (dict): {"territories": {...} , "continents": {...} }
    """
    base_dir = os.path.dirname(__file__)
    full_path = os.path.join(base_dir, path)
    with open(full_path, "r") as f:
        map_data = json.load(f)

    return map_data


def build_map_objects(map_data):
    """
    Converts raw map dictionaries into Territory and Continent objects with proper references.

    Args:
        map_data (dict): from load_map()

    Returns:
        tuple: (territories, continents)
            - territories (list of Territory)
            - continents (list of Continent)
    """
    territory_data, continent_data = map_data["territories"], map_data["continents"]

    # Step 1: Create Territory objects with neighbor names (temporarily)
    territories = {}
    for name, info in territory_data.items():
        territories[name] = Territory(
            name=name,
            continent=info["continent"],
            neighbors=info["neighbors"]
        )

    # Step 2: Replace neighbor names with references to Territory objects
    for territory in territories.values():
        territory.neighbors = [territories[n_name] for n_name in territory.neighbors]

    # Step 3: Create Continent objects
    continents = {}
    for name, info in continent_data.items():
        continent_territories = [territories[t_name] for t_name in info["territories"]]
        continents[name] = Continent(
            name=name,
            bonus=info["bonus"],
            territories=continent_territories
        )

    return list(territories.values()), list(continents.values())

