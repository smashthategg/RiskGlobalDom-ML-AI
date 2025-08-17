# game_loop.py
import pygame
from renderer import Renderer
from input_handler import get_territory_from_click

def run_game(screen, assets):
    renderer = Renderer(assets)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                territory = renderer.get_territory_at(x, y)
                if territory:
                    print("Clicked territory:", territory)

        renderer.update_hover(pygame.mouse.get_pos())
        renderer.draw_board(screen)
        pygame.display.flip()
        clock.tick(60)
