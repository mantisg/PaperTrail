"""Inventory system for items: weapons, equipment, and relics.

ARCHITECTURE:
=============
The item system is designed to be scalable and follows the same pattern as the Enemy class:

1. ITEM CLASS (This file)
   - Base Item class: Defines what an item IS (name, type, description, image, effects)
   - Equipment/Weapon/Relic subclasses: Define specific item types with their behaviors
   - These are PURE DATA classes that define item properties and apply effects

2. GROUND ITEM RENDERING (Objects/item_drop.py)
   - GroundItem class: Handles rendering, animation, and pickup logic
   - ALL animation parameters are class variables that can be overridden
   - Simply pass any Item instance to GroundItem to display it on ground
   - Animation: smooth bob (up/down) and rotation with no jitter

3. INVENTORY UI (ui.py)
   - InventoryUI classes: Render items in inventory slots
   - Automatically use item's image and properties

ADDING A NEW ITEM:
==================
Example: Create a new equipment item "Armor"

Step 1: Create Objects/Equipment/armor.py
    from Objects.Equipment.equipment import Equipment
    
    class Armor(Equipment):
        DEFENSE_BONUS = 20
        
        def __init__(self):
            super().__init__(
                name="Armor",
                description="Increases defense by 20",
                rarity="uncommon",
                image_path=get_asset_path("Armor-card.png")
            )
        
        def apply_effect(self, player):
            player.defense = getattr(player, 'defense', 0) + self.DEFENSE_BONUS
        
        def remove_effect(self, player):
            player.defense = max(0, player.defense - self.DEFENSE_BONUS)

Step 2: Import in main.py
    from Objects.Equipment.armor import Armor

Step 3: Add to item spawn pool
    sample_items = [
        Armor(),
        Quicks(),
        # ... other items
    ]

That's it! The item will automatically:
- Display on ground with smooth animation and glow
- Display in inventory slots with proper icon
- Show on pause menu with description
- Apply/remove effects when picked up/unequipped
"""
import pygame


class Item:
    """Base class for collectible items."""
    
    def __init__(self, name, item_type, description="", rarity="common", image_path=None):
        """
        Initialize an item.
        
        Args:
            name: Display name of the item
            item_type: One of 'weapon', 'equipment', or 'relic'
            description: Item description
            rarity: Item rarity (common, uncommon, rare, epic, legendary)
            image_path: Path to item icon image
        """
        self.name = name
        self.item_type = item_type
        self.description = description
        self.rarity = rarity
        self.image_path = image_path
        self._image = None
    
    def get_image(self, size=40):
        """Get item icon image, loading and caching if needed."""
        if self._image is None and self.image_path:
            try:
                self._image = pygame.image.load(self.image_path).convert_alpha()
            except Exception:
                self._image = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.rect(self._image, (100, 100, 100), (0, 0, size, size))
        
        if self._image is None:
            # Default item icon
            self._image = pygame.Surface((size, size), pygame.SRCALPHA)
            color = self._get_rarity_color()
            pygame.draw.rect(self._image, color, (0, 0, size, size))
        
        # Scale to desired size if needed
        if self._image.get_size() != (size, size):
            self._image = pygame.transform.scale(self._image, (size, size))
        
        return self._image
    
    def _get_rarity_color(self):
        """Get color based on rarity."""
        rarity_colors = {
            'common': (200, 200, 200),      # Gray
            'uncommon': (0, 255, 0),        # Green
            'rare': (0, 100, 255),          # Blue
            'epic': (160, 0, 255),          # Purple
            'legendary': (255, 165, 0),     # Orange
        }
        return rarity_colors.get(self.rarity, (200, 200, 200))
    
    def __repr__(self):
        return f"Item({self.name}, {self.item_type})"


class Inventory:
    """Player inventory system with slots for weapons, equipment, and relics."""
    
    WEAPON_SLOTS = 5
    EQUIPMENT_SLOTS = 5
    RELIC_SLOTS = 3
    
    def __init__(self):
        """Initialize empty inventory."""
        self.weapons = []
        self.equipment = []
        self.relics = []
    
    def add_item(self, item):
        """
        Add item to appropriate inventory slot.
        
        Returns: True if item was added, False if inventory slot is full
        """
        if item.item_type == 'weapon':
            if len(self.weapons) < self.WEAPON_SLOTS:
                self.weapons.append(item)
                return True
        elif item.item_type == 'equipment':
            if len(self.equipment) < self.EQUIPMENT_SLOTS:
                self.equipment.append(item)
                return True
        elif item.item_type == 'relic':
            if len(self.relics) < self.RELIC_SLOTS:
                self.relics.append(item)
                return True
        
        return False
    
    def remove_item(self, item):
        """Remove item from inventory."""
        if item in self.weapons:
            self.weapons.remove(item)
            return True
        elif item in self.equipment:
            self.equipment.remove(item)
            return True
        elif item in self.relics:
            self.relics.remove(item)
            return True
        return False
    
    def get_all_items(self):
        """Return all items in inventory."""
        return self.weapons + self.equipment + self.relics
    
    def get_item_at(self, item_type, slot_index):
        """Get item at specific slot."""
        if item_type == 'weapon' and slot_index < len(self.weapons):
            return self.weapons[slot_index]
        elif item_type == 'equipment' and slot_index < len(self.equipment):
            return self.equipment[slot_index]
        elif item_type == 'relic' and slot_index < len(self.relics):
            return self.relics[slot_index]
        return None
    
    def is_full(self, item_type):
        """Check if a particular inventory type is full."""
        if item_type == 'weapon':
            return len(self.weapons) >= self.WEAPON_SLOTS
        elif item_type == 'equipment':
            return len(self.equipment) >= self.EQUIPMENT_SLOTS
        elif item_type == 'relic':
            return len(self.relics) >= self.RELIC_SLOTS
        return False
    
    def count_items(self, item_type=None):
        """Count items in inventory, optionally by type."""
        if item_type == 'weapon':
            return len(self.weapons)
        elif item_type == 'equipment':
            return len(self.equipment)
        elif item_type == 'relic':
            return len(self.relics)
        elif item_type is None:
            return len(self.get_all_items())
        return 0
