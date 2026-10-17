"""
Pixel art palettes, procedural sprite generators, and character rendering.
Strict 16-color aesthetic with detailed pixel-level character drawing.
"""

import math
import pygame
from typing import Dict, List, Tuple

# Strict 16-color curated pixel palette
PALETTE = {
    "black": (16, 16, 26),
    "dark_navy": (34, 32, 52),
    "slate_blue": (63, 63, 116),
    "soft_blue": (91, 110, 225),
    "grass_green": (99, 171, 63),
    "dark_green": (50, 115, 69),
    "ruby_red": (172, 50, 50),
    "rose_pink": (217, 87, 99),
    "lilac": (215, 123, 186),
    "dark_brown": (102, 57, 49),
    "warm_brown": (143, 86, 59),
    "ember_orange": (223, 113, 38),
    "gold": (251, 242, 54),
    "peach": (238, 195, 154),
    "iron_grey": (155, 173, 183),
    "white": (245, 245, 255),
}

# Color options for Character Customization
HAIR_COLOR_DATA = [
    {"name": "Chestnut", "color": (143, 86, 59)},
    {"name": "Raven Black", "color": (24, 24, 34)},
    {"name": "Golden Blonde", "color": (251, 242, 54)},
    {"name": "Auburn Red", "color": (172, 50, 50)},
    {"name": "Cerulean", "color": (91, 110, 225)},
    {"name": "Forest Green", "color": (99, 171, 63)},
    {"name": "Mystic Lilac", "color": (215, 123, 186)},
    {"name": "Silver White", "color": (220, 225, 235)},
]

SKIN_TONE_DATA = [
    {"name": "Fair", "color": (248, 218, 188)},
    {"name": "Peach", "color": (238, 195, 154)},
    {"name": "Warm Tan", "color": (216, 164, 120)},
    {"name": "Olive", "color": (182, 126, 88)},
    {"name": "Bronze", "color": (140, 88, 56)},
    {"name": "Espresso", "color": (88, 52, 36)},
]

OUTFIT_COLOR_DATA = [
    {"name": "Crimson", "color": (172, 50, 50)},
    {"name": "Cobalt Blue", "color": (91, 110, 225)},
    {"name": "Emerald", "color": (99, 171, 63)},
    {"name": "Ochre", "color": (223, 113, 38)},
    {"name": "Royal Purple", "color": (215, 123, 186)},
    {"name": "Leather", "color": (143, 86, 59)},
    {"name": "Slate", "color": (63, 63, 116)},
    {"name": "Pure White", "color": (220, 225, 235)},
]

HAIR_COLORS = [d["color"] for d in HAIR_COLOR_DATA]
SKIN_TONES = [d["color"] for d in SKIN_TONE_DATA]
OUTFIT_COLORS = [d["color"] for d in OUTFIT_COLOR_DATA]

HAIRSTYLES = [
    {"name": "Adventurer", "id": 0},
    {"name": "Spiky", "id": 1},
    {"name": "Explorer (Long)", "id": 2},
    {"name": "Mohawk", "id": 3},
    {"name": "Ponytail", "id": 4},
    {"name": "Short Crop", "id": 5},
]


def draw_pixel_character(
    surface: pygame.Surface,
    x: int,
    y: int,
    scale: int = 1,
    hair_style: int = 0,
    hair_color: Tuple[int, int, int] = HAIR_COLORS[0],
    skin_tone: Tuple[int, int, int] = SKIN_TONES[1],
    shirt_color: Tuple[int, int, int] = OUTFIT_COLORS[1],
    pants_color: Tuple[int, int, int] = OUTFIT_COLORS[6],
    frame: int = 0,
):
    """
    Renders an authentic 14x24 pixel-art Terraria-style humanoid character.
    Includes hair shading, eye reflections, collar, belt, boots, and breathing bob.
    """
    # 1px vertical breathing offset on frame 1
    bob = 1 if frame == 1 else 0

    # Shading helpers
    def shade(color, mult=0.75):
        return (int(color[0] * mult), int(color[1] * mult), int(color[2] * mult))

    def tint(color, mult=1.25):
        return (min(255, int(color[0] * mult)), min(255, int(color[1] * mult)), min(255, int(color[2] * mult)))

    skin_dark = shade(skin_tone, 0.78)
    shirt_dark = shade(shirt_color, 0.72)
    pants_dark = shade(pants_color, 0.70)
    hair_dark = shade(hair_color, 0.65)
    hair_light = tint(hair_color, 1.2)

    # Base grid surface (16 x 26 pixels)
    char_surf = pygame.Surface((16, 26), pygame.SRCALPHA)

    # 1. HEAD & NECK
    head_y = 4 + bob
    # Head block (10x8)
    pygame.draw.rect(char_surf, skin_tone, (3, head_y, 10, 8))
    # Head shadow/jaw
    pygame.draw.rect(char_surf, skin_dark, (4, head_y + 7, 8, 1))
    # Neck (4x2)
    pygame.draw.rect(char_surf, skin_dark, (6, head_y + 8, 4, 2))

    # Eyes (Terraria style: 2x2 with dark pupil + white glint)
    pygame.draw.rect(char_surf, (20, 20, 30), (5, head_y + 3, 2, 2))
    pygame.draw.rect(char_surf, (255, 255, 255), (5, head_y + 3, 1, 1))
    pygame.draw.rect(char_surf, (20, 20, 30), (9, head_y + 3, 2, 2))
    pygame.draw.rect(char_surf, (255, 255, 255), (9, head_y + 3, 1, 1))

    # 2. HAIRSTYLE
    hy = head_y
    if hair_style == 0:  # Adventurer (Full mop with fringe)
        pygame.draw.rect(char_surf, hair_color, (2, hy - 3, 12, 4))
        pygame.draw.rect(char_surf, hair_light, (4, hy - 3, 6, 2))
        pygame.draw.rect(char_surf, hair_color, (2, hy, 2, 5))
        pygame.draw.rect(char_surf, hair_color, (12, hy, 2, 5))
        pygame.draw.rect(char_surf, hair_dark, (4, hy + 1, 3, 2))
        pygame.draw.rect(char_surf, hair_dark, (8, hy + 1, 3, 1))
    elif hair_style == 1:  # Spiky
        pygame.draw.rect(char_surf, hair_color, (3, hy - 2, 10, 3))
        pygame.draw.rect(char_surf, hair_light, (4, hy - 4, 3, 3))
        pygame.draw.rect(char_surf, hair_light, (9, hy - 4, 3, 3))
        pygame.draw.rect(char_surf, hair_dark, (2, hy - 1, 2, 4))
        pygame.draw.rect(char_surf, hair_dark, (12, hy - 1, 2, 4))
        pygame.draw.rect(char_surf, hair_color, (6, hy + 1, 4, 1))
    elif hair_style == 2:  # Long Explorer
        pygame.draw.rect(char_surf, hair_color, (2, hy - 3, 12, 4))
        pygame.draw.rect(char_surf, hair_light, (4, hy - 3, 7, 2))
        # Long side strands falling past shoulders
        pygame.draw.rect(char_surf, hair_color, (1, hy, 3, 10))
        pygame.draw.rect(char_surf, hair_dark, (12, hy, 3, 10))
    elif hair_style == 3:  # Mohawk
        pygame.draw.rect(char_surf, hair_color, (6, hy - 4, 4, 6))
        pygame.draw.rect(char_surf, hair_light, (7, hy - 4, 2, 3))
        pygame.draw.rect(char_surf, hair_dark, (5, hy - 1, 1, 2))
        pygame.draw.rect(char_surf, hair_dark, (10, hy - 1, 1, 2))
    elif hair_style == 4:  # Ponytail
        pygame.draw.rect(char_surf, hair_color, (2, hy - 3, 12, 4))
        pygame.draw.rect(char_surf, hair_light, (4, hy - 3, 6, 2))
        pygame.draw.rect(char_surf, (223, 113, 38), (1, hy - 1, 2, 2))  # Ribbon tie
        pygame.draw.rect(char_surf, hair_color, (0, hy + 1, 3, 6))       # Tail
        pygame.draw.rect(char_surf, hair_dark, (1, hy + 5, 2, 4))
    else:  # Short Crop
        pygame.draw.rect(char_surf, hair_color, (3, hy - 2, 10, 3))
        pygame.draw.rect(char_surf, hair_light, (5, hy - 2, 5, 1))
        pygame.draw.rect(char_surf, hair_dark, (2, hy, 2, 3))
        pygame.draw.rect(char_surf, hair_dark, (12, hy, 2, 3))

    # 3. TORSO & SHIRT
    torso_y = head_y + 9
    # Shirt main body (10x7)
    pygame.draw.rect(char_surf, shirt_color, (3, torso_y, 10, 6))
    # Shirt shading & collar
    pygame.draw.rect(char_surf, shirt_dark, (3, torso_y + 5, 10, 1))
    pygame.draw.rect(char_surf, tint(shirt_color, 1.2), (6, torso_y, 4, 1))
    pygame.draw.rect(char_surf, skin_tone, (7, torso_y, 2, 1))  # collar opening

    # Arms / Sleeves
    pygame.draw.rect(char_surf, shirt_color, (1, torso_y, 2, 4))
    pygame.draw.rect(char_surf, shirt_color, (13, torso_y, 2, 4))
    # Hands (skin tone)
    pygame.draw.rect(char_surf, skin_tone, (1, torso_y + 4, 2, 3))
    pygame.draw.rect(char_surf, skin_tone, (13, torso_y + 4, 2, 3))

    # Belt (leather brown with gold buckle)
    pygame.draw.rect(char_surf, (102, 57, 49), (3, torso_y + 6, 10, 1))
    pygame.draw.rect(char_surf, (251, 242, 54), (7, torso_y + 6, 2, 1))

    # 4. PANTS & LEGS
    legs_y = torso_y + 7
    # Left leg & Right leg
    pygame.draw.rect(char_surf, pants_color, (3, legs_y, 4, 6))
    pygame.draw.rect(char_surf, pants_color, (9, legs_y, 4, 6))
    # Inner leg shadow gap
    pygame.draw.rect(char_surf, pants_dark, (7, legs_y, 2, 6))

    # 5. BOOTS / SHOES (Dark brown leather with sole)
    boot_y = legs_y + 6
    pygame.draw.rect(char_surf, (102, 57, 49), (2, boot_y, 5, 3))
    pygame.draw.rect(char_surf, (102, 57, 49), (9, boot_y, 5, 3))
    pygame.draw.rect(char_surf, (34, 32, 52), (2, boot_y + 2, 5, 1))
    pygame.draw.rect(char_surf, (34, 32, 52), (9, boot_y + 2, 5, 1))

    # Scale up with crisp nearest-neighbor
    scaled_w = 16 * scale
    scaled_h = 26 * scale
    scaled_surf = pygame.transform.scale(char_surf, (scaled_w, scaled_h))
    surface.blit(scaled_surf, (x, y))


def draw_character_preview(
    surface: pygame.Surface,
    center_x: int,
    center_y: int,
    hair_style: int = 0,
    hair_color: Tuple[int, int, int] = HAIR_COLORS[0],
    skin_tone: Tuple[int, int, int] = SKIN_TONES[1],
    shirt_color: Tuple[int, int, int] = OUTFIT_COLORS[1],
    pants_color: Tuple[int, int, int] = OUTFIT_COLORS[6],
    frame: int = 0,
    scale: int = 4,
):
    """
    Renders a magnified 4x character with a stone pedestal and soft shadow.
    """
    char_w = 16 * scale
    char_h = 26 * scale
    draw_x = center_x - char_w // 2
    draw_y = center_y - char_h // 2 - 4

    # 1. Soft oval drop shadow beneath feet
    shadow_surf = pygame.Surface((char_w + 16, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (16, 16, 26, 140), (0, 0, char_w + 16, 12))
    surface.blit(shadow_surf, (center_x - (char_w + 16) // 2, draw_y + char_h - 4))

    # 2. Draw character
    draw_pixel_character(
        surface=surface,
        x=draw_x,
        y=draw_y,
        scale=scale,
        hair_style=hair_style,
        hair_color=hair_color,
        skin_tone=skin_tone,
        shirt_color=shirt_color,
        pants_color=pants_color,
        frame=frame,
    )
