from .game_object import GameObject
import os


class Pie(GameObject):
    """Health pickup item. Increases player health by 10 (capped at 100)."""
    image_path = os.path.join("assets", "pie.png")

    def __init__(self, pos):
        super().__init__(pos)
        self.picked = False
