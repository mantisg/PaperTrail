from .player import Player
from asset_manager import get_asset_path

class Sqwerewolf(Player):
    # Image paths (Player will load these if present)
    standing_image_path = get_asset_path("Sqwerewolf-1.png")
    moving_image_paths = [
        get_asset_path("Sqwerewolf-2.png"),
        get_asset_path("Sqwerewolf-3.png"),
    ]

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
    weapon_duration = 1.5     # Active duration
    weapon_cooldown = 0.7     # Cooldown duration (matches fire_rate)
    
    def __init__(self, pos, radius=40, speed=300):
        super().__init__(pos, radius, speed)