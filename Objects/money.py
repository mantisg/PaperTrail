from .game_object import GameObject
import os


class Money(GameObject):
    """Money pickup object. Dropped by enemies and scattered on the map."""
    image_path = os.path.join("assets", "Money.png")

    def __init__(self, pos, amount=1):
        super().__init__(pos)
        self.amount = amount
