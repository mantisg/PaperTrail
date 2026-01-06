import pygame

class Camera:
	def __init__(self, screen_size, world_size):
		self.screen_w, self.screen_h = screen_size
		self.world_w, self.world_h = world_size
		self.offset = pygame.Vector2(0, 0)

	def update(self, target_pos: pygame.Vector2):
		x = target_pos.x - self.screen_w / 2
		y = target_pos.y - self.screen_h / 2

		# Clamp to world bounds so camera doesn't show outside the world
		x = max(0, min(x, self.world_w - self.screen_w))
		y = max(0, min(y, self.world_h - self.screen_h))

		self.offset.update(x, y)

	def apply(self, pos: pygame.Vector2) -> pygame.Vector2:
		return pygame.Vector2(pos.x - self.offset.x, pos.y - self.offset.y)