# input_handler.py

def get_territory_from_click(mask_surface, pos, mask_color_map):
    color = mask_surface.get_at(pos)[:3]  # ignore alpha
    return mask_color_map.get(color)
