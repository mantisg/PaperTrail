from .enemy import Enemy
import os


class AttackRobot(Enemy):
    image_path = os.path.join("assets", "attack_robot_1.png")
    speed = 90

    def __init__(self, pos):
        super().__init__(pos)
