import pygame
import math


class Projectile:
    """Base projectile class for player attacks.
    
    Handles direction, speed, lifetime, and simple linear movement.
    """

    def __init__(self, pos, direction, speed=500, lifetime=5.0, damage=10, radius=8, image_path=None,
                 size_mult=1.0, speed_mult=1.0):
        """Create a projectile.

        `size_mult` and `speed_mult` are multipliers applied to the base `radius`
        and `speed` respectively. Use a base of 1.0 when no multipliers are
        provided so callers can treat these as optional upgrades.
        """
        self.pos = pygame.Vector2(pos)
        self.direction = direction.normalize() if direction.length() > 0 else pygame.Vector2(1, 0)
        # Apply speed multiplier to base speed
        try:
            self.speed = float(speed) * float(speed_mult)
        except Exception:
            self.speed = float(speed)
        self.lifetime = lifetime
        self.age = 0
        self.damage = damage
        # Apply size multiplier to base radius (ensure at least 1 px)
        try:
            self.radius = max(1, int(radius * float(size_mult)))
        except Exception:
            self.radius = int(radius)
        self.dead = False
        self.image = None
        self.image_path = image_path
        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
            except Exception:
                self.image = None

    def update(self, dt):
        """Update projectile position and lifetime."""
        if self.dead:
            return

        # Move projectile
        movement = self.direction * self.speed * dt
        self.pos += movement

        # Update lifetime
        self.age += dt
        if self.age >= self.lifetime:
            self.dead = True

    def draw(self, surface, camera):
        """Draw projectile as a simple circle."""
        screen_pos = camera.apply(self.pos)
        if self.image:
            img = self.image
            rect = img.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
            surface.blit(img, rect)
        else:
            pygame.draw.circle(surface, (255, 255, 0), (int(screen_pos.x), int(screen_pos.y)), self.radius)

    def check_collision_with_enemy(self, enemy):
        """Check if projectile hits an enemy (simple circular collision)."""
        dist = self.pos.distance_to(enemy.pos)
        enemy_img = enemy.get_image()
        enemy_radius = max(enemy_img.get_width(), enemy_img.get_height()) / 2
        return dist < (self.radius + enemy_radius)
