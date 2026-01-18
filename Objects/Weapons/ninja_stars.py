"""Ninja Stars weapon for Ninjircle."""
from Objects.Weapons.weapon import Weapon
from asset_manager import get_asset_path


class NinjaStars(Weapon):
    """Ninja Stars weapon - rapid projectile attack."""
    
    # Weapon parameters
    FIRE_RATE = 1.5
    DAMAGE = 8
    WEAPON_RANGE = 400
    WEAPON_SIZE = 6
    WEAPON_SPEED = 700
    
    def __init__(self):
        """Initialize Ninja Stars weapon."""
        super().__init__(
            name="Ninja Stars",
            description="Rapid throwing stars with decent range.",
            rarity="uncommon",
            image_path=get_asset_path("NinjaStar.png"),
            fire_rate=self.FIRE_RATE,
            damage=self.DAMAGE,
            weapon_range=self.WEAPON_RANGE
        )
    
    def fire(self, player, enemies, projectiles_list):
        """Fire ninja stars projectiles."""
        if not self.can_fire() or not enemies:
            return
        
        # Find closest enemy
        closest_enemy = None
        closest_distance = float('inf')
        for enemy in enemies:
            if enemy.dead:
                continue
            distance = (enemy.pos - player.pos).length()
            if distance < closest_distance:
                closest_distance = distance
                closest_enemy = enemy
        
        if not closest_enemy:
            return
        
        # Fire projectile at enemy
        direction = (closest_enemy.pos - player.pos)
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = player.last_attack_direction
        
        from projectile import Projectile
        projectile = Projectile(
            player.pos.copy(),
            direction,
            speed=self.WEAPON_SPEED,
            lifetime=max(0.1, self.WEAPON_RANGE / self.WEAPON_SPEED),
            damage=self.DAMAGE,
            radius=self.WEAPON_SIZE,
            image_path=get_asset_path("NinjaStar.png")
        )
        projectiles_list.append(projectile)
        self.last_fire_time = 0.0

