from .player import Player
from asset_manager import get_asset_path
from Objects.Weapons.wizard_confetti import WizardConfetti


class Tridolf(Player):
    # Multi-frame images: standing + moving frames
    standing_image_path = get_asset_path("Tridolf-1.png")
    moving_image_paths = [
        get_asset_path("Tridolf-2.png"),
        get_asset_path("Tridolf-3.png"),
    ]
    
    # Starting weapon
    starting_weapon_class = WizardConfetti
    
    # Weapon: wizard confetti (projectile type)
    weapon_type = "projectile"
    weapon_fire_rate = 1.0
    weapon_damage = 10
    weapon_image = get_asset_path("WizardConfetti.png")
    weapon_range = 500
    weapon_size = 10
    weapon_speed = 600
    
    def __init__(self, pos, radius=40, speed=300):
        super().__init__(pos, radius, speed)
        # Add starting weapon to inventory
        if hasattr(self, 'starting_weapon_class') and self.starting_weapon_class:
            starting_weapon = self.starting_weapon_class()
            self.inventory.add_item(starting_weapon)
            starting_weapon.apply_effect(self)