from .player import Player
from asset_manager import get_asset_path


class Tridolf(Player):
    # Multi-frame images: standing + moving frames
    standing_image_path = get_asset_path("Tridolf-1.png")
    moving_image_paths = [
        get_asset_path("Tridolf-2.png"),
        get_asset_path("Tridolf-3.png"),
    ]
    # Weapon: wizard confetti (kept from previous)
    weapon_fire_rate = 1.0
    weapon_damage = 10
    weapon_image = get_asset_path("WizardConfetti.png")
    weapon_range = 500
