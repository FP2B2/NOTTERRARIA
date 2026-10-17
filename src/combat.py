"""
Combat system: Hitbox detection, Training Dummy enemy, floating damage numbers,
hitstop (freeze frame), screen shake juice, and respawn mechanics.
"""

import math
import random
import pygame
from typing import List, Tuple, Set, Optional
from .sprites import PALETTE
from .audio import SoundManager


class DamageNumber:
    def __init__(self, x: float, y: float, damage: int, is_crit: bool = False):
        self.x = x + random.uniform(-4, 4)
        self.y = y
        self.damage = damage
        self.is_crit = is_crit
        self.vy = -1.8
        self.vx = random.uniform(-0.6, 0.6)
        self.alpha = 255.0
        self.life = 0
        self.max_life = 45  # frames (~0.75s)

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.04  # gentle gravity deceleration
        self.life += 1
        if self.life > 25:
            self.alpha = max(0.0, 255.0 * (1.0 - (self.life - 25) / 20.0))
        return self.life < self.max_life

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, cam_x: int, cam_y: int):
        sx = int(self.x - cam_x)
        sy = int(self.y - cam_y)

        text = str(self.damage)
        color = (255, 140, 40) if self.is_crit else (255, 230, 50)  # Orange for crit, yellow for standard

        # Text with shadow
        shadow_surf = font.render(text, True, (20, 20, 30))
        text_surf = font.render(text, True, color)

        if self.alpha < 250:
            shadow_surf.set_alpha(int(self.alpha))
            text_surf.set_alpha(int(self.alpha))

        surface.blit(shadow_surf, (sx + 1, sy + 1))
        surface.blit(text_surf, (sx, sy))


class TrainingDummy:
    """
    Combat Training Dummy (Green Slime / Target Dummy).
    Features health, hit flash, knockback physics, health bar, and auto-respawn.
    """
    def __init__(self, x_pixel: float, y_pixel: float):
        self.home_x = x_pixel
        self.home_y = y_pixel
        self.x = x_pixel
        self.y = y_pixel
        self.width = 20
        self.height = 16
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = True

        # Health
        self.max_hp = 50
        self.hp = 50
        self.is_alive = True
        self.respawn_timer = 0.0  # seconds until respawn

        # Hit reaction
        self.hit_flash_timer = 0  # frames to render pure white
        self.damaged_recently = 0

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    @property
    def center(self) -> Tuple[float, float]:
        return self.x + self.width / 2.0, self.y + self.height / 2.0

    def take_hit(self, damage: int, knockback_dir: float, knockback_force: float = 4.2):
        if not self.is_alive:
            return

        self.hp -= damage
        self.hit_flash_timer = 5  # 5 frames of pure white flash
        self.damaged_recently = 120  # show health bar for 2 seconds

        # Apply directional knockback
        self.vx = knockback_dir * knockback_force
        self.vy = -2.4  # slight pop into air
        self.on_ground = False

        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False
            self.respawn_timer = 2.5  # Respawn after 2.5 seconds
            SoundManager.get().play("enemy_die")

    def update(self, floor_y: float):
        if not self.is_alive:
            self.respawn_timer -= 1.0 / 60.0
            if self.respawn_timer <= 0:
                self.respawn()
            return

        # Decay hit flash
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
        if self.damaged_recently > 0:
            self.damaged_recently -= 1

        # Horizontal physics & friction
        self.x += self.vx
        self.vx *= 0.85
        if abs(self.vx) < 0.05:
            self.vx = 0.0

        # Gravity & Floor Collision
        self.vy += 0.38
        if self.vy > 8.0:
            self.vy = 8.0
        self.y += self.vy

        if self.y + self.height >= floor_y:
            self.y = floor_y - self.height
            self.vy = 0.0
            self.on_ground = True

    def respawn(self):
        self.x = self.home_x
        self.y = self.home_y
        self.vx = 0.0
        self.vy = 0.0
        self.hp = self.max_hp
        self.is_alive = True
        self.hit_flash_timer = 0
        self.damaged_recently = 0

    def draw(self, surface: pygame.Surface, cam_x: int, cam_y: int, font: pygame.font.Font):
        if not self.is_alive:
            return

        dx = int(self.x - cam_x)
        dy = int(self.y - cam_y)

        # 1. Slime Body (Matching the uploaded reference green slime!)
        slime_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.hit_flash_timer > 0:
            # Pure white silhouette hit flash
            pygame.draw.ellipse(slime_surf, (255, 255, 255), (0, 0, self.width, self.height))
        else:
            # Main jelly green dome
            base_green = (67, 160, 71)
            dark_green = (35, 95, 45)
            highlight_green = (120, 215, 90)

            pygame.draw.ellipse(slime_surf, dark_green, (0, 0, self.width, self.height))
            pygame.draw.ellipse(slime_surf, base_green, (1, 1, self.width - 2, self.height - 2))
            # Jelly shine highlight on top-left
            pygame.draw.ellipse(slime_surf, highlight_green, (3, 2, 7, 4))
            pygame.draw.ellipse(slime_surf, (220, 255, 200), (4, 3, 3, 2))

            # Flat bottom base
            pygame.draw.line(slime_surf, (20, 60, 25), (2, self.height - 1), (self.width - 3, self.height - 1), 2)

        surface.blit(slime_surf, (dx, dy))

        # 2. Health Bar (Displayed when damaged)
        if self.damaged_recently > 0 and self.hp > 0:
            bar_w = 24
            bar_h = 4
            bx = dx + (self.width - bar_w) // 2
            by = dy - 8

            hp_ratio = max(0.0, self.hp / self.max_hp)
            pygame.draw.rect(surface, (20, 20, 30), (bx - 1, by - 1, bar_w + 2, bar_h + 2))
            pygame.draw.rect(surface, (180, 40, 40), (bx, by, bar_w, bar_h))  # Red missing
            pygame.draw.rect(surface, (80, 220, 90), (bx, by, int(bar_w * hp_ratio), bar_h))  # Green remaining

        # 3. Label above dummy
        lbl_surf = font.render("Dummy", True, (190, 200, 220))
        surface.blit(lbl_surf, (dx + (self.width - lbl_surf.get_width()) // 2, dy - 18))


class CombatJuiceManager:
    """
    Manages Screen Shake and HitStop (Freeze-frame) juice for combat impact.
    """
    def __init__(self):
        self.shake_duration = 0
        self.shake_intensity = 0.0
        self.hitstop_frames = 0
        self.sound = SoundManager.get()

    def trigger_hit(self, shake_amount: float = 3.5, hitstop_count: int = 3):
        """Called upon successful sword hit."""
        self.shake_duration = 6  # frames
        self.shake_intensity = shake_amount
        self.hitstop_frames = hitstop_count  # ~50ms freeze frame
        self.sound.play("hit_impact")

    def update(self) -> Tuple[int, int, bool]:
        """
        Updates juice timers.
        Returns (offset_x, offset_y, should_freeze_frame).
        """
        # Hitstop check
        if self.hitstop_frames > 0:
            self.hitstop_frames -= 1
            return 0, 0, True  # Freeze gameplay update

        # Screen shake
        ox, oy = 0, 0
        if self.shake_duration > 0:
            self.shake_duration -= 1
            damping = self.shake_duration / 6.0
            ox = int((random.random() * 2.0 - 1.0) * self.shake_intensity * damping)
            oy = int((random.random() * 2.0 - 1.0) * self.shake_intensity * damping)

        return ox, oy, False
