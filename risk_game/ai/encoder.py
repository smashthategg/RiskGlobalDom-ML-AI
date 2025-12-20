"""
encoder.py

For reinforcement learning on NumPy we need to convert territory/continent id's to integers.
We also want an adjacency array (graph of connected territories) to set up the environment.
"""
import numpy as np
import json

class GameSchema:
    """
    Docstring for GameSchema
    
    Static info of map topology for encoders. Called once per game.
    """
    def __init__(self, map_data):
        self.terr_id = self._encode_ids(map_data["territories"].keys())
        self.cont_id = self._encode_ids(map_data["continents"].keys())
        self.id_terr = {v: k for k, v in self.terr_id.items()}
        self.adj = self._build_adjacency(map_data["territories"])

    def _encode_ids(self, names):
        return {name: i for i, name in enumerate(names)}

    def _build_adjacency(self, terr_data):
        N = len(self.terr_id)
        adj = np.zeros((N, N), dtype=np.int8)
        for t, info in terr_data.items():
            i = self.terr_id[t]
            for n in info["neighbors"]:
                j = self.terr_id[n]
                adj[i, j] = 1
        return adj


class StateEncoder():
    def __init__(self, schema, history_length=0):
        """
        Docstring for __init__
        
        :param map_data: dictionary of territory/continents (indexed by String name, not object references)

        On initialization we want to create and store the integer encoding & adjacency matrix (this is static).
        We will regularly update the rest via the game state.
        """
        self.history_length = history_length
        self.schema = schema

    def encode(self, state):
        """
        Encode the current GameState into RL-friendly numeric arrays.

        Args:
            game_state (GameState): The serialized game state snapshot.
            history_length (int): Number of previous turns to store per player.

        Returns:
            dict: Contains numeric representations:
                - 'territories': np.ndarray, shape (num_territories, 3) -> [owner_id, armies, continent_id]
                - 'adjacency': np.ndarray, shape (num_territories, num_territories)
                - 'players': np.ndarray, shape (num_players, 4) -> [total_armies, num_territories, num_continents, num_cards]
                - 'current_player': int
                - 'draft_bonus': int
                - 'card_bonus': int
                - 'history': np.ndarray, shape (num_players, history_length, 5) if include_history
        """
         # --- 1. Territories ---
        territories_array = []
        for _, t_info in state["territories"].items():
            territories_array.append([
                t_info["owner_index"],
                t_info["armies"],
            ])
        territories_array = np.array(territories_array, dtype=np.int32)

        # --- 2. Player summary ---
        players_array = []
        for p_info in state["players"]:
            players_array.append( [
                p_info["armies"],  # total armies
                p_info["territories"],
                p_info["cards"]
            ] )
        players_array = np.array(players_array, dtype=np.int32)

        # --- 3. Singular info ---
        current_player = state["current_player_index"]
        draft_bonus = state.get("draft_bonus", 0)
        card_bonus = state.get("card_bonus", 0)   
        continents = [i for i in state["continent_ownership"].values()]
        
        
        # --- 4. Optional historical info ---
        history_array = None
        if self.history_length:
            # Initialize with zeros: shape (num_players, history_length, 5)
            # Columns: [action_type, from_territory, to_territory, armies, target_owner]
            history_array = np.zeros((len(state["players"]), self.history_length, 5), dtype=np.int32)
            # For now, leave it zero-filled. You can update per action when logging.
            # action_type: 0=draft,1=attack,2=fortify (example)
            # from_territory / to_territory: use territory_index_map
            # armies: number of armies moved/lost
            # target_owner: owner id of target territory (if applicable)

        return {
            "territories": territories_array,
            "adjacency": self.schema.adj,
            "players": players_array,
            "current_player": current_player,
            "draft_bonus": draft_bonus,
            "card_bonus": card_bonus,
            "continents": continents,
            "history": history_array
        }
    
class ActionEncoder:
    """
    Encodes actions for RISK into RL-friendly numeric form.

    Supports:
        - Draft
        - Attack
        - Fortify
    """

    def __init__(self, game):
        """
        Args:
            game (Game): The Game instance (with self.state)
        """
        self.game = game
        self.territory_index = {t.name: i for i, t in enumerate(game.state.territories)}
        self.num_territories = len(game.state.territories)
        self.num_players = len(game.state.players)

    # -------------------
    # Phase-specific masks
    # -------------------
    def draft_mask(self):
        """Returns a boolean mask of length num_territories: True if draft allowed on that territory."""
        mask = np.zeros(self.num_territories, dtype=bool)
        current_player = self.game.state.current_player()
        for i, t in enumerate(self.game.state.territories):
            if t.owner == current_player:
                mask[i] = True
        return mask

    def attack_mask(self):
        """Returns a boolean mask shape (num_territories, num_territories): True if legal attack from i->j"""
        mask = np.zeros((self.num_territories, self.num_territories), dtype=bool)
        current_player = self.game.state.current_player()
        for i, t_from in enumerate(self.game.state.territories):
            if t_from.owner != current_player or t_from.armies <= 1:
                continue
            for t_to in t_from.neighbors:
                j = self.territory_index[t_to.name]
                if t_to.owner != current_player:
                    mask[i, j] = True
        return mask

    def fortify_mask(self):
        """Returns a boolean mask shape (num_territories, num_territories): True if legal fortify from i->j"""
        mask = np.zeros((self.num_territories, self.num_territories), dtype=bool)
        current_player = self.game.state.current_player()
        for i, t_from in enumerate(self.game.state.territories):
            if t_from.owner != current_player or t_from.armies <= 1:
                continue
            for t_to in t_from.neighbors:
                j = self.territory_index[t_to.name]
                if t_to.owner == current_player:
                    mask[i, j] = True
        return mask

    # -------------------
    # Flattened masks for RL agents
    # -------------------
    def flatten_mask(self, mask):
        """Flattens 2D mask into 1D"""
        return mask.flatten()

    def get_action_space(self, phase):
        """
        Returns the legal actions for the given phase.

        Args:
            phase (str): 'draft', 'attack', or 'fortify'

        Returns:
            dict:
                - 'mask': flattened legal actions (1D boolean array)
                - 'mapping': list of tuples mapping flattened index -> action params
        """
        mapping = []

        if phase == "draft":
            mask = self.draft_mask()
            flat_mask = mask
            for i, allowed in enumerate(mask):
                mapping.append(('draft', i, None))
        elif phase == "attack":
            mask = self.attack_mask()
            flat_mask = self.flatten_mask(mask)
            for i in range(self.num_territories):
                for j in range(self.num_territories):
                    mapping.append(('attack', i, j))
        elif phase == "fortify":
            mask = self.fortify_mask()
            flat_mask = self.flatten_mask(mask)
            for i in range(self.num_territories):
                for j in range(self.num_territories):
                    mapping.append(('fortify', i, j))
        else:
            raise ValueError("Phase must be 'draft', 'attack', or 'fortify'")

        return {
            "mask": flat_mask,
            "mapping": mapping
        }