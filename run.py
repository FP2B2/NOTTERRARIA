#!/usr/bin/env python3
"""
Project Terracraft - Modular Screen Flow Manager
Screen 1: Title Screen (Dusk Parallax, Glowing Logo, Sound Hooks)
Screen 2: Character Creation (Live Preview, Customizer, Difficulty)
Screen 3: Sandbox Game World (Procedural Strata & Local Gemma 4 AI)
"""

import sys
import os
import pygame

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import INTERNAL_WIDTH, INTERNAL_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT
from src.title_screen import TitleScreen
from src.character_screen import CharacterScreen
from src.game import Game


def main():
    print("==================================================")
    print("  TERRACRAFT - STARTING MODULAR SCREEN FLOW")
    print("==================================================")
    print("Screen 1: Title Screen (Parallax Ruins, Glowing Logo)")
    print("Screen 2: Character Creation (Live Preview, Swatches)")
    print("==================================================")

    pygame.init()
    pygame.display.set_caption("Project Terracraft - A 2D Sandbox Odyssey")

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
    clock = pygame.time.Clock()

    current_state = "title"
    character_data = None

    while True:
        if current_state == "title":
            title_screen = TitleScreen()
            action = title_screen.run(canvas, window, clock)

            if action == "play":
                current_state = "character"
            elif action == "quit":
                break

        elif current_state == "character":
            char_screen = CharacterScreen()
            char_data = char_screen.run(canvas, window, clock)

            if char_data is None:
                # User clicked Back -> return to Title Screen
                current_state = "title"
            else:
                # User completed character creation!
                print("\n[SUCCESS] Character Created:")
                print(f"  • Name:       {char_data['name']}")
                print(f"  • Style:      {char_data['hair_style']}")
                print(f"  • Hair RGB:   {char_data['hair_color']}")
                print(f"  • Skin RGB:   {char_data['skin_tone']}")
                print(f"  • Shirt RGB:  {char_data['shirt_color']}")
                print(f"  • Pants RGB:  {char_data['pants_color']}")
                print(f"  • Difficulty: {char_data['difficulty']}")

                character_data = char_data
                current_state = "game"

        elif current_state == "game":
            print("\nLaunching Game World with created character...")
            game = Game(character_data=character_data, canvas=canvas, window=window, clock=clock)
            game.run()
            # If player exits game, return to title screen
            current_state = "title"

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
