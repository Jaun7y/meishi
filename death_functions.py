from game_states import GameStates
from render_functions import RenderOrder


def kill_player(player, colours):
    player.char = '%'
    player.colour = colours.get('dark_red')

    return 'You died', GameStates.PLAYER_DEAD


def kill_monster(monster, colours):
    death_message = '{0} is dead!'.format(monster.name.capitalize())

    monster.char = '%'
    monster.colour = colours.get('dark_red')
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.render_order = RenderOrder.CORPSE

    return death_message
