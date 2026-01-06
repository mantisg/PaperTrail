import pygame
import os
import math


class Enemy:
    image_path = None
    speed = 120
    max_health = 30

    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self._image = None
        self._mask = None
        self._image_loaded = False
        self.dead = False
        self.health = self.max_health

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
            img = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(img, (255, 0, 0), (16, 16), 16)
        self._image = img
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

    def draw(self, surface, camera):
        screen_pos = camera.apply(self.pos)
        img = self.get_image()
        rect = img.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
        surface.blit(img, rect)

    def update(self, dt, player, world_objects, spatial_grid=None):
        """Basic enemy update: seek towards player with simple obstacle avoidance.
        """
        if self.dead:
            return

        # Desired velocity towards player
        to_player = (player.pos - self.pos)
        dist = to_player.length()
        if dist > 0:
            desired = to_player.normalize() * self.speed
        else:
            desired = pygame.Vector2(0, 0)

        # Obstacle avoidance: get nearby static objects
        avoidance = pygame.Vector2(0, 0)
        avoid_radius = 80
        avoid_strength = 250
        nearby = world_objects
        if spatial_grid:
            nearby = spatial_grid.get_nearby(self.pos, radius=1)

        for obj in nearby:
            # skip very far
            offset = self.pos - obj.pos
            d = offset.length()
            if d <= 0 or d > avoid_radius:
                continue
            # compute repulsion
            rep = offset.normalize() * (avoid_strength * (avoid_radius - d) / avoid_radius)
            avoidance += rep

        # Combine desired and avoidance
        steer = desired + avoidance
        if steer.length() > 0:
            movement = steer.normalize() * self.speed * dt
        else:
            movement = pygame.Vector2(0, 0)

        new_pos = self.pos + movement

        # Collision with static objects: prevent overlap
        # Check potential collisions; if colliding, attempt simple steering adjustments
        collision = False
        enemy_mask = self.get_mask()
        for obj in nearby:
            # Only collide with trees and bushes
            if obj.__class__.__name__ in ("Tree", "Bush"):
                if obj.overlaps(new_pos, enemy_mask):
                    collision = True
                    break

        if not collision:
            self.pos = new_pos
            return

        # Try angle offsets to slide around obstacle
        angles = [30, -30, 60, -60, 90, -90]
        for a in angles:
            rad = math.radians(a)
            cos, sin = math.cos(rad), math.sin(rad)
            dir_vec = to_player.normalize()
            rotated = pygame.Vector2(dir_vec.x * cos - dir_vec.y * sin, dir_vec.x * sin + dir_vec.y * cos)
            test_move = rotated.normalize() * self.speed * dt
            test_pos = self.pos + test_move
            blocked = False
            for obj in nearby:
                if obj.__class__.__name__ in ("Tree", "Bush"):
                    if obj.overlaps(test_pos, enemy_mask):
                        blocked = True
                        break
            if not blocked:
                self.pos = test_pos
                return

        # otherwise remain in place

    def on_hit_player(self, player):
        # Placeholder when enemy touches player
        pass

    def overlaps(self, other_pos, other_mask):
        """Check overlap between this enemy and another mask at other_pos."""
        img = self.get_image()
        self_rect = img.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        other_size = other_mask.get_size()
        other_rect = pygame.Rect(int(other_pos.x - other_size[0] / 2),
                                  int(other_pos.y - other_size[1] / 2),
                                  other_size[0], other_size[1])

        if not self_rect.colliderect(other_rect):
            return False

        offset = (other_rect.x - self_rect.x, other_rect.y - self_rect.y)
        try:
            return self._mask.overlap(other_mask, offset)
        except Exception:
            return True
