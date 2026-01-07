import pygame
import math


class RadiusWeapon:
    """Melee radius weapon that orbits around the player.
    
    The weapon appears at a distance from the player and swings in a circular
    path around them for a duration, then enters cooldown before activating again.
    
    Attributes:
        radius_size: Distance from player center to orbit path (pixels)
        object_size: Diameter of the attack object sprite (pixels)
        speed: Angular speed of orbit (radians per second)
        duration: How long weapon stays active (seconds)
        cooldown: How long before weapon can activate again (seconds)
    """

    def __init__(self, player_pos, damage=10, radius_size=80, object_size=30, 
                 speed=4.0, duration=0.5, cooldown=1.0, image_path=None):
        """Initialize a radius weapon.
        
        Args:
            player_pos: pygame.Vector2 of the player's position
            damage: Damage dealt on hit
            radius_size: Distance from player to orbit path
            object_size: Size of the weapon sprite
            speed: Radians per second (orbital angular velocity)
            duration: Active time in seconds
            cooldown: Cooldown time in seconds after duration
            image_path: Optional path to weapon image
        """
        self.player_pos = player_pos.copy()
        self.damage = damage
        self.radius_size = radius_size
        self.object_size = object_size
        self.speed = speed  # radians per second
        self.duration = duration
        self.cooldown = cooldown
        self.image_path = image_path
        
        # State tracking
        self.active = True  # Currently swinging
        self.age = 0.0  # Time elapsed in current phase
        self.total_age = 0.0  # Total time since creation
        self.angle = 0.0  # Current angle in radians
        self.dead = False
        
        # Load image
        self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                # Scale if needed
                w, h = self.image.get_size()
                if w != object_size or h != object_size:
                    self.image = pygame.transform.scale(self.image, (object_size, object_size))
            except Exception:
                self.image = None

    @property
    def pos(self):
        """Current position based on angle and radius (as property for compatibility)."""
        offset_x = math.cos(self.angle) * self.radius_size
        offset_y = math.sin(self.angle) * self.radius_size
        return self.player_pos + pygame.Vector2(offset_x, offset_y)

    def get_position(self):
        """Calculate current position based on angle and radius."""
        return self.pos

    def update(self, dt, player_pos):
        """Update weapon state: position, timing, and lifecycle.
        
        Args:
            dt: Delta time in seconds
            player_pos: Current player position (to track moving player)
        """
        if self.dead:
            return
        
        # Update player position reference
        self.player_pos = player_pos.copy()
        
        # Update total age
        self.total_age += dt
        self.age += dt
        
        if self.active:
            # Weapon is swinging
            self.angle += self.speed * dt
            
            # Check if duration expired
            if self.age >= self.duration:
                self.active = False
                self.age = 0.0
        else:
            # Weapon is in cooldown
            if self.age >= self.cooldown:
                # Duration + cooldown complete: mark as dead
                self.dead = True

    def draw(self, surface, camera):
        """Draw the radius weapon at its current orbit position."""
        # Only draw while active (during duration). Hide during cooldown.
        if not self.active:
            return

        pos = self.get_position()
        screen_pos = camera.apply(pos)

        if self.image:
            rect = self.image.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
            surface.blit(self.image, rect)
        else:
            # Fallback: draw circle
            pygame.draw.circle(surface, (200, 100, 50), (int(screen_pos.x), int(screen_pos.y)), 
                             self.object_size // 2)

    def check_collision_with_enemy(self, enemy):
        """Check if weapon hits an enemy (circular collision)."""
        # Only check collisions while active
        if not self.active:
            return False
        pos = self.get_position()
        dist = pos.distance_to(enemy.pos)
        enemy_img = enemy.get_image()
        enemy_radius = max(enemy_img.get_width(), enemy_img.get_height()) / 2
        weapon_radius = self.object_size / 2
        return dist < (weapon_radius + enemy_radius)
