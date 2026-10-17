"""
Procedural 8-bit retro sound synthesizer using pygame.mixer.
Generates crisp clicks, chirps, and chimes in memory with zero external assets.
"""

import math
import struct
import pygame
from typing import Dict, Optional


class SoundManager:
    _instance: Optional["SoundManager"] = None

    def __init__(self):
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.enabled = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.enabled = True
            self._generate_sounds()
        except Exception as e:
            self.enabled = False

    @classmethod
    def get(cls) -> "SoundManager":
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    def _create_sound_from_samples(self, samples, sample_rate=22050) -> Optional[pygame.mixer.Sound]:
        raw_bytes = bytearray()
        for s in samples:
            val = max(-32767, min(32767, int(s * 30000)))
            raw_bytes.extend(struct.pack("<h", val))
        try:
            return pygame.mixer.Sound(buffer=bytes(raw_bytes))
        except Exception:
            return None

    def _generate_sounds(self):
        rate = 22050

        # 1. Hover click (soft 800Hz blip, 20ms)
        hover_samples = []
        for i in range(int(rate * 0.025)):
            t = i / rate
            env = 1.0 - (i / (rate * 0.025))
            val = math.sin(2 * math.pi * 880 * t) * env * 0.25
            hover_samples.append(val)
        s_hover = self._create_sound_from_samples(hover_samples)
        if s_hover:
            self.sounds["hover"] = s_hover

        # 2. Click (snappy square/sine wave punch, 40ms)
        click_samples = []
        for i in range(int(rate * 0.04)):
            t = i / rate
            env = (1.0 - (i / (rate * 0.04))) ** 1.5
            freq = 600 - t * 4000
            val = math.sin(2 * math.pi * freq * t) * env * 0.4
            click_samples.append(val)
        s_click = self._create_sound_from_samples(click_samples)
        if s_click:
            self.sounds["click"] = s_click

        # 3. Select / Swatch change (two-tone ascending chirp)
        select_samples = []
        dur = int(rate * 0.06)
        for i in range(dur):
            t = i / rate
            env = 1.0 - (i / dur)
            freq = 520 if i < dur // 2 else 780
            val = math.sin(2 * math.pi * freq * t) * env * 0.35
            select_samples.append(val)
        s_select = self._create_sound_from_samples(select_samples)
        if s_select:
            self.sounds["select"] = s_select

        # 4. Back (descending tone)
        back_samples = []
        dur = int(rate * 0.07)
        for i in range(dur):
            t = i / rate
            env = 1.0 - (i / dur)
            freq = 660 if i < dur // 2 else 440
            val = math.sin(2 * math.pi * freq * t) * env * 0.35
            back_samples.append(val)
        s_back = self._create_sound_from_samples(back_samples)
        if s_back:
            self.sounds["back"] = s_back

        # 5. Start Fanfare (triumphant 3-note arpeggio)
        start_samples = []
        dur = int(rate * 0.18)
        step = dur // 3
        for i in range(dur):
            t = i / rate
            env = 1.0 - (i / dur)
            if i < step:
                freq = 440.0   # A4
            elif i < step * 2:
                freq = 554.37 # C#5
            else:
                freq = 659.25 # E5
            val = math.sin(2 * math.pi * freq * t) * env * 0.45
            start_samples.append(val)
        s_start = self._create_sound_from_samples(start_samples)
        if s_start:
            self.sounds["start"] = s_start

        # 6. Sword Swing Whoosh (white noise + pitch down sweep)
        swing_samples = []
        s_dur = int(rate * 0.12)
        import random
        for i in range(s_dur):
            t = i / s_dur
            env = math.sin(t * math.pi) ** 1.8
            freq = 320 * (1.0 - t * 0.6)
            tone = math.sin(2 * math.pi * freq * (i / rate))
            noise = (random.random() * 2.0 - 1.0) * 0.45
            val = (tone * 0.55 + noise * 0.45) * env * 0.4
            swing_samples.append(val)
        s_swing = self._create_sound_from_samples(swing_samples)
        if s_swing:
            self.sounds["sword_swing"] = s_swing

        # 7. Hit Impact / Flesh slice (sharp crack + low thud)
        hit_samples = []
        h_dur = int(rate * 0.08)
        for i in range(h_dur):
            t = i / h_dur
            env = (1.0 - t) ** 2.5
            freq = 240 * (1.0 - t * 0.7)
            tone = math.sin(2 * math.pi * freq * (i / rate))
            noise = (random.random() * 2.0 - 1.0) * (0.8 if t < 0.2 else 0.2)
            val = (tone * 0.6 + noise * 0.4) * env * 0.65
            hit_samples.append(val)
        s_hit = self._create_sound_from_samples(hit_samples)
        if s_hit:
            self.sounds["hit_impact"] = s_hit

        # 8. Enemy Defeat / Slime Splat
        die_samples = []
        d_dur = int(rate * 0.16)
        for i in range(d_dur):
            t = i / d_dur
            env = (1.0 - t) ** 2.0
            freq = 480 - t * 360
            val = (math.sin(2 * math.pi * freq * (i / rate)) + (random.random() - 0.5) * 0.3) * env * 0.5
            die_samples.append(val)
        s_die = self._create_sound_from_samples(die_samples)
        if s_die:
            self.sounds["enemy_die"] = s_die

    def play(self, name: str):
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass
