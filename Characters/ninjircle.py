from .player import Player
from asset_manager import get_asset_path


class Ninjircle(Player):
    """Ninjircle player: declares image paths and weapon properties only.

    Animation, loading, flipping and timing are handled by `Player`.
    """
    # Image paths (Player will load these if present)
    standing_image_path = get_asset_path("Ninjircle-1.png")
    moving_image_paths = [
        get_asset_path("Ninjircle-2.png"),
        get_asset_path("Ninjircle-2_1.png"),
    ]

    # Weapon: ninja stars (projectile type)
    weapon_type = "projectile"
    weapon_fire_rate = 0.5
    weapon_damage = 5
    weapon_image = get_asset_path("NinjaStar.png")
    weapon_range = 400
    weapon_size = 6
    weapon_speed = 700

    # Optional: tweak animation timing for this subclass
    ANIMATION_FRAME_TIME = 0.3

    def __init__(self, pos, radius=40, speed=300):
        super().__init__(pos, radius, speed)

