"""
Tile definitions, attributes, light emissions, and visual styling.
"""

from dataclasses import dataclass
from typing import Tuple, Optional

# Tile IDs
AIR = 0
DIRT = 1
GRASS = 2
STONE = 3
WOOD = 4
LEAVES = 5
COPPER_ORE = 6
IRON_ORE = 7
SILVER_ORE = 8
GOLD_ORE = 9
DEMONITE_ORE = 10
HELLSTONE = 11
ASH = 12
SAND = 13
TORCH = 14
WORKBENCH = 15
FURNACE = 16
ANVIL = 17
WOOD_WALL = 18
DOOR_CLOSED = 19
DOOR_OPEN = 20
CHEST = 21
PLATFORM = 22


@dataclass
class TileDef:
    id: int
    name: str
    is_solid: bool
    is_platform: bool = False
    is_wall: bool = False
    hardness: float = 1.0  # seconds or hits with standard pickaxe
    tool_type: str = "pickaxe"  # "pickaxe", "axe", "none"
    light_emission: Tuple[int, int, int] = (0, 0, 0)
    light_absorption: int = 45  # how much light drops when traversing this tile
    base_color: Tuple[int, int, int] = (100, 100, 100)
    border_color: Optional[Tuple[int, int, int]] = None
    drop_item: Optional[str] = None


TILE_REGISTRY = {
    AIR: TileDef(
        id=AIR,
        name="Air",
        is_solid=False,
        light_absorption=10,
        base_color=(0, 0, 0),
        drop_item=None,
    ),
    DIRT: TileDef(
        id=DIRT,
        name="Dirt",
        is_solid=True,
        hardness=0.6,
        tool_type="pickaxe",
        light_absorption=55,
        base_color=(134, 96, 67),
        border_color=(108, 74, 50),
        drop_item="dirt_block",
    ),
    GRASS: TileDef(
        id=GRASS,
        name="Grass",
        is_solid=True,
        hardness=0.7,
        tool_type="pickaxe",
        light_absorption=55,
        base_color=(67, 160, 71),
        border_color=(46, 125, 50),
        drop_item="dirt_block",
    ),
    STONE: TileDef(
        id=STONE,
        name="Stone",
        is_solid=True,
        hardness=1.2,
        tool_type="pickaxe",
        light_absorption=70,
        base_color=(128, 128, 128),
        border_color=(90, 90, 90),
        drop_item="stone_block",
    ),
    WOOD: TileDef(
        id=WOOD,
        name="Wood",
        is_solid=True,
        hardness=0.8,
        tool_type="axe",
        light_absorption=50,
        base_color=(160, 116, 74),
        border_color=(120, 84, 50),
        drop_item="wood",
    ),
    LEAVES: TileDef(
        id=LEAVES,
        name="Leaves",
        is_solid=False,
        hardness=0.2,
        tool_type="axe",
        light_absorption=20,
        base_color=(56, 142, 60),
        border_color=(43, 110, 46),
        drop_item="acorn",
    ),
    COPPER_ORE: TileDef(
        id=COPPER_ORE,
        name="Copper Ore",
        is_solid=True,
        hardness=1.5,
        tool_type="pickaxe",
        light_absorption=70,
        base_color=(198, 124, 78),
        border_color=(150, 90, 52),
        drop_item="copper_ore",
    ),
    IRON_ORE: TileDef(
        id=IRON_ORE,
        name="Iron Ore",
        is_solid=True,
        hardness=1.8,
        tool_type="pickaxe",
        light_absorption=70,
        base_color=(165, 146, 124),
        border_color=(120, 105, 88),
        drop_item="iron_ore",
    ),
    SILVER_ORE: TileDef(
        id=SILVER_ORE,
        name="Silver Ore",
        is_solid=True,
        hardness=2.0,
        tool_type="pickaxe",
        light_absorption=70,
        base_color=(205, 218, 226),
        border_color=(155, 168, 176),
        drop_item="silver_ore",
    ),
    GOLD_ORE: TileDef(
        id=GOLD_ORE,
        name="Gold Ore",
        is_solid=True,
        hardness=2.4,
        tool_type="pickaxe",
        light_absorption=70,
        base_color=(255, 215, 0),
        border_color=(200, 165, 0),
        drop_item="gold_ore",
    ),
    DEMONITE_ORE: TileDef(
        id=DEMONITE_ORE,
        name="Demonite Ore",
        is_solid=True,
        hardness=3.0,
        tool_type="pickaxe",
        light_emission=(40, 10, 70),
        light_absorption=70,
        base_color=(92, 40, 148),
        border_color=(60, 20, 100),
        drop_item="demonite_ore",
    ),
    HELLSTONE: TileDef(
        id=HELLSTONE,
        name="Hellstone",
        is_solid=True,
        hardness=4.0,
        tool_type="pickaxe",
        light_emission=(180, 50, 20),
        light_absorption=70,
        base_color=(184, 51, 23),
        border_color=(120, 30, 15),
        drop_item="hellstone",
    ),
    ASH: TileDef(
        id=ASH,
        name="Ash",
        is_solid=True,
        hardness=0.6,
        tool_type="pickaxe",
        light_absorption=60,
        base_color=(68, 64, 69),
        border_color=(45, 42, 46),
        drop_item="ash_block",
    ),
    SAND: TileDef(
        id=SAND,
        name="Sand",
        is_solid=True,
        hardness=0.5,
        tool_type="pickaxe",
        light_absorption=50,
        base_color=(226, 213, 149),
        border_color=(185, 172, 115),
        drop_item="sand_block",
    ),
    TORCH: TileDef(
        id=TORCH,
        name="Torch",
        is_solid=False,
        hardness=0.1,
        tool_type="none",
        light_emission=(255, 205, 90),
        light_absorption=5,
        base_color=(255, 170, 40),
        drop_item="torch",
    ),
    WORKBENCH: TileDef(
        id=WORKBENCH,
        name="Work Bench",
        is_solid=False,
        is_platform=True,
        hardness=0.8,
        tool_type="axe",
        light_absorption=15,
        base_color=(180, 130, 80),
        drop_item="workbench",
    ),
    FURNACE: TileDef(
        id=FURNACE,
        name="Furnace",
        is_solid=True,
        hardness=1.5,
        tool_type="pickaxe",
        light_emission=(120, 50, 10),
        light_absorption=50,
        base_color=(120, 110, 105),
        drop_item="furnace",
    ),
    ANVIL: TileDef(
        id=ANVIL,
        name="Iron Anvil",
        is_solid=True,
        hardness=2.0,
        tool_type="pickaxe",
        light_absorption=40,
        base_color=(90, 95, 100),
        drop_item="iron_anvil",
    ),
    WOOD_WALL: TileDef(
        id=WOOD_WALL,
        name="Wood Wall",
        is_solid=False,
        is_wall=True,
        hardness=0.4,
        tool_type="none",
        light_absorption=25,
        base_color=(115, 80, 50),
        drop_item="wood_wall",
    ),
    PLATFORM: TileDef(
        id=PLATFORM,
        name="Wood Platform",
        is_solid=False,
        is_platform=True,
        hardness=0.3,
        tool_type="axe",
        light_absorption=5,
        base_color=(175, 125, 75),
        drop_item="wood_platform",
    ),
    DOOR_CLOSED: TileDef(
        id=DOOR_CLOSED,
        name="Wooden Door (Closed)",
        is_solid=True,
        hardness=0.8,
        tool_type="axe",
        light_absorption=50,
        base_color=(150, 100, 60),
        drop_item="wooden_door",
    ),
    DOOR_OPEN: TileDef(
        id=DOOR_OPEN,
        name="Wooden Door (Open)",
        is_solid=False,
        hardness=0.8,
        tool_type="axe",
        light_absorption=10,
        base_color=(140, 95, 55),
        drop_item="wooden_door",
    ),
}
