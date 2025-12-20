# config.py
import pygame

class Config:
    def __init__(self):
        self.colors = {
            "red": (220, 20, 60),
            "orange": (255, 140, 0),
            "yellow": (200, 180, 0),
            "green": (144, 238, 144),
            "blue": (173, 216, 230),
            "purple": (138, 43, 226),
            "magenta": (255, 0, 255),
            "white": (230, 230, 230),
        }
        self.assets = {
            "board": "risk_game/ui/assets/classic_map/outline.png",
            "mask": "risk_game/ui/assets/classic_map/mask.png",
            "map": "risk_game/ui/assets/classic_map/territory_ui.json",
            "pixels": "risk_game/ui/assets/classic_map/territory_pixels.json",
            "arrow": "risk_game/ui/assets/images/arrow.png",
            "pfp": "risk_game/ui/assets/images/bot_avatar.png",
            "pfp_border": "risk_game/ui/assets/images/profile.png",
            "tooltip": "risk_game/ui/assets/images/tooltip.png"
        }
        self.font = pygame.font.SysFont(None, 22)