import json
from structures import Territory, Continent

def load_map(path): 
    with open(path, "r") as f:
        map_data = json.load(f)

    territory_data = map_data["territories"]
    continent_data = map_data["continents"]

    # Step 1: Create Territory objects (neighbors as names for now)
    territories = {}
    for name, info in territory_data.items():
        territories[name] = Territory(name=name, continent=info["continent"], neighbors=info["neighbors"])

    # Step 2: Replace neighbor names with Territory objects
    for territory in territories.values():
        territory.neighbors = [territories[n_name] for n_name in territory.neighbors]

    # Step 3: Create Continent objects with Territory references
    continents = {}
    for name, info in continent_data.items():
        continent_territories = [territories[t_name] for t_name in info["territories"]]
        continents[name] = Continent(name=name, bonus=info["bonus"], territories=continent_territories)

    return list(territories.values()), list(continents.values())
