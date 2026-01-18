"""Base Equipment class for equipment items."""
from inventory import Item


class Equipment(Item):
    """Base class for equipment items that provide passive effects."""
    
    def __init__(self, name, description="", rarity="common", image_path=None):
        """
        Initialize equipment.
        
        Args:
            name: Display name of the equipment
            description: Equipment description
            rarity: Item rarity (common, uncommon, rare, epic, legendary)
            image_path: Path to item icon image
        """
        super().__init__(name, "equipment", description, rarity, image_path)
    
    def apply_effect(self, player):
        """Apply equipment effect to player. Override in subclasses."""
        pass
    
    def remove_effect(self, player):
        """Remove equipment effect from player. Override in subclasses."""
        pass
