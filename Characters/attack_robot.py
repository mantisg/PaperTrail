from .enemy import Enemy
from asset_manager import get_asset_path


class AttackRobot(Enemy):
    image_path = get_asset_path("attack_robot_1.png")
    speed = 90
    max_health = 2
    contact_damage = 1
    contact_cooldown = 0.7

    def __init__(self, pos):
        super().__init__(pos)
