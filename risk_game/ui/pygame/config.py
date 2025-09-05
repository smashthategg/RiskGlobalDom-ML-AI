# config.py
import pygame

class Config:
    def __init__(self):
        self.player_colors = {
            0: (255, 0, 0),   
            1: (255, 128, 0),   
            2: (255, 255, 0),
            3: (0, 255, 0),
            4: (0, 128, 255),
            5: (128, 0, 255)
        }
        self.assets = {
            "board": "risk_game/ui/assets/classic_map/outline.png",
            "mask": "risk_game/ui/assets/classic_map/mask.png",
            "map": "risk_game/ui/assets/classic_map/territory_ui.json",
            "pixels": "risk_game/ui/assets/classic_map/territory_pixels.json",
        }
        self.font = pygame.font.SysFont(None, 22)