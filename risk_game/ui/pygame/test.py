import pygame
import json
from config import *

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Load mask
mask = pygame.image.load(ASSETS["mask"]).convert_alpha()
width, height = mask.get_size()

territory_colors = json.load(open(ASSETS["map"]))

territory_pixels = {}

for territory, data in territory_colors.items():
    mask_color = tuple(int(data["color"][i:i+2], 16) for i in (1, 3, 5))
    pixels = []
    for x in range(width):
        for y in range(height):
            if mask.get_at((x, y))[:3] == mask_color:
                pixels.append((x, y))
    territory_pixels[territory] = pixels

# Save the pixel coordinates to JSON
with open("territory_pixels.json", "w") as f:
    json.dump(territory_pixels, f)
