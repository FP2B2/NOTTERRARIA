"""
Player Entity with responsive platformer physics:
Smooth acceleration/deceleration, variable jump height, coyote time,
jump buffering, landing squash & stretch, and sword combat hitbox generation.
"""

import math
import pygame
from typing import Optional, Tuple, Set
from .config import TILE_SIZE, GRAVITY, TERMINAL_VELOCITY
from .tiles import AIR, DOOR_CLOSED, DOOR_OPEN, WOOD, LEAVES, TILE_REGISTRY
from .inventory import Inventory
from .animation import PlayerAnimator
from .audio import SoundManager


class Player:
    def __init__(self, x_pixel: float, y_pixel: float):
        self.x = x_pixel
        self.y = y_pixel
        self.width = 14
        self.height = 26
        self.vx = 0.0
        self.vy = 0.0

        # Ground detection & Jump feel
        self.on_ground = False
        self.was_on_ground = False
        self.coyote_timer = 0       # frames player can jump after leaving ground (~100ms = 6 frames)
        self.jump_buffer_timer = 0  # frames jump press is remembered before touching ground (~116ms = 7 frames)
        self.is_jumping = False     # whether current ascent was initiated by a jump
        self.landing_squash = 0     # frames for squash effect on landing

        # Physics tuning (smooth acceleration & deceleration)
        self.run_speed = 2.9
        self.accel = 0.28
        self.friction = 0.82
        self.jump_force = -7.4

        # Facing direction
        self.facing_right = True

        # Sword Swing & Combat
        self.is_swinging = False
        self.swing_timer = 0
        self.swing_duration = 14     # frames per swing
        self.swing_cooldown = 0     # recovery frames between swings
        self.already_hit: Set[int] = set()  # entity IDs hit in current swing
        self.sword_damage = 14

        # Stats
        self.health = 100
        self.max_health = 100
        self.mana = 20
        self.max_mana = 20
        self.defense = 0

        # Inventory (spawns with sword in slot 0)
        self.inventory = Inventory()

        # Customization Appearance
        self.name = "Player"
        self.hair_style = 0
        self.hair_color = (143, 86, 59)
        self.skin_tone = (238, 195, 154)
        self.shirt_color = (91, 110, 225)
        self.pants_color = (63, 63, 116)
        self.difficulty = "Normal"

        # Animator helper
        self.animator = PlayerAnimator()
        self.sound = SoundManager.get()

        # Interaction reach
        self.reach_distance = 5.5 * TILE_SIZE

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    @property
    def center(self) -> Tuple[float, float]:
        return self.x + self.width / 2.0, self.y + self.height / 2.0

    def trigger_swing(self):
        """Initiates a sword swing if not already swinging or in cooldown."""
        if self.swing_timer <= 0 and self.swing_cooldown <= 0:
            self.is_swinging = True
            self.swing_timer = self.swing_duration
            self.already_hit.clear()
            self.sound.play("sword_swing")

    def get_sword_hitbox(self) -> Optional[pygame.Rect]:
        """
        Returns active sword collision hitbox during the middle frames of the swing.
        Hits are registered during frames 3 through 9 of the 14-frame swing.
        """
        if not self.is_swinging:
            return None

        current_frame = self.swing_duration - self.swing_timer
        if 3 <= current_frame <= 9:
            reach = 22
            box_h = 24
            cx, cy = self.center
            if self.facing_right:
                return pygame.Rect(int(cx + 2), int(cy - 12), reach, box_h)
            else:
                return pygame.Rect(int(cx - 2 - reach), int(cy - 12), reach, box_h)
        return None

    def update(self, keys, world=None, floor_y: Optional[float] = None, dt: float = 1.0):
        # 1. Update Coyote Time & Landing Squash
        if self.on_ground:
            self.coyote_timer = 6  # 6 frames (~100ms) coyote time
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1

        if self.landing_squash > 0:
            self.landing_squash -= 1


        # 2. Horizontal Movement (Smooth acceleration & deceleration)
        target_vx = 0.0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            target_vx -= self.run_speed
            self.facing_right = False
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            target_vx += self.run_speed
            self.facing_right = True

        if target_vx != 0:
            self.vx += (target_vx - self.vx) * self.accel
        else:
            self.vx *= self.friction
            if abs(self.vx) < 0.08:
                self.vx = 0.0

        # Update walk animation timer
        self.animator.update_walk(self.vx, dt)

        # 3. Jump Input, Buffering & Variable Jump Height
        jump_pressed = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

        if jump_pressed:
            self.jump_buffer_timer = 7  # buffer for 7 frames (~116ms)
        elif self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= 1

        # Check if buffered jump can execute
        drop_through = keys[pygame.K_s] or keys[pygame.K_DOWN]
        if self.jump_buffer_timer > 0 and (self.on_ground or self.coyote_timer > 0) and not drop_through:
            self.vy = self.jump_force
            self.on_ground = False
            self.coyote_timer = 0
            self.jump_buffer_timer = 0
            self.is_jumping = True

        # Variable jump height: cut vertical speed if jump key is released early during ascent
        if not jump_pressed and self.is_jumping and self.vy < -2.0:
            self.vy *= 0.52
            self.is_jumping = False

        # Gravity
        self.vy += GRAVITY
        if self.vy > TERMINAL_VELOCITY:
            self.vy = TERMINAL_VELOCITY

        # 4. Movement & Collision
        self._move_and_collide(world, floor_y, drop_through)

        # 5. Combat Swing Timing
        if self.swing_timer > 0:
            self.swing_timer -= 1
            if self.swing_timer <= 0:
                self.is_swinging = False
                self.swing_cooldown = 4  # brief 4-frame cooldown
        elif self.swing_cooldown > 0:
            self.swing_cooldown -= 1

        # Check 'J' key for keyboard attack
        if keys[pygame.K_j]:
            self.trigger_swing()

    def _move_and_collide(self, world, floor_y: Optional[float], drop_through: bool):
        # Move Horizontal
        self.x += self.vx
        rect_x = self.rect

        if world is not None:
            min_tx = max(0, rect_x.left // TILE_SIZE)
            max_tx = min(world.width - 1, rect_x.right // TILE_SIZE)
            min_ty = max(0, rect_x.top // TILE_SIZE)
            max_ty = min(world.height - 1, rect_x.bottom // TILE_SIZE)

            for ty in range(min_ty, max_ty + 1):
                for tx in range(min_tx, max_tx + 1):
                    if world.is_solid(tx, ty):
                        tile_rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        if rect_x.colliderect(tile_rect):
                            if self.vx > 0:
                                self.x = tile_rect.left - self.width
                                self.vx = 0.0
                            elif self.vx < 0:
                                self.x = tile_rect.right
                                self.vx = 0.0
                            rect_x = self.rect

        # Move Vertical
        self.y += self.vy
        rect_y = self.rect
        self.on_ground = False

        # Flat Test Floor Collision
        if floor_y is not None:
            if self.y + self.height >= floor_y:
                self.y = floor_y - self.height
                if self.vy > 0:
                    self.landing_squash = 6
                self.vy = 0.0
                self.on_ground = True
                rect_y = self.rect

        # World Tile Collision
        if world is not None and not self.on_ground:
            min_tx = max(0, rect_y.left // TILE_SIZE)
            max_tx = min(world.width - 1, rect_y.right // TILE_SIZE)
            min_ty = max(0, rect_y.top // TILE_SIZE)
            max_ty = min(world.height - 1, rect_y.bottom // TILE_SIZE)

            for ty in range(min_ty, max_ty + 1):
                for tx in range(min_tx, max_tx + 1):
                    is_solid = world.is_solid(tx, ty)
                    is_plat = world.is_platform(tx, ty)

                    if is_solid or (is_plat and not drop_through and self.vy >= 0):
                        tile_rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        if rect_y.colliderect(tile_rect):
                            if self.vy > 0 and rect_y.bottom - self.vy <= tile_rect.top + 6:
                                self.y = tile_rect.top - self.height
                                self.landing_squash = 6
                                self.vy = 0.0
                                self.on_ground = True
                            elif self.vy < 0 and is_solid:
                                self.y = tile_rect.bottom
                                self.vy = 0.0
                            rect_y = self.rect

    def draw(self, surface: pygame.Surface, cam_x: int, cam_y: int):
        """Renders the player sprite with state machine, squash & stretch, and sword swing arc."""
        dx = int(self.x - cam_x)
        dy = int(self.y - cam_y)

        # Determine animation state
        state = self.animator.get_state(self.vx, self.vy, self.on_ground, self.is_swinging)

        # Calculate squash factor on landing
        squash_y = 0
        squash_x = 0
        if self.landing_squash > 0:
            squash_y = int((self.landing_squash / 6.0) * 3)
            squash_x = int((self.landing_squash / 6.0) * 4)

        swing_prog = 0.0
        if self.is_swinging:
            swing_prog = 1.0 - (self.swing_timer / self.swing_duration)

        # Draw Player Body
        self.animator.draw_player(
            surface=surface,
            x=dx,
            y=dy,
            state=state,
            facing_right=self.facing_right,
            hair_style=self.hair_style,
            hair_color=self.hair_color,
            skin_tone=self.skin_tone,
            shirt_color=self.shirt_color,
            pants_color=self.pants_color,
            squash_y=squash_y,
            squash_x=squash_x,
            swing_progress=swing_prog,
        )

        # Draw Sword Swing Arc
        if self.is_swinging:
            cx = dx + self.width // 2
            cy = dy + self.height // 2
            self.animator.draw_sword_swing_arc(
                surface=surface,
                player_cx=cx,
                player_cy=cy,
                facing_right=self.facing_right,
                progress=swing_prog,
            )
