"""UI rendering for inventory and game HUD."""
import pygame


class InventoryUI:
    """Renders inventory slots at the top of the screen during gameplay."""
    
    def __init__(self, width, height, padding=10, slot_size=40, gap=5):
        """
        Initialize inventory UI.
        
        Args:
            width: Screen width
            height: Screen height
            padding: Padding from edges
            slot_size: Size of each inventory slot
            gap: Gap between slots
        """
        self.width = width
        self.height = height
        self.padding = padding
        self.slot_size = slot_size
        self.gap = gap
        self.recently_added_items = []  # List of (item, time_added) tuples
        self.item_display_duration = 3.0  # Show item for 3 seconds
        
        # Font for labels
        self.font_small = pygame.font.Font(None, 20)
        self.font_label = pygame.font.Font(None, 16)
    
    def update(self, dt):
        """Update recently added items, removing old ones."""
        self.recently_added_items = [
            (item, time_left - dt) 
            for item, time_left in self.recently_added_items 
            if time_left - dt > 0
        ]
    
    def add_item_notification(self, item):
        """Add item to notification queue."""
        self.recently_added_items.append((item, self.item_display_duration))
    
    def draw_inventory_bars(self, surface, inventory):
        """Draw weapon and equipment inventory at top of screen."""
        y = self.padding
        x = self.padding
        
        # Draw weapons section
        self._draw_inventory_section(
            surface, inventory.weapons, "WEAPONS", 
            x, y, inventory.WEAPON_SLOTS
        )
        
        # Draw equipment section below weapons
        equipment_y = y + (self.slot_size + self.gap * 2) + 30
        self._draw_inventory_section(
            surface, inventory.equipment, "EQUIPMENT", 
            x, equipment_y, inventory.EQUIPMENT_SLOTS
        )
    
    def draw_relic_slots(self, surface, inventory):
        """Draw relic inventory (usually on pause screen)."""
        y = self.padding
        x = self.padding
        
        self._draw_inventory_section(
            surface, inventory.relics, "RELICS", 
            x, y, inventory.RELIC_SLOTS
        )
    
    def _draw_inventory_section(self, surface, items, label, x, y, max_slots):
        """Draw a single inventory section (weapons, equipment, or relics)."""
        # Draw label
        label_surf = self.font_small.render(label, True, (200, 200, 200))
        surface.blit(label_surf, (x, y))
        
        slot_y = y + 25
        slot_x = x
        
        # Draw empty and filled slots
        for i in range(max_slots):
            # Slot background
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)
            
            if i < len(items):
                # Draw filled slot
                item = items[i]
                color = item._get_rarity_color()
                pygame.draw.rect(surface, color, slot_rect, 2)
                pygame.draw.rect(surface, (50, 50, 50), slot_rect)
                
                # Draw item icon
                item_img = item.get_image(self.slot_size - 6)
                img_rect = item_img.get_rect(center=slot_rect.center)
                surface.blit(item_img, img_rect)
                
                # Draw item count or hover info (slot number)
                count_text = self.font_label.render(str(i + 1), True, (255, 255, 255))
                surface.blit(count_text, (slot_x + 2, slot_y + 2))
            else:
                # Draw empty slot
                pygame.draw.rect(surface, (100, 100, 100), slot_rect, 1)
            
            slot_x += self.slot_size + self.gap
    
    def draw_notifications(self, surface):
        """Draw recently added item notifications."""
        x = self.width - self.padding - 200
        y = self.padding
        
        for item, time_left in self.recently_added_items:
            # Calculate alpha based on time remaining (fade out)
            alpha = int(255 * (time_left / self.item_display_duration))
            
            # Create notification box
            notification_height = 60
            notification_rect = pygame.Rect(x, y, 200, notification_height)
            
            # Draw background with semi-transparency
            notification_surf = pygame.Surface((200, notification_height), pygame.SRCALPHA)
            pygame.draw.rect(notification_surf, (30, 30, 30, alpha), (0, 0, 200, notification_height))
            pygame.draw.rect(notification_surf, (*item._get_rarity_color(), alpha), 
                            (0, 0, 200, notification_height), 2)
            surface.blit(notification_surf, notification_rect.topleft)
            
            # Draw item name
            name_text = self.font_small.render(f"+ {item.name}", True, (200, 200, 200))
            name_text.set_alpha(alpha)
            surface.blit(name_text, (x + 10, y + 10))
            
            # Draw item type
            type_text = self.font_label.render(item.item_type.upper(), True, (150, 150, 150))
            type_text.set_alpha(alpha)
            surface.blit(type_text, (x + 10, y + 35))
            
            y += notification_height + self.gap


class PauseMenuInventoryUI:
    """Renders full inventory details on pause screen."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font_title = pygame.font.Font(None, 36)
        self.font_label = pygame.font.Font(None, 24)
        self.font_text = pygame.font.Font(None, 18)
    
    def draw(self, surface, inventory, pause_menu_alpha=200):
        """Draw full inventory on pause screen."""
        # Draw semi-transparent background overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, pause_menu_alpha), (0, 0, self.width, self.height))
        surface.blit(overlay, (0, 0))
        
        # Draw inventory sections
        padding = 40
        
        # Title
        title = self.font_title.render("INVENTORY", True, (255, 200, 100))
        surface.blit(title, (padding, padding))
        
        # Weapons section
        y = padding + 60
        self._draw_section(surface, inventory.weapons, "WEAPONS", 
                         padding, y, inventory.WEAPON_SLOTS)
        
        # Equipment section
        y += 200
        self._draw_section(surface, inventory.equipment, "EQUIPMENT", 
                         padding, y, inventory.EQUIPMENT_SLOTS)
        
        # Relics section
        y += 200
        self._draw_section(surface, inventory.relics, "RELICS", 
                         padding, y, inventory.RELIC_SLOTS)
    
    def _draw_section(self, surface, items, label, x, y, max_slots):
        """Draw a full inventory section with details."""
        # Section label
        label_text = self.font_label.render(label, True, (200, 200, 200))
        surface.blit(label_text, (x, y))
        
        item_y = y + 40
        for i in range(max_slots):
            if i < len(items):
                item = items[i]
                color = item._get_rarity_color()
                
                # Item box
                item_box = pygame.Rect(x, item_y, 500, 40)
                pygame.draw.rect(surface, color, item_box, 2)
                
                # Item icon
                item_img = item.get_image(35)
                surface.blit(item_img, (x + 5, item_y + 2))
                
                # Item name and type
                name_text = self.font_text.render(f"{item.name} ({item.item_type})", True, (255, 255, 255))
                surface.blit(name_text, (x + 45, item_y + 5))
                
                # Item description
                desc_text = self.font_text.render(item.description, True, (150, 150, 150))
                surface.blit(desc_text, (x + 45, item_y + 22))
            
            item_y += 50
