# main.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS
from game_loop import run_game

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini Risk Demo")
run_game(screen, ASSETS)
pygame.quit()
