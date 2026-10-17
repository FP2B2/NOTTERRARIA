"""
Generates high-res image captures of Screen 1 (Title) and Screen 2 (Character Creation).
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.config import INTERNAL_WIDTH, INTERNAL_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT
from src.title_screen import TitleScreen
from src.character_screen import CharacterScreen

def capture():
    pygame.init()
    canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

    # 1. Capture Title Screen
    title = TitleScreen()
    title.time = 2.5
    title.mountain_scroll = 40.0
    title.ruins_scroll = 90.0
    for p in title.particles:
        p.update(title.time)
    title.render(canvas)

    scaled_title = pygame.transform.scale(canvas, (WINDOW_WIDTH, WINDOW_HEIGHT))
    out_dir = os.path.dirname(os.path.abspath(__file__))
    title_path = os.path.join(out_dir, "title_screen.png")
    pygame.image.save(scaled_title, title_path)
    print(f"Captured: {title_path}")

    # 2. Capture Character Screen (Hairstyle Tab)
    char_screen = CharacterScreen()
    char_screen.name = "Rowan"
    char_screen.time = 1.0
    char_screen.hair_style_idx = 1
    char_screen.hair_color_idx = 2  # Blonde
    char_screen.shirt_color_idx = 1  # Cobalt Blue
    char_screen.active_tab = 0
    char_screen.render(canvas, mouse_pos=(300, 150))

    scaled_char = pygame.transform.scale(canvas, (WINDOW_WIDTH, WINDOW_HEIGHT))
    char_path = os.path.join(out_dir, "character_screen.png")
    pygame.image.save(scaled_char, char_path)
    print(f"Captured: {char_path}")

    # 3. Capture Character Screen (Color Swatches Tab)
    char_screen.active_tab = 1  # Hair Color Tab
    char_screen.render(canvas, mouse_pos=(300, 150))
    scaled_color = pygame.transform.scale(canvas, (WINDOW_WIDTH, WINDOW_HEIGHT))
    color_path = os.path.join(out_dir, "character_color_tab.png")
    pygame.image.save(scaled_color, color_path)
    print(f"Captured: {color_path}")

if __name__ == "__main__":
    capture()
