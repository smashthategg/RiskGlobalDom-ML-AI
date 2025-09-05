import pygame
import json

class Renderer:
    def __init__(self, config):
        self.territory_masks = {}
        self.assets = config.assets
        self.player_colors = config.player_colors
        self.font = config.font

        # Load board and mask
        self.board = pygame.image.load(config.assets["board"]).convert_alpha()
        self.mask = pygame.image.load(config.assets["mask"]).convert_alpha()
        with open(self.assets["map"]) as f:
            self.territory_ui = json.load(f)
        self.mask_color_map = {
            tuple(int(data["color"][i:i+2], 16) for i in (1, 3, 5)): territory
            for territory, data in self.territory_ui.items()
        }

        # Generate highlight surfaces
        with open(config.assets["pixels"]) as f:
            self.territory_pixels = json.load(f)
        self.territory_masks = {}
        for territory, pixels in self.territory_pixels.items():
            surf = pygame.Surface((800, 500), pygame.SRCALPHA)
            for x, y in pixels:
                surf.set_at((x, y), (255, 255, 255, 50))  # highlight alpha
            self.territory_masks[territory] = surf


    def draw_board(self, screen, ui_state=None):
        screen.fill((255, 255, 255))
        screen.blit(self.board, (0, 0))

        if ui_state:
            for terr_name, terr_data in ui_state["territories"].items():
                self.draw_territory(screen, terr_name, terr_data)

        if self.hovered_territory:
            self.draw_hover(screen, self.hovered_territory)

    def draw_territory(self, screen, territory_name, terr_data):
        """Draws army count + ownership color on a territory"""
        if territory_name not in self.territory_ui:
            return

        label_pos = self.territory_ui[territory_name]["label_pos"]

        # Territory color by owner
        owner_index = terr_data.get("owner_index", None)
        color = self.player_colors.get(owner_index, (169, 169, 169))

        # Draw colored territory mask
        if territory_name in self.territory_masks:
            mask = self.territory_masks[territory_name].copy()
            for x, y in self.territory_pixels[territory_name]:
                mask.set_at((x, y), (*color, 180))  # fully opaque color for just the territory
            screen.blit(mask, (0, 0))

        # Draw armies number
        armies = terr_data.get("armies", 0)
        self.draw_text(screen, str(armies), label_pos)

    def get_territory_at(self, x, y):
        if x < 0 or y < 0 or x >= self.mask.get_width() or y >= self.mask.get_height():
            return None
        color = self.mask.get_at((x, y))[:3]
        return self.mask_color_map.get(color, None)
    
    def update_hover(self, pos):
        """Call every frame with current mouse position"""
        x, y = pos
        self.hovered_territory = self.get_territory_at(x,y)

    def draw_hover(self, screen, territory_name):
        # Blit the precomputed overlay
        if territory_name in self.territory_masks:
            screen.blit(self.territory_masks[territory_name], (0, 0))

        # Draw territory name just below the label position
        if territory_name in self.territory_ui:
            label_pos = self.territory_ui[territory_name]["label_pos"].copy()
            label_pos[1] = label_pos[1] + 20
            
            self.draw_text(screen, territory_name, label_pos)

    def draw_text(self, screen, text, pos, color=(255,255,255), font=None, shadow=True):
        """Draw text at a certain place. Options for color, font, shadowing."""
        if font is None:
            font = self.font
        if shadow:
            shadow_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for ox, oy in shadow_offsets:
                shadow_surf = font.render(text, True, (0, 0, 0))  # black shadow
                shadow_rect = shadow_surf.get_rect(center=(pos[0] + ox, pos[1] + oy))
                screen.blit(shadow_surf, shadow_rect)

        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=pos)
        screen.blit(text_surf, text_rect)