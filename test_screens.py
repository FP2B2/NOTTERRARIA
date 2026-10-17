"""
Headless validation script for TitleScreen and CharacterScreen modules.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.config import INTERNAL_WIDTH, INTERNAL_HEIGHT
from src.title_screen import TitleScreen
from src.character_screen import CharacterScreen
from src.sprites import draw_character_preview
from src.audio import SoundManager

def test_screens():
    print("1. Initializing pygame headless...")
    pygame.init()
    canvas = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))

    print("2. Testing SoundManager...")
    sound = SoundManager.get()
    sound.play("click")
    sound.play("hover")
    sound.play("select")
    sound.play("start")
    print("   -> Audio synthesis working!")

    print("3. Testing TitleScreen...")
    title = TitleScreen()
    # Simulate 5 frames of render
    for _ in range(5):
        title.time += 0.016
        title.render(canvas)
    print("   -> TitleScreen rendered cleanly without errors!")

    print("4. Testing CharacterScreen...")
    char_screen = CharacterScreen()
    # Test randomizing
    char_screen._randomize()
    assert char_screen.name != ""
    print(f"   -> Randomize rolled character: {char_screen.name}")

    # Simulate render
    for _ in range(5):
        char_screen.time += 0.016
        char_screen.render(canvas, (100, 100))
    print("   -> CharacterScreen rendered cleanly without errors!")

    # Verify character dict format
    data = char_screen._get_character_dict()
    assert "name" in data
    assert "hair_style" in data
    assert "hair_color" in data
    assert "skin_tone" in data
    assert "shirt_color" in data
    assert "pants_color" in data
    assert "difficulty" in data
    print(f"   -> Character Dict: {data}")

    print("\nALL SCREEN TESTS PASSED WITH 100% SUCCESS!")

if __name__ == "__main__":
    test_screens()
