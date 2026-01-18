import pygame
import os
import random
import time
import tkinter as tk
import sys
from camera import Camera
from Characters.player import Player
from Characters.ninjircle import Ninjircle
from Characters.triangle_wizard import Tridolf
from Characters.sqwerewolf import Sqwerewolf
from Characters.starficer import Starficer
from Objects.tree import Tree
from Objects.bush import Bush
from Objects.pie import Pie
from Objects.item_drop import ItemDrop
from Objects.Equipment.quicks import Quicks
from Objects.Weapons.ninja_stars import NinjaStars
from Objects.Weapons.wizard_confetti import WizardConfetti
from Objects.Weapons.squirrel_burst import SquirrelBurst
from pause_menu import PauseMenu
from spatial_grid import SpatialGrid
from Characters.minion import Minion
from Characters.mini_boss import MiniBoss
from Characters.attack_robot import AttackRobot
from projectile import Projectile
from radius_weapon import RadiusWeapon
from asset_manager import get_asset_path
from title_screen import TitleScreen
from ui import InventoryUI, PauseMenuInventoryUI
from inventory import Item


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
TREE_DENSITY = 0.25
BUSH_DENSITY = 0.20


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

    # Show title screen first
    title_screen = TitleScreen(WIDTH, HEIGHT)
    title_screen.run(screen)

    # Character selection screen before starting
    def character_selection_screen(screen):
        choices = [
            ("Ninjircle", get_asset_path("Ninjircle-1.png"), Ninjircle),
            ("Tridolf", get_asset_path("Tridolf-1.png"), Tridolf),
            ("Sqwerewolf", get_asset_path("Sqwerewolf-1.png"), Sqwerewolf),
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

    # Outer game loop to allow restarting after character selection
    game_running = True
    while game_running:
        SelectedClass = character_selection_screen(screen)
        
        # Initialize game state for this run
        # Place player at center of the world so they appear centered on the world
        player = SelectedClass((WORLD_W / 2, WORLD_H / 2))
        camera = Camera((WIDTH, HEIGHT), (WORLD_W, WORLD_H))
        pause_menu = PauseMenu(WIDTH, HEIGHT)
        pause_menu.add_button(get_asset_path("Menu-Button.png"), "menu")
        pause_menu.add_button(get_asset_path("Exit-Button.png"), "exit")
        
        # Initialize UI
        inventory_ui = InventoryUI(WIDTH, HEIGHT)
        pause_inventory_ui = PauseMenuInventoryUI(WIDTH, HEIGHT)

        # Pre-generate all world objects for the entire world (fresh generation each game)
        world_objects = []
        for tile_y in range(0, WORLD_H, TILE_H):
            for tile_x in range(0, WORLD_W, TILE_W):
                world_objects.extend(generate_objects_in_tile(tile_x, tile_y))

        # Initialize spatial grid for efficient collision detection
        spatial_grid = SpatialGrid(WORLD_W, WORLD_H, cell_size=256)
        for obj in world_objects:
            spatial_grid.insert(obj)

        # Spawn 3 pie health items scattered randomly around the world
        pies = []
        PIE_COUNT = 3
        attempts = 0
        while len(pies) < PIE_COUNT and attempts < 200:
            attempts += 1
            x = random.randint(0, WORLD_W)
            y = random.randint(0, WORLD_H)
            pos = pygame.Vector2(x, y)
            # Avoid spawning too close to center so player has to find them
            if pos.distance_to(pygame.Vector2(WORLD_W / 2, WORLD_H / 2)) < max(WIDTH, HEIGHT) // 2:
                continue
            pie = Pie((x, y))
            pies.append(pie)
            world_objects.append(pie)
            spatial_grid.insert(pie)
        
        # Spawn sample items for pickup
        item_drops = []
        # Build item pool, excluding the player's starting weapon
        all_items = [
            NinjaStars(),
            WizardConfetti(),
            SquirrelBurst(),
            Quicks(),
        ]
        
        # Filter out the player's starting weapon from the pool
        sample_items = []
        if hasattr(player, 'starting_weapon_class') and player.starting_weapon_class:
            starting_weapon_type = player.starting_weapon_class
            for item in all_items:
                if type(item) != starting_weapon_type:
                    sample_items.append(item)
        else:
            sample_items = all_items
        
        ITEM_DROP_COUNT = 6
        item_attempts = 0
        while len(item_drops) < ITEM_DROP_COUNT and item_attempts < 200:
            item_attempts += 1
            x = random.randint(0, WORLD_W)
            y = random.randint(0, WORLD_H)
            pos = pygame.Vector2(x, y)
            # Avoid spawning too close to center
            if pos.distance_to(pygame.Vector2(WORLD_W / 2, WORLD_H / 2)) < max(WIDTH, HEIGHT) // 2:
                continue
            item = random.choice(sample_items)
            item_drop = ItemDrop((x, y), item)
            item_drops.append(item_drop)
            world_objects.append(item_drop)
            spatial_grid.insert(item_drop)
        
        # Enemy list
        enemies = []
        
        # Wave system: list of (wave_time_seconds, wave_minion_count, wave_miniboss_count)
        waves = [
            (0.0, 30, 0),      # Initial wave at 0:00 with 30 minions
            (10.0, 50, 0),     # Second wave at 0:10 with 50 minions
            (25.0, 50, 5),     # Third wave at 0:25 with 50 minions and 5 mini bosses
        ]
        wave_index = 0
        wave_spawn_time = 0.0
        wave_spawn_duration = 10.0  # Spawn each wave over 10 seconds
        wave_spawn_count = 0
        wave_miniboss_count = 0
        enemies_spawned = 0
        minibosses_spawned = 0

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
                    minion_type = random.choice(["multiply", "positive", "divisive"])
                    enemies.append(Minion((x, y), minion_type=minion_type))
                    return True
            return False

        def spawn_miniboss():
            """Spawn a single mini boss outside player's view."""
            attempts = 0
            while attempts < 50:
                attempts += 1
                x = random.randint(0, WORLD_W)
                y = random.randint(0, WORLD_H)
                pos = pygame.Vector2(x, y)
                # Require spawn outside player's view (at least one screen away)
                if pos.distance_to(pygame.Vector2(WORLD_W / 2, WORLD_H / 2)) > max(WIDTH, HEIGHT):
                    miniboss_type = random.choice(["starficer", "attack_robot", "illuminawty"])
                    enemies.append(MiniBoss((x, y), miniboss_type=miniboss_type))
                    return True
            return False

        # Projectiles list
        projectiles = []
        
        # Game timer
        game_timer = 0.0  # Elapsed time in seconds
        MAX_GAME_TIME = 20 * 60  # 20 minutes in seconds
        
        # Create font for timer display
        timer_font = pygame.font.Font(None, 56)

        # Inner game loop for current game session
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
                        if player.try_attack(dt) and player.can_fire_weapon():
                            weapon_type = getattr(player, 'weapon_type', None)
                            if weapon_type == 'radius':
                                weapon = player.fire_radius_weapon()
                                if weapon:
                                    projectiles.append(weapon)
                                    player.weapon_last_fire = 0.0
                            else:
                                projectiles.append(player.fire_projectile(direction))
                                player.weapon_last_fire = 0.0

                # Let pause menu handle click events when paused
                result = pause_menu.handle_event(event)
                if result == "exit":
                    pygame.quit()
                    sys.exit()
                elif result == "menu":
                    # Menu button: return to character selection and restart game
                    pause_menu.exit()
                    running = False

            if not pause_menu.paused:
                # Update game timer (only when not paused)
                game_timer += dt
                if game_timer > MAX_GAME_TIME:
                    game_timer = MAX_GAME_TIME
                
                # Check if a new wave should start
                if wave_index < len(waves):
                    wave_data = waves[wave_index]
                    wave_start_time = wave_data[0]
                    wave_minion_count = wave_data[1]
                    wave_miniboss_count = wave_data[2] if len(wave_data) > 2 else 0
                    
                    if game_timer >= wave_start_time:
                        # Wave has started, spawn minions and mini bosses
                        time_into_wave = game_timer - wave_start_time
                        if time_into_wave >= 0:
                            # Spawn minions
                            target_minions_spawned = int((time_into_wave / wave_spawn_duration) * wave_minion_count)
                            while enemies_spawned < target_minions_spawned and enemies_spawned < wave_minion_count:
                                spawn_minion()
                                enemies_spawned += 1
                            
                            # Spawn mini bosses
                            target_minibosses_spawned = int((time_into_wave / wave_spawn_duration) * wave_miniboss_count)
                            while minibosses_spawned < target_minibosses_spawned and minibosses_spawned < wave_miniboss_count:
                                spawn_miniboss()
                                minibosses_spawned += 1
                            
                            # Check if wave is complete
                            if enemies_spawned >= wave_minion_count and minibosses_spawned >= wave_miniboss_count and time_into_wave > wave_spawn_duration:
                                wave_index += 1
                                enemies_spawned = 0
                                minibosses_spawned = 0
                
                player.handle_input(dt, world_objects, spatial_grid)
                camera.update(player.pos)
                # Advance player's weapon cooldown timer
                player.update_weapon_timer(dt)

                # Check for nearby Pie pickups
                try:
                    nearby_for_pickup = spatial_grid.get_nearby(player.pos, radius=1)
                    for obj in nearby_for_pickup:
                        if isinstance(obj, Pie) and not getattr(obj, 'picked', False):
                            if obj.overlaps(player.pos, player.get_mask()):
                                # Pickup: increase health by 10, capped at max_health
                                player.health = min(player.max_health, player.health + 10)
                                obj.picked = True
                                # Remove from world_objects so it's no longer considered
                                try:
                                    if obj in world_objects:
                                        world_objects.remove(obj)
                                except Exception:
                                    pass
                                try:
                                    if obj in pies:
                                        pies.remove(obj)
                                except Exception:
                                    pass
                        
                        # Check for item drop pickups
                        if isinstance(obj, ItemDrop) and not obj.picked:
                            if obj.can_pickup(player.pos):
                                # Check if weapon uniqueness constraint is met
                                from Objects.Weapons.weapon import Weapon
                                if isinstance(obj.item, Weapon):
                                    # Check if player already has this weapon type
                                    weapon_name = obj.item.name
                                    already_has = any(w.name == weapon_name for w in player.inventory.weapons)
                                    if already_has:
                                        # Skip this weapon, don't pick up
                                        continue
                                
                                # Try to add to inventory
                                if player.inventory.add_item(obj.item):
                                    inventory_ui.add_item_notification(obj.item)
                                    obj.picked = True
                                    
                                    # Apply equipment/weapon effects immediately
                                    if hasattr(obj.item, 'apply_effect'):
                                        try:
                                            obj.item.apply_effect(player)
                                        except Exception:
                                            pass
                                    
                                    # If this is a weapon, remove all duplicates from the ground
                                    if isinstance(obj.item, Weapon):
                                        weapon_name = obj.item.name
                                        for drop in item_drops[:]:
                                            if not drop.picked and isinstance(drop.item, Weapon):
                                                if drop.item.name == weapon_name:
                                                    drop.picked = True
                                                    try:
                                                        if drop in world_objects:
                                                            world_objects.remove(drop)
                                                    except Exception:
                                                        pass
                                    
                                    # Remove from world
                                    try:
                                        if obj in world_objects:
                                            world_objects.remove(obj)
                                    except Exception:
                                        pass
                                    try:
                                        if obj in item_drops:
                                            item_drops.remove(obj)
                                    except Exception:
                                        pass
                except Exception:
                    pass
                
                # Update inventory UI
                inventory_ui.update(dt)

                # Update projectiles and radius weapons
                for p in projectiles[:]:  # Iterate over copy to allow removal
                    # Handle radius weapons vs projectiles
                    if isinstance(p, RadiusWeapon):
                        p.update(dt, player.pos)
                    else:
                        p.update(dt)

                    # Check collision with enemies
                    for e in enemies[:]:
                        if p.check_collision_with_enemy(e):
                            e.take_damage(p.damage)
                            # Only mark as dead on collision for projectiles
                            if not isinstance(p, RadiusWeapon):
                                p.dead = True
                            break

                    # Remove dead projectiles/weapons
                    if p.dead:
                        projectiles.remove(p)

                # Auto-fire player weapons
                player.auto_fire(dt, enemies, projectiles)
                
                # Update item drops
                for item_drop in item_drops:
                    if not item_drop.picked:
                        item_drop.update(dt)

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
                    if getattr(obj, 'picked', False):
                        continue
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
                
                # Draw inventory UI (weapons and equipment at top)
                inventory_ui.draw_inventory_bars(screen, player.inventory)
                
                # Draw recently added item notifications
                inventory_ui.draw_notifications(screen)
                
                # Draw game timer at top center
                minutes = int(game_timer) // 60
                seconds = int(game_timer) % 60
                timer_text = f"{minutes:02d}:{seconds:02d}"
                timer_surface = timer_font.render(timer_text, True, (0, 0, 0))
                timer_rect = timer_surface.get_rect(center=(WIDTH // 2, 30))
                screen.blit(timer_surface, timer_rect)

                pygame.display.flip()
            else:
                # Paused: render paused menu (blurred snapshot + exit button)
                pause_menu.render(screen)
                
                # Draw full inventory on pause screen
                pause_inventory_ui.draw(screen, player.inventory, pause_menu_alpha=200)
                
                pygame.display.flip()


if __name__ == "__main__":
    main()