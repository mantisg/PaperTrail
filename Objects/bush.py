from .game_object import GameObject
import os


class Bush(GameObject):
    """A bush object that blocks the player."""
    image_path = os.path.join("assets", "bush2.png")
