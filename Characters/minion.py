from .enemy import Enemy
from asset_manager import get_asset_path


class Minion(Enemy):
    # Map minion types to their sprite images
    MINION_SPRITES = {
        "multiply": get_asset_path("minion-multiply.png"),
        "positive": get_asset_path("positive.png"),
        "divisive": get_asset_path("divisive.png"),
    }
    
    speed = 140
    max_health = 2
    contact_damage = 1
    contact_cooldown = 0.7

    def __init__(self, pos, minion_type="multiply"):
        super().__init__(pos)
        self.type = minion_type
        self.health = self.max_health
        
        # Set image based on minion type
        if minion_type in self.MINION_SPRITES:
            self.image_path = self.MINION_SPRITES[minion_type]
        else:
            self.image_path = self.MINION_SPRITES["multiply"]  # Default to multiply
