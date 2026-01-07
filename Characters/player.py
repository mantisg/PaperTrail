import pygame
import os
import math
from asset_manager import get_asset_path


class Player:
    """Base player class. Subclasses should provide `image_path` or override `_load_image`.

    Handles movement, sprite loading/flipping, mask creation, and attack/projectiles.
    """

    image_path = None

    def __init__(self, pos, radius=40, speed=300):
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.speed = speed

        self._image = None
        self._image_flipped = None
        self._mask = None
        self._partial_mask = None  # Cache for bottom third
        self._image_loaded = False
        self.facing_left = False

        # Attack system
        self.last_attack_time = 0
        self.attack_cooldown = 0.2  # seconds between attacks
        self.attack_speed = 500  # projectile speed
        self.attack_damage = 10
        self.last_attack_direction = pygame.Vector2(1, 0)

    def _load_image(self):
        if self._image_loaded:
            return

        if self.image_path:
            try:
                load_path = self.image_path
                # Resolve relative paths when running from PyInstaller bundle
                if (not os.path.isabs(load_path)) and (not os.path.exists(load_path)):
                    load_path = get_asset_path(os.path.basename(load_path))
                img = pygame.image.load(load_path).convert_alpha()
            except Exception:
                img = None
        else:
            img = None

        if img is None:
            # fallback to a simple circle surface
            img = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(img, (255, 0, 0), (self.radius, self.radius), self.radius)

        self._image = img
        self._image_flipped = pygame.transform.flip(self._image, True, False)
        # Create mask from non-transparent pixels for collision detection
        self._mask = pygame.mask.from_surface(self._image)
        self._image_loaded = True

    def get_image(self):
        if not self._image_loaded:
            self._load_image()
        return self._image_flipped if self.facing_left else self._image

    def get_mask(self):
        if not self._image_loaded:
            self._load_image()
        return self._mask

    def get_partial_mask_bottom_third(self):
        """Return a mask representing only the bottom 1/3rd of the player."""
        if self._partial_mask is not None:
            return self._partial_mask

        if not self._image_loaded:
            self._load_image()

        w, h = self._mask.get_size()
        third_h = max(1, h // 3)
        
        # Create a new mask for the bottom third
        partial = pygame.mask.Mask((w, third_h))
        
        # Copy pixels from bottom third of original mask
        for y in range(third_h):
            for x in range(w):
                src_y = h - third_h + y  # Bottom third starts here
                if self._mask.get_at((x, src_y)):
                    partial.set_at((x, y), True)
        
        self._partial_mask = partial
        return self._partial_mask

    def handle_input(self, dt, world_objects=None, spatial_grid=None):
        keys = pygame.key.get_pressed()
        movement = pygame.Vector2(0, 0)
        if keys[pygame.K_w]:
            movement.y -= 1
        if keys[pygame.K_s]:
            movement.y += 1
        if keys[pygame.K_a]:
            movement.x -= 1
            self.facing_left = True
        if keys[pygame.K_d]:
            movement.x += 1
            self.facing_left = False

        if movement.length_squared() > 0:
            movement = movement.normalize() * self.speed * dt
            new_pos = self.pos + movement

            # Check collision with nearby objects only (using spatial grid if available)
            collision = False
            if world_objects:
                player_mask = self.get_mask()
                player_partial_mask = self.get_partial_mask_bottom_third()
                
                # Get only nearby objects for collision check
                if spatial_grid:
                    objects_to_check = spatial_grid.get_nearby(new_pos, radius=1)
                else:
                    objects_to_check = world_objects
                
                for obj in objects_to_check:
                    # Trees: use bottom 1/3rd of both masks
                    if obj.__class__.__name__ == "Tree":
                        tree_partial_mask = obj.get_partial_mask_bottom_third()
                        if obj.overlaps_partial(new_pos, player_partial_mask, 
                                               use_self_partial=True, use_other_partial=True):
                            collision = True
                            break
                    # Bushes: use full masks
                    elif obj.__class__.__name__ == "Bush":
                        if obj.overlaps(new_pos, player_mask):
                            collision = True
                            break

                if not collision:
                    self.pos = new_pos
            else:
                self.pos = new_pos

    def draw(self, surface, camera):
        screen_pos = camera.apply(self.pos)
        self._load_image()
        img = self._image_flipped if self.facing_left else self._image
        rect = img.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
        surface.blit(img, rect)

    def try_attack(self, dt):
        """Update attack cooldown and return True if ready to attack."""
        self.last_attack_time += dt
        if self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = 0
            return True
        return False

    def fire_projectile(self, direction):
        """Create a projectile in the given direction. Return the Projectile instance."""
        from projectile import Projectile
        return Projectile(self.pos.copy(), direction, self.attack_speed, lifetime=5.0, 
                         damage=self.attack_damage)