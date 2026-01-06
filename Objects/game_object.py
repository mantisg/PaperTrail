import pygame
import os


class GameObject:
    """Base class for all game objects (trees, bushes, money, xp, etc).
    
    Handles sprite loading, mask creation for collisions, and rendering.
    """

    image_path = None

    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self._image = None
        self._mask = None
        self._partial_mask = None  # Cache for bottom third mask
        self._image_loaded = False

    def _load_image(self):
        if self._image_loaded:
            return

        if self.image_path:
            try:
                img = pygame.image.load(self.image_path).convert_alpha()
            except Exception:
                img = None
        else:
            img = None

        if img is None:
            # Fallback: create a simple gray circle
            img = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(img, (150, 150, 150), (20, 20), 20)

        self._image = img
        # Create mask from non-transparent pixels for collision detection
        self._mask = pygame.mask.from_surface(self._image)
        self._image_loaded = True

    def get_image(self):
        if not self._image_loaded:
            self._load_image()
        return self._image

    def get_mask(self):
        if not self._image_loaded:
            self._load_image()
        return self._mask

    def get_partial_mask_bottom_third(self):
        """Return a mask representing only the bottom 1/3rd of the object.
        
        Useful for collision detection on tall objects like trees where only
        the base should collide. Result is cached.
        """
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

    def draw(self, surface, camera):
        """Draw the object on the surface using camera coordinates."""
        screen_pos = camera.apply(self.pos)
        img = self.get_image()
        rect = img.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
        surface.blit(img, rect)

    def overlaps(self, other_pos, other_mask):
        """Check if this object's mask overlaps with another mask at a given position.
        
        Args:
            other_pos: pygame.Vector2 position to test
            other_mask: pygame.mask.Mask object to test against
        
        Returns:
            True if masks overlap, False otherwise
        """
        img = self.get_image()
        # Get the rect for this object centered on its position
        self_rect = img.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        
        # Get the rect for the other object
        other_rect = other_mask.get_size()
        other_rect = pygame.Rect(int(other_pos.x - other_rect[0] / 2), 
                                  int(other_pos.y - other_rect[1] / 2), 
                                  other_rect[0], other_rect[1])
        
        # Check if rects overlap first (fast check)
        if not self_rect.colliderect(other_rect):
            return False
        
        # If rects overlap, check mask overlap
        offset = (other_rect.x - self_rect.x, other_rect.y - self_rect.y)
        try:
            return self._mask.overlap(other_mask, offset)
        except Exception:
            # Fallback to rect collision if mask collision fails
            return True

    def overlaps_partial(self, other_pos, other_mask, use_self_partial=False, use_other_partial=False):
        """Check overlap using partial masks (bottom 1/3rd).
        
        Args:
            other_pos: pygame.Vector2 position to test
            other_mask: pygame.mask.Mask to test against
            use_self_partial: Use bottom 1/3rd of self's mask
            use_other_partial: Use bottom 1/3rd of other's mask
        
        Returns:
            True if masks overlap, False otherwise
        """
        img = self.get_image()
        self_h = img.get_height()
        
        # Get masks (partial or full)
        self_mask = self.get_partial_mask_bottom_third() if use_self_partial else self._mask
        other_mask_to_use = other_mask  # We receive already-processed mask from caller
        
        # Adjust rect positions if using partial mask
        self_rect = img.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        if use_self_partial:
            self_rect.y = int(self.pos.y + self_h / 3)  # Shift to bottom third
        
        # Get the rect for the other object
        other_size = other_mask_to_use.get_size()
        other_rect = pygame.Rect(int(other_pos.x - other_size[0] / 2), 
                                  int(other_pos.y - other_size[1] / 2), 
                                  other_size[0], other_size[1])
        if use_other_partial:
            other_rect.y = int(other_pos.y + other_size[1] / 3)  # Shift to bottom third
        
        # Check if rects overlap first (fast check)
        if not self_rect.colliderect(other_rect):
            return False
        
        # If rects overlap, check mask overlap
        offset = (other_rect.x - self_rect.x, other_rect.y - self_rect.y)
        try:
            return self_mask.overlap(other_mask_to_use, offset)
        except Exception:
            # Fallback to rect collision if mask collision fails
            return True

    def get_bottom_y(self):
        """Get the y-coordinate of the bottom of this object (for depth sorting)."""
        img = self.get_image()
        return self.pos.y + img.get_height() / 2
