def render_all(con, entities, game_map, root_console, screen_width, screen_height, colours):
    # Draw all the tiles in the game map
    for x, y in game_map:
        wall = not game_map.transparent[x,y]

        if wall:
            con.draw_char(x, y, None, fg=None, bg=colours.get('dark_wall'))
        else:
            con.draw_char(x, y, None, fg=None, bg=colours.get('dark_ground'))

    # Draw all entities in the list
    for entity in entities:
        draw_entity(con, entity)

    root_console.blit(con, 0, 0, screen_width, screen_height, 0, 0)


def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity):
    con.draw_char(entity.x, entity.y, entity.char, entity.colour, bg=None)


def clear_entity(con, entity):
    # Erase the entity that represents this object
    con.draw_char(entity.x, entity.y, ' ', entity.colour, bg=None)
