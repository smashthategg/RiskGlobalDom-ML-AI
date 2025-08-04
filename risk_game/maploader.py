"""
maploader.py

Module responsible for loading the map data for a RISK game from a JSON file.

Functions:
    load_map(path): Loads and returns Territory and Continent objects from the given JSON file.
"""

import json
from structures import Territory, Continent

def load_map(path):
    """
    Loads map data from a JSON file and constructs Territory and Continent objects.

    The JSON file is expected to have the following structure:
    {
        "territories": {
            "TerritoryName": {
                "continent": "ContinentName",
                "neighbors": ["Neighbor1", "Neighbor2", ...]
            },
            ...
        },
        "continents": {
            "ContinentName": {
                "bonus": int,
                "territories": ["Territory1", "Territory2", ...]
            },
            ...
        }
    }

    Args:
        path (str): The file path to the JSON map data.

    Returns:
        tuple: (territories, continents)
            - territories (list[Territory]): List of Territory objects with neighbor references.
            - continents (list[Continent]): List of Continent objects with linked territories.
    """

    with open(path, "r") as f:
        map_data = json.load(f)

    territory_data = map_data["territories"]
    continent_data = map_data["continents"]

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

    # Step 3: Create Continent objects with references to Territory objects
    continents = {}
    for name, info in continent_data.items():
        continent_territories = [territories[t_name] for t_name in info["territories"]]
        continents[name] = Continent(
            name=name,
            bonus=info["bonus"],
            territories=continent_territories
        )

    return list(territories.values()), list(continents.values())
