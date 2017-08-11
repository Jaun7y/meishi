class Entity:
    """
    A generic object to represent players, enemies, items etc
    """
    def __init__(self, x, y, char, colour):
        self.x = x
        self.y = y
        self.char = char
        self.colour = colour

    def move(self, dx, dy):
        # Move the entity by a given amount
        self.x += dx
        self.y += dy
