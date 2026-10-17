"""
Item definitions, tool tiers, weapons, placeable blocks, and crafting recipes.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from .tiles import (
    DIRT,
    STONE,
    WOOD,
    TORCH,
    WORKBENCH,
    FURNACE,
    ANVIL,
    PLATFORM,
    WOOD_WALL,
    DOOR_CLOSED,
    COPPER_ORE,
    IRON_ORE,
    SILVER_ORE,
    GOLD_ORE,
    DEMONITE_ORE,
    HELLSTONE,
    ASH,
    SAND,
)


@dataclass
class ItemDef:
    id: str
    name: str
    item_type: str  # "tool", "weapon", "tile", "wall", "material", "consumable"
    tool_type: Optional[str] = None  # "pickaxe", "axe", "hammer"
    tool_power: float = 1.0  # pickaxe/axe power multiplier
    damage: int = 0
    knockback: float = 1.0
    use_time: int = 15  # frames per swing
    tile_to_place: Optional[int] = None
    max_stack: int = 999
    color: Tuple[int, int, int] = (200, 200, 200)
    description: str = ""


ITEM_REGISTRY: Dict[str, ItemDef] = {
    # Starting Copper Tools
    "copper_pickaxe": ItemDef(
        id="copper_pickaxe",
        name="Copper Pickaxe",
        item_type="tool",
        tool_type="pickaxe",
        tool_power=1.0,
        damage=4,
        use_time=14,
        max_stack=1,
        color=(198, 124, 78),
        description="Used to mine dirt, stone, and early ores.",
    ),
    "copper_axe": ItemDef(
        id="copper_axe",
        name="Copper Axe",
        item_type="tool",
        tool_type="axe",
        tool_power=1.0,
        damage=3,
        use_time=18,
        max_stack=1,
        color=(198, 124, 78),
        description="Used to chop down trees for wood.",
    ),
    "copper_shortsword": ItemDef(
        id="copper_shortsword",
        name="Copper Shortsword",
        item_type="weapon",
        damage=7,
        knockback=2.5,
        use_time=12,
        max_stack=1,
        color=(215, 140, 90),
        description="A light thrusting weapon for self-defense.",
    ),
    # Placeable Blocks
    "dirt_block": ItemDef(
        id="dirt_block",
        name="Dirt",
        item_type="tile",
        tile_to_place=DIRT,
        max_stack=999,
        color=(134, 96, 67),
        description="Basic earth block for building walls and dirt mounds.",
    ),
    "stone_block": ItemDef(
        id="stone_block",
        name="Stone",
        item_type="tile",
        tile_to_place=STONE,
        max_stack=999,
        color=(128, 128, 128),
        description="Sturdy stone block.",
    ),
    "wood": ItemDef(
        id="wood",
        name="Wood",
        item_type="tile",
        tile_to_place=WOOD,
        max_stack=999,
        color=(160, 116, 74),
        description="Essential crafting material and building block.",
    ),
    "torch": ItemDef(
        id="torch",
        name="Torch",
        item_type="tile",
        tile_to_place=TORCH,
        max_stack=999,
        color=(255, 180, 50),
        description="Emits a soft radius of warm light in the dark.",
    ),
    "wood_platform": ItemDef(
        id="wood_platform",
        name="Wood Platform",
        item_type="tile",
        tile_to_place=PLATFORM,
        max_stack=999,
        color=(175, 125, 75),
        description="You can jump up through it or press Down to drop.",
    ),
    "wood_wall": ItemDef(
        id="wood_wall",
        name="Wood Wall",
        item_type="wall",
        tile_to_place=WOOD_WALL,
        max_stack=999,
        color=(115, 80, 50),
        description="Background wall necessary for valid NPC housing.",
    ),
    "wooden_door": ItemDef(
        id="wooden_door",
        name="Wooden Door",
        item_type="tile",
        tile_to_place=DOOR_CLOSED,
        max_stack=99,
        color=(150, 100, 60),
        description="Right-click to open or close.",
    ),
    "workbench": ItemDef(
        id="workbench",
        name="Work Bench",
        item_type="tile",
        tile_to_place=WORKBENCH,
        max_stack=99,
        color=(180, 130, 80),
        description="Enables basic furniture, doors, and wooden gear crafting.",
    ),
    "furnace": ItemDef(
        id="furnace",
        name="Furnace",
        item_type="tile",
        tile_to_place=FURNACE,
        max_stack=99,
        color=(120, 110, 105),
        description="Used to smelt mined ores into metal bars.",
    ),
    "iron_anvil": ItemDef(
        id="iron_anvil",
        name="Iron Anvil",
        item_type="tile",
        tile_to_place=ANVIL,
        max_stack=99,
        color=(90, 95, 100),
        description="Used to smith armor, weapons, and advanced metal tools.",
    ),
    # Raw Ores
    "copper_ore": ItemDef(id="copper_ore", name="Copper Ore", item_type="material", max_stack=999, color=(198, 124, 78)),
    "iron_ore": ItemDef(id="iron_ore", name="Iron Ore", item_type="material", max_stack=999, color=(165, 146, 124)),
    "silver_ore": ItemDef(id="silver_ore", name="Silver Ore", item_type="material", max_stack=999, color=(205, 218, 226)),
    "gold_ore": ItemDef(id="gold_ore", name="Gold Ore", item_type="material", max_stack=999, color=(255, 215, 0)),
    "demonite_ore": ItemDef(id="demonite_ore", name="Demonite Ore", item_type="material", max_stack=999, color=(92, 40, 148)),
    "hellstone": ItemDef(id="hellstone", name="Hellstone", item_type="material", max_stack=999, color=(184, 51, 23)),
    "ash_block": ItemDef(id="ash_block", name="Ash", item_type="tile", tile_to_place=ASH, max_stack=999, color=(68, 64, 69)),
    "sand_block": ItemDef(id="sand_block", name="Sand", item_type="tile", tile_to_place=SAND, max_stack=999, color=(226, 213, 149)),
    # Drops
    "acorn": ItemDef(id="acorn", name="Acorn", item_type="material", max_stack=99, color=(100, 70, 40)),
    "gel": ItemDef(id="gel", name="Gel", item_type="material", max_stack=999, color=(50, 150, 255)),
}


@dataclass
class CraftingRecipe:
    result_item: str
    result_count: int
    station: Optional[str]  # None (by hand), "workbench", "furnace", "anvil"
    ingredients: Dict[str, int]


RECIPES: List[CraftingRecipe] = [
    # Hand Crafting
    CraftingRecipe(result_item="workbench", result_count=1, station=None, ingredients={"wood": 10}),
    CraftingRecipe(result_item="torch", result_count=3, station=None, ingredients={"wood": 1, "gel": 1}),
    CraftingRecipe(result_item="wood_platform", result_count=2, station=None, ingredients={"wood": 1}),
    
    # Workbench Crafting
    CraftingRecipe(result_item="wood_wall", result_count=4, station="workbench", ingredients={"wood": 1}),
    CraftingRecipe(result_item="wooden_door", result_count=1, station="workbench", ingredients={"wood": 6}),
    CraftingRecipe(result_item="furnace", result_count=1, station="workbench", ingredients={"stone_block": 20, "wood": 4, "torch": 3}),
    
    # Furnace Smelting
    CraftingRecipe(result_item="iron_anvil", result_count=1, station="furnace", ingredients={"iron_ore": 15}),
]
