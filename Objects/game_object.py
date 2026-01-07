import pygame
import os
import sys
from asset_manager import get_asset_path


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
        # Delegate to centralized collision utilities
        from collision import mask_vs_object
        return mask_vs_object(other_mask, other_pos, self)

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
        # Delegate to centralized collision utilities
        from collision import mask_vs_object
        # When use_self_partial is True, we want to use the bottom-third mask for self
        return mask_vs_object(other_mask, other_pos, self, use_obj_partial=use_self_partial)

    def get_bottom_y(self):
        """Get the y-coordinate of the bottom of this object (for depth sorting)."""
        img = self.get_image()
        return self.pos.y + img.get_height() / 2
