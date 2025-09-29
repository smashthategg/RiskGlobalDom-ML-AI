# main.py
import pygame
from risk_game.ui.pygame.config import Config
from risk_game.ui.pygame.game_loop import run_replay
from risk_game.ui.pygame.state_adapter import StateAdapter
from risk_game.ui.pygame.renderer import Renderer
from risk_game.engine.main import create_game, play_game




def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 500))
    config = Config()
    pygame.display.set_caption("RISK Simulation Demo")


    # --- Simulation start and storage of replay view ---
    game = create_game()
    adapter = StateAdapter()
    game.add_listener(adapter.ui_listener)
    play_game(game)

    # --- Renderer ---
    init = adapter.history[0] 
    renderer = Renderer(config, init)

    # --- Run the loop ---
    run_replay(screen, adapter, renderer)

    pygame.quit()

if __name__ == "__main__":
    main()