from .enemy import Enemy
import os


class Minion(Enemy):
    # For now, reuse multiply image; later other types map to different images
    image_path = os.path.join("assets", "minion-multiply.png")
    speed = 140

    def __init__(self, pos, minion_type="multiply"):
        super().__init__(pos)
        self.type = minion_type
        # Optionally set different images per type in future
