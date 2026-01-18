"""Item drops and ground items for pickup."""
import pygame
import math


class GroundItem:
    """
    Base class for items sitting on the ground that can be picked up by the player.
    
    Provides shared animation, rendering, and pickup logic. All items inherit from this.
    Specific item behaviors are defined in the Item class passed to this.
    """
    
    # Animation parameters - can be overridden per-instance
    BOB_SPEED = 2.0          # Cycles per second
    BOB_AMOUNT = 5.0         # Maximum vertical offset in pixels
    ROTATION_SPEED = 45.0    # Degrees per second (slowed from 90 to reduce jitter)
    GLOW_SIZE = 40           # Base glow radius
    GLOW_PULSE = 5           # Glow pulse amount
    ITEM_DISPLAY_SIZE = 30   # Size of item icon on ground
    PICKUP_RADIUS = 30       # Distance at which player can pickup
    
    def __init__(self, pos, item, pickup_radius=None):
        """
        Initialize a ground item.
        
        Args:
            pos: (x, y) position in world
            item: Item instance with name, get_image(), etc.
            pickup_radius: Distance at which player can pickup (uses class default if None)
        """
        self.pos = pygame.Vector2(pos)
        self.item = item
        self.pickup_radius = pickup_radius if pickup_radius is not None else self.PICKUP_RADIUS
        self.picked = False
        
        # Animation state
        self.bob_timer = 0.0    # Tracks time for bob animation (fixed)
        self.rotation = 0.0     # Current rotation in degrees
    
    def update(self, dt):
        """Update animation state."""
        # Smooth bob animation using proper sine wave
        self.bob_timer += dt
        # Rotation continues smoothly without jitter
        self.rotation += self.ROTATION_SPEED * dt
        self.rotation %= 360.0
    
    def _get_bob_offset(self):
        """Calculate vertical bob offset using smooth sine wave."""
        return math.sin(self.bob_timer * self.BOB_SPEED * math.pi) * self.BOB_AMOUNT
    
    def _get_glow_radius(self):
        """Calculate glow radius with gentle pulsing."""
        return self.GLOW_SIZE + math.sin(self.bob_timer * self.BOB_SPEED * math.pi) * self.GLOW_PULSE
    
    def draw(self, surface, camera):
        """Draw the item drop on screen."""
        screen_pos = camera.apply(self.pos)
        
        # Draw glow effect with gentle pulsing
        glow_radius = self._get_glow_radius()
        pygame.draw.circle(surface, (100, 150, 255, 50), 
                         (int(screen_pos.x), int(screen_pos.y)), int(glow_radius), 1)
        
        # Get and rotate item image
        item_img = self.item.get_image(self.ITEM_DISPLAY_SIZE)
        rotated = pygame.transform.rotate(item_img, self.rotation)
        
        # Draw with bob animation
        bob_offset = self._get_bob_offset()
        adjusted_y = int(screen_pos.y) + int(bob_offset)
        rect = rotated.get_rect(center=(int(screen_pos.x), adjusted_y))
        surface.blit(rotated, rect)
        
        # Draw item name above
        font = pygame.font.Font(None, 16)
        name_text = font.render(self.item.name, True, (200, 200, 200))
        name_rect = name_text.get_rect(centerx=int(screen_pos.x), bottom=int(screen_pos.y) - 40)
        surface.blit(name_text, name_rect)
    
    def can_pickup(self, player_pos):
        """Check if player is close enough to pick up this item."""
        distance = (self.pos - player_pos).length()
        return distance <= self.pickup_radius
    
    def get_bottom_y(self):
        """Get bottom y coordinate for depth sorting."""
        return self.pos.y + 20
    
    def overlaps(self, other_pos, other_mask):
        """Compatibility method for world object collision."""
        # Item drops use simple distance-based pickup, not mask collision
        return self.can_pickup(other_pos)


# Alias for backwards compatibility
ItemDrop = GroundItem
