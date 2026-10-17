"""
Game configuration constants, layer boundaries, and physics tuning.
"""

TILE_SIZE = 16  # 16x16 pixel tiles

# Window and Internal Render Target
INTERNAL_WIDTH = 640
INTERNAL_HEIGHT = 360
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# World Dimensions (in tiles)
WORLD_WIDTH = 600
WORLD_HEIGHT = 400

# Strata Depth Thresholds (in tile Y coordinates)
STRATA_SKY_END = 70
STRATA_SURFACE_START = 70
STRATA_SURFACE_END = 150
STRATA_UNDERGROUND_END = 270
STRATA_CAVERNS_END = 350
STRATA_UNDERWORLD_START = 350

# Physics
GRAVITY = 0.4
TERMINAL_VELOCITY = 10.0
PLAYER_SPEED = 2.8
PLAYER_JUMP_FORCE = -7.2
PLAYER_ACCEL = 0.5
PLAYER_FRICTION = 0.82

# Day / Night (in game seconds; 1 full day = 240 seconds = 4 minutes)
DAY_DURATION_SECONDS = 240.0
TIME_SPEED = 1.0  # multiplier

# Ollama Settings
OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "gemma4:12b"
