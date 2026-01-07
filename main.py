import pygame
import os
import random
import time
import tkinter as tk
import sys
from camera import Camera
from Characters.player import Player
from Characters.circle_ninja import CircleNinja
from Characters.ninjircle import Ninjircle
from Characters.starficer import Starficer
from Characters.triangle_wizard import TriangleWizard
from Objects.tree import Tree
from Objects.bush import Bush
from pause_menu import PauseMenu
from spatial_grid import SpatialGrid
from Characters.minion import Minion
from Characters.attack_robot import AttackRobot
from projectile import Projectile
pygame.font.init()
from asset_manager import get_asset_path


pygame.font.init()

root = tk.Tk()
WIDTH = root.winfo_screenwidth()
HEIGHT = root.winfo_screenheight()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PaperTrail: Escape from this Dimension")


# World size (bigger than screen so player can move through environment)
WORLD_W = WIDTH * 3
WORLD_H = HEIGHT * 3

# Load background tile (do not scale) and get tile size
BG_TILE = pygame.image.load(get_asset_path("paper_bg_3.png")).convert()
TILE_W, TILE_H = BG_TILE.get_size()

# Object spawn density per tile (0.0 to 1.0)
TREE_DENSITY = 0.20
BUSH_DENSITY = 0.15


def generate_objects_in_tile(tile_x, tile_y, seed_offset=0):
    """Generate tree and bush objects for a tile based on seeded randomness."""
    objects = []

    # Use tile coordinates as part of the seed for consistency
    tile_seed = hash((tile_x, tile_y, seed_offset)) % (2**32)
    rng = random.Random(tile_seed)

    # Spawn trees
    if rng.random() < TREE_DENSITY:
        x = tile_x + rng.uniform(10, TILE_W - 10)
        y = tile_y + rng.uniform(10, TILE_H - 10)
        objects.append(Tree((x, y)))

    # Spawn bushes
    if rng.random() < BUSH_DENSITY:
        x = tile_x + rng.uniform(10, TILE_W - 10)
        y = tile_y + rng.uniform(10, TILE_H - 10)
        objects.append(Bush((x, y)))

    return objects


def main():
    FPS = 60
    clock = pygame.time.Clock()

    # Global list to hold all spawned objects (trees, bushes, etc.)
    world_objects = []

    # Place player at center of the world so they appear centered on screen
    # Character selection screen before starting
    def character_selection_screen(screen):
        choices = [
            ("CircleNinja", get_asset_path("Circle-Ninja.png"), CircleNinja),
            ("Ninjircle", get_asset_path("Ninjircle-1.png"), Ninjircle),
            ("Starficer", get_asset_path("starficer.png"), Starficer),
            ("TriangleWizard", get_asset_path("Triangle-Wizard.png"), TriangleWizard),
        ]

        imgs = []
        max_size = 180
        for name, path, cls in choices:
            try:
                img = pygame.image.load(path).convert_alpha()
            except Exception:
                img = pygame.Surface((max_size, max_size), pygame.SRCALPHA)
                pygame.draw.circle(img, (200, 200, 200), (max_size//2, max_size//2), max_size//2)

            # scale if too large
            w, h = img.get_size()
            scale = min(1.0, max_size / max(w, h))
            if scale < 1.0:
                img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
            imgs.append((img, cls))

        selecting = True
        while selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    # detect clicks on images
                    n = len(imgs)
                    for i, (img, cls) in enumerate(imgs):
                        cx = WIDTH * (i + 1) // (n + 1)
                        cy = HEIGHT // 2
                        rect = img.get_rect(center=(cx, cy))
                        if rect.collidepoint((mx, my)):
                            return cls

            screen.fill((30, 30, 30))
            n = len(imgs)
            for i, (img, cls) in enumerate(imgs):
                cx = WIDTH * (i + 1) // (n + 1)
                cy = HEIGHT // 2
                rect = img.get_rect(center=(cx, cy))
                screen.blit(img, rect)

            pygame.display.flip()

    SelectedClass = character_selection_screen(screen)
    # Place player at center of the world so they appear centered on the world
    player = SelectedClass((WORLD_W / 2, WORLD_H / 2))
    camera = Camera((WIDTH, HEIGHT), (WORLD_W, WORLD_H))
    pause_menu = PauseMenu(WIDTH, HEIGHT, get_asset_path("Exit-Button.png"))

    # Pre-generate all world objects for the entire world
    for tile_y in range(0, WORLD_H, TILE_H):
        for tile_x in range(0, WORLD_W, TILE_W):
            world_objects.extend(generate_objects_in_tile(tile_x, tile_y))

    # Initialize spatial grid for efficient collision detection
    spatial_grid = SpatialGrid(WORLD_W, WORLD_H, cell_size=256)
    for obj in world_objects:
        spatial_grid.insert(obj)

    # Enemy list
    enemies = []
    wave_spawn_time = 0.0
    wave_spawn_duration = 10.0  # Spawn over 10 seconds
    wave_spawn_count = 30
    enemies_spawned = 0

    def spawn_minion():
        """Spawn a single minion outside player's view."""
        attempts = 0
        while attempts < 50:
            attempts += 1
            x = random.randint(0, WORLD_W)
            y = random.randint(0, WORLD_H)
            pos = pygame.Vector2(x, y)
            # Require spawn outside player's view (at least one screen away)
            if pos.distance_to(pygame.Vector2(WORLD_W / 2, WORLD_H / 2)) > max(WIDTH, HEIGHT):
                enemies.append(Minion((x, y)))
                return True
        return False

    # Projectiles list
    projectiles = []

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # Toggle pause on ESC
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if not pause_menu.paused:
                    pause_menu.enter(screen)
                else:
                    pause_menu.exit()

            # Handle mouse click for attacks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not pause_menu.paused:
                mouse_pos = pygame.mouse.get_pos()
                # Calculate direction from player to mouse
                screen_center = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
                direction = mouse_pos - screen_center
                if direction.length() > 0:
                    direction = direction.normalize()
                    # Try to attack
                    if player.try_attack(dt):
                        projectiles.append(player.fire_projectile(direction))

            # Let pause menu handle click events when paused
            result = pause_menu.handle_event(event)
            if result == "quit":
                pygame.quit()
                sys.exit()

        if not pause_menu.paused:
            # Update wave spawn timer
            wave_spawn_time += dt
            target_spawned = int((wave_spawn_time / wave_spawn_duration) * wave_spawn_count)
            while enemies_spawned < target_spawned and enemies_spawned < wave_spawn_count:
                spawn_minion()
                enemies_spawned += 1
            player.handle_input(dt, world_objects, spatial_grid)
            camera.update(player.pos)

            # Update projectiles
            for p in projectiles[:]:  # Iterate over copy to allow removal
                p.update(dt)
                
                # Check collision with enemies
                for e in enemies[:]:
                    if p.check_collision_with_enemy(e):
                        e.take_damage(p.damage)
                        p.dead = True
                        break
                
                # Remove dead projectiles
                if p.dead:
                    projectiles.remove(p)

            # Auto-fire player weapons
            player.auto_fire(dt, enemies, projectiles)

            # Update enemies
            for e in enemies:
                e.update(dt, player, world_objects, spatial_grid, enemies)
                # check collision with player (mask-based)
                try:
                    if e.overlaps(player.pos, player.get_mask()):
                        # Apply contact damage with cooldown per enemy
                        now = pygame.time.get_ticks() / 1000.0
                        if now - getattr(e, 'last_contact_time', -9999.0) >= getattr(e, 'contact_cooldown', 0.7):
                            e.last_contact_time = now
                            player.take_damage(getattr(e, 'contact_damage', 1))
                except Exception:
                    pass

            # Draw world: tile the background image to cover the visible world area
            offset = camera.offset

            # Determine first tile coordinates (world space) to draw
            first_tile_x = (int(offset.x) // TILE_W) * TILE_W
            first_tile_y = (int(offset.y) // TILE_H) * TILE_H

            # Number of tiles needed to cover the screen (add 2 for buffer)
            tiles_x = WIDTH // TILE_W + 3
            tiles_y = HEIGHT // TILE_H + 3

            for ix in range(tiles_x):
                for iy in range(tiles_y):
                    tile_x = first_tile_x + ix * TILE_W
                    tile_y = first_tile_y + iy * TILE_H

                    # Skip tiles outside the defined world bounds
                    if tile_x + TILE_W < 0 or tile_x > WORLD_W:
                        continue
                    if tile_y + TILE_H < 0 or tile_y > WORLD_H:
                        continue

                    screen_x = tile_x - offset.x
                    screen_y = tile_y - offset.y
                    screen.blit(BG_TILE, (int(screen_x), int(screen_y)))

                    # Draw semi-transparent 1px border around each tile to match thin grid lines
                    border_surface = pygame.Surface((TILE_W, TILE_H), pygame.SRCALPHA)
                    pygame.draw.rect(border_surface, (0, 0, 0, 50), (0, 0, TILE_W, TILE_H), 1)
                    screen.blit(border_surface, (int(screen_x), int(screen_y)))

            # Draw world objects and player sorted by depth (y-coordinate of bottom edge)
            # Collect visible renderable entities with their depth
            render_list = []
            
            # Get nearby objects for rendering (larger radius for better render distance)
            nearby_render_objs = spatial_grid.get_nearby(camera.offset + pygame.Vector2(WIDTH / 2, HEIGHT / 2), radius=5)
            
            for obj in nearby_render_objs:
                # Only include if on-screen
                screen_x = obj.pos.x - offset.x
                screen_y = obj.pos.y - offset.y
                if -200 < screen_x < WIDTH + 200 and -200 < screen_y < HEIGHT + 200:
                    depth = obj.get_bottom_y()
                    render_list.append((depth, obj, "object"))

            # Add player to render list
            player_depth = player.pos.y + player.get_image().get_height() / 2
            render_list.append((player_depth, player, "player"))

            # Remove dead enemies before rendering
            enemies[:] = [en for en in enemies if not en.dead]

            # Include visible enemies in render list
            for e in enemies:
                screen_x = e.pos.x - offset.x
                screen_y = e.pos.y - offset.y
                if -200 < screen_x < WIDTH + 200 and -200 < screen_y < HEIGHT + 200:
                    render_list.append((e.pos.y + e.get_image().get_height() / 2, e, "enemy"))

            # Include projectiles in render list
            for p in projectiles:
                screen_x = p.pos.x - offset.x
                screen_y = p.pos.y - offset.y
                if -200 < screen_x < WIDTH + 200 and -200 < screen_y < HEIGHT + 200:
                    render_list.append((p.pos.y, p, "projectile"))

            # Sort by depth (y-coordinate of bottom edge)
            render_list.sort(key=lambda x: x[0])

            # Render all entities in depth order
            for depth, entity, entity_type in render_list:
                if entity_type == "object":
                    entity.draw(screen, camera)
                elif entity_type == "player":
                    entity.draw(screen, camera)
                elif entity_type == "enemy":
                    entity.draw(screen, camera)
                elif entity_type == "projectile":
                    entity.draw(screen, camera)

            pygame.display.flip()
        else:
            # Paused: render paused menu (blurred snapshot + exit button)
            pause_menu.render(screen)
            pygame.display.flip()


if __name__ == "__main__":
    main()