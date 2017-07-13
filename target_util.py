''' look and targeting related functions '''

from time import sleep
import tdl
import settings
import colors
import global_vars as gv
from gui_util import message
from input_util import handle_keys,process_input
from render_util import render_all

def look_at_ground(x,y):
    # check if there's an object at the current position, excluding the cursor
    spotted = [obj.name for obj in gv.gameobjects if ([obj.x,obj.y] == [x,y] and not obj == gv.cursor and not obj == gv.player)]
    if len(spotted) > 0:    # if more than one object is present, output the names as a message
         message('You see: ' + (', '.join(spotted)))

def target_tile():
    '''Display a targeting cursor'''
    message('Select a target by moving your cursor. Enter to confirm the target, any other key to cancel.')
    if not gv.player.is_targeting:
        #message('You begin targeting.')
        gv.player.is_active = False
        gv.player.is_targeting = True
        gv.cursor.activate('X',colors.red)
    while gv.player.is_targeting:
        render_all()
        tdl.flush()
        player_action = handle_keys(tdl.event.key_wait())
        if not player_action == None:
            if 'move' in player_action:
                process_input(player_action)
            elif 'confirm' in player_action:
                gv.player.is_targeting = False
                gv.cursor.deactivate()
                return (gv.cursor.x,gv.cursor.y) #Return the cursor's current coordinates to the calling function
            else:
                gv.player.is_targeting = False
                gv.cursor.deactivate()
                break