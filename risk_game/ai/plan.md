We create a smaller map to train bots on. See `/maps/small.json`

Let (ABC) be a continent +3 bonus.
Let (DEF) be a continent +4 bonus.
Let (GHIJ) be a continent +5 bonus.

A -- B -- C
     |     \
D -- E ---- F
|            \  
G -- H -- I - J

DONE!


### The Loop

1. Using listeners, game states are sent to the encoder (non-serialized)
2. The encoded state is sent to the agent
3. The agent outputs action indices (TO-DO)
4. Send back to game, game updates game state.

