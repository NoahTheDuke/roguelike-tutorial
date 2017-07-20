''' look and targeting related functions '''

import tdl

import settings
import colors
import global_vars as gv

from classes.messages import Message

from game_states import GameStates
from input_util import handle_keys,process_input
from render_util import render_all

def look_at_ground(x,y):
    # check if there's an object at the current position, excluding the cursor
    spotted = [obj.name for obj in gv.gameobjects if ([obj.x,obj.y] == [x,y] and not obj == gv.cursor and not obj == gv.player)]
    if len(spotted) > 0:    # if more than one object is present, output the names as a message
         Message('You see: ' + (', '.join(spotted)))

def target_tile():
    '''Display a targeting cursor'''
    Message('Select a target by moving your cursor. Enter to confirm the target, press ESC to cancel.')
    if gv.gamestate is not GameStates.CURSOR_ACTIVE:  # If the player-state is not yet targeting, enable it and create the cursor
        gv.gamestate = GameStates.CURSOR_ACTIVE
        gv.cursor.activate('X',colors.red)
    while gv.gamestate == GameStates.CURSOR_ACTIVE: # While the player is considered targeting, suspend game-play to control the cursor and get a target
        render_all()
        tdl.flush()
        player_action = handle_keys(tdl.event.key_wait())
        if not player_action == None:
            if 'move' in player_action: # if key is a movement key process input as normal (will move the cursor)
                process_input(player_action)
                look_at_ground(gv.cursor.x,gv.cursor.y)
            elif 'confirm' in player_action: # if enter was pressed, return the coordinates of the cursor
                gv.gamestate = GameStates.ENEMY_TURN
                gv.cursor.deactivate()
                return (gv.cursor.x,gv.cursor.y) #Return the cursor's current coordinates to the calling function
            elif 'exit' in player_action:
                gv.gamestate =  GameStates.ENEMY_TURN
                gv.cursor.deactivate()
                break