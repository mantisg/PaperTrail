from .enemy import Enemy
from asset_manager import get_asset_path
import pygame
import os


class MiniBoss(Enemy):
    # Map mini boss types to their sprite images
    MINIBOSS_SPRITES = {
        "starficer": get_asset_path("starficer.png"),
        "attack_robot": get_asset_path("attack_robot_1.png"),
        "illuminawty": get_asset_path("illuminawty.png"),
    }
    
    speed = 150
    max_health = 50
    contact_damage = 10
    contact_cooldown = 0.5

    def __init__(self, pos, miniboss_type="starficer"):
        super().__init__(pos)
        self.type = miniboss_type
        self.health = self.max_health
        
        # Set contact damage and cooldown for mini boss
        self.contact_damage = 10
        self.contact_cooldown = 0.5
        
        # Set image based on mini boss type
        if miniboss_type in self.MINIBOSS_SPRITES:
            self.image_path = self.MINIBOSS_SPRITES[miniboss_type]
        else:
            self.image_path = self.MINIBOSS_SPRITES["starficer"]  # Default to starficer

    def _load_image(self):
        """Load image and scale attack_robot sprite by 50%."""
        if self._image_loaded:
            return
        
        if self.image_path:
            try:
                load_path = self.image_path
                if (not os.path.isabs(load_path)) and (not os.path.exists(load_path)):
                    load_path = get_asset_path(os.path.basename(load_path))
                img = pygame.image.load(load_path).convert_alpha()
            except Exception:
                img = None
        else:
            img = None
        
        if img is None:
            img = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(img, (200, 100, 0), (16, 16), 16)
        
        # Scale attack_robot sprite by 50% (1.5x)
        if self.type == "attack_robot":
            w, h = img.get_size()
            img = pygame.transform.smoothscale(img, (int(w * 1.5), int(h * 1.5)))
        
        self._image = img
        self._mask = pygame.mask.from_surface(self._image)
        self._image_loaded = True
