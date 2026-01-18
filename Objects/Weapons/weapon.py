"""Base Weapon class for weapon items.

WEAPON SYSTEM ARCHITECTURE:
===========================
Weapons follow the same scalable pattern as Equipment and other items.

1. WEAPON CLASS (this file)
   - Base class defining what a weapon IS
   - Properties: fire_rate, damage, weapon_range
   - apply_effect(): Adds weapon to player's active_weapons list
   - Multiple weapons can be active at the same time

2. SPECIFIC WEAPON CLASSES
   - Inherit from Weapon
   - Define weapon-specific stats
   - Can override apply_effect() for custom behavior

3. CHARACTER STARTING WEAPONS
   - Each character class has starting_weapon_class attribute
   - Automatically added to inventory on character init
   - Applies effect immediately (weapon becomes active)

4. MULTI-WEAPON SUPPORT
   - Player.active_weapons tracks all active weapons
   - When weapon is picked up, it's added to active_weapons
   - Auto-fire system fires all active weapons simultaneously
   - Example: Wizard picks up Ninja Stars -> shoots both confetti AND stars

ADDING A NEW WEAPON:
===================
1. Create Objects/Weapons/new_weapon.py:
    from Objects.Weapons.weapon import Weapon
    from asset_manager import get_asset_path
    
    class NewWeapon(Weapon):
        def __init__(self):
            super().__init__(
                name="New Weapon",
                description="...",
                rarity="uncommon",
                image_path=get_asset_path("New-Weapon-card.png"),
                fire_rate=2.0,
                damage=10,
                weapon_range=400
            )

2. If it's a starting weapon, add to character class:
    starting_weapon_class = NewWeapon

3. Add to item spawn pool in main.py:
    sample_items = [
        NewWeapon(),
        # ... other items
    ]

That's it! The weapon automatically:
- Displays in inventory with proper icon
- Can be picked up on ground
- Activates when picked up or equipped
- Fires simultaneously with other active weapons
"""
from inventory import Item


class Weapon(Item):
    """Base class for weapon items that provide attack capabilities."""
    
    def __init__(self, name, description="", rarity="common", image_path=None, 
                 fire_rate=1.0, damage=10, weapon_range=500):
        """
        Initialize weapon.
        
        Args:
            name: Display name of the weapon
            description: Weapon description
            rarity: Item rarity (common, uncommon, rare, epic, legendary)
            image_path: Path to item icon image
            fire_rate: Shots per second
            damage: Damage per shot
            weapon_range: Range of weapon in pixels
        """
        super().__init__(name, "weapon", description, rarity, image_path)
        self.fire_rate = fire_rate
        self.damage = damage
        self.weapon_range = weapon_range
        self.last_fire_time = 0.0
    
    def apply_effect(self, player):
        """Add this weapon to player's active weapons. Override in subclasses if needed."""
        if not hasattr(player, 'active_weapons'):
            player.active_weapons = []
        if self not in player.active_weapons:
            player.active_weapons.append(self)
    
    def remove_effect(self, player):
        """Remove this weapon from player's active weapons."""
        if hasattr(player, 'active_weapons') and self in player.active_weapons:
            player.active_weapons.remove(self)
    
    def update(self, dt):
        """Update weapon cooldown timer. Call once per frame."""
        self.last_fire_time += dt
    
    def can_fire(self):
        """Check if enough time has passed to fire this weapon."""
        if self.fire_rate <= 0:
            return False
        return self.last_fire_time >= (1.0 / self.fire_rate)
    
    def fire(self, player, enemies, projectiles_list):
        """Fire this weapon at the closest enemy.
        
        Override in subclasses to implement specific firing behavior.
        This is the default projectile implementation.
        """
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
            speed=self.fire_rate * self.damage * 10,  # Rough approximation
            lifetime=max(0.1, self.weapon_range / (self.fire_rate * self.damage * 10)),
            damage=self.damage,
            radius=4,
            image_path=None
        )
        projectiles_list.append(projectile)
        self.last_fire_time = 0.0
