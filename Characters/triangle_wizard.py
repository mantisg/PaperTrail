from .player import Player
import os
from asset_manager import get_asset_path


class TriangleWizard(Player):
    image_path = os.path.join("assets", "Triangle-Wizard.png")
    # Weapon: wizard confetti
    weapon_fire_rate = 1.0
    weapon_damage = 10
    weapon_image = get_asset_path("WizardConfetti.png")
    weapon_range = 500
