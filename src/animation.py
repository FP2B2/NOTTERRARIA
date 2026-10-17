"""
Player animation system, walk cycles, squash & stretch, and sword swing visual arcs.
Strict pixel-art style drawn in code with crisp scaling.
"""

import math
import pygame
from typing import Tuple, Optional
from .sprites import PALETTE


class PlayerAnimator:
    def __init__(self):
        self.walk_timer = 0.0
        self.walk_frame = 0

    def get_state(self, vx: float, vy: float, on_ground: bool, is_swinging: bool) -> str:
        if is_swinging:
            return "swing"
        if not on_ground:
            return "jump" if vy < -0.5 else "fall"
        if abs(vx) > 0.2:
            return "run"
        return "idle"

    def update_walk(self, vx: float, dt: float):
        if abs(vx) > 0.2:
            self.walk_timer += abs(vx) * 0.18
            self.walk_frame = int(self.walk_timer) % 4
        else:
            self.walk_timer = 0.0
            self.walk_frame = 0

    def draw_player(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        state: str,
        facing_right: bool,
        hair_style: int,
        hair_color: Tuple[int, int, int],
        skin_tone: Tuple[int, int, int],
        shirt_color: Tuple[int, int, int],
        pants_color: Tuple[int, int, int],
        squash_y: int = 0,
        squash_x: int = 0,
        swing_progress: float = 0.0,
    ):
        """
        Draws the animated pixel-art player in their current state.
        Dimensions: 16x26 base character.
        """
        char_surf = pygame.Surface((18, 28), pygame.SRCALPHA)

        def shade(color, mult=0.75):
            return (int(color[0] * mult), int(color[1] * mult), int(color[2] * mult))

        def tint(color, mult=1.25):
            return (min(255, int(color[0] * mult)), min(255, int(color[1] * mult)), min(255, int(color[2] * mult)))

        skin_dark = shade(skin_tone, 0.78)
        shirt_dark = shade(shirt_color, 0.72)
        pants_dark = shade(pants_color, 0.70)
        hair_dark = shade(hair_color, 0.65)
        hair_light = tint(hair_color, 1.2)

        # Base offsets depending on state
        bob_y = 0
        leg_offset_l = 0
        leg_offset_r = 0
        arm_angle = 0.0

        if state == "idle":
            # 1px breathing bob
            bob_y = 1 if int(pygame.time.get_ticks() / 350) % 2 == 1 else 0
        elif state == "run":
            # 4-frame walk cycle
            # Frame 0: Right leg forward, Left back
            # Frame 1: Center stride
            # Frame 2: Left leg forward, Right back
            # Frame 3: Center stride
            if self.walk_frame == 0:
                leg_offset_r = -2
                leg_offset_l = 2
                bob_y = 1
            elif self.walk_frame == 2:
                leg_offset_r = 2
                leg_offset_l = -2
                bob_y = 1
            else:
                bob_y = 0
        elif state == "jump":
            bob_y = -1
            leg_offset_r = -1
            leg_offset_l = -1
        elif state == "fall":
            bob_y = 0
            leg_offset_r = 1
            leg_offset_l = 1

        # 1. HEAD & EYES
        hy = 3 + bob_y
        pygame.draw.rect(char_surf, skin_tone, (4, hy, 10, 8))
        pygame.draw.rect(char_surf, skin_dark, (5, hy + 7, 8, 1))
        # Neck
        pygame.draw.rect(char_surf, skin_dark, (7, hy + 8, 4, 2))

        # Eyes (Facing direction aware)
        eye_x = 7 if facing_right else 5
        pygame.draw.rect(char_surf, (20, 20, 30), (eye_x, hy + 3, 2, 2))
        pygame.draw.rect(char_surf, (255, 255, 255), (eye_x, hy + 3, 1, 1))
        if facing_right:
            pygame.draw.rect(char_surf, (20, 20, 30), (eye_x + 4, hy + 3, 2, 2))
            pygame.draw.rect(char_surf, (255, 255, 255), (eye_x + 4, hy + 3, 1, 1))
        else:
            pygame.draw.rect(char_surf, (20, 20, 30), (eye_x - 4, hy + 3, 2, 2))
            pygame.draw.rect(char_surf, (255, 255, 255), (eye_x - 4, hy + 3, 1, 1))

        # 2. HAIRSTYLE
        if hair_style == 0:  # Adventurer
            pygame.draw.rect(char_surf, hair_color, (3, hy - 3, 12, 4))
            pygame.draw.rect(char_surf, hair_light, (5, hy - 3, 6, 2))
            pygame.draw.rect(char_surf, hair_color, (3, hy, 2, 5))
            pygame.draw.rect(char_surf, hair_color, (13, hy, 2, 5))
            fringe_x = 7 if facing_right else 5
            pygame.draw.rect(char_surf, hair_dark, (fringe_x, hy + 1, 3, 2))
        elif hair_style == 1:  # Spiky
            pygame.draw.rect(char_surf, hair_color, (4, hy - 2, 10, 3))
            pygame.draw.rect(char_surf, hair_light, (5, hy - 4, 3, 3))
            pygame.draw.rect(char_surf, hair_light, (10, hy - 4, 3, 3))
            pygame.draw.rect(char_surf, hair_dark, (3, hy - 1, 2, 4))
            pygame.draw.rect(char_surf, hair_dark, (13, hy - 1, 2, 4))
        elif hair_style == 2:  # Long Explorer
            pygame.draw.rect(char_surf, hair_color, (3, hy - 3, 12, 4))
            pygame.draw.rect(char_surf, hair_light, (5, hy - 3, 7, 2))
            pygame.draw.rect(char_surf, hair_color, (2, hy, 3, 10))
            pygame.draw.rect(char_surf, hair_dark, (13, hy, 3, 10))
        elif hair_style == 3:  # Mohawk
            pygame.draw.rect(char_surf, hair_color, (7, hy - 4, 4, 6))
            pygame.draw.rect(char_surf, hair_light, (8, hy - 4, 2, 3))
        elif hair_style == 4:  # Ponytail
            pygame.draw.rect(char_surf, hair_color, (3, hy - 3, 12, 4))
            ribbon_x = 2 if facing_right else 14
            tail_x = 0 if facing_right else 15
            pygame.draw.rect(char_surf, (223, 113, 38), (ribbon_x, hy - 1, 2, 2))
            pygame.draw.rect(char_surf, hair_color, (tail_x, hy + 1, 3, 6))
        else:  # Short Crop
            pygame.draw.rect(char_surf, hair_color, (4, hy - 2, 10, 3))
            pygame.draw.rect(char_surf, hair_dark, (3, hy, 2, 3))
            pygame.draw.rect(char_surf, hair_dark, (13, hy, 2, 3))

        # 3. TORSO & SHIRT
        ty = hy + 9
        pygame.draw.rect(char_surf, shirt_color, (4, ty, 10, 6))
        pygame.draw.rect(char_surf, shirt_dark, (4, ty + 5, 10, 1))
        pygame.draw.rect(char_surf, tint(shirt_color, 1.2), (7, ty, 4, 1))

        # Belt
        pygame.draw.rect(char_surf, (102, 57, 49), (4, ty + 6, 10, 1))
        pygame.draw.rect(char_surf, (251, 242, 54), (8, ty + 6, 2, 1))

        # 4. PANTS & LEGS (with walk offsets)
        py_legs = ty + 7
        # Left Leg
        pygame.draw.rect(char_surf, pants_color, (4, py_legs + leg_offset_l, 4, 6))
        # Right Leg
        pygame.draw.rect(char_surf, pants_color, (10, py_legs + leg_offset_r, 4, 6))
        # Inner leg gap
        pygame.draw.rect(char_surf, pants_dark, (8, py_legs, 2, 5))

        # 5. BOOTS
        pygame.draw.rect(char_surf, (102, 57, 49), (3, py_legs + 6 + leg_offset_l, 5, 2))
        pygame.draw.rect(char_surf, (102, 57, 49), (10, py_legs + 6 + leg_offset_r, 5, 2))

        # 6. ARMS (unless swinging sword)
        if not is_swinging:
            arm_swing_l = -leg_offset_l
            arm_swing_r = -leg_offset_r
            # Left Arm
            pygame.draw.rect(char_surf, shirt_color, (2, ty + arm_swing_l, 2, 4))
            pygame.draw.rect(char_surf, skin_tone, (2, ty + 4 + arm_swing_l, 2, 2))
            # Right Arm
            pygame.draw.rect(char_surf, shirt_color, (14, ty + arm_swing_r, 2, 4))
            pygame.draw.rect(char_surf, skin_tone, (14, ty + 4 + arm_swing_r, 2, 2))

        # Apply squash & stretch transform on landing
        draw_w = 18 + squash_x
        draw_h = 28 - squash_y
        final_surf = pygame.transform.scale(char_surf, (draw_w, draw_h))

        # Blit adjusted for squash anchor at bottom
        surface.blit(final_surf, (x - squash_x // 2, y + squash_y))

    def draw_sword_swing_arc(
        self,
        surface: pygame.Surface,
        player_cx: int,
        player_cy: int,
        facing_right: bool,
        progress: float,  # 0.0 to 1.0
        sword_color: Tuple[int, int, int] = (205, 218, 226),  # Silver/Iron blade
        hilt_color: Tuple[int, int, int] = (143, 86, 59),
    ):
        """
        Draws Terraria-style sword swing with swooshing crescent slice arc.
        Progress 0.0 = back high, 0.5 = forward slice, 1.0 = follow-through down.
        """
        # Arc sweeps from -110 deg (overhead-back) down to +55 deg (forward-low)
        start_angle = -115 if facing_right else -65
        end_angle = 50 if facing_right else 230

        if facing_right:
            angle_deg = start_angle + progress * 165
        else:
            angle_deg = 180 - (-115 + progress * 165)

        rad = math.radians(angle_deg)
        blade_len = 22
        hilt_len = 6

        # Hand pivot point
        hx = player_cx + (5 if facing_right else -5)
        hy = player_cy - 1

        # Blade tip
        tx = hx + math.cos(rad) * blade_len
        ty = hy + math.sin(rad) * blade_len

        # Guard position
        gx = hx + math.cos(rad) * hilt_len
        gy = hy + math.sin(rad) * hilt_len

        # 1. Crescent Slice Swoosh Trail (for middle frames of swing)
        if 0.15 <= progress <= 0.85:
            arc_alpha = int(math.sin((progress - 0.15) / 0.70 * math.pi) * 230)
            arc_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)

            trail_pts = []
            steps = 8
            trail_span = 45 if facing_right else -45
            for s in range(steps + 1):
                t_ratio = s / steps
                t_angle = rad - math.radians(trail_span * (1.0 - t_ratio))
                dist = blade_len + 3
                px = hx + math.cos(t_angle) * dist
                py = hy + math.sin(t_angle) * dist
                trail_pts.append((px, py))

            # Inner edge of trail
            for s in range(steps, -1, -1):
                t_ratio = s / steps
                t_angle = rad - math.radians(trail_span * (1.0 - t_ratio))
                dist = blade_len - 6
                px = hx + math.cos(t_angle) * dist
                py = hy + math.sin(t_angle) * dist
                trail_pts.append((px, py))

            if len(trail_pts) >= 3:
                # Translucent cyan/white crescent slash effect
                pygame.draw.polygon(arc_surf, (220, 245, 255, arc_alpha), trail_pts)
                pygame.draw.polygon(arc_surf, (140, 210, 255, arc_alpha // 2), trail_pts, 2)
                surface.blit(arc_surf, (0, 0))

        # 2. Draw Hilt (Dark brown leather wrap)
        pygame.draw.line(surface, hilt_color, (hx, hy), (gx, gy), 3)
        # Gold crossguard
        guard_perp_x = -math.sin(rad) * 4
        guard_perp_y = math.cos(rad) * 4
        pygame.draw.line(surface, (251, 242, 54), (gx - guard_perp_x, gy - guard_perp_y), (gx + guard_perp_x, gy + guard_perp_y), 3)

        # 3. Draw Blade (Silver metal with bright shine center)
        pygame.draw.line(surface, sword_color, (gx, gy), (tx, ty), 3)
        pygame.draw.line(surface, (255, 255, 255), (gx, gy), (tx, ty), 1)  # Blade shine
