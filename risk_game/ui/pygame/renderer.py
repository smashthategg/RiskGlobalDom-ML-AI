import pygame, json, random
from risk_game.ui.pygame.ui_components import *

class Renderer:
    """
    Attributes:
        territory_masks { # Stores masks for hit detection with cursor, but we already have such a system in place. This is probably redundant but it helps build territory_surfaces.
            name (str): mask (pygame.Mask)
        }
        territroy_surfaces { # Stores colored territory surfaces for display, accounting for all player colors.
            owner_index (int or "hover"): { # "hover" is just a semi-transparent white surface that we can add to highlight a territory the cursor is on.
                terr_name (str): surf (pygame.Surface)
            }
        } 
        territory_offsets { # Stores the positions of the territory masks and surfaces.
            name (str): xy-coordinate ((int, int))
        }
        assets { # Stores the filepaths of game assets, see config.py.
            name (str): filepath (str)
        }
        player_colors { # Stores the player colors}
        
    """
    def __init__(self, config, init):    
        self.init = init
        # We will build these in the constructor.
        self.territory_masks, self.territory_surfaces, self.territory_offsets = {}, {}, {}
        
        # Easy load from Config object
        self.assets, self.font = config.assets, config.font

        # Set player colors
        selected = random.sample(list(config.colors.values()), 6)
        self.player_colors = {i: color for i, color in enumerate(selected)}
        
        # Load UI component classes
        self.text = TextLabel()
        self.avatar = Avatar(pygame.image.load(config.assets["pfp"]).convert_alpha(),
                             pygame.image.load(config.assets["pfp_border"]).convert_alpha())
        self.buttons = {"mode": ToggleButton("Manual", "Auto", (80, 470))}

        self.auto = True

        # Load board and mask
        self.board = pygame.image.load(config.assets["board"]).convert_alpha()
        self.mask = pygame.image.load(config.assets["mask"]).convert_alpha()
        with open(self.assets["map"]) as f:
            self.territory_ui = json.load(f) 
        self.mask_color_map = {
            tuple(int(data["color"][i:i+2], 16) for i in (1, 3, 5)): territory # Color code is converted to RGB, mapped to each territory
            for territory, data in self.territory_ui.items()
        }

        # Generate masks for hit detection (cursor to each territory). This may not be needed.
        with open(config.assets["pixels"]) as f:
            self.territory_pixels = json.load(f)
        for territory, pixels in self.territory_pixels.items():
            xs = [x for x, _ in pixels]
            ys = [y for _, y in pixels]
            min_x, min_y, max_x, max_y = min(xs), min(ys), max(xs), max(ys)
            width, height = max_x - min_x + 1, max_y - min_y + 1
            mask = pygame.Mask((width,height))
            for x, y in pixels:
                mask.set_at((x - min_x, y - min_y), 1)
            self.territory_masks[territory] = mask
            self.territory_offsets[territory] = (min_x, min_y)

        # Generate colored surfaces for display (territory)
        for territory, mask in self.territory_masks.items():
            self.territory_surfaces[territory] = {}
            for owner_index, color in self.player_colors.items():
                surf = mask.to_surface(
                    setcolor=(*color, 180),
                    unsetcolor=(0, 0, 0, 0)
                )
                self.territory_surfaces[territory][owner_index] = surf
            surf = mask.to_surface(
                setcolor=(255,255,255,80),
                unsetcolor=(0,0,0,0)
            )
            self.territory_surfaces[territory]["hover"] = surf

    

    def draw_board(self, screen, ui_state=None):
        screen.fill((255, 255, 255))
        screen.blit(self.board, (0, 0))
    

        if ui_state:
            for terr_name, terr_data in ui_state["territories"].items():
                self.draw_territory(screen, terr_name, terr_data)
            if ui_state["highlights"]["selected"]:
                self.draw_hover(screen, ui_state["highlights"]["selected"]["territory"])
            if ui_state["highlights"]["target"]:
                self.draw_hover(screen, ui_state["highlights"]["target"]["territory"])
            arrow = pygame.image.load(self.assets["arrow"]).convert_alpha()
            y = 37 + 80*ui_state["current_player_index"]
            screen.blit(arrow, (670,y))

        if self.hovered_territory:
            self.draw_hover(screen, self.hovered_territory)

        for i in range(len(self.init["players"])):
            y = 50 + 80*i 
            self.avatar.draw(screen, color=self.player_colors[i], pos=(730,y))
        
        self.buttons["mode"].draw(screen)
        

    def draw_territory(self, screen, territory_name, terr_data):
        """Draws army count + ownership color on a territory"""
        if territory_name not in self.territory_ui:
            return

        label_pos = self.territory_ui[territory_name]["label_pos"]
        owner_index = terr_data.get("owner_index", None)

        # Draw colored territory mask
        if territory_name in self.territory_surfaces:
            surf = self.territory_surfaces[territory_name][owner_index]
            offset = self.territory_offsets[territory_name]
            screen.blit(surf, offset)

        # Draw armies number
        armies = terr_data.get("armies", 0)
        self.text.draw(screen, str(armies), label_pos)

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
            screen.blit(self.territory_surfaces[territory_name]["hover"], self.territory_offsets[territory_name])

        # Draw territory name just below the label position
        if territory_name in self.territory_ui:
            label_pos = self.territory_ui[territory_name]["label_pos"].copy()
            label_pos[1] = label_pos[1] + 20
            
            self.text.draw(screen, territory_name, label_pos)

    def check_clicked_buttons(self, event): 
        mode = self.buttons["mode"]
        if mode.handle_event(event):
            self.auto = False if mode.state else True