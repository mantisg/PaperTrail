from .player import Player
import os
from asset_manager import get_asset_path


class CircleNinja(Player):
    image_path = get_asset_path("Circle-Ninja.png")
