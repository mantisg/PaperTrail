import pygame
import sys
from asset_manager import get_asset_path


class TitleScreen:
    """Title screen that shows at game start with start button."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Load and scale title screen background to fill screen
        try:
            self.background = pygame.image.load(get_asset_path("Title_Screen.png")).convert()
            self.background = pygame.transform.scale(self.background, (width, height))
        except Exception:
            # Fallback if image not found
            self.background = pygame.Surface((width, height))
            self.background.fill((20, 20, 20))

        # Load start button image
        try:
            self.start_button_img = pygame.image.load(get_asset_path("Start-Button.png")).convert_alpha()
        except Exception:
            # Fallback if image not found
            self.start_button_img = pygame.Surface((200, 80), pygame.SRCALPHA)
            pygame.draw.rect(self.start_button_img, (100, 200, 100), (0, 0, 200, 80))

        # Scale button if needed
        max_btn_width = int(width * 0.2)
        btn_w, btn_h = self.start_button_img.get_size()
        if btn_w > max_btn_width:
            scale = max_btn_width / btn_w
            new_w = int(btn_w * scale)
            new_h = int(btn_h * scale)
            self.start_button_img = pygame.transform.smoothscale(self.start_button_img, (new_w, new_h))

        # Calculate button position: center X, halfway between center and bottom on Y
        btn_w, btn_h = self.start_button_img.get_size()
        self.button_rect = self.start_button_img.get_rect()
        self.button_rect.centerx = width // 2
        # Y: halfway between center (height//2) and bottom (height)
        self.button_rect.y = height // 2 + (height - height // 2) // 2 - btn_h // 2

    def handle_event(self, event):
        """Handle events. Return True if Start button clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.button_rect.collidepoint((mx, my)):
                return True
        return False

    def draw(self, screen):
        """Draw title screen."""
        screen.blit(self.background, (0, 0))
        screen.blit(self.start_button_img, self.button_rect)

    def run(self, screen):
        """Run title screen loop. Returns when player clicks start."""
        clock = pygame.time.Clock()
        fps = 60

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.handle_event(event):
                    return  # Start button clicked, exit title screen

            self.draw(screen)
            pygame.display.flip()
            clock.tick(fps)
