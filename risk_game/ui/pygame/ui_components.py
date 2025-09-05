import pygame

class TextLabel:
    def __init__(self):
        self.offsets = [(-1,-1), (-1,1), (1,-1), (1,1)] # shadows

    def draw(self, screen, text, pos, color, align="center"):
        # Render shadow layers
        for ox, oy in self.offsets:
            shadow_surf = self.font.render(text, True, self.shadow_color)
            rect = shadow_surf.get_rect(**{align: (pos[0] + ox, pos[1] + oy)})
            screen.blit(shadow_surf, rect)

        # Render main text
        text_surf = self.font.render(text, True, color)
        rect = text_surf.get_rect(**{align: pos})
        screen.blit(text_surf, rect)
