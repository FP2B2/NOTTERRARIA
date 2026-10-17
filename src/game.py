"""
Main 60 FPS Game Loop with Platformer Movement, Sword Combat,
Screen Shake Juice, Hitstop, Training Dummy, and Guide NPC interaction.
"""

import math
import random
import pygame
from typing import Tuple, List, Optional, Dict, Any

from .config import (
    INTERNAL_WIDTH,
    INTERNAL_HEIGHT,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    TILE_SIZE,
    DAY_DURATION_SECONDS,
    STRATA_SURFACE_START,
    STRATA_SURFACE_END,
    STRATA_UNDERGROUND_END,
    STRATA_CAVERNS_END,
    STRATA_UNDERWORLD_START,
)
from .tiles import (
    AIR,
    GRASS,
    DIRT,
    STONE,
    TORCH,
    WOOD_WALL,
    TILE_REGISTRY,
)
from .world import World
from .player import Player
from .lighting import LightingEngine
from .ui import UIRenderer
from .ai_guide import AIGuideBridge
from .combat import TrainingDummy, DamageNumber, CombatJuiceManager


class GuideNPC:
    def __init__(self, x_pixel: float, y_pixel: float):
        self.x = x_pixel
        self.y = y_pixel
        self.width = 14
        self.height = 28
        self.vx = 0.0
        self.vy = 0.0
        self.facing_right = True
        self.walk_timer = 0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def update(self, world):
        self.walk_timer += 1
        if self.walk_timer > 180:
            self.walk_timer = 0
            choice = random.choice([-0.8, 0.0, 0.8])
            self.vx = choice
            if choice != 0:
                self.facing_right = choice > 0

        self.vy += 0.4
        if self.vy > 8.0:
            self.vy = 8.0

        self.x += self.vx
        rx = self.rect
        for ty in range(rx.top // TILE_SIZE, rx.bottom // TILE_SIZE + 1):
            for tx in range(rx.left // TILE_SIZE, rx.right // TILE_SIZE + 1):
                if world.is_solid(tx, ty):
                    self.vx = -self.vx
                    self.facing_right = not self.facing_right
                    break

        self.y += self.vy
        ry = self.rect
        for ty in range(ry.top // TILE_SIZE, ry.bottom // TILE_SIZE + 1):
            for tx in range(ry.left // TILE_SIZE, ry.right // TILE_SIZE + 1):
                if world.is_solid(tx, ty):
                    if self.vy > 0:
                        self.y = ty * TILE_SIZE - self.height
                        self.vy = 0.0
                    break


class Game:
    def __init__(self, character_data=None, canvas=None, window=None, clock=None):
        if not pygame.get_init():
            pygame.init()
        pygame.display.set_caption("Project Terracraft - A 2D Sandbox Odyssey")

        self.window = window if window is not None else pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.canvas = canvas if canvas is not None else pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        self.clock = clock if clock is not None else pygame.time.Clock()
        self.running = True

        # Systems & World
        self.world = World()

        # Create a flat testing arena on the surface around spawn point
        self.floor_tile_y = self.world.spawn_y + 1
        self.floor_pixel_y = self.floor_tile_y * TILE_SIZE
        for tx in range(self.world.spawn_x - 35, self.world.spawn_x + 35):
            for ty in range(self.world.spawn_y - 8, self.floor_tile_y):
                self.world.set_tile(tx, ty, AIR)
            self.world.set_tile(tx, self.floor_tile_y, GRASS)
            for ty in range(self.floor_tile_y + 1, self.floor_tile_y + 6):
                self.world.set_tile(tx, ty, DIRT)

        player_start_x = self.world.spawn_x * TILE_SIZE
        player_start_y = (self.world.spawn_y - 1) * TILE_SIZE
        self.player = Player(player_start_x, player_start_y)

        # Apply character customization if provided
        if character_data:
            self.player.name = character_data.get("name", "Player")
            self.player.hair_style = character_data.get("hair_style", 0)
            self.player.hair_color = character_data.get("hair_color", (143, 86, 59))
            self.player.skin_tone = character_data.get("skin_tone", (238, 195, 154))
            self.player.shirt_color = character_data.get("shirt_color", (91, 110, 225))
            self.player.pants_color = character_data.get("pants_color", (63, 63, 116))
            self.player.difficulty = character_data.get("difficulty", "Normal")

        # NPCs & Combat Entities
        self.guide_npc = GuideNPC(player_start_x - 45, player_start_y)
        # Training Dummy positioned right on the combat testing floor
        dummy_x = player_start_x + 75
        dummy_y = self.floor_pixel_y - 18
        self.dummy = TrainingDummy(dummy_x, dummy_y)

        # Combat Juice & Damage Numbers
        self.juice = CombatJuiceManager()
        self.damage_numbers: List[DamageNumber] = []
        self.combat_font = pygame.font.SysFont("monospace", 10, bold=True)
        self.hint_font = pygame.font.SysFont("monospace", 10, bold=True)

        self.lighting = LightingEngine(INTERNAL_WIDTH, INTERNAL_HEIGHT)
        self.ui = UIRenderer(INTERNAL_WIDTH, INTERNAL_HEIGHT)
        self.ai = AIGuideBridge()

        # Camera
        self.cam_x = float(player_start_x - INTERNAL_WIDTH // 2)
        self.cam_y = float(player_start_y - INTERNAL_HEIGHT // 2)
        self.shake_offset = (0, 0)

        # Day/Night State
        self.day_time = 0.28
        self.time_speed = 1.0 / (DAY_DURATION_SECONDS * FPS)

        # Stars for night sky
        self.stars = [
            (random.randint(0, INTERNAL_WIDTH), random.randint(0, INTERNAL_HEIGHT // 2), random.randint(1, 2))
            for _ in range(50)
        ]

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.render()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Hotbar selection 1-9, 0
                if pygame.K_1 <= event.key <= pygame.K_9:
                    self.player.inventory.select_slot(event.key - pygame.K_1)
                elif event.key == pygame.K_0:
                    self.player.inventory.select_slot(9)

                # Combat Sword Swing Key (J)
                elif event.key == pygame.K_j:
                    self.player.trigger_swing()

                # Toggle Guide Dialogue
                elif event.key == pygame.K_g:
                    self.ui.dialogue_open = not self.ui.dialogue_open
                    if self.ui.dialogue_open and not self.ui.dialogue_text:
                        self._trigger_guide_query("What should I do first?")

                # In Dialogue Quick Prompts
                elif self.ui.dialogue_open:
                    if event.key == pygame.K_ESCAPE:
                        self.ui.dialogue_open = False
                    elif event.key == pygame.K_1:
                        self._trigger_guide_query("What should I do first?")
                    elif event.key == pygame.K_2:
                        self._trigger_guide_query("How do I build a valid house for NPCs?")
                    elif event.key == pygame.K_3:
                        self._trigger_guide_query("What can I craft with the items in my pack?")
                    elif event.key == pygame.K_4:
                        self._trigger_guide_query("What dangers lurk underground?")

            # Mouse wheel cycles hotbar
            elif event.type == pygame.MOUSEWHEEL:
                cur = self.player.inventory.selected_slot
                new_slot = (cur - event.y) % 10
                self.player.inventory.select_slot(new_slot)

    def _trigger_guide_query(self, question: str):
        self.ui.guide_thinking = True
        self.ui.dialogue_text = ""
        self.ui.dialogue_displayed = ""

        depth_tile = int(self.player.y // TILE_SIZE)
        stratum = "Surface"
        if depth_tile < STRATA_SURFACE_START:
            stratum = "Sky"
        elif depth_tile < STRATA_UNDERGROUND_END:
            stratum = "Underground"
        elif depth_tile < STRATA_CAVERNS_END:
            stratum = "Caverns"
        elif depth_tile >= STRATA_UNDERWORLD_START:
            stratum = "Underworld"

        time_str = "Day" if 0.2 <= self.day_time <= 0.8 else "Night"

        ctx = {
            "stratum": stratum,
            "time_of_day": time_str,
            "health": self.player.health,
            "max_health": self.player.max_health,
            "inventory_summary": self.player.inventory.get_summary_for_ai(),
        }

        self.ai.query_guide_async(ctx, question)

    def update(self):
        # 1. Update Combat Juice (Screen Shake & Freeze Frame Hitstop)
        shake_x, shake_y, hitstop = self.juice.update()
        self.shake_offset = (shake_x, shake_y)

        # Freeze Frame: skip entity physics to give palpable punchy hit pause
        if hitstop:
            return

        # 2. Day / Night cycle progression
        self.day_time = (self.day_time + self.time_speed) % 1.0

        # 3. Player Input & Physics
        keys = pygame.key.get_pressed()
        self.player.update(keys, self.world, floor_y=self.floor_pixel_y)
        self.dummy.update(floor_y=self.floor_pixel_y)
        self.guide_npc.update(self.world)

        # 4. Sword Attack & Hitbox Collision Detection
        selected_stack = self.player.inventory.get_selected()
        mouse_buttons = pygame.mouse.get_pressed()

        # If holding sword or weapon, left click triggers sword swing!
        if mouse_buttons[0] and not self.ui.dialogue_open:
            if selected_stack and selected_stack.item_def and selected_stack.item_def.item_type in ("weapon", "tool"):
                self.player.trigger_swing()

        # Check Sword Hitbox against Dummy
        sword_hitbox = self.player.get_sword_hitbox()
        if sword_hitbox and self.dummy.is_alive and (id(self.dummy) not in self.player.already_hit):
            if sword_hitbox.colliderect(self.dummy.rect):
                self.player.already_hit.add(id(self.dummy))

                # Calculate damage with 20% critical strike chance
                is_crit = random.random() < 0.20
                base_dmg = 14
                final_dmg = (base_dmg + random.randint(-2, 3)) * (2 if is_crit else 1)

                # Directional knockback
                kb_dir = 1.0 if self.player.facing_right else -1.0
                self.dummy.take_hit(final_dmg, kb_dir, knockback_force=4.8)

                # Juice: Screen Shake & Hit Pause
                self.juice.trigger_hit(shake_amount=4.0, hitstop_count=3)

                # Spawn floating damage number
                num_x = self.dummy.center[0]
                num_y = self.dummy.y - 4
                self.damage_numbers.append(DamageNumber(num_x, num_y, final_dmg, is_crit))

        # Update floating damage numbers
        self.damage_numbers = [d for d in self.damage_numbers if d.update()]

        # 5. Mouse Tile Interaction (if not clicking sword on enemies)
        if mouse_buttons[2] and not self.ui.dialogue_open:  # Right click: Place / open door
            mx, my = pygame.mouse.get_pos()
            scale_x = INTERNAL_WIDTH / WINDOW_WIDTH
            scale_y = INTERNAL_HEIGHT / WINDOW_HEIGHT
            world_mx = int(mx * scale_x + self.cam_x)
            world_my = int(my * scale_y + self.cam_y)
            target_tx = world_mx // TILE_SIZE
            target_ty = world_my // TILE_SIZE
            self.player.interact_tile(target_tx, target_ty, self.world, is_primary=False)

        # 6. Smooth Camera Lerp Tracking
        target_cam_x = self.player.x - INTERNAL_WIDTH // 2
        target_cam_y = self.player.y - INTERNAL_HEIGHT // 2
        self.cam_x += (target_cam_x - self.cam_x) * 0.12
        self.cam_y += (target_cam_y - self.cam_y) * 0.12

        # Clamp camera to world bounds
        self.cam_x = max(0, min(self.cam_x, self.world.width * TILE_SIZE - INTERNAL_WIDTH))
        self.cam_y = max(0, min(self.cam_y, self.world.height * TILE_SIZE - INTERNAL_HEIGHT))

        # 7. Poll AI tokens
        if self.ai.is_thinking or not self.ai.dialogue_queue.empty():
            token = self.ai.poll_token()
            if token:
                self.ui.dialogue_text += token
                self.ui.guide_thinking = False
        elif not self.ai.is_thinking:
            self.ui.guide_thinking = False

        self.ui.update_typewriter()

    def render(self):
        # 1. Sky color based on time of day
        day_factor = math.sin(self.day_time * 2 * math.pi)
        day_light_ratio = max(0.0, day_factor)

        if day_light_ratio > 0.1:
            sky_r = int(120 * day_light_ratio + 10)
            sky_g = int(180 * day_light_ratio + 15)
            sky_b = int(255 * day_light_ratio + 35)
        else:
            sky_r, sky_g, sky_b = (12, 14, 28)

        self.canvas.fill((sky_r, sky_g, sky_b))

        # Stars at night
        if day_light_ratio < 0.25:
            for sx, sy, sz in self.stars:
                pygame.draw.circle(self.canvas, (240, 240, 255), (sx, sy), sz)

        # Camera with screen shake offset
        cam_xi = int(self.cam_x + self.shake_offset[0])
        cam_yi = int(self.cam_y + self.shake_offset[1])

        # 2. Render Background Walls
        min_tx = max(0, cam_xi // TILE_SIZE)
        max_tx = min(self.world.width, (cam_xi + INTERNAL_WIDTH) // TILE_SIZE + 2)
        min_ty = max(0, cam_yi // TILE_SIZE)
        max_ty = min(self.world.height, (cam_yi + INTERNAL_HEIGHT) // TILE_SIZE + 2)

        for ty in range(min_ty, max_ty):
            for tx in range(min_tx, max_tx):
                wall_id = self.world.get_wall(tx, ty)
                if wall_id != AIR:
                    tile_def = TILE_REGISTRY.get(wall_id)
                    if tile_def:
                        wc = (tile_def.base_color[0] // 2, tile_def.base_color[1] // 2, tile_def.base_color[2] // 2)
                        rect = pygame.Rect(tx * TILE_SIZE - cam_xi, ty * TILE_SIZE - cam_yi, TILE_SIZE, TILE_SIZE)
                        pygame.draw.rect(self.canvas, wc, rect)

        # 3. Render Foreground Tiles
        for ty in range(min_ty, max_ty):
            for tx in range(min_tx, max_tx):
                tile_id = self.world.get_tile(tx, ty)
                if tile_id != AIR:
                    tile_def = TILE_REGISTRY.get(tile_id)
                    if tile_def:
                        rect = pygame.Rect(tx * TILE_SIZE - cam_xi, ty * TILE_SIZE - cam_yi, TILE_SIZE, TILE_SIZE)
                        pygame.draw.rect(self.canvas, tile_def.base_color, rect)
                        if tile_def.border_color:
                            pygame.draw.rect(self.canvas, tile_def.border_color, rect, 1)

                        if tile_id == TORCH:
                            flame_rect = pygame.Rect(rect.centerx - 2, rect.top + 2, 4, 6)
                            flicker = random.choice([(255, 230, 100), (255, 180, 40)])
                            pygame.draw.rect(self.canvas, flicker, flame_rect)

        # 4. Render Guide NPC
        npc_rect = pygame.Rect(int(self.guide_npc.x - cam_xi), int(self.guide_npc.y - cam_yi), self.guide_npc.width, self.guide_npc.height)
        pygame.draw.rect(self.canvas, (50, 120, 200), npc_rect)
        pygame.draw.rect(self.canvas, (230, 180, 130), pygame.Rect(npc_rect.x, npc_rect.y, npc_rect.width, 10))
        pygame.draw.rect(self.canvas, (80, 50, 20), pygame.Rect(npc_rect.x, npc_rect.y, npc_rect.width, 4))

        # 5. Render Training Dummy Enemy
        self.dummy.draw(self.canvas, cam_xi, cam_yi, self.combat_font)

        # 6. Render Player with State Machine & Sword Swing Arc
        self.player.draw(self.canvas, cam_xi, cam_yi)

        # 7. Render Floating Damage Numbers
        for dmg_num in self.damage_numbers:
            dmg_num.draw(self.canvas, self.combat_font, cam_xi, cam_yi)

        # 8. Dynamic Lighting Pass
        self.lighting.render_lighting(self.canvas, self.world, cam_xi, cam_yi, day_light_ratio)

        # 9. UI Layer (HUD, Hearts, Dialogue)
        depth_tile = int(self.player.y // TILE_SIZE)
        stratum_name = "Surface"
        if depth_tile < STRATA_SURFACE_START:
            stratum_name = "Sky"
        elif depth_tile < STRATA_UNDERGROUND_END:
            stratum_name = "Underground"
        elif depth_tile < STRATA_CAVERNS_END:
            stratum_name = "Caverns"
        elif depth_tile >= STRATA_UNDERWORLD_START:
            stratum_name = "Underworld"

        time_hours = int((self.day_time * 24 + 6) % 24)
        time_minutes = int((self.day_time * 24 * 60) % 60)
        am_pm = "AM" if time_hours < 12 else "PM"
        display_hour = 12 if time_hours in (0, 12) else time_hours % 12
        time_str = f"{display_hour:02d}:{time_minutes:02d} {am_pm}"

        self.ui.render_hud(self.canvas, self.player, time_str, stratum_name)
        self.ui.render_dialogue(self.canvas)

        # Controls banner at bottom
        controls_msg = "A/D: Run • Space: Jump (Hold for high) • Click / J: Sword Slash • G: Guide AI"
        ctrl_surf = self.hint_font.render(controls_msg, True, (240, 240, 255))
        # Draw dark shadow behind controls banner
        sh_surf = self.hint_font.render(controls_msg, True, (16, 16, 26))
        bx = INTERNAL_WIDTH // 2 - ctrl_surf.get_width() // 2
        by = INTERNAL_HEIGHT - 14
        self.canvas.blit(sh_surf, (bx + 1, by + 1))
        self.canvas.blit(ctrl_surf, (bx, by))

        # 10. Blit Canvas to Full Window
        pygame.transform.scale(self.canvas, (WINDOW_WIDTH, WINDOW_HEIGHT), self.window)
        pygame.display.flip()
