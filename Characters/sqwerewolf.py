from .player import Player
from asset_manager import get_asset_path
from Objects.Weapons.squirrel_burst import SquirrelBurst

class Sqwerewolf(Player):
    # Image paths (Player will load these if present)
    standing_image_path = get_asset_path("Sqwerewolf-1.png")
    moving_image_paths = [
        get_asset_path("Sqwerewolf-2.png"),
        get_asset_path("Sqwerewolf-3.png"),
    ]

    # Starting weapon
    starting_weapon_class = SquirrelBurst

    # Weapon: melee paw attack (radius weapon)
    weapon_fire_rate = 1.3
    weapon_damage = 20
    weapon_image = get_asset_path("Paw-Attack.png")
    weapon_range = 150
    
    # Radius weapon attributes
    weapon_type = "radius"  # Marks this as a radius weapon
    weapon_radius_size = 90   # Distance from player to orbit path
    weapon_object_size = 50   # Size of attack object
    weapon_speed = 4.0        # Radians per second (orbital speed)
    weapon_duration = 3.0     # Active duration
    weapon_cooldown = 0.7     # Cooldown duration (matches fire_rate)
    
    def __init__(self, pos, radius=40, speed=300):
        super().__init__(pos, radius, speed)
        # Add starting weapon to inventory
        if hasattr(self, 'starting_weapon_class') and self.starting_weapon_class:
            starting_weapon = self.starting_weapon_class()
            self.inventory.add_item(starting_weapon)
            starting_weapon.apply_effect(self)