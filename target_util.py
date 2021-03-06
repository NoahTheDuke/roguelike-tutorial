''' look and targeting related functions '''

import tdl

import settings
import colors
import global_vars as gv

# GUI
from gui.render_main import render_all
from gui.messages import Message

from game_states import GameStates
from input_util import handle_keys, process_input


def target_tile():
    '''Display a targeting cursor'''
    Message('Select a target by moving your cursor. Enter to confirm the target, press ESC to cancel.')
    if gv.gamestate is not GameStates.CURSOR_ACTIVE:  # If the player-state is not yet targeting, enable it and create the cursor
        gv.gamestate = GameStates.CURSOR_ACTIVE
        gv.cursor.activate('X', colors.red)
    while gv.gamestate == GameStates.CURSOR_ACTIVE:  # While the player is considered targeting, suspend game-play to control the cursor and get a target

        # update the screen
        render_all()
        tdl.flush()

        player_action = handle_keys(tdl.event.key_wait())
        if player_action is not None:
            if 'move' in player_action:  # if key is a movement key process input as normal (will move the cursor)
                process_input(player_action)
            elif 'confirm' in player_action:  # if enter was pressed, return the coordinates of the cursor
                gv.gamestate = GameStates.ENEMY_TURN
                gv.cursor.deactivate()
                return (gv.cursor.x, gv.cursor.y)  #Return the cursor's current coordinates to the calling function
            elif 'cancel' in player_action:
                gv.gamestate = GameStates.ENEMY_TURN
                gv.cursor.deactivate()
                break
