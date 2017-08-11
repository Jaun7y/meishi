import tdl
import colors
import math
from random import randint
import textwrap
# from GameObject import GameObject

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20
MAP_WIDTH = 80
MAP_HEIGHT = 43
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
FOV_ALGO = 'BASIC'
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
MAX_ROOM_MONSTERS = 3
PLAYER_SPEED = 2
DEFAULT_SPEED = 8
DEFAULT_ATTACK_SPEED = 20

BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

colour_dark_wall = (0, 0, 100)
colour_light_wall = (130, 110, 50)
colour_dark_ground = (50, 50, 150)
colour_light_ground = (200, 180, 50)

tdl.set_font('consolas10x10_gs_tc.png', greyscale=True, altLayout=True)

root = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Meishi", fullscreen=False)
con = tdl.Console(SCREEN_WIDTH, SCREEN_HEIGHT)

tdl.setFPS(LIMIT_FPS)


class Tile:
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False

        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight


class GameObject:
    def __init__(self, x, y, char, name, colour, bg_colour=None, blocks=False, fighter=None, ai=None, speed=DEFAULT_SPEED):
        self.x = x
        self.y = y
        self.char = char
        self.colour = colour
        self.bg_colour = bg_colour
        self.name = name
        self.blocks = blocks
        self.speed = speed
        self.wait = 0
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        if self.ai:
            self.ai.owner = self

    def send_to_back(self):
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def move(self, dx, dy):
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            self.wait = self.speed

    def draw(self):
        if(self.x, self.y) in visible_tiles:
            con.draw_char(self.x, self.y, self.char, self.colour, None)

    def clear(self):
        con.draw_char(self.x, self.y, ' ', self.colour, bg=None)


class Fighter:
    def __init__(self, hp, defense, power, death_function=None, attack_speed=DEFAULT_ATTACK_SPEED):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.death_function = death_function
        self.attack_speed = attack_speed

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)

    def attack(self, target):
        damage = self.power - target.fighter.defense

        if damage > 0:
            print(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points')
            target.fighter.take_damage(damage)
        else:
            print(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect')

        self.owner.wait = self.attack_speed


class BasicMonster:
    def take_turn(self):
        monster = self.owner
        if (monster.x, monster.y) in visible_tiles:
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)


class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)


def player_death(player):
    global game_state
    print("You died")
    game_state = 'dead'

    player.char = '#'
    player.color = colors.dark_red

def monster_death(monster):
    print(monster.name.capitalize() + ' is dead')
    monster.char = '%'
    monster.color = colors.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = "remains of " + monster.name
    monster.send_to_back()



def create_h_tunnel(x1, x2, y):
    global my_map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False


def create_v_tunnel(y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False


def move_or_attack(dx, dy):
    global fov_recompute

    x = player.x + dx
    y = player.y + dy

    target = None
    for obj in objects:
        if obj.fighter and obj.x == x and obj.y == y:
            target = obj
            break

    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute = True


def is_visible_tile(x, y):
    global my_map
    if x >= MAP_WIDTH or x < 0:
        return False
    elif y >= MAP_HEIGHT or y < 0:
        return False
    elif my_map[x][y].blocked:
        return False
    elif my_map[x][y].block_sight:
        return False
    else:
        return True


def render_all():
    global fov_recompute
    global visible_tiles

    if fov_recompute:
        fov_recompute = False
        visible_tiles = tdl.map.quick_fov(player.x, player.y, is_visible_tile, fov=FOV_ALGO, radius=TORCH_RADIUS, lightWalls=FOV_LIGHT_WALLS)

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = (x, y) in visible_tiles
                wall = my_map[x][y].block_sight
                if not visible:
                    if my_map[x][y].explored:
                        if wall:
                            con.draw_char(x, y, None, fg=None, bg=colour_dark_wall)
                        else:
                            con.draw_char(x, y, None, fg=None, bg=colour_dark_ground)
                else:
                    if wall:
                        con.draw_char(x, y, None, fg=None, bg=colour_light_wall)
                    else:
                        con.draw_char(x, y, None, fg=None, bg=colour_light_ground)

                    my_map[x][y].explored = True

    for obj in objects:
        if obj != player:
            obj.draw()
    player.draw()

    root.blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)
    # con.draw_str(1, SCREEN_HEIGHT - 2, 'HP: ' + str(player.fighter.hp) + '/' + str(player.fighter.max_hp) + ' ')
    #prepare to render the gui panel
    panel.clear(fg=colors.white, bg=colors.black)

    #print the game msgs one line at a time
    y = 1
    for (line, colour) in game_msgs:
        panel.draw_str(MSG_X, y, line, bg=None, fg=colour)
        y += 1

    #show the players stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp, colors.light_red, colors.darker_red)

    panel.draw_str(1,0, get_names_under_mouse(), bg=None, fg=colors.light_grey)

    #blit the contents of the panel to the root console
    root.blit(panel, 0, PANEL_Y, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0)



def create_room(room):
    global my_map
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            my_map[x][y].blocked = False
            my_map[x][y].block_sight = False


def make_map():
    global my_map

    my_map = [[Tile(True) for y in range(MAP_HEIGHT)] for x in range(MAP_WIDTH)]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        w = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)

        x = randint(0, MAP_WIDTH - w - 1)
        y = randint(0, MAP_HEIGHT - h - 1)

        new_room = Rect(x, y, w, h)

        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
        if not failed:
            create_room(new_room)

            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                player.x = new_x
                player.y = new_y
            else:
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                if randint(0, 1):
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            place_objects(new_room)
            rooms.append(new_room)
            num_rooms += 1


def place_objects(room):
    global objects
    num_monsters = randint(0, MAX_ROOM_MONSTERS)

    for i in range(MAX_ROOM_MONSTERS):
        x = randint(room.x1 + 1, room.x2 - 1)
        y = randint(room.y1 + 1, room.y2 - 1)

        if not is_blocked(x, y):
            if randint(0, 100) < 80:
                fighter_component = Fighter(hp=10, defense=0, power=3, death_function=monster_death)
                ai_component = BasicMonster()
                monster = GameObject(x, y, 'o', 'Orc', colors.desaturated_green, bg_colour=None, blocks=True,
                                     fighter=fighter_component, ai=ai_component)
            else:
                fighter_component = Fighter(hp=16, defense=1, power=4, death_function=monster_death)
                ai_component= BasicMonster()
                monster = GameObject(x, y, 'T', 'Troll', colors.darker_green, bg_colour=None, blocks=True,
                                     fighter=fighter_component, ai=ai_component)

            objects.append(monster)


def is_blocked(x, y):
    if my_map[x][y].blocked:
        return True

    for obj in objects:
        if obj.blocks and obj.x == x and obj.y == y:
            return True

    return False


def handle_keys():
    global fov_recompute
    global mouse_coord
    # user_input = tdl.event.key_wait()
    keypress = False
    for event in tdl.event.get():
        if event.type == "KEYDOWN":
            user_input = event
            keypress = True
        if event.type == 'MOUSEMOTION':
            mouse_cood = event.cell
    if player.wait > 0:
        player.wait -= 1
        return
    if not keypress:
        return

    if user_input.key == "ENTER" and user_input.alt:
        tdl.set_fullscreen(not tdl.get_fullscreen())
    elif user_input.key == "ESCAPE":
        return 'exit'
    elif game_state == "playing":

        if user_input.key == "UP":
            move_or_attack(0, -1)
            fov_recompute = True
        elif user_input.key == "DOWN":
            move_or_attack(0, 1)
            fov_recompute = True
        elif user_input.key == "RIGHT":
            move_or_attack(1, 0)
            fov_recompute = True
        elif user_input.key == "LEFT":
            move_or_attack(-1, 0)
            fov_recompute = True


def get_names_under_mouse():
    global visible_tiles

    # return a string with the names of all objects under the mouse
    # (x, y) = mouse_coord

    names = [obj.name for obj in objects if obj.x == mouse_cood[0] and obj.y == mouse_cood[1] and (obj.x, obj.y) in visible_tiles]

    names = ', ' .join(names) #join the names separated by commas
    print(names)

    return names.capitalize()


def render_bar(x, y, total_width, name, value, maximum, bar_colour, back_colour):
    bar_width = int(float(value) / maximum * total_width)

    panel.draw_rect(x, y, total_width, 1, None, bg=back_colour)

    if bar_width > 0:
        panel.draw_rect(x, y, bar_width, 1, None, bg=bar_colour)

    text = name + ': ' + str(value) + '/' + str(maximum)
    x_centered = x + (total_width - len(text))//2
    panel.draw_str(x_centered, y, text, fg=colors.white, bg=None)


def message(new_msg, colour=colors.white):
    #split the message if necessary among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        game_msgs.append((line, colour))


fighter_component = Fighter(hp=30, defense=2, power=5, death_function=player_death)
player = GameObject(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, '@', 'Player', (255, 255, 255), bg_colour=None, blocks=True, fighter=fighter_component, speed=PLAYER_SPEED)

game_msgs = []
objects = [player]
make_map()
fov_recompute = True
game_state = 'playing'
player_action = None

panel = tdl.Console(SCREEN_WIDTH, PANEL_HEIGHT)

message("Welcome stranger! Prepare to perish in the Tomb of Ancient Kings!", colors.red)

mouse_cood = (0, 0)

while not tdl.event.is_window_closed():
    render_all()
    tdl.flush()
    for obj in objects:
        obj.clear()

    player_action = handle_keys()
    if player_action == 'exit':
        break

    if game_state == "playing":
        # print(player_action)
        for obj in objects:
            if obj.ai:
                if obj.wait > 0:
                    obj.wait -= 1
                else:
                    obj.ai.take_turn()
