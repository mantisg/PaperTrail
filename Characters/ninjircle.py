from .player import Player
import pygame
from asset_manager import get_asset_path


class Ninjircle(Player):
    """Animated Ninjircle character with multi-frame sprites and movement animation.
    
    Uses sprite animation while moving (alternating between two poses) and a standing
    pose when idle. Intended as a test character that can be easily removed.
    
    Sprites:
    - Ninjircle-1.png: Standing pose (used when idle)
    - Ninjircle-2.png: Moving pose 1
    - Ninjircle2-1.png: Moving pose 2
    """
    
    # Weapon: ninja stars (same as CircleNinja)
    weapon_fire_rate = 0.5
    weapon_damage = 5
    weapon_image = get_asset_path("NinjaStar.png")
    weapon_range = 400
    
    # Animation timing
    ANIMATION_FRAME_TIME = 0.3  # seconds between frame switches while moving
    
    def __init__(self, pos, radius=40, speed=300):
        super().__init__(pos, radius, speed)
        
        # Load sprite images
        self.standing_image = get_asset_path("Ninjircle-1.png")
        self.moving_image_1 = get_asset_path("Ninjircle-2.png")
        self.moving_image_2 = get_asset_path("Ninjircle-2_1.png")
        
        # Sprite caches (original and flipped)
        self._standing_img = None
        self._standing_img_flipped = None
        self._moving_img_1 = None
        self._moving_img_1_flipped = None
        self._moving_img_2 = None
        self._moving_img_2_flipped = None
        
        # Animation state
        self.is_moving = False
        self.animation_timer = 0.0
        self.current_moving_frame = 1  # 1 or 2
        
    def _load_sprite_images(self):
        """Load all sprite images and their flipped versions."""
        if self._standing_img is not None:
            return  # Already loaded
            
        # Helper function to load image with fallback
        def load_image(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return img
            except Exception:
                return None
        
        # Load standing pose
        img = load_image(self.standing_image)
        if img is None:
            img = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(img, (100, 100, 255), (self.radius, self.radius), self.radius)
        self._standing_img = img
        self._standing_img_flipped = pygame.transform.flip(img, True, False)
        
        # Load moving pose 1
        img = load_image(self.moving_image_1)
        if img is None:
            img = self._standing_img.copy()
        self._moving_img_1 = img
        self._moving_img_1_flipped = pygame.transform.flip(img, True, False)
        
        # Load moving pose 2
        img = load_image(self.moving_image_2)
        if img is None:
            img = self._standing_img.copy()
        self._moving_img_2 = img
        self._moving_img_2_flipped = pygame.transform.flip(img, True, False)
    
    def _get_current_image(self):
        """Get the current sprite image based on movement state and animation frame."""
        self._load_sprite_images()
        
        if not self.is_moving:
            # Standing pose
            return self._standing_img_flipped if self.facing_left else self._standing_img
        else:
            # Alternating moving poses
            if self.current_moving_frame == 1:
                return self._moving_img_1_flipped if self.facing_left else self._moving_img_1
            else:
                return self._moving_img_2_flipped if self.facing_left else self._moving_img_2
    
    def handle_input(self, dt, world_objects=None, spatial_grid=None):
        """Handle movement input and update animation state."""
        keys = pygame.key.get_pressed()
        movement = pygame.Vector2(0, 0)
        
        # Check if any movement key is held
        keys_pressed = keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]
        
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
        
        # Determine if moving based on keys held, not calculated movement
        was_moving = self.is_moving
        self.is_moving = keys_pressed
        
        # Reset animation if just started moving
        if self.is_moving and not was_moving:
            self.animation_timer = 0.0
            self.current_moving_frame = 1
        
        # Stop animation and reset frame if stopped moving
        if not self.is_moving and was_moving:
            self.animation_timer = 0.0
            self.current_moving_frame = 1
        
        # Update animation timer while moving
        if self.is_moving:
            self.animation_timer += dt
            if self.animation_timer >= self.ANIMATION_FRAME_TIME:
                self.animation_timer -= self.ANIMATION_FRAME_TIME  # Preserve overflow
                # Toggle between frame 1 and 2
                self.current_moving_frame = 2 if self.current_moving_frame == 1 else 1
        
        # Handle movement with collision detection
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
    
    def get_image(self):
        """Return the current sprite image for rendering."""
        return self._get_current_image()
    
    def get_mask(self):
        """Return collision mask based on current sprite."""
        self._load_sprite_images()
        # Use standing image mask for collision (most reliable)
        return pygame.mask.from_surface(self._standing_img)
    
    def get_partial_mask_bottom_third(self):
        """Return a mask representing only the bottom 1/3rd of the character."""
        self._load_sprite_images()
        
        if self._partial_mask is not None:
            return self._partial_mask

        base_img = self._standing_img
        w, h = base_img.get_width(), base_img.get_height()
        base_mask = pygame.mask.from_surface(base_img)
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
    
    def draw(self, surface, camera):
        """Draw the character with animation and health bar."""
        screen_pos = camera.apply(self.pos)
        img = self._get_current_image()
        rect = img.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
        surface.blit(img, rect)
        
        # Draw health bar above character
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
