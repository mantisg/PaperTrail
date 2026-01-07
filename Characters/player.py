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
        # Animation / multi-frame sprite support
        # Subclasses may set `standing_image_path` (string) and
        # `moving_image_paths` (list of strings). If not set, the
        # legacy `image_path` is used as a single-frame sprite.
        self.standing_image_path = getattr(self, 'standing_image_path', None)
        self.moving_image_paths = getattr(self, 'moving_image_paths', None)
        self._standing_img = None
        self._standing_img_flipped = None
        self._moving_imgs = None
        self._moving_imgs_flipped = None
        self.is_moving = False
        self.animation_timer = 0.0
        self.ANIMATION_FRAME_TIME = getattr(self, 'ANIMATION_FRAME_TIME', 0.4)
        self.current_moving_frame = 0

        # Attack system
        self.last_attack_time = 0
        self.attack_cooldown = 0.2  # seconds between attacks
        self.attack_speed = 500  # projectile speed
        self.attack_damage = 10
        self.last_attack_direction = pygame.Vector2(1, 0)
        # Health
        self.max_health = 100
        self.health = self.max_health
        # Weapon (defaults - subclasses override)
        self.weapon_fire_rate = getattr(self, 'weapon_fire_rate', None)
        self.weapon_damage = getattr(self, 'weapon_damage', None)
        self.weapon_image = getattr(self, 'weapon_image', None)
        self.weapon_range = getattr(self, 'weapon_range', None)
        # Initialize last fire so player can fire immediately on start
        self.weapon_last_fire = float(self.weapon_fire_rate) if self.weapon_fire_rate else 0.0

    def _load_image(self):
        if self._image_loaded:
            return
        # Prefer multi-frame sprite fields if provided by subclass
        # Load standing + moving frames, else fall back to legacy single image
        def _resolve(path):
            if not path:
                return None
            load_path = path
            if (not os.path.isabs(load_path)) and (not os.path.exists(load_path)):
                load_path = get_asset_path(os.path.basename(load_path))
            try:
                return pygame.image.load(load_path).convert_alpha()
            except Exception:
                return None

        if self.standing_image_path or self.moving_image_paths:
            # Load standing image
            s_img = _resolve(self.standing_image_path) or None
            if s_img is None:
                s_img = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(s_img, (255, 0, 0), (self.radius, self.radius), self.radius)
            self._standing_img = s_img
            self._standing_img_flipped = pygame.transform.flip(s_img, True, False)

            # Load moving images list
            self._moving_imgs = []
            self._moving_imgs_flipped = []
            if self.moving_image_paths:
                for p in self.moving_image_paths:
                    m = _resolve(p)
                    if m is None:
                        m = s_img.copy()
                    self._moving_imgs.append(m)
                    self._moving_imgs_flipped.append(pygame.transform.flip(m, True, False))

            # For collision and legacy use, keep _image/_mask referencing standing image
            self._image = self._standing_img
            self._image_flipped = self._standing_img_flipped
            self._mask = pygame.mask.from_surface(self._image)
            self._image_loaded = True
            # initialize animation frame index
            self.current_moving_frame = 0
            return

        # Legacy single-image path: keep previous behavior
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
        # If multi-frame sprites are present, select correct frame
        if self._standing_img is not None and self._moving_imgs is not None:
            if not getattr(self, 'is_moving', False) or not self._moving_imgs:
                return self._standing_img_flipped if self.facing_left else self._standing_img
            # moving: pick frame based on timer index
            idx = int(self.current_moving_frame) % max(1, len(self._moving_imgs))
            return self._moving_imgs_flipped[idx] if self.facing_left else self._moving_imgs[idx]
        return self._image_flipped if self.facing_left else self._image

    def get_mask(self):
        if not self._image_loaded:
            self._load_image()
        # Prefer standing-image mask if available
        if self._standing_img is not None:
            return pygame.mask.from_surface(self._standing_img)
        return self._mask

    def get_partial_mask_bottom_third(self):
        """Return a mask representing only the bottom 1/3rd of the player."""
        if self._partial_mask is not None:
            return self._partial_mask

        if not self._image_loaded:
            self._load_image()

        # Use standing image as the base for partial mask when available
        base_img = self._standing_img if self._standing_img is not None else self._image
        base_mask = pygame.mask.from_surface(base_img)
        w, h = base_mask.get_size()
        third_h = max(1, h // 3)
        
        # Create a new mask for the bottom third
        partial = pygame.mask.Mask((w, third_h))
        
        # Copy pixels from bottom third of original mask
        for y in range(third_h):
            for x in range(w):
                src_y = h - third_h + y  # Bottom third starts here
                if base_mask.get_at((x, src_y)):
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

        # Determine movement state for animation based on keys held
        keys_pressed = keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]
        was_moving = getattr(self, 'is_moving', False)
        self.is_moving = keys_pressed

        # Update animation timer while moving
        if self.is_moving:
            self.animation_timer += dt
            # advance frames when timer exceeds threshold
            if self.animation_timer >= self.ANIMATION_FRAME_TIME:
                # consume intervals (support slow/fast dt)
                steps = int(self.animation_timer / self.ANIMATION_FRAME_TIME)
                self.animation_timer -= steps * self.ANIMATION_FRAME_TIME
                if self._moving_imgs:
                    # cycle through moving frames
                    self.current_moving_frame = (self.current_moving_frame + steps) % len(self._moving_imgs)
                else:
                    self.current_moving_frame = 0
        else:
            # Reset to standing frame when not moving
            self.animation_timer = 0.0
            self.current_moving_frame = 0

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
        img = self.get_image()
        rect = img.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
        surface.blit(img, rect)
        # Draw health bar above player
        bar_width = max(40, img.get_width())
        bar_height = 6
        bar_x = int(screen_pos.x - bar_width / 2)
        bar_y = int(screen_pos.y - img.get_height() / 2) - 10
        # Background (red for missing health)
        pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # Foreground (green for current health)
        hp_frac = max(0.0, min(1.0, self.health / float(self.max_health)))
        green_width = int(bar_width * hp_frac)
        if green_width > 0:
            pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, green_width, bar_height))

    def take_damage(self, amount):
        """Apply damage to player. Returns True if player died."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return True
        return False

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
        # Determine projectile speed baseline: twice player speed
        speed = max(self.attack_speed, self.speed * 2)
        img_path = None
        if self.weapon_image:
            img_path = self.weapon_image
        lifetime = 5.0
        if self.weapon_range is not None:
            lifetime = max(0.1, self.weapon_range / float(speed))
        return Projectile(self.pos.copy(), direction, speed=speed, lifetime=lifetime,
                          damage=self.weapon_damage or self.attack_damage, radius=6, image_path=img_path)

    def fire_radius_weapon(self):
        """Create a radius weapon (melee swing). Return RadiusWeapon instance or None."""
        weapon_type = getattr(self, 'weapon_type', None)
        if weapon_type != 'radius':
            return None
        
        from radius_weapon import RadiusWeapon
        radius_size = getattr(self, 'weapon_radius_size', 80)
        object_size = getattr(self, 'weapon_object_size', 50)
        speed = getattr(self, 'weapon_speed', 4.0)
        duration = getattr(self, 'weapon_duration', 0.5)
        cooldown = getattr(self, 'weapon_cooldown', 1.0)
        
        return RadiusWeapon(
            self.pos.copy(),
            damage=self.weapon_damage or self.attack_damage,
            radius_size=radius_size,
            object_size=object_size,
            speed=speed,
            duration=duration,
            cooldown=cooldown,
            image_path=self.weapon_image
        )

    def get_closest_enemy(self, enemies, max_range=None):
        """Return the closest enemy object from `enemies` or None if empty/not in range."""
        best = None
        best_d = None
        for e in enemies:
            if e.dead:
                continue
            d = (e.pos - self.pos).length()
            if max_range is not None and d > max_range:
                continue
            if best is None or d < best_d:
                best = e
                best_d = d
        return best

    def auto_fire(self, dt, enemies, projectiles_or_weapons):
        """Automatic weapon firing based on weapon_fire_rate and targeting closest enemy.
        
        Handles both projectile and radius weapons. Pass the appropriate list.
        For radius weapons, the list will be updated with RadiusWeapon instances.
        """
        if not self.weapon_fire_rate or not enemies:
            return
        # Respect per-weapon cooldown interval (projectiles use weapon_fire_rate,
        # radius weapons use duration+cooldown)
        interval = self._weapon_cooldown_interval()
        if self.weapon_last_fire < interval:
            return
        # Ready to fire
        target = self.get_closest_enemy(enemies)
        if not target:
            return
        
        # Fire based on weapon type
        weapon_type = getattr(self, 'weapon_type', None)
        
        if weapon_type == 'radius':
            # Fire radius weapon
            weapon = self.fire_radius_weapon()
            if weapon:
                projectiles_or_weapons.append(weapon)
                try:
                    print(f"Auto-fire: {self.__class__.__name__} triggered radius weapon with damage {weapon.damage}")
                except Exception:
                    pass
        else:
            # Fire projectile (default)
            direction = (target.pos - self.pos)
            if direction.length() == 0:
                direction = pygame.Vector2(1, 0)
            else:
                direction = direction.normalize()
            proj = self.fire_projectile(direction)
            projectiles_or_weapons.append(proj)
            # Debug print for firing (visible when running from source)
            try:
                print(f"Auto-fire: {self.__class__.__name__} fired at enemy at {target.pos} with damage {proj.damage}")
            except Exception:
                pass
        
        self.weapon_last_fire = 0.0

    def _weapon_cooldown_interval(self):
        """Return cooldown interval in seconds before next weapon activation.

        For radius weapons this is duration + cooldown; for projectiles use
        `weapon_fire_rate`.
        """
        wtype = getattr(self, 'weapon_type', None)
        if wtype == 'radius':
            duration = getattr(self, 'weapon_duration', None)
            cooldown = getattr(self, 'weapon_cooldown', None)
            # fallback to weapon_fire_rate if specific fields missing
            if duration is None or cooldown is None:
                return getattr(self, 'weapon_fire_rate', 0.0)
            return float(duration) + float(cooldown)
        return float(getattr(self, 'weapon_fire_rate', 0.0))

    def can_fire_weapon(self):
        """Return True if weapon cooldown has elapsed and weapon can be fired now."""
        interval = self._weapon_cooldown_interval()
        return self.weapon_last_fire >= interval

    def update_weapon_timer(self, dt):
        """Advance internal weapon cooldown timer. Call once per frame."""
        self.weapon_last_fire += dt