import pygame
import math


class Projectile:
    """Base projectile class for player attacks.
    
    Handles direction, speed, lifetime, and simple linear movement.
    """

    def __init__(self, pos, direction, speed=500, lifetime=5.0, damage=10, radius=8):
        self.pos = pygame.Vector2(pos)
        self.direction = direction.normalize() if direction.length() > 0 else pygame.Vector2(1, 0)
        self.speed = speed
        self.lifetime = lifetime
        self.age = 0
        self.damage = damage
        self.radius = radius
        self.dead = False

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
        pygame.draw.circle(surface, (255, 255, 0), (int(screen_pos.x), int(screen_pos.y)), self.radius)

    def check_collision_with_enemy(self, enemy):
        """Check if projectile hits an enemy (simple circular collision)."""
        dist = self.pos.distance_to(enemy.pos)
        enemy_img = enemy.get_image()
        enemy_radius = max(enemy_img.get_width(), enemy_img.get_height()) / 2
        return dist < (self.radius + enemy_radius)
