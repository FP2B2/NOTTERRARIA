"""
2D dynamic cellular and radial lighting engine.
Renders smooth atmospheric lighting with torch radiuses and
sunlight attenuation, blended via BLEND_MULT for authentic Terraria caves.
"""

import math
import pygame
from typing import Tuple
from .config import TILE_SIZE, STRATA_SURFACE_START, STRATA_UNDERGROUND_END, STRATA_UNDERWORLD_START
from .tiles import AIR, TORCH, HELLSTONE, DEMONITE_ORE, FURNACE, TILE_REGISTRY


class LightingEngine:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.light_surface = pygame.Surface((screen_width, screen_height))

        # Pre-render radial light masks for torches and glowing ores
        self.torch_mask = self._create_radial_mask(radius=110, inner_color=(255, 215, 120), outer_color=(0, 0, 0))
        self.ore_mask = self._create_radial_mask(radius=60, inner_color=(160, 60, 240), outer_color=(0, 0, 0))
        self.lava_mask = self._create_radial_mask(radius=90, inner_color=(255, 80, 20), outer_color=(0, 0, 0))

    def _create_radial_mask(self, radius: int, inner_color: Tuple[int, int, int], outer_color: Tuple[int, int, int]) -> pygame.Surface:
        surf = pygame.Surface((radius * 2, radius * 2))
        surf.fill((0, 0, 0))
        for r in range(radius, 0, -3):
            ratio = r / radius
            r_c = int(inner_color[0] * (1.0 - ratio) + outer_color[0] * ratio)
            g_c = int(inner_color[1] * (1.0 - ratio) + outer_color[1] * ratio)
            b_c = int(inner_color[2] * (1.0 - ratio) + outer_color[2] * ratio)
            pygame.draw.circle(surf, (r_c, g_c, b_c), (radius, radius), r)
        return surf

    def render_lighting(
        self,
        surface: pygame.Surface,
        world,
        cam_x: int,
        cam_y: int,
        day_light_factor: float,  # 0.0 (night) to 1.0 (noon)
    ):
        """Builds and applies the lighting overlay onto the game viewport."""
        # 1. Base ambient lighting based on depth and time
        # Above surface: bright sunlight. Below surface: deep darkness.
        min_tx = max(0, cam_x // TILE_SIZE)
        max_tx = min(world.width, (cam_x + self.width) // TILE_SIZE + 2)
        min_ty = max(0, cam_y // TILE_SIZE)
        max_ty = min(world.height, (cam_y + self.height) // TILE_SIZE + 2)

        # Base ambient color
        # In caves, ambient light is dark navy/black (15, 15, 22)
        ambient_r = int(220 * day_light_factor + 20)
        ambient_g = int(220 * day_light_factor + 20)
        ambient_b = int(235 * day_light_factor + 30)

        # Clear light surface with black
        self.light_surface.fill((16, 16, 24))

        # 2. Draw sunlight in open sky/surface areas
        for ty in range(min_ty, max_ty):
            screen_y = ty * TILE_SIZE - cam_y
            depth_ratio = max(0.0, min(1.0, (ty - STRATA_SURFACE_START) / 35.0))
            
            # Attenuate daylight as we go deeper underground
            cur_r = int(ambient_r * (1.0 - depth_ratio * 0.92))
            cur_g = int(ambient_g * (1.0 - depth_ratio * 0.92))
            cur_b = int(ambient_b * (1.0 - depth_ratio * 0.90))

            if cur_r > 20:
                rect = pygame.Rect(0, screen_y, self.width, TILE_SIZE)
                pygame.draw.rect(self.light_surface, (cur_r, cur_g, cur_b), rect)

        # 3. Add point lights from placed torches, furnaces, and ores
        for ty in range(min_ty, max_ty):
            for tx in range(min_tx, max_tx):
                tile = world.get_tile(tx, ty)
                if tile == TORCH:
                    pos = (tx * TILE_SIZE + TILE_SIZE // 2 - cam_x - 110, ty * TILE_SIZE + TILE_SIZE // 2 - cam_y - 110)
                    self.light_surface.blit(self.torch_mask, pos, special_flags=pygame.BLEND_ADD)
                elif tile == HELLSTONE or tile == FURNACE:
                    pos = (tx * TILE_SIZE + TILE_SIZE // 2 - cam_x - 90, ty * TILE_SIZE + TILE_SIZE // 2 - cam_y - 90)
                    self.light_surface.blit(self.lava_mask, pos, special_flags=pygame.BLEND_ADD)
                elif tile == DEMONITE_ORE:
                    pos = (tx * TILE_SIZE + TILE_SIZE // 2 - cam_x - 60, ty * TILE_SIZE + TILE_SIZE // 2 - cam_y - 60)
                    self.light_surface.blit(self.ore_mask, pos, special_flags=pygame.BLEND_ADD)

        # 4. Multiplicative blend onto game screen
        surface.blit(self.light_surface, (0, 0), special_flags=pygame.BLEND_MULT)
