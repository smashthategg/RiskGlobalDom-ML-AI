import pygame
import json

class Renderer:
    def __init__(self, assets):
        self.territory_masks = {}
        self.assets = assets

        # Load board and mask
        self.board = pygame.image.load(self.assets["board"]).convert_alpha()
        self.mask = pygame.image.load(self.assets["mask"]).convert_alpha()

        # Load territory UI data (color + label positions)
        with open(self.assets["map"]) as f:
            self.territory_ui = json.load(f)

        # Map mask color -> territory name
        self.mask_color_map = {
            tuple(int(data["color"][i:i+2], 16) for i in (1, 3, 5)): territory
            for territory, data in self.territory_ui.items()
        }

        self.font = pygame.font.SysFont(None, 22)

        # Generate highlight surfaces
        with open(self.assets["pixels"]) as f:
            territory_pixels = json.load(f)

        self.territory_masks = {}
        for territory, pixels in territory_pixels.items():
            surf = pygame.Surface((800, 500), pygame.SRCALPHA)
            for x, y in pixels:
                surf.set_at((x, y), (255, 255, 255, 50))  # highlight alpha
            self.territory_masks[territory] = surf


    def draw_board(self, screen):
        screen.fill((255, 255, 255))
        screen.blit(self.board, (0, 0))

        if self.hovered_territory:
            self.draw_hover(screen, self.hovered_territory)

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
            label_pos = self.territory_ui[territory_name]["label_pos"]
            text = territory_name
            font = self.font

            # Offsets for shadow
            shadow_offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for ox, oy in shadow_offsets:
                shadow_surf = font.render(text, True, (0, 0, 0))  # black shadow
                shadow_rect = shadow_surf.get_rect(midtop=(label_pos[0] + ox, label_pos[1] + 5 + oy))
                screen.blit(shadow_surf, shadow_rect)

            # Main white text
            text_surf = font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(midtop=(label_pos[0], label_pos[1] + 5))
            screen.blit(text_surf, text_rect)

