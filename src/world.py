"""
Procedural world generator and 2D tile grid manager.
Supports strata (Sky, Surface, Underground, Caverns, Underworld),
biome elevation, cave carving, ore veins, and trees.
"""

import math
import random
from typing import Tuple, List, Optional
import noise

from .config import (
    WORLD_WIDTH,
    WORLD_HEIGHT,
    STRATA_SURFACE_START,
    STRATA_SURFACE_END,
    STRATA_UNDERGROUND_END,
    STRATA_CAVERNS_END,
    STRATA_UNDERWORLD_START,
)
from .tiles import (
    AIR,
    DIRT,
    GRASS,
    STONE,
    WOOD,
    LEAVES,
    COPPER_ORE,
    IRON_ORE,
    SILVER_ORE,
    GOLD_ORE,
    DEMONITE_ORE,
    HELLSTONE,
    ASH,
    SAND,
    TORCH,
    WOOD_WALL,
    TILE_REGISTRY,
)


class World:
    def __init__(self, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT, seed: Optional[int] = None):
        self.width = width
        self.height = height
        self.seed = seed if seed is not None else random.randint(1000, 99999)
        
        # 1D flattened arrays for high-speed indexing: index = y * width + x
        # Foreground tiles and background walls
        self.tiles = bytearray(width * height)
        self.walls = bytearray(width * height)
        
        # Tile damage tracker: dict of (x, y) -> damage float (0.0 to hardness)
        self.tile_damage = {}
        
        # Spawn position (tile coordinates)
        self.spawn_x = width // 2
        self.spawn_y = STRATA_SURFACE_START
        
        # Light grid (R, G, B) stored as bytearray
        self.light_r = bytearray(width * height)
        self.light_g = bytearray(width * height)
        self.light_b = bytearray(width * height)
        
        # Generate the world
        self.generate()

    def get_tile(self, x: int, y: int) -> int:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y * self.width + x]
        return STONE if y >= STRATA_SURFACE_END else AIR

    def set_tile(self, x: int, y: int, tile_id: int):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y * self.width + x] = tile_id
            if (x, y) in self.tile_damage:
                del self.tile_damage[(x, y)]

    def get_wall(self, x: int, y: int) -> int:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.walls[y * self.width + x]
        return AIR

    def set_wall(self, x: int, y: int, wall_id: int):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.walls[y * self.width + x] = wall_id

    def is_solid(self, x: int, y: int) -> bool:
        tile_id = self.get_tile(x, y)
        tile_def = TILE_REGISTRY.get(tile_id)
        return tile_def.is_solid if tile_def else False

    def is_platform(self, x: int, y: int) -> bool:
        tile_id = self.get_tile(x, y)
        tile_def = TILE_REGISTRY.get(tile_id)
        return tile_def.is_platform if tile_def else False

    def generate(self):
        """Generates all strata layers, biomes, cave networks, ore clusters, and trees."""
        base_surface_y = (STRATA_SURFACE_START + STRATA_SURFACE_END) // 2
        
        # 1. Height map for the surface
        height_map = [0] * self.width
        for x in range(self.width):
            nx = x * 0.015
            # Multi-octave Perlin elevation
            elevation = (
                noise.pnoise1(nx, octaves=3, persistence=0.5, base=self.seed) * 22
                + noise.pnoise1(nx * 3.5, octaves=2, persistence=0.4, base=self.seed + 10) * 6
            )
            height_map[x] = int(base_surface_y + elevation)

        # 2. Fill basic strata
        for x in range(self.width):
            surface_y = height_map[x]
            
            # Biome determination by horizontal X coordinate
            is_desert = 0.65 * self.width <= x <= 0.85 * self.width
            
            for y in range(self.height):
                idx = y * self.width + x
                
                # Sky
                if y < surface_y:
                    self.tiles[idx] = AIR
                    self.walls[idx] = AIR
                # Surface Top (Grass or Sand)
                elif y == surface_y:
                    self.tiles[idx] = SAND if is_desert else GRASS
                    self.walls[idx] = DIRT
                # Surface Sub-layer (Dirt or Sand)
                elif y < surface_y + 8:
                    self.tiles[idx] = SAND if is_desert else DIRT
                    self.walls[idx] = DIRT
                # Underground Layer
                elif y < STRATA_UNDERGROUND_END:
                    self.tiles[idx] = STONE if random.random() < 0.65 else DIRT
                    self.walls[idx] = DIRT
                # Caverns Layer
                elif y < STRATA_UNDERWORLD_START:
                    self.tiles[idx] = STONE
                    self.walls[idx] = STONE
                # Underworld Layer
                else:
                    self.tiles[idx] = ASH
                    self.walls[idx] = ASH

        # 3. Carve Caves using 2D Perlin Noise
        for x in range(self.width):
            surface_y = height_map[x]
            for y in range(surface_y + 4, self.height - 25):
                n2d = noise.pnoise2(x * 0.045, y * 0.045, octaves=3, persistence=0.5, base=self.seed + 50)
                # Cave opening threshold gets wider in Caverns
                threshold = 0.16 if y > STRATA_UNDERGROUND_END else 0.22
                if abs(n2d) > threshold:
                    self.tiles[y * self.width + x] = AIR

        # 4. Underworld Lava Caves (Open chasms)
        under_start = min(STRATA_UNDERWORLD_START + 10, max(0, self.height - 15))
        for x in range(self.width):
            for y in range(under_start, self.height):
                n_under = noise.pnoise2(x * 0.05, y * 0.04, octaves=2, base=self.seed + 100)
                if abs(n_under) > 0.18:
                    self.tiles[y * self.width + x] = AIR

        # 5. Ore Veins
        self._spawn_ores(height_map)

        # 6. Surface Trees
        self._grow_trees(height_map)

        # 7. Locate player spawn
        self.spawn_x = self.width // 2
        self.spawn_y = height_map[self.spawn_x] - 3

    def _spawn_ores(self, height_map: List[int]):
        """Injects clusters of tiered ores at their respective depth strata."""
        # Scale ranges safely to world dimensions
        h = self.height
        surf_start = min(STRATA_SURFACE_START + 10, h // 4)
        underground_end = min(STRATA_UNDERGROUND_END, int(h * 0.65))
        caverns_end = min(STRATA_CAVERNS_END, int(h * 0.85))
        underworld_start = min(STRATA_UNDERWORLD_START + 5, int(h * 0.88))

        # Copper / Tin (Underground & lower surface)
        self._create_ore_clusters(COPPER_ORE, count=90, min_y=surf_start, max_y=underground_end, size=7)
        # Iron / Lead (Underground & upper caverns)
        self._create_ore_clusters(IRON_ORE, count=75, min_y=surf_start + 10, max_y=caverns_end, size=6)
        # Silver (Lower underground & caverns)
        self._create_ore_clusters(SILVER_ORE, count=55, min_y=max(surf_start, underground_end - 20), max_y=caverns_end, size=5)
        # Gold / Platinum (Caverns)
        self._create_ore_clusters(GOLD_ORE, count=40, min_y=max(surf_start, underground_end + 20), max_y=max(surf_start + 1, underworld_start - 10), size=5)
        # Demonite Ore (Scattered rare underground)
        self._create_ore_clusters(DEMONITE_ORE, count=25, min_y=underground_end, max_y=max(underground_end + 1, underworld_start), size=4)
        # Hellstone (Underworld only)
        self._create_ore_clusters(HELLSTONE, count=60, min_y=underworld_start, max_y=max(underworld_start + 1, h - 2), size=6)

    def _create_ore_clusters(self, ore_id: int, count: int, min_y: int, max_y: int, size: int):
        if min_y >= max_y or self.width <= 20:
            return
        for _ in range(count):
            cx = random.randint(10, self.width - 10)
            cy = random.randint(min_y, max_y)
            for _ in range(size * 2):
                ox = cx + random.randint(-size // 2, size // 2)
                oy = cy + random.randint(-size // 2, size // 2)
                if 0 <= ox < self.width and 0 <= oy < self.height:
                    cur = self.get_tile(ox, oy)
                    # Only replace stone, dirt, or ash
                    if cur in (STONE, DIRT, ASH):
                        self.set_tile(ox, oy, ore_id)

    def _grow_trees(self, height_map: List[int]):
        """Plants trees on flat surface grass tiles."""
        x = 15
        while x < self.width - 15:
            # Check if surface is grass
            sy = height_map[x]
            if self.get_tile(x, sy) == GRASS and self.get_tile(x, sy - 1) == AIR:
                if random.random() < 0.45:
                    height = random.randint(5, 9)
                    # Trunk
                    for ty in range(sy - height, sy):
                        self.set_tile(x, ty, WOOD)
                    # Leaves canopy
                    canopy_top = sy - height - 3
                    for lx in range(x - 2, x + 3):
                        for ly in range(canopy_top, sy - height + 1):
                            if self.get_tile(lx, ly) == AIR:
                                self.set_tile(lx, ly, LEAVES)
                    x += 4
            x += 1
