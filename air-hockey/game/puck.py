"""
Puck: the disc players are trying to hit into the opponent's goal.
"""


class Puck:
    def __init__(self, x, y, radius=12):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 0.0
        self.vy = 0.0

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def move_by_scale(self, scale):
        self.x += self.vx * scale
        self.y += self.vy * scale

    def bounce_off_walls(self, height, margin):
        """Bounce off the top and bottom walls only."""
        if self.y - self.radius < margin:
            self.y = margin + self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius > height - margin:
            self.y = height - margin - self.radius
            self.vy = -abs(self.vy)