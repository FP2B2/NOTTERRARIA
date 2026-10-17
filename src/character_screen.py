"""
Character Creation Screen:
Live 4x preview with idle animation, spacious color swatches with names,
unified collision boxes for 100% reliable button clicking, and zero-lag rendering.
"""

import math
import random
import pygame
from typing import Optional, Dict, Any, Tuple, List

from .config import INTERNAL_WIDTH, INTERNAL_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from .sprites import (
    PALETTE,
    HAIRSTYLES,
    HAIR_COLOR_DATA,
    SKIN_TONE_DATA,
    OUTFIT_COLOR_DATA,
    HAIR_COLORS,
    SKIN_TONES,
    OUTFIT_COLORS,
    draw_character_preview,
)
from .audio import SoundManager

RANDOM_NAMES = [
    "Rowan", "Kaelen", "Lyra", "Theron", "Aria", "Finley",
    "Bram", "Zephyr", "Elowen", "Corin", "Sylas", "Mira",
]


class CharacterScreen:
    def __init__(self):
        pygame.font.init()
        self.font_header = pygame.font.SysFont("monospace", 15, bold=True)
        self.font_section = pygame.font.SysFont("monospace", 12, bold=True)
        self.font_body = pygame.font.SysFont("monospace", 12)
        self.font_small = pygame.font.SysFont("monospace", 11)
        self.font_btn = pygame.font.SysFont("monospace", 13, bold=True)

        self.sound = SoundManager.get()

        # Character State
        self.name = "Player"
        self.name_active = False
        self.hair_style_idx = 0
        self.hair_color_idx = 0
        self.skin_tone_idx = 1
        self.shirt_color_idx = 1
        self.pants_color_idx = 6
        self.difficulty_idx = 1  # 0: Chill, 1: Normal, 2: Brutal

        # Active Tab (0: Hairstyle, 1: Hair Color, 2: Skin Tone, 3: Shirt, 4: Pants)
        self.active_tab = 0
        self.tab_titles = ["Hair Style", "Hair Color", "Skin Tone", "Shirt Color", "Pants Color"]

        # Animation state
        self.time = 0.0
        self.idle_frame = 0
        self.cursor_timer = 0
        self.cursor_visible = True

        # Pre-calculate UI Layout Rectangles (Ensures 100% click & render accuracy)
        self._init_layout()

        # Pre-render Background to eliminate lag
        self._pre_render_bg()

    def _init_layout(self):
        """Centralized layout definition so render and click detection share identical coordinates."""
        # Main Dialog Frame
        self.frame_rect = pygame.Rect(45, 24, 550, 252)

        # Left Column: Character Preview
        self.preview_rect = pygame.Rect(65, 52, 115, 192)

        # Right Column Layout
        rx_start = 205

        # 1. Tab Bar at Top of Customizer
        self.tab_rects = []
        tab_w = 72
        tab_h = 24
        for i in range(5):
            self.tab_rects.append(pygame.Rect(rx_start + i * (tab_w + 4), 48, tab_w, tab_h))

        # 2. Name Input Row
        self.name_label_pos = (rx_start, 82)
        self.name_box_rect = pygame.Rect(rx_start + 55, 78, 250, 24)

        # 3. Hairstyle Cycling Controls
        self.style_prev_rect = pygame.Rect(rx_start + 60, 130, 32, 26)
        self.style_box_rect = pygame.Rect(rx_start + 98, 130, 160, 26)
        self.style_next_rect = pygame.Rect(rx_start + 264, 130, 32, 26)

        # 4. Swatch Matrix (Dedicated row with large 30x26 swatches and 8px gaps)
        self.swatch_rects = []
        swatch_w, swatch_h = 30, 26
        swatch_gap = 8
        for i in range(8):
            self.swatch_rects.append(pygame.Rect(rx_start + i * (swatch_w + swatch_gap), 130, swatch_w, swatch_h))

        # 5. Difficulty Buttons Row
        self.diff_label_pos = (rx_start, 172)
        self.diff_rects = [
            pygame.Rect(rx_start + 95, 168, 75, 25),
            pygame.Rect(rx_start + 176, 168, 75, 25),
            pygame.Rect(rx_start + 257, 168, 75, 25),
        ]

        # 6. Bottom Action Buttons (Outside frame for clear accessibility)
        btn_y = 286
        btn_w, btn_h = 120, 32
        self.back_btn_rect = pygame.Rect(65, btn_y, btn_w, btn_h)
        self.rand_btn_rect = pygame.Rect(260, btn_y, btn_w, btn_h)
        self.start_btn_rect = pygame.Rect(475, btn_y, btn_w, btn_h)

    def _pre_render_bg(self):
        """Pre-renders the static dusk sky background so zero math runs per frame."""
        self.bg_surf = pygame.Surface((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        for y in range(INTERNAL_HEIGHT):
            ratio = y / INTERNAL_HEIGHT
            r = int(24 + ratio * 85)
            g = int(22 + ratio * 42)
            b = int(58 + ratio * 32)
            pygame.draw.line(self.bg_surf, (r, g, b), (0, y), (INTERNAL_WIDTH, y))

        # Distant mountain silhouette
        m_pts = [(0, INTERNAL_HEIGHT)]
        for x in range(0, INTERNAL_WIDTH + 24, 20):
            my = 280 - math.sin(x * 0.01) * 35
            m_pts.append((x, int(my)))
        m_pts.append((INTERNAL_WIDTH, INTERNAL_HEIGHT))
        pygame.draw.polygon(self.bg_surf, (38, 30, 52), m_pts)

    def run(self, canvas: pygame.Surface, window: pygame.Surface, clock: pygame.time.Clock) -> Optional[Dict[str, Any]]:
        running = True

        while running:
            dt = clock.tick(FPS) / 1000.0
            self.time += dt

            # 0.4s idle breathing
            self.idle_frame = 1 if int(self.time * 2.5) % 2 == 1 else 0

            # Cursor blinking
            self.cursor_timer += dt
            if self.cursor_timer > 0.45:
                self.cursor_timer = 0
                self.cursor_visible = not self.cursor_visible

            scale_x = INTERNAL_WIDTH / WINDOW_WIDTH
            scale_y = INTERNAL_HEIGHT / WINDOW_HEIGHT
            raw_mx, raw_my = pygame.mouse.get_pos()
            mouse_pos = (int(raw_mx * scale_x), int(raw_my * scale_y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                elif event.type == pygame.KEYDOWN:
                    if self.name_active:
                        if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                            self.name_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.name = self.name[:-1]
                            self.sound.play("click")
                        else:
                            if len(self.name) < 16 and (event.unicode.isalnum() or event.unicode in " _-"):
                                self.name += event.unicode
                                self.sound.play("click")
                    else:
                        if event.key == pygame.K_ESCAPE:
                            self.sound.play("back")
                            return None

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    result = self._handle_click(mouse_pos)
                    if result == "back":
                        self.sound.play("back")
                        return None
                    elif result == "create":
                        self.sound.play("start")
                        return self._get_character_dict()
                    elif result == "randomize":
                        self._randomize()

            self.render(canvas, mouse_pos)
            pygame.transform.scale(canvas, (WINDOW_WIDTH, WINDOW_HEIGHT), window)
            pygame.display.flip()

        return None

    def _get_character_dict(self) -> Dict[str, Any]:
        diff_names = ["Chill", "Normal", "Brutal"]
        return {
            "name": self.name.strip() or "Adventurer",
            "hair_style": self.hair_style_idx,
            "hair_color": HAIR_COLORS[self.hair_color_idx],
            "skin_tone": SKIN_TONES[self.skin_tone_idx],
            "shirt_color": OUTFIT_COLORS[self.shirt_color_idx],
            "pants_color": OUTFIT_COLORS[self.pants_color_idx],
            "difficulty": diff_names[self.difficulty_idx],
        }

    def _randomize(self):
        self.sound.play("select")
        self.name = random.choice(RANDOM_NAMES)
        self.hair_style_idx = random.randint(0, len(HAIRSTYLES) - 1)
        self.hair_color_idx = random.randint(0, len(HAIR_COLORS) - 1)
        self.skin_tone_idx = random.randint(0, len(SKIN_TONES) - 1)
        self.shirt_color_idx = random.randint(0, len(OUTFIT_COLORS) - 1)
        self.pants_color_idx = random.randint(0, len(OUTFIT_COLORS) - 1)

    def _handle_click(self, m: Tuple[int, int]) -> Optional[str]:
        # 1. Name input box focus
        if self.name_box_rect.collidepoint(m):
            self.name_active = True
            self.sound.play("click")
            return None
        else:
            self.name_active = False

        # 2. Tab Selection
        for i, rect in enumerate(self.tab_rects):
            if rect.collidepoint(m):
                self.active_tab = i
                self.sound.play("select")
                return None

        # 3. Active Tab Customization Controls
        if self.active_tab == 0:  # Hairstyle arrows
            if self.style_prev_rect.collidepoint(m):
                self.hair_style_idx = (self.hair_style_idx - 1) % len(HAIRSTYLES)
                self.sound.play("select")
                return None
            elif self.style_next_rect.collidepoint(m):
                self.hair_style_idx = (self.hair_style_idx + 1) % len(HAIRSTYLES)
                self.sound.play("select")
                return None

        else:  # Color Swatches
            color_count = len(SKIN_TONES) if self.active_tab == 2 else 8
            for idx in range(color_count):
                if self.swatch_rects[idx].collidepoint(m):
                    if self.active_tab == 1:
                        self.hair_color_idx = idx
                    elif self.active_tab == 2:
                        self.skin_tone_idx = idx
                    elif self.active_tab == 3:
                        self.shirt_color_idx = idx
                    elif self.active_tab == 4:
                        self.pants_color_idx = idx
                    self.sound.play("select")
                    return None

        # 4. Difficulty Buttons
        for d, rect in enumerate(self.diff_rects):
            if rect.collidepoint(m):
                self.difficulty_idx = d
                self.sound.play("select")
                return None

        # 5. Bottom Action Buttons
        if self.back_btn_rect.collidepoint(m):
            return "back"
        elif self.rand_btn_rect.collidepoint(m):
            return "randomize"
        elif self.start_btn_rect.collidepoint(m):
            return "create"

        return None

    def render(self, surface: pygame.Surface, mouse_pos: Tuple[int, int]):
        # 1. Blit Pre-rendered Background (Instant 0ms)
        surface.blit(self.bg_surf, (0, 0))

        # 2. Main Dialog Frame (Large & Spacious)
        fx, fy, fw, fh = self.frame_rect
        # Drop shadow
        pygame.draw.rect(surface, (16, 16, 26), (fx + 3, fy + 3, fw, fh), border_radius=6)
        # Body
        pygame.draw.rect(surface, (34, 38, 58), self.frame_rect, border_radius=6)
        # Border
        pygame.draw.rect(surface, (63, 72, 116), self.frame_rect, width=2, border_radius=6)

        # Header Title Tab
        hw, hh = 180, 24
        hx = (INTERNAL_WIDTH - hw) // 2
        hy = fy - 12
        pygame.draw.rect(surface, (16, 16, 26), (hx + 2, hy + 2, hw, hh), border_radius=4)
        pygame.draw.rect(surface, (52, 60, 92), (hx, hy, hw, hh), border_radius=4)
        pygame.draw.rect(surface, (91, 110, 225), (hx, hy, hw, hh), width=2, border_radius=4)

        t_surf = self.font_header.render("New Character", True, (251, 242, 54))
        surface.blit(t_surf, (hx + (hw - t_surf.get_width()) // 2, hy + 3))

        # 3. Left Column: Character Live Preview Box
        px, py, pw, ph = self.preview_rect
        pygame.draw.rect(surface, (20, 22, 34), self.preview_rect, border_radius=4)
        pygame.draw.rect(surface, (50, 55, 80), self.preview_rect, width=1, border_radius=4)

        # Grassy pedestal
        ped_y = py + ph - 25
        pygame.draw.rect(surface, (102, 57, 49), (px + 12, ped_y, pw - 24, 8))
        pygame.draw.rect(surface, (99, 171, 63), (px + 12, ped_y - 2, pw - 24, 3))

        # Live 4x scaled animated preview
        draw_character_preview(
            surface=surface,
            center_x=px + pw // 2,
            center_y=py + 80,
            hair_style=self.hair_style_idx,
            hair_color=HAIR_COLORS[self.hair_color_idx],
            skin_tone=SKIN_TONES[self.skin_tone_idx],
            shirt_color=OUTFIT_COLORS[self.shirt_color_idx],
            pants_color=OUTFIT_COLORS[self.pants_color_idx],
            frame=self.idle_frame,
            scale=4,
        )

        # Character sub-label
        preview_lbl = self.font_small.render("Idle Preview", True, (130, 140, 170))
        surface.blit(preview_lbl, (px + (pw - preview_lbl.get_width()) // 2, py + ph - 14))

        # 4. Right Column: Customization Controls
        # TAB BUTTONS (Spacious, bold, clear highlights)
        short_names = ["Hairstyle", "Hair Color", "Skin Tone", "Shirt", "Pants"]
        for i, rect in enumerate(self.tab_rects):
            is_active = (i == self.active_tab)
            is_hover = rect.collidepoint(mouse_pos)

            bg = (63, 72, 116) if is_active else ((48, 54, 80) if is_hover else (30, 34, 52))
            border = (251, 242, 54) if is_active else ((140, 150, 190) if is_hover else (55, 62, 95))

            pygame.draw.rect(surface, bg, rect, border_radius=3)
            pygame.draw.rect(surface, border, rect, width=2 if is_active else 1, border_radius=3)

            tc = (255, 255, 255) if is_active else (190, 195, 215)
            s_surf = self.font_small.render(short_names[i], True, tc)
            surface.blit(s_surf, (rect.x + (rect.w - s_surf.get_width()) // 2, rect.y + 5))

        # ROW 1: NAME INPUT (Spacious & high contrast)
        nl_surf = self.font_section.render("Name:", True, (255, 255, 255))
        surface.blit(nl_surf, self.name_label_pos)

        nb_color = (251, 242, 54) if self.name_active else (75, 85, 130)
        pygame.draw.rect(surface, (18, 20, 30), self.name_box_rect, border_radius=3)
        pygame.draw.rect(surface, nb_color, self.name_box_rect, width=2 if self.name_active else 1, border_radius=3)

        display_name = self.name + ("|" if self.name_active and self.cursor_visible else "")
        if not self.name and not self.name_active:
            name_txt = self.font_body.render("Click to enter name...", True, (110, 115, 140))
        else:
            name_txt = self.font_body.render(display_name, True, (255, 255, 255))
        surface.blit(name_txt, (self.name_box_rect.x + 8, self.name_box_rect.y + 5))

        # ROW 2: ACTIVE TAB PICKER
        curr_tab_title = self.tab_titles[self.active_tab]

        if self.active_tab == 0:
            # HAIRSTYLE PICKER
            cur_name = HAIRSTYLES[self.hair_style_idx]["name"]
            style_head = self.font_section.render(f"Hairstyle: {cur_name} ({self.hair_style_idx + 1}/{len(HAIRSTYLES)})", True, (251, 242, 54))
            surface.blit(style_head, (205, 110))

            for rect, arrow in [(self.style_prev_rect, "<"), (self.style_next_rect, ">")]:
                is_h = rect.collidepoint(mouse_pos)
                bg = (52, 60, 92) if is_h else (38, 44, 70)
                border = (251, 242, 54) if is_h else (91, 110, 225)
                pygame.draw.rect(surface, bg, rect, border_radius=3)
                pygame.draw.rect(surface, border, rect, width=1, border_radius=3)

                arr_surf = self.font_btn.render(arrow, True, (255, 255, 255))
                surface.blit(arr_surf, (rect.x + (rect.w - arr_surf.get_width()) // 2, rect.y + 3))

            # Style name box
            pygame.draw.rect(surface, (22, 25, 40), self.style_box_rect, border_radius=3)
            pygame.draw.rect(surface, (63, 72, 116), self.style_box_rect, width=1, border_radius=3)
            st_surf = self.font_section.render(cur_name, True, (251, 242, 54))
            surface.blit(st_surf, (self.style_box_rect.x + (self.style_box_rect.w - st_surf.get_width()) // 2, self.style_box_rect.y + 5))

        else:
            # COLOR SWATCHES (Spacious 30x26 buttons with clean borders)
            if self.active_tab == 1:
                data_list = HAIR_COLOR_DATA
                sel_idx = self.hair_color_idx
            elif self.active_tab == 2:
                data_list = SKIN_TONE_DATA
                sel_idx = self.skin_tone_idx
            elif self.active_tab == 3:
                data_list = OUTFIT_COLOR_DATA
                sel_idx = self.shirt_color_idx
            else:
                data_list = OUTFIT_COLOR_DATA
                sel_idx = self.pants_color_idx

            active_name = data_list[sel_idx]["name"]
            cat_lbl = self.font_section.render(f"{curr_tab_title}: {active_name}", True, (251, 242, 54))
            surface.blit(cat_lbl, (205, 110))

            for idx, item in enumerate(data_list):
                s_rect = self.swatch_rects[idx]
                is_sel = (idx == sel_idx)
                is_h = s_rect.collidepoint(mouse_pos)

                # Swatch color block
                pygame.draw.rect(surface, item["color"], s_rect, border_radius=3)

                # Selection / Hover frames
                if is_sel:
                    pygame.draw.rect(surface, (251, 242, 54), s_rect, width=3, border_radius=3)
                    pygame.draw.circle(surface, (255, 255, 255), (s_rect.centerx, s_rect.centery), 3)
                elif is_h:
                    pygame.draw.rect(surface, (255, 255, 255), s_rect, width=2, border_radius=3)
                else:
                    pygame.draw.rect(surface, (20, 22, 34), s_rect, width=1, border_radius=3)

        # ROW 3: DIFFICULTY SELECTION (Generous 75x25 buttons)
        diff_lbl = self.font_section.render("Difficulty:", True, (255, 255, 255))
        surface.blit(diff_lbl, self.diff_label_pos)

        diff_configs = [
            ("Chill", (50, 115, 69), (99, 171, 63)),
            ("Normal", (63, 63, 116), (91, 110, 225)),
            ("Brutal", (120, 40, 40), (172, 50, 50)),
        ]

        for d, (d_name, base_c, hi_c) in enumerate(diff_configs):
            d_rect = self.diff_rects[d]
            is_sel = (d == self.difficulty_idx)
            is_h = d_rect.collidepoint(mouse_pos)

            bg = hi_c if is_sel else (hi_c if is_h else base_c)
            border = (255, 255, 255) if is_sel else ((251, 242, 54) if is_h else (25, 25, 40))

            pygame.draw.rect(surface, bg, d_rect, border_radius=3)
            pygame.draw.rect(surface, border, d_rect, width=2 if is_sel else 1, border_radius=3)

            dt_surf = self.font_section.render(d_name, True, (255, 255, 255))
            surface.blit(dt_surf, (d_rect.x + (d_rect.w - dt_surf.get_width()) // 2, d_rect.y + 5))

        # Difficulty description (Clearly readable with ample spacing)
        diff_descs = [
            "Chill: Gentle survival. Keep items and money on defeat.",
            "Normal: The classic experience. Drop coins on defeat.",
            "Brutal: Hardcore challenge. Drop all items on defeat.",
        ]
        desc_surf = self.font_small.render(diff_descs[self.difficulty_idx], True, (175, 185, 215))
        surface.blit(desc_surf, (205, 198))

        # 5. BOTTOM ACTION BUTTONS: [Back], [Randomize], [Start]
        # (Spacious 120x32 with prominent contrast and sound feedback)
        btn_configs = [
            ("Back", self.back_btn_rect, (150, 45, 45), (195, 65, 65)),
            ("Randomize", self.rand_btn_rect, (52, 58, 94), (75, 85, 130)),
            ("Start", self.start_btn_rect, (45, 110, 60), (70, 160, 85)),
        ]

        for text, rect, base_c, hover_c in btn_configs:
            is_h = rect.collidepoint(mouse_pos)
            bg = hover_c if is_h else base_c
            border = (251, 242, 54) if is_h else (16, 16, 26)

            # Shadow
            pygame.draw.rect(surface, (16, 16, 26), (rect.x + 2, rect.y + 2, rect.w, rect.h), border_radius=4)
            # Body
            pygame.draw.rect(surface, bg, rect, border_radius=4)
            pygame.draw.rect(surface, border, rect, width=2 if is_h else 1, border_radius=4)

            # Label
            lbl = self.font_btn.render(text, True, (255, 255, 255))
            surface.blit(lbl, (rect.x + (rect.w - lbl.get_width()) // 2, rect.y + 7))
