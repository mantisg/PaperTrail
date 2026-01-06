import pygame


class SpatialGrid:
    """Spatial partitioning grid for efficient collision detection.
    
    Divides the world into cells and stores objects in their respective cells.
    Only objects in the same or adjacent cells are checked for collision.
    """

    def __init__(self, world_width, world_height, cell_size=256):
        self.world_w = world_width
        self.world_h = world_height
        self.cell_size = cell_size
        self.cols = (world_width + cell_size - 1) // cell_size
        self.rows = (world_height + cell_size - 1) // cell_size
        self.grid = [[[] for _ in range(self.cols)] for _ in range(self.rows)]

    def clear(self):
        """Clear all objects from the grid."""
        for row in self.grid:
            for cell in row:
                cell.clear()

    def insert(self, obj):
        """Insert an object into the grid based on its position."""
        x = int(obj.pos.x)
        y = int(obj.pos.y)
        col = min(self.cols - 1, max(0, x // self.cell_size))
        row = min(self.rows - 1, max(0, y // self.cell_size))
        self.grid[row][col].append(obj)

    def get_nearby(self, pos, radius=1):
        """Get all objects in cells near the given position (within radius cells).
        
        Args:
            pos: pygame.Vector2 position
            radius: Number of cells to check in each direction (default 1 for 3x3)
        
        Returns:
            List of nearby objects
        """
        x = int(pos.x)
        y = int(pos.y)
        col = x // self.cell_size
        row = y // self.cell_size

        nearby = []
        for r in range(max(0, row - radius), min(self.rows, row + radius + 1)):
            for c in range(max(0, col - radius), min(self.cols, col + radius + 1)):
                nearby.extend(self.grid[r][c])

        return nearby
