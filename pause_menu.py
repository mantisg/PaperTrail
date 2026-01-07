import pygame
import os
import sys
from asset_manager import get_asset_path


class PauseMenu:
    def __init__(self, width, height, exit_image_path, blur_scale=0.08):
        self.width = width
        self.height = height
        self.blur_scale = blur_scale
        img_path = exit_image_path
        if (not os.path.isabs(img_path)) and (not os.path.exists(img_path)):
            img_path = get_asset_path(os.path.basename(img_path))
        self.exit_img = pygame.image.load(img_path).convert_alpha()
        self.paused = False
        self.blurred = None
        self.exit_rect = None

    def blur_surface(self, surf):
        scale = self.blur_scale
        small_size = (max(1, int(self.width * scale)), max(1, int(self.height * scale)))
        small = pygame.transform.smoothscale(surf, small_size)
        return pygame.transform.smoothscale(small, (self.width, self.height))

    def enter(self, screen):
        snapshot = screen.copy()
        self.blurred = self.blur_surface(snapshot)
        self.exit_rect = self.exit_img.get_rect(center=(self.width // 2, self.height // 2))
        self.paused = True

    def exit(self):
        self.paused = False
        self.blurred = None
        self.exit_rect = None

    def handle_event(self, event):
        # Return "quit" when exit button clicked
        if not self.paused:
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.exit_rect and self.exit_rect.collidepoint(event.pos):
                return "quit"
        return None

    def render(self, screen):
        if self.blurred:
            screen.blit(self.blurred, (0, 0))
        else:
            screen.fill((0, 0, 0))
        if self.exit_rect:
            screen.blit(self.exit_img, self.exit_rect)
