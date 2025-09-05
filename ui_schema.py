import json

ui_state = {
    "players": [
        {"name": "Alice", "cards": 1, "armies": 30, "territories": 7},
        {"name": "Bob", "cards": 2, "armies": 25, "territories": 6},
        # ... all other players
    ],
    "territories": {
        "Alaska": {
            "owner_index": 0,  # index into players list
            "armies": 3        # number of troops stationed
        },
        "Northwest Territory": {
            "owner_index": 1,
            "armies": 2
        },
        # ... all other territories
    },
    "continent_ownership": {
        "North America": 0,
        "South America": 1,
        # ...
    },
    "highlights": {
        "selected": {
            "territory": "Alaska", # can be none
            "change": 3 # 0 if no change, negative if a battle loss
        },
        "target": {
            "territory": "Northwest Territory", # destination for attack/fortify. can be None
            "change": 2
        } 
    },
    "current_player_index": 0,
    "current_player_bonus": 4,
    "card_bonus": 12,
    "phase": "draft"  # or "attack", "fortify"

}

print(json.dumps(ui_state))