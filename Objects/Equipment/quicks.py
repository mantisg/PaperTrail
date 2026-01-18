"""Quicks equipment: Provides a small speed boost."""
from Objects.Equipment.equipment import Equipment
from asset_manager import get_asset_path


class Quicks(Equipment):
    """Quicks equipment - provides a 20% movement speed boost (cumulative)."""
    
    SPEED_MULTIPLIER = 1.2  # 20% speed increase per item
    
    def __init__(self):
        """Initialize Quicks equipment."""
        super().__init__(
            name="Quicks",
            description="I am speeeeeed!!!! +20% move speed (stacks)",
            rarity="common",
            image_path=get_asset_path("Quicks-card.png")
        )
    
    def apply_effect(self, player):
        """Apply speed boost to player.
        
        Quicks can stack. Each Quicks adds 20% to base speed.
        Calls player's update_speed_from_equipment() to recalculate.
        """
        if hasattr(player, 'update_speed_from_equipment'):
            player.update_speed_from_equipment()
    
    def remove_effect(self, player):
        """Remove speed boost from player (recalculates based on remaining Quicks)."""
        if hasattr(player, 'update_speed_from_equipment'):
            player.update_speed_from_equipment()
