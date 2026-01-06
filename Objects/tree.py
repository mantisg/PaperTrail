from .game_object import GameObject
import os


class Tree(GameObject):
    """A tree object that blocks the player."""
    image_path = os.path.join("assets", "tree.png")
