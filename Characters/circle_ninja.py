from .player import Player
import os
from asset_manager import get_asset_path


class CircleNinja(Player):
    image_path = get_asset_path("Circle-Ninja.png")
    # Weapon: ninja stars
    weapon_fire_rate = 0.5
    weapon_damage = 5
    weapon_image = get_asset_path("NinjaStar.png")
    weapon_range = 400
