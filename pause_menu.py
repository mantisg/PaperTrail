import pygame
import os
import sys
from asset_manager import get_asset_path


class PauseMenu:
    def __init__(self, width, height, exit_image_path=None, menu_image_path=None, blur_scale=0.08):
        self.width = width
        self.height = height
        self.blur_scale = blur_scale
        
        # Button list: (image_path, button_id)
        # Order matters - buttons will be spaced evenly from top to bottom
        self.buttons = []
        self.button_rects = {}  # Map button_id -> rect
        self.paused = False
        self.blurred = None
        
        # Load buttons if provided
        if menu_image_path:
            self.add_button(menu_image_path, "menu")
        if exit_image_path:
            self.add_button(exit_image_path, "exit")
    
    def add_button(self, image_path, button_id):
        """Add a button to the pause menu. Buttons are arranged top-to-bottom."""
        if not os.path.isabs(image_path) and not os.path.exists(image_path):
            image_path = get_asset_path(os.path.basename(image_path))
        try:
            img = pygame.image.load(image_path).convert_alpha()
            self.buttons.append((img, button_id))
        except Exception as e:
            print(f"Failed to load button image {image_path}: {e}")
    
    def _calculate_button_positions(self):
        """Calculate positions for all buttons with even vertical spacing, centered on X."""
        if not self.buttons:
            return
        
        num_buttons = len(self.buttons)
        
        # Calculate vertical spacing: distribute buttons evenly across middle 60% of screen height
        usable_height = self.height * 0.6
        button_spacing = usable_height / (num_buttons + 1)  # +1 for padding above and below
        start_y = (self.height - usable_height) / 2 + button_spacing
        
        # Calculate button positions
        for i, (img, button_id) in enumerate(self.buttons):
            rect = img.get_rect()
            rect.centerx = self.width // 2
            rect.y = int(start_y + i * button_spacing)
            self.button_rects[button_id] = rect
    
    def blur_surface(self, surf):
        scale = self.blur_scale
        small_size = (max(1, int(self.width * scale)), max(1, int(self.height * scale)))
        small = pygame.transform.smoothscale(surf, small_size)
        return pygame.transform.smoothscale(small, (self.width, self.height))

    def enter(self, screen):
        snapshot = screen.copy()
        self.blurred = self.blur_surface(snapshot)
        self._calculate_button_positions()
        self.paused = True

    def exit(self):
        self.paused = False
        self.blurred = None
        self.button_rects = {}

    def handle_event(self, event):
        """Return button_id when clicked, None otherwise."""
        if not self.paused:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for button_id, rect in self.button_rects.items():
                if rect.collidepoint((mx, my)):
                    return button_id
        return None

    def render(self, screen):
        if self.blurred:
            screen.blit(self.blurred, (0, 0))
        else:
            screen.fill((0, 0, 0))
        
        # Draw all buttons
        for button_id, rect in self.button_rects.items():
            # Find and draw the image for this button
            for img, bid in self.buttons:
                if bid == button_id:
                    screen.blit(img, rect)
                    break
