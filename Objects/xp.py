from .game_object import GameObject
import os


class XP(GameObject):
    """Experience point pickup object. Dropped by enemies and scattered on the map.
    
    Supports multiple XP types: "exp-10", "exp-50", "exp-100", etc.
    """

    XP_TYPES = {
        "exp-10": (os.path.join("assets", "exp-10.png"), 10),
        "exp-50": (os.path.join("assets", "exp-50.png"), 50),
        "exp-100": (os.path.join("assets", "exp-100.png"), 100),
    }

    def __init__(self, pos, xp_type="exp-10"):
        super().__init__(pos)
        if xp_type not in self.XP_TYPES:
            xp_type = "exp-10"
        self.xp_type = xp_type
        self.image_path = self.XP_TYPES[xp_type][0]
        self.value = self.XP_TYPES[xp_type][1]
