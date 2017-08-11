class GameObject:
    def __init__(self, x, y, char, colour, console, obj_map):
        self.x = x
        self.y = y
        self.char = char
        self.colour = colour
        self.con = console
        self.my_map = obj_map

    def move(self, dx, dy):
        if not self.my_map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy

    def draw(self):
        self.con.draw_char(self.x, self.y, self.char, self.colour)

    def clear(self):
        self.con.draw_char(self.x, self.y, ' ', self.colour, bg=None)