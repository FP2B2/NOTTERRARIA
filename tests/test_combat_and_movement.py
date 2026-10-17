import os
import sys
import pygame

# Set dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import INTERNAL_WIDTH, INTERNAL_HEIGHT, GRAVITY
from src.player import Player
from src.combat import TrainingDummy, CombatJuiceManager
from src.audio import SoundManager

def test_movement_and_combat():
    pygame.init()
    floor_y = 300.0

    player = Player(100.0, floor_y - 26)
    dummy = TrainingDummy(140.0, floor_y - 16)
    juice = CombatJuiceManager()

    print("[TEST] Initialized player at:", player.x, player.y)

    # Simulate 1 frame to land firmly on test floor
    keys = {
        pygame.K_a: False, pygame.K_d: False, pygame.K_SPACE: False,
        pygame.K_w: False, pygame.K_s: False, pygame.K_LEFT: False,
        pygame.K_RIGHT: False, pygame.K_UP: False, pygame.K_DOWN: False,
        pygame.K_j: False
    }
    player.update(keys, floor_y=floor_y)
    assert player.on_ground, "Player should be on ground"
    print("[TEST] Ground detection OK")

    # 1. Horizontal Movement & Acceleration
    keys[pygame.K_d] = True
    for _ in range(15):
        player.update(keys, floor_y=floor_y)
    assert player.vx > 1.0, f"Player should accelerate right, got vx={player.vx}"
    assert player.facing_right, "Player should face right"
    print(f"[TEST] Movement Right OK: vx={player.vx:.2f}, x={player.x:.2f}")

    # Deceleration
    keys[pygame.K_d] = False
    for _ in range(25):
        player.update(keys, floor_y=floor_y)
    assert player.vx == 0.0, f"Player should come to a full stop, got vx={player.vx}"
    print("[TEST] Deceleration friction OK")

    # 2. Jump & Variable Jump
    keys[pygame.K_SPACE] = True
    player.update(keys, floor_y=floor_y)
    assert player.vy < 0, f"Player should jump upwards, got vy={player.vy}"
    assert not player.on_ground, "Player should be airborne"
    initial_jump_vy = player.vy
    print(f"[TEST] Jump OK: vy={initial_jump_vy:.2f}")

    # Release jump early to verify variable jump height cut
    keys[pygame.K_SPACE] = False
    player.update(keys, floor_y=floor_y)
    assert player.vy > initial_jump_vy * 0.8, "Variable jump cut should damp upward velocity"
    print(f"[TEST] Variable jump cut OK: new vy={player.vy:.2f}")

    # Let player fall back down to test floor until landing
    landed = False
    for _ in range(60):
        player.update(keys, floor_y=floor_y)
        if player.on_ground:
            landed = True
            break
    assert landed, "Player should land safely on test floor"
    print(f"[TEST] Landing squash and recovery OK (squash={player.landing_squash})")
    assert player.landing_squash > 0, "Landing squash frames should be triggered on landing"


    # 3. Sword Swing & Hitbox
    player.x = dummy.x - 24
    player.facing_right = True
    player.trigger_swing()
    assert player.is_swinging, "Player should be swinging"

    hit_registered = False
    dummy_initial_hp = dummy.hp
    for frame in range(player.swing_duration):
        player.update(keys, floor_y=floor_y)
        hitbox = player.get_sword_hitbox()
        if hitbox and (id(dummy) not in player.already_hit):
            if hitbox.colliderect(dummy.rect):
                dummy.take_hit(player.sword_damage, knockback_dir=1.0)
                player.already_hit.add(id(dummy))
                juice.trigger_hit(screenshake_strength=4.0, hitstop_frames=3)
                hit_registered = True
                print(f"[TEST] Hit connected on frame {frame}!")

    assert hit_registered, "Sword swing arc hitbox should hit the dummy"
    assert dummy.hp == dummy_initial_hp - player.sword_damage, f"Dummy HP should decrease from {dummy_initial_hp} to {dummy_initial_hp - player.sword_damage}, got {dummy.hp}"
    assert dummy.hit_flash_timer > 0, "Dummy should have hit flash active"
    assert dummy.vx > 0, "Dummy should receive directional knockback"
    assert juice.is_frozen, "Combat juice hitstop freeze should be active"
    assert juice.trauma > 0, "Screen shake trauma should be active"
    print("[TEST] Combat mechanics (hitbox, damage, knockback, flash, screen shake, hitstop) verified OK!")

    # 4. Dummy Defeat & Auto-Respawn
    dummy.take_hit(999, knockback_dir=1.0)
    assert not dummy.is_alive, "Dummy should be defeated"
    assert dummy.respawn_timer > 0, "Dummy respawn timer should be running"
    print(f"[TEST] Dummy defeated. Waiting for respawn timer ({dummy.respawn_timer}s)...")

    # Fast forward respawn
    for _ in range(180): # 3 seconds at 60 FPS
        dummy.update(floor_y=floor_y)
    assert dummy.is_alive, "Dummy should respawn after cooldown"
    assert dummy.hp == dummy.max_hp, "Dummy should be back at full HP"
    print("[TEST] Dummy auto-respawn OK!")

    print("\n>>> ALL UNIT & INTEGRATION TESTS PASSED! <<<")

if __name__ == "__main__":
    test_movement_and_combat()
