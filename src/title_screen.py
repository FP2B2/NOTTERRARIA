"""
Title Screen: Layered parallax ruins at dusk, drifting ash particles,
animated styled logo with glow, and interactive menu buttons with sound hooks.
Optimized for 60 FPS zero-lag execution via pre-rendered assets.
"""

import math
import random
import pygame
from typing import List, Tuple, Dict, Any, Optional
from .config import INTERNAL_WIDTH, INTERNAL_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from .sprites import PALETTE
from .audio import SoundManager


class Particle:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.speed_y = random.uniform(0.4, 0.9)
        self.sway_speed = random.uniform(1.5, 3.0)
        self.sway_amp = random.uniform(0.3, 0.8)
        self.size = random.choice([1, 1, 2, 2, 3])
        self.color = random.choice([
            PALETTE["ember_orange"],
            PALETTE["gold"],
            PALETTE["rose_pink"],
            (255, 140, 50),
        ])
        self.time_offset = random.uniform(0, 100)

    def update(self, t: float):
        self.y -= self.speed_y
        self.x += math.sin(t * self.sway_speed + self.time_offset) * self.sway_amp
        if self.y < -10:
            self.y = INTERNAL_HEIGHT + random.uniform(5, 20)
            self.x = random.uniform(0, INTERNAL_WIDTH)


class Button:
    def __init__(self, rect: pygame.Rect, text: str, action: str):
        self.rect = rect
        self.text = text
        self.action = action
        self.is_hovered = False
        self.was_hovered = False
        self.click_flash = 0

    def update(self, mouse_pos: Tuple[int, int], sound: SoundManager):
        self.was_hovered = self.is_hovered
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        if self.is_hovered and not self.was_hovered:
            sound.play("hover")

        if self.click_flash > 0:
            self.click_flash -= 1

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        x, y, w, h = self.rect

        if self.click_flash > 0:
            bg_color = (91, 110, 225)
            border_color = (255, 255, 255)
        elif self.is_hovered:
            bg_color = (52, 58, 94)
            border_color = (251, 242, 54)
        else:
            bg_color = (34, 32, 52)
            border_color = (63, 63, 116)

        # Shadow
        pygame.draw.rect(surface, (16, 16, 26), (x + 2, y + 2, w, h), border_radius=4)
        # Background
        pygame.draw.rect(surface, bg_color, (x, y, w, h), border_radius=4)
        # Bevel highlight on top
        pygame.draw.line(surface, (border_color[0] // 2 + 50, border_color[1] // 2 + 50, border_color[2] // 2 + 50), (x + 2, y + 1), (x + w - 3, y + 1))
        # Outer border
        pygame.draw.rect(surface, border_color, (x, y, w, h), width=2, border_radius=4)

        # Text with shadow
        text_color = (255, 255, 255) if self.is_hovered else (210, 215, 230)
        t_surf = font.render(self.text, True, text_color)
        t_shadow = font.render(self.text, True, (16, 16, 26))

        tx = x + (w - t_surf.get_width()) // 2
        ty = y + (h - t_surf.get_height()) // 2
        surface.blit(t_shadow, (tx + 1, ty + 1))
        surface.blit(t_surf, (tx, ty))


class TitleScreen:
    def __init__(self):
        pygame.font.init()
        self.font_logo = pygame.font.SysFont("impact", 36) or pygame.font.SysFont("arial", 34, bold=True)
        self.font_btn = pygame.font.SysFont("monospace", 13, bold=True)
        self.font_sub = pygame.font.SysFont("monospace", 11, bold=True)
        self.font_modal = pygame.font.SysFont("monospace", 12)

        self.sound = SoundManager.get()

        self.time = 0.0
        self.mountain_scroll = 0.0
        self.ruins_scroll = 0.0

        # Ash & ember particles
        self.particles: List[Particle] = [
            Particle(random.uniform(0, INTERNAL_WIDTH), random.uniform(0, INTERNAL_HEIGHT))
            for _ in range(50)
        ]

        # Buttons
        btn_w, btn_h = 160, 28
        start_x = (INTERNAL_WIDTH - btn_w) // 2
        start_y = 195
        spacing = 36

        self.buttons = [
            Button(pygame.Rect(start_x, start_y, btn_w, btn_h), "Play", "play"),
            Button(pygame.Rect(start_x, start_y + spacing, btn_w, btn_h), "Settings", "settings"),
            Button(pygame.Rect(start_x, start_y + spacing * 2, btn_w, btn_h), "Credits", "credits"),
            Button(pygame.Rect(start_x, start_y + spacing * 3, btn_w, btn_h), "Exit", "quit"),
        ]

        self.modal_view: Optional[str] = None

        # PRE-RENDER PERFORMANCE CACHES (Avoids 60 FPS redraw lag)
        self._pre_render_sky()
        self._pre_render_logo()
        self._pre_render_footer()

    def _pre_render_sky(self):
        """Pre-renders the vertical dusk gradient onto a static surface once."""
        self.sky_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        for y in range(INTERNAL_HEIGHT):
            ratio = y / INTERNAL_HEIGHT
            if ratio < 0.55:
                r = int(24 + ratio * 150)
                g = int(22 + ratio * 60)
                b = int(58 + ratio * 40)
            else:
                sub_r = (ratio - 0.55) / 0.45
                r = int(106 + sub_r * 115)
                g = int(55 + sub_r * 58)
                b = int(80 - sub_r * 42)
            pygame.draw.line(self.sky_surf, (r, g, b), (0, y), (INTERNAL_WIDTH, y))

    def _pre_render_footer(self):
        """Pre-renders static footer text."""
        self.footer_surf = self.font_sub.render("v0.1 Alpha • Powered by local Gemma 4 12B", True, (130, 130, 160))

    def _pre_render_logo(self):
        """Pre-renders the 3D logo typography once to avoid hundreds of font calls per frame."""
        logo_str = "TERRACRAFT"
        letter_colors = [
            (99, 171, 63),   # T - Green
            (115, 185, 75),  # E
            (145, 195, 80),  # R
            (210, 190, 60),  # R
            (251, 242, 54),  # A - Gold
            (251, 220, 50),  # C
            (223, 150, 45),  # R
            (223, 113, 38),  # A - Orange
            (190, 80, 40),   # F
            (172, 50, 50),   # T - Ruby
        ]

        rendered_chars = [self.font_logo.render(ch, True, c) for ch, c in zip(logo_str, letter_colors)]
        shadow_chars = [self.font_logo.render(ch, True, (16, 16, 26)) for ch in logo_str]
        glow_chars = [self.font_logo.render(ch, True, (255, 230, 140)) for ch in logo_str]

        total_w = sum(ch.get_width() - 2 for ch in rendered_chars) + 12
        logo_h = 70

        self.logo_surf = pygame.Surface((total_w, logo_h), pygame.SRCALPHA)

        cur_x = 4
        for i in range(len(logo_str)):
            ch_surf = rendered_chars[i]
            sh_surf = shadow_chars[i]
            gl_surf = glow_chars[i]
            w = ch_surf.get_width() - 2

            # Shadows
            self.logo_surf.blit(sh_surf, (cur_x + 3, 7))
            self.logo_surf.blit(sh_surf, (cur_x + 2, 6))
            # Rim glow
            self.logo_surf.blit(gl_surf, (cur_x, 3))
            # Face
            self.logo_surf.blit(ch_surf, (cur_x, 4))
            cur_x += w

        self.logo_w = total_w
        self.logo_h = logo_h

    def run(self, canvas: pygame.Surface, window: pygame.Surface, clock: pygame.time.Clock) -> str:
        running = True

        while running:
            dt = clock.tick(FPS) / 1000.0
            self.time += dt
            self.mountain_scroll += 0.25
            self.ruins_scroll += 0.65

            scale_x = INTERNAL_WIDTH / WINDOW_WIDTH
            scale_y = INTERNAL_HEIGHT / WINDOW_HEIGHT
            raw_mx, raw_my = pygame.mouse.get_pos()
            canvas_mouse = (int(raw_mx * scale_x), int(raw_my * scale_y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.modal_view:
                            self.sound.play("back")
                            self.modal_view = None
                        else:
                            return "quit"

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.modal_view:
                        self.sound.play("back")
                        self.modal_view = None
                    else:
                        for btn in self.buttons:
                            if btn.is_hovered:
                                btn.click_flash = 6
                                self.sound.play("click")
                                if btn.action == "play":
                                    return "play"
                                elif btn.action in ("settings", "credits"):
                                    self.modal_view = btn.action
                                elif btn.action == "quit":
                                    return "quit"

            if not self.modal_view:
                for btn in self.buttons:
                    btn.update(canvas_mouse, self.sound)

            for p in self.particles:
                p.update(self.time)

            self.render(canvas)
            if self.modal_view:
                self.render_modal(canvas, self.modal_view)

            pygame.transform.scale(canvas, (WINDOW_WIDTH, WINDOW_HEIGHT), window)
            pygame.display.flip()

        return "quit"

    def render(self, surface: pygame.Surface):
        # 1. Blit Pre-rendered Sky (1 single blit instead of 360 line draws)
        surface.blit(self.sky_surf, (0, 0))

        # 2. Twinkling Stars
        for i in range(35):
            sx = (i * 41 + int(self.time * 2)) % INTERNAL_WIDTH
            sy = (i * 23) % (INTERNAL_HEIGHT // 2)
            alpha_pulse = (math.sin(self.time * 2.5 + i) + 1.0) * 0.5
            brightness = int(140 + alpha_pulse * 115)
            pygame.draw.circle(surface, (brightness, brightness, 255), (sx, sy), 1)

        # 3. Distant Mountains (Layer 1)
        self._draw_mountain_range(surface, offset=self.mountain_scroll, base_y=240, color=(54, 40, 72), amp=45, freq=0.008)

        # 4. Midground Ruins (Layer 2)
        self._draw_ruins_layer(surface, offset=self.ruins_scroll)

        # 5. Foreground Craggy Ridge
        self._draw_foreground_ridge(surface)

        # 6. Particles
        for p in self.particles:
            pygame.draw.rect(surface, p.color, (int(p.x), int(p.y), p.size, p.size))
            if p.size > 1:
                pygame.draw.rect(surface, (255, 180, 50), (int(p.x) - 1, int(p.y) - 1, p.size + 2, p.size + 2), 1)

        # 7. Pre-rendered Logo & Glow
        self._draw_logo(surface)

        # 8. Menu Buttons
        for btn in self.buttons:
            btn.draw(surface, self.font_btn)

        # 9. Pre-rendered Footer
        surface.blit(self.footer_surf, (INTERNAL_WIDTH // 2 - self.footer_surf.get_width() // 2, INTERNAL_HEIGHT - 16))

    def _draw_mountain_range(self, surface: pygame.Surface, offset: float, base_y: int, color: Tuple[int, int, int], amp: int, freq: float):
        pts = [(0, INTERNAL_HEIGHT)]
        for x in range(0, INTERNAL_WIDTH + 32, 24):
            y = base_y - math.sin((x + offset) * freq) * amp - math.cos((x + offset) * freq * 2.3) * (amp * 0.4)
            pts.append((x, int(y)))
        pts.append((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        pygame.draw.polygon(surface, color, pts)

    def _draw_ruins_layer(self, surface: pygame.Surface, offset: float):
        color = (38, 30, 50)
        highlight = (68, 55, 85)
        pygame.draw.rect(surface, color, (0, 260, INTERNAL_WIDTH, INTERNAL_HEIGHT - 260))

        for i in range(-1, 7):
            rx = int(i * 115 - (offset % 115))
            pygame.draw.rect(surface, color, (rx, 180, 18, 85))
            pygame.draw.rect(surface, highlight, (rx, 180, 3, 85))
            pygame.draw.rect(surface, color, (rx - 4, 174, 26, 8))
            pygame.draw.rect(surface, highlight, (rx - 4, 174, 26, 2))
            if i % 2 == 0:
                pygame.draw.rect(surface, color, (rx + 18, 184, 97, 6))

    def _draw_foreground_ridge(self, surface: pygame.Surface):
        color = (20, 18, 30)
        grass_color = (60, 95, 45)
        pygame.draw.rect(surface, color, (0, 310, INTERNAL_WIDTH, 50))
        for x in range(0, INTERNAL_WIDTH, 6):
            gh = int(310 + math.sin(x * 0.15) * 3)
            pygame.draw.line(surface, grass_color, (x, gh), (x, gh + 2))

    def _draw_logo(self, surface: pygame.Surface):
        bob = math.sin(self.time * 2.0) * 3.5
        center_x = INTERNAL_WIDTH // 2
        logo_y = 65 + bob

        # Blit pre-rendered logo
        surface.blit(self.logo_surf, (center_x - self.logo_w // 2, int(logo_y)))

        # Decorative Underline Bar
        line_y = int(logo_y + 44)
        pygame.draw.line(surface, (143, 86, 59), (center_x - 110, line_y), (center_x + 110, line_y), 2)
        pygame.draw.line(surface, (251, 242, 54), (center_x - 60, line_y), (center_x + 60, line_y), 2)

        # Center Diamond
        diamond_pts = [
            (center_x, line_y - 4),
            (center_x + 5, line_y),
            (center_x, line_y + 4),
            (center_x - 5, line_y),
        ]
        pygame.draw.polygon(surface, (251, 242, 54), diamond_pts)
        pygame.draw.polygon(surface, (16, 16, 26), diamond_pts, 1)

        # Subtitle
        sub_alpha = (math.sin(self.time * 2.2) + 1.0) * 0.5
        sub_color = (int(189 + sub_alpha * 40), int(147 + sub_alpha * 40), int(249))
        sub_surf = self.font_sub.render("~ A 2D SANDBOX ODYSSEY ~", True, sub_color)
        sub_shadow = self.font_sub.render("~ A 2D SANDBOX ODYSSEY ~", True, (16, 16, 26))
        surface.blit(sub_shadow, (center_x - sub_surf.get_width() // 2 + 1, line_y + 8))
        surface.blit(sub_surf, (center_x - sub_surf.get_width() // 2, line_y + 7))

    def render_modal(self, surface: pygame.Surface, view: str):
        modal_w, modal_h = 360, 200
        mx = (INTERNAL_WIDTH - modal_w) // 2
        my = (INTERNAL_HEIGHT - modal_h) // 2

        dim_overlay = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT), pygame.SRCALPHA)
        dim_overlay.fill((0, 0, 0, 160))
        surface.blit(dim_overlay, (0, 0))

        pygame.draw.rect(surface, (16, 16, 26), (mx + 3, my + 3, modal_w, modal_h), border_radius=6)
        pygame.draw.rect(surface, (34, 32, 52), (mx, my, modal_w, modal_h), border_radius=6)
        pygame.draw.rect(surface, (91, 110, 225), (mx, my, modal_w, modal_h), width=2, border_radius=6)

        title = "SETTINGS" if view == "settings" else "CREDITS"
        t_surf = self.font_btn.render(title, True, (251, 242, 54))
        surface.blit(t_surf, (mx + (modal_w - t_surf.get_width()) // 2, my + 14))

        if view == "settings":
            lines = [
                "• Master Audio: 100% (Synthetic 8-bit)",
                "• Resolution: 1280x720 (Internal 640x360)",
                "• Display: Pixel-art Integer Scaling",
                "• AI Engine: Ollama (gemma4:12b Active)",
                "",
                "[Click anywhere or press ESC to return]",
            ]
        else:
            lines = [
                "PROJECT TERRACRAFT",
                "Created by Francisco Barroca & Antigravity",
                "Powered by Gemma 4 12B Local Intelligence",
                "Retro 16-color procedural pixel art",
                "",
                "[Click anywhere or press ESC to return]",
            ]

        for i, line in enumerate(lines):
            c = (245, 245, 255) if i < len(lines) - 1 else (150, 150, 180)
            l_surf = self.font_modal.render(line, True, c)
            surface.blit(l_surf, (mx + (modal_w - l_surf.get_width()) // 2, my + 48 + i * 20))
