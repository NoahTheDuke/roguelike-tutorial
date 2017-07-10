from time import sleep
import tdl
import settings
import colors
import global_vars as glob
from gui_util import message
from input_util import handle_keys, process_input
from render_util import render_all

def look_at_ground():
    spotted = []
    for obj in (glob.gameobjects):
        if [obj.x,obj.y] == [glob.cursor.x,glob.cursor.y] and not obj == glob.cursor:
            spotted.append(obj.name)
    if len(spotted) > 0:
        message('You see: ' + (', '.join(spotted)))

def target_tile():
    '''Display a targeting cursor'''
    if not glob.player.is_targeting:
        message('You begin targeting.')
        glob.player.is_active = False
        glob.player.is_targeting = True
        glob.cursor.activate('X',colors.red)
    while glob.player.is_targeting:
        render_all()
        tdl.flush()
        player_action = handle_keys(tdl.event.key_wait())
        print('targ:'+str(player_action))
        if not player_action == None:
            if player_action.key == 'ENTER':
                print('done')
                glob.player.is_targeting = False
                glob.cursor.deactivate()
                break
        else:
            glob.player.is_targeting = False
            glob.cursor.deactivate()
            break
    # if not glob.cursor.is_active:
    #     glob.cursor.activate('X',color.red)
    # while True:
    #     #player_action = (tdl.event.key_wait())
    #     render_all()
    #     tdl.flush()
    #     player_action = handle_keys(tdl.event.key_wait())
    #     print('tar:'+str(player_action))
    #     if not player_action == None:
    #         if 'exit' in player_action:
    #             glob.player.is_targeting = False
    #         elif 'confirm' in player_action:
    #             print(glob.cursor.x,glob.cursor.y)
    #             return(glob.cursor.x,glob.cursor.y)
    #         else:
    #             process_input(player_action)
    #         break
        # if player_action.key in ['ENTER','KPENTER']:
        #     print(glob.cursor.x,glob.cursor.y)
        #     break
        # elif player_action.key == 'ESCAPE':
        #     break

    # else:   # if looking cursor was active, flip it to the targeting cursor at the same position
    #     glob.cursor.char = 'X'
    #     glob.player.is_looking = False
    #message('Select a tile to target and confirm with Enter. \'l\' cancels', colors.light_cyan)
    
    #return x,y
    # while glob.player.is_targeting:
    #     if not glob.player.is_targeting:
    #         print('Cancel')
    #         break