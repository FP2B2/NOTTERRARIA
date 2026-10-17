# Project Terracraft

A 2D procedural sandbox survival adventure inspired by *Terraria*, powered by **local Gemma 4 12B via Ollama**.

---

## 🌟 Key Features

1. **5 Strata Procedural World Generation**:
   - **Sky**: High altitude clouds and potential floating islands.
   - **Surface**: Rolling hills, grass, trees, and desert sand.
   - **Underground**: Dirt, stone, and veins of copper, tin, iron, and lead.
   - **Caverns**: Deep open caves, silver, gold, and demonite ore.
   - **Underworld**: Volcanic ash, lava glow, and hellstone deposits.

2. **Core Sandbox Survival Mechanics**:
   - Smooth 2D cellular and torch lighting engine with multiplicative darkening.
   - Day & Night cycle with changing sky colors, stars, and darkness.
   - Progressive tile hardness, tool power tiers, and recursive tree felling.
   - 10-slot hotbar with copper starter kit (Pickaxe, Axe, Shortsword, Torches, Wood).
   - Platform drop-through physics and door interaction.

3. **Intelligent Local AI Guide (Gemma 4 12B via Ollama)**:
   - Non-blocking asynchronous query pipeline that never drops frames from the 60 FPS game loop.
   - Full live context injection: The Guide knows your exact stratum depth, current health, time of day, and items carried in your inventory.
   - Real-time typewriter streaming text with quick-prompt shortcuts.

---

## 🎮 Controls

| Action | Key / Input |
| :--- | :--- |
| **Move Left / Right** | `A` / `D` or `Left` / `Right` Arrows |
| **Jump** | `W` / `Space` or `Up` Arrow |
| **Drop Through Platforms** | `S` or `Down` Arrow |
| **Mine / Chop / Attack** | `Left Mouse Click` (Hold to swing) |
| **Place Block / Open Door** | `Right Mouse Click` |
| **Hotbar Selection** | Number keys `1` – `0` or `Mouse Wheel` |
| **Talk to The Guide** | `G` key (Opens Gemma 4 12B Dialogue) |
| **Quick Guide Queries** | `1`, `2`, `3`, `4` (while dialogue is open) |
| **Close Dialogue** | `ESC` |

---

## 🚀 How to Run

Activate the virtual environment and start the game:

```bash
cd /Users/franciscobarroca/.gemini/antigravity/scratch/terracraft
./.venv/bin/python3 run.py
```
