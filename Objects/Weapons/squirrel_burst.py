"""Sqwerewolf weapon for Sqwerewolf."""
from Objects.Weapons.weapon import Weapon
from asset_manager import get_asset_path


class SquirrelBurst(Weapon):
    """Squirrel Burst weapon - heavy damage, slower attack."""
    
    # Weapon parameters
    FIRE_RATE = 0.3
    DAMAGE = 15
    WEAPON_RANGE = 450
    WEAPON_RADIUS_SIZE = 90   # Distance from player to orbit path
    WEAPON_OBJECT_SIZE = 50   # Size of attack object
    WEAPON_SPEED = 4.0        # Radians per second (orbital speed)
    WEAPON_DURATION = 3.0     # Active duration
    WEAPON_COOLDOWN = 0.7     # Cooldown duration
    
    def __init__(self):
        """Initialize Squirrel Burst weapon."""
        super().__init__(
            name="Squirrel Burst",
            description="Powerful paws swipe at the enemy, orbiting around you for a short time",
            rarity="uncommon",
            image_path=get_asset_path("Paw-Attack.png"),
            fire_rate=self.FIRE_RATE,
            damage=self.DAMAGE,
            weapon_range=self.WEAPON_RANGE
        )
    
    def fire(self, player, enemies, projectiles_list):
        """Fire squirrel burst radius weapon."""
        if not self.can_fire():
            return
        
        # Fire radius weapon (paw attack that orbits)
        from radius_weapon import RadiusWeapon
        weapon = RadiusWeapon(
            player.pos.copy(),
            damage=self.DAMAGE,
            radius_size=self.WEAPON_RADIUS_SIZE,
            object_size=self.WEAPON_OBJECT_SIZE,
            speed=self.WEAPON_SPEED,
            duration=self.WEAPON_DURATION,
            cooldown=self.WEAPON_COOLDOWN,
            image_path=get_asset_path("Paw-Attack.png")
        )
        projectiles_list.append(weapon)
        self.last_fire_time = 0.0

