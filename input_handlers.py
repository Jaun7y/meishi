def handle_keys(user_input):
    # Movement keys
    if user_input.key == 'UP' or user_input.key == "KP8":
        return {'move': (0, -1)}
    elif user_input.key == 'DOWN' or user_input.key == 'KP2':
        return {'move': (0, 1)}
    elif user_input.key == 'LEFT' or user_input.key == 'KP4':
        return {'move': (-1, 0)}
    elif user_input.key == 'RIGHT' or user_input.key == 'KP6':
        return {'move': (1, 0)}
    elif user_input.key == 'KP7':
        return {'move': (-1, -1)}
    elif user_input.key == 'KP9':
        return {'move': (1, -1)}
    elif user_input.key == 'KP3':
        return {'move': (1, 1)}
    elif user_input.key == 'KP1':
        return {'move': (-1, 1)}

    if user_input.key == 'ENTER' and user_input.alt:
        # Alt + Enter: toggle full screen
        return {'fullscreen': True}
    elif user_input.key == 'ESCAPE':
        # Exit the game
        return {'exit': True}

    # No key was pressed
    return {}