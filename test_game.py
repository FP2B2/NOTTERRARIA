"""
Smoke test suite to verify world generation, physics step, inventory, and tile interaction without requiring a display.
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

from src.world import World
from src.player import Player
from src.inventory import Inventory
from src.config import TILE_SIZE
from src.tiles import AIR, DIRT, GRASS, STONE, TORCH

def test_headless():
    print("1. Testing World Generation...")
    world = World(width=100, height=80, seed=42)
    assert world.width == 100
    assert world.height == 80
    assert world.spawn_x > 0
    print(f"   -> World generated! Spawn point: ({world.spawn_x}, {world.spawn_y})")

    print("2. Testing Player Physics & AABB Collision...")
    player = Player(world.spawn_x * TILE_SIZE, (world.spawn_y - 2) * TILE_SIZE)
    class DummyKeys:
        def __getitem__(self, k):
            return False
    keys = DummyKeys()
    player.update(keys, world)
    print(f"   -> Player updated! Position: ({player.x:.1f}, {player.y:.1f}), on_ground={player.on_ground}")

    print("3. Testing Inventory and AI context string...")
    inv = player.inventory
    inv.add_item("copper_ore", 12)
    inv.add_item("gold_ore", 3)
    summary = inv.get_summary_for_ai()
    print(f"   -> AI Inventory Summary: {summary}")
    assert "Copper Ore" in summary
    assert "Gold Ore" in summary

    print("4. Testing Mining & Placing Mechanics...")
    # Find a solid tile near spawn
    sx, sy = world.spawn_x, world.spawn_y + 1
    tile = world.get_tile(sx, sy)
    print(f"   -> Tile at ({sx}, {sy}): id={tile}")
    # Mine it
    res = player.interact_tile(sx, sy, world, is_primary=True)
    print(f"   -> Mine action result: {res}")

    print("\nALL SMOKE TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    test_headless()
