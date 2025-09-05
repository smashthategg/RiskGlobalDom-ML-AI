"""
state_adapter.py

"""

class StateAdapter:
    """
    Attributes:
        history (list of dict): Stores previous instances of state.
        state (dict): Optional snapshot of most recent data.
    """
    def __init__(self):
        self.history = []
        self.state = None

    def ui_listener(self, state):
        """Gets the serialized dict game state and adds it to event log."""
        self.history.append(state)
        self.state = state

    def register_listeners(self, game):
        """Adds ui_listener to Game object."""
        game.add_listener(self.ui_listener)

