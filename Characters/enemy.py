import pygame
import os
import math
import sys
import random
from asset_manager import get_asset_path


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
        # Contact damage state
        self.contact_damage = 1
        self.contact_cooldown = 0.7
        self.last_contact_time = -9999.0
        self.tilt_speed = 10.0
        self.tilt_time = random.uniform(0, 2 * math.pi / self.tilt_speed)
        self.tilt_amplitude = 10.0

    def _load_image(self):
        if self._image_loaded:
            return
        if self.image_path:
            try:
                load_path = self.image_path
                if (not os.path.isabs(load_path)) and (not os.path.exists(load_path)):
                    load_path = get_asset_path(os.path.basename(load_path))
                img = pygame.image.load(load_path).convert_alpha()
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
        img = self.get_tilted_image()
        rect = img.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
        surface.blit(img, rect)

    def get_tilted_image(self):
        """
        Returns a smoothly tilted version of the enemy sprite.
        Rotation oscillates between -tilt_amplitude and +tilt_amplitude.
        """
        base_image = self.get_image()

        # Sinusoidal oscillation
        angle = math.sin(self.tilt_time * self.tilt_speed) * self.tilt_amplitude

        rotated = pygame.transform.rotate(base_image, angle)
        return rotated

    def update(self, dt, player, world_objects, spatial_grid=None, enemies=None):
        """Basic enemy update: seek towards player with simple obstacle avoidance.
        """
        if self.dead:
            return

        # Desired velocity towards player
        self.tilt_time += dt
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

        # Collision with static objects: prevent overlap using bottom-third partial masks
        # Check potential collisions; if colliding, attempt simple steering adjustments
        collision = False
        enemy_mask = self.get_mask()
        for obj in nearby:
            # Only collide with trees and bushes using their bottom-third mask so enemies can go behind
            if obj.__class__.__name__ in ("Tree", "Bush"):
                try:
                    if obj.overlaps_partial(new_pos, enemy_mask, use_self_partial=True):
                        collision = True
                        break
                except Exception:
                    # Fallback to full overlap check
                    if obj.overlaps(new_pos, enemy_mask):
                        collision = True
                        break

        # Also check collisions with other enemies (prevent stacking)
        if not collision and enemies is not None:
            from collision import objects_overlap
            for other in enemies:
                if other is self or other.dead:
                    continue
                # quick distance check to avoid expensive mask ops
                if (self.pos - other.pos).length_squared() > ((self.get_image().get_width() + other.get_image().get_width())) ** 2:
                    continue
                if objects_overlap(self, new_pos, other, other.pos):
                    collision = True
                    break

        if not collision:
            self.pos = new_pos
            return

        # Try a lightweight tangent-slide around the blocking object(s) first
        blockers = []
        for obj in nearby:
            if obj.__class__.__name__ in ("Tree", "Bush"):
                try:
                    if obj.overlaps_partial(new_pos, enemy_mask, use_self_partial=True):
                        blockers.append(obj)
                except Exception:
                    if obj.overlaps(new_pos, enemy_mask):
                        blockers.append(obj)

        if blockers:
            # compute average offset from blockers to enemy to estimate tangent
            avg_offset = pygame.Vector2(0, 0)
            for b in blockers:
                avg_offset += (self.pos - b.pos)
            avg_offset /= max(1, len(blockers))
            # tangent vector (perpendicular) to try sliding along
            tangent = pygame.Vector2(-avg_offset.y, avg_offset.x)
            if tangent.length() > 0:
                tangent = tangent.normalize()
                for sign in (1, -1):
                    test_move = tangent * sign * self.speed * dt
                    test_pos = self.pos + test_move
                    blocked = False
                    for obj in nearby:
                        if obj.__class__.__name__ in ("Tree", "Bush"):
                            try:
                                if obj.overlaps_partial(test_pos, enemy_mask, use_self_partial=True):
                                    blocked = True
                                    break
                            except Exception:
                                if obj.overlaps(test_pos, enemy_mask):
                                    blocked = True
                                    break
                    if not blocked and enemies is not None:
                        from collision import objects_overlap
                        for other in enemies:
                            if other is self or other.dead:
                                continue
                            if objects_overlap(self, test_pos, other, other.pos):
                                blocked = True
                                break
                    if not blocked:
                        self.pos = test_pos
                        return

        # Try angle offsets to slide around obstacle
        angles = [15, -15, 30, -30, 60, -60, 90, -90]
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
                    try:
                        if obj.overlaps_partial(test_pos, enemy_mask, use_self_partial=True):
                            blocked = True
                            break
                    except Exception:
                        if obj.overlaps(test_pos, enemy_mask):
                            blocked = True
                            break
            # check test_pos vs other enemies
            if not blocked and enemies is not None:
                from collision import objects_overlap
                for other in enemies:
                    if other is self or other.dead:
                        continue
                    if objects_overlap(self, test_pos, other, other.pos):
                        blocked = True
                        break
            if not blocked:
                self.pos = test_pos
                return

        # otherwise remain in place

    def on_hit_player(self, player):
        # Legacy placeholder kept for compatibility
        pass

    def take_damage(self, amount):
        """Reduce health by amount and mark dead if depleted."""
        try:
            self.health -= amount
        except Exception:
            self.health = self.max_health - amount
        if self.health <= 0:
            self.dead = True

    def overlaps(self, other_pos, other_mask):
        """Check overlap between this enemy and another mask at other_pos."""
        # Delegate to centralized collision utilities
        from collision import mask_vs_object
        return mask_vs_object(other_mask, other_pos, self)
