"""
In-game HUD, hearts, mana stars, 10-slot hotbar, and the interactive
Gemma 4 12B Guide Dialogue interface.
"""

import pygame
from typing import Optional, List
from .items import ITEM_REGISTRY, ItemDef
from .inventory import Inventory


class UIRenderer:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height

        # Initialize fonts
        pygame.font.init()
        self.font_small = pygame.font.SysFont("monospace", 10, bold=True)
        self.font_normal = pygame.font.SysFont("monospace", 12, bold=True)
        self.font_title = pygame.font.SysFont("monospace", 14, bold=True)

        # Dialogue state
        self.dialogue_open = False
        self.dialogue_text = ""
        self.dialogue_displayed = ""
        self.typewriter_speed = 2  # characters per frame
        self.guide_thinking = False

        # Quick questions
        self.quick_prompts = [
            ("1", "What should I do first?"),
            ("2", "How do I build a valid house?"),
            ("3", "What can I craft with my current items?"),
            ("4", "What dangers lurk in the dark?"),
        ]

    def render_hud(
        self,
        surface: pygame.Surface,
        player,
        time_string: str,
        stratum_name: str,
    ):
        """Draws the hotbar, hearts, and depth/time indicators."""
        # 1. Hotbar (10 slots)
        slot_size = 24
        slot_padding = 3
        start_x = 10
        start_y = 10

        for i in range(10):
            x = start_x + i * (slot_size + slot_padding)
            y = start_y
            slot_rect = pygame.Rect(x, y, slot_size, slot_size)

            # Slot background
            bg_color = (40, 42, 54) if i != player.inventory.selected_slot else (80, 90, 120)
            border_color = (241, 250, 140) if i == player.inventory.selected_slot else (98, 114, 164)
            pygame.draw.rect(surface, bg_color, slot_rect)
            pygame.draw.rect(surface, border_color, slot_rect, 1)

            # Slot number label (1-9, 0)
            key_label = str((i + 1) % 10)
            num_surf = self.font_small.render(key_label, True, (139, 233, 253))
            surface.blit(num_surf, (x + 2, y + 1))

            # Item rendering
            slot = player.inventory.slots[i]
            if slot and slot.item_def:
                # Color block icon
                icon_rect = pygame.Rect(x + 5, y + 5, 14, 14)
                pygame.draw.rect(surface, slot.item_def.color, icon_rect)
                pygame.draw.rect(surface, (20, 20, 20), icon_rect, 1)

                # Count text
                if slot.count > 1:
                    count_surf = self.font_small.render(str(slot.count), True, (255, 255, 255))
                    surface.blit(count_surf, (x + slot_size - count_surf.get_width() - 2, y + slot_size - count_surf.get_height() - 1))

        # Selected item name text
        selected = player.inventory.get_selected()
        if selected and selected.item_def:
            name_surf = self.font_normal.render(selected.item_def.name, True, (255, 255, 255))
            surface.blit(name_surf, (start_x, start_y + slot_size + 4))

        # 2. Hearts (Health) at Top Right
        heart_w = 12
        heart_h = 12
        hearts_count = max(1, player.max_health // 20)
        curr_hearts = player.health / 20.0
        h_start_x = self.width - (hearts_count * (heart_w + 3)) - 10
        h_start_y = 10

        for h in range(hearts_count):
            hx = h_start_x + h * (heart_w + 3)
            hy = h_start_y
            rect = pygame.Rect(hx, hy, heart_w, heart_h)

            if curr_hearts >= h + 1:
                # Full red heart
                pygame.draw.rect(surface, (230, 40, 50), rect)
                pygame.draw.rect(surface, (140, 20, 25), rect, 1)
            elif curr_hearts > h:
                # Half heart
                pygame.draw.rect(surface, (230, 40, 50), pygame.Rect(hx, hy, heart_w // 2, heart_h))
                pygame.draw.rect(surface, (60, 60, 60), rect, 1)
            else:
                # Empty heart
                pygame.draw.rect(surface, (50, 50, 50), rect)
                pygame.draw.rect(surface, (30, 30, 30), rect, 1)

        hp_text = self.font_small.render(f"{player.health}/{player.max_health}", True, (255, 200, 200))
        surface.blit(hp_text, (self.width - hp_text.get_width() - 10, h_start_y + heart_h + 3))

        # 3. Time & Depth Indicator
        info_text = f"[{stratum_name}] • {time_string} • Press 'G' to consult Guide"
        info_surf = self.font_small.render(info_text, True, (189, 147, 249))
        surface.blit(info_surf, (self.width // 2 - info_surf.get_width() // 2, 8))

    def render_dialogue(self, surface: pygame.Surface):
        """Renders the Guide NPC AI dialogue box when active."""
        if not self.dialogue_open:
            return

        box_w = self.width - 60
        box_h = 110
        box_x = 30
        box_y = self.height - box_h - 15

        # Background panel
        bg_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg_surf.fill((20, 22, 32, 230))
        surface.blit(bg_surf, (box_x, box_y))
        pygame.draw.rect(surface, (255, 184, 108), pygame.Rect(box_x, box_y, box_w, box_h), 2)

        # Header title
        title_surf = self.font_title.render("THE GUIDE [Gemma 4 12B Active]", True, (255, 184, 108))
        surface.blit(title_surf, (box_x + 10, box_y + 8))

        # Status or speech
        if self.guide_thinking and not self.dialogue_displayed:
            think_surf = self.font_normal.render("The Guide is pondering your situation...", True, (139, 233, 253))
            surface.blit(think_surf, (box_x + 10, box_y + 32))
        else:
            # Word-wrapped speech rendering
            self._render_wrapped_text(surface, self.dialogue_displayed, box_x + 10, box_y + 32, box_w - 20)

        # Quick question hints at bottom
        hint_str = " | ".join(f"[{k}] {q}" for k, q in self.quick_prompts)
        hint_surf = self.font_small.render(f"{hint_str} | [ESC: Close]", True, (80, 250, 123))
        surface.blit(hint_surf, (box_x + 10, box_y + box_h - 18))

    def _render_wrapped_text(self, surface: pygame.Surface, text: str, x: int, y: int, max_w: int):
        words = text.split(" ")
        lines: List[str] = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if self.font_normal.size(test_line)[0] < max_w:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Render up to 3 lines
        for i, line in enumerate(lines[:3]):
            line_surf = self.font_normal.render(line, True, (248, 248, 242))
            surface.blit(line_surf, (x, y + i * 16))

    def update_typewriter(self):
        """Advances the typewriter effect for streaming speech."""
        if len(self.dialogue_displayed) < len(self.dialogue_text):
            step = min(self.typewriter_speed, len(self.dialogue_text) - len(self.dialogue_displayed))
            self.dialogue_displayed += self.dialogue_text[len(self.dialogue_displayed): len(self.dialogue_displayed) + step]
