import pygame

pygame.font.init()

class TextLabel:
    def __init__(self):
        self.offsets = [(-1,-1), (-1,1), (1,-1), (1,1)] # shadows

    def draw(self, screen, text, pos, color=(255,255,255), font=pygame.font.SysFont(None, 22), shadow=True, align="center"):
        # Render shadow layers
        for ox, oy in self.offsets:
            shadow_surf = font.render(text, True, (0,0,0))
            rect = shadow_surf.get_rect(**{align: (pos[0] + ox, pos[1] + oy)})
            screen.blit(shadow_surf, rect)

        # Render main text
        text_surf = font.render(text, True, color)
        rect = text_surf.get_rect(**{align: pos})
        screen.blit(text_surf, rect)

class Avatar:
    def __init__(self, avatar, border, padding_frac=0.12):
        self.avatar = avatar # should be loaded pygame image type
        self.border = border
        self.padding_frac = padding_frac

    def draw(self, screen, color, pos):
            w, h = self.border.get_size()

            colored_border = self.replace_color(self.border, color)
            rect = colored_border.get_rect(center=pos)

            # 1. draw colored border background (outline + color fill)
            screen.blit(colored_border, rect)

            # 2. scale avatar image and draw avatar
            pad = int(min(w, h) * self.padding_frac)
            avatar_w = max(1, w - 2 * pad)
            avatar_h = max(1, h - 2 * pad)
            avatar_scaled = pygame.transform.smoothscale(self.avatar, (avatar_w, avatar_h))
            avatar_rect = avatar_scaled.get_rect()
            avatar_rect.center = rect.center

            screen.blit(avatar_scaled, avatar_rect)

    def replace_color(self, surface, new_color, old_color=(255,255,255)):
        """Return a copy of surface where white pixels are replaced by color."""
        new_surf = surface.copy()

        # lock pixels
        px = pygame.PixelArray(new_surf)
        old = new_surf.map_rgb(old_color)
        px.replace(old, new_surf.map_rgb((*new_color, 255)))

        del px  # unlock

        return new_surf

class Button:
    def __init__(self, text, pos, size=(150, 50), 
                 font=pygame.font.SysFont(None, 28),
                 bg_color=(0, 100, 200), hover_color=(0, 128, 255), text_color=(255, 255, 255)):
        self.text = text
        self.pos = pos  # (x, y) center position
        self.size = size
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = pos
        self.text_label = TextLabel()

    def draw(self, screen):
        # Check if hovering
        mouse_pos = pygame.mouse.get_pos()
        hovering = self.rect.collidepoint(mouse_pos)
        color = self.hover_color if hovering else self.bg_color

        # Draw button rectangle
        pygame.draw.rect(screen, color, self.rect, border_radius=8)

        # Draw button text centered
        self.text_label.draw(screen, self.text, self.rect.center, self.text_color, self.font, shadow=True)

    def is_clicked(self, event):
        """Returns True if left mouse button clicked on this button."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class ToggleButton(Button):
    def __init__(self, text_off, text_on, pos, size=(150, 50), 
                 font=pygame.font.SysFont(None, 28),
                 bg_color=(0, 100, 200), hover_color=(0, 128, 255), 
                 bg_color2=(0, 200, 100), hover_color2=(0, 255, 128),
                 text_color=(255, 255, 255)):
        # Start with the "off" text
        super().__init__(text_off, pos, size, font, bg_color, hover_color, text_color)
        self.on_states = (text_on, bg_color2, hover_color2)
        self.off_states = (text_off, bg_color, hover_color)
        self.state = False  # False = off, True = on

    def draw(self, screen):
        # Override the text based on state
        self.text, self.bg_color, self.hover_color = self.on_states if self.state else self.off_states
        super().draw(screen)

    def handle_event(self, event):
        """Toggle state when clicked. Returns True if state changed."""
        if self.is_clicked(event):
            self.state = not self.state
            return True
        return False
