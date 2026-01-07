from .enemy import Enemy
from asset_manager import get_asset_path


class Minion(Enemy):
    # For now, reuse multiply image; later other types map to different images
    image_path = get_asset_path("minion-multiply.png")
    speed = 140
    max_health = 2
    contact_damage = 1
    contact_cooldown = 0.7

    def __init__(self, pos, minion_type="multiply"):
        super().__init__(pos)
        self.type = minion_type
        self.health = self.max_health
