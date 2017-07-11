from time import sleep
import tdl
import settings
import colors
import global_vars as gv
from gui_util import message
from input_util import handle_keys, process_input
from render_util import render_all

def look_at_ground():
    spotted = []
    for obj in (gv.gameobjects):
        if [obj.x,obj.y] == [gv.cursor.x,gv.cursor.y] and not obj == gv.cursor:
            spotted.append(obj.name)
    if len(spotted) > 0:
        message('You see: ' + (', '.join(spotted)))

def target_tile():
    '''Display a targeting cursor'''
    if not gv.player.is_targeting:
        message('You begin targeting.')
        gv.player.is_active = False
        gv.player.is_targeting = True
        gv.cursor.activate('X',colors.red)
    while gv.player.is_targeting:
        render_all()
        tdl.flush()
        player_action = handle_keys(tdl.event.key_wait())
        print('targ:'+str(player_action))
        if not player_action == None:
            if player_action.key == 'ENTER':
                print('done')
                gv.player.is_targeting = False
                gv.cursor.deactivate()
                break
        else:
            gv.player.is_targeting = False
            gv.cursor.deactivate()
            break
    # if not gv.cursor.is_active:
    #     gv.cursor.activate('X',color.red)
    # while True:
    #     #player_action = (tdl.event.key_wait())
    #     render_all()
    #     tdl.flush()
    #     player_action = handle_keys(tdl.event.key_wait())
    #     print('tar:'+str(player_action))
    #     if not player_action == None:
    #         if 'exit' in player_action:
    #             gv.player.is_targeting = False
    #         elif 'confirm' in player_action:
    #             print(gv.cursor.x,gv.cursor.y)
    #             return(gv.cursor.x,gv.cursor.y)
    #         else:
    #             process_input(player_action)
    #         break
        # if player_action.key in ['ENTER','KPENTER']:
        #     print(gv.cursor.x,gv.cursor.y)
        #     break
        # elif player_action.key == 'ESCAPE':
        #     break

    # else:   # if looking cursor was active, flip it to the targeting cursor at the same position
    #     gv.cursor.char = 'X'
    #     gv.player.is_looking = False
    #message('Select a tile to target and confirm with Enter. \'l\' cancels', colors.light_cyan)
    
    #return x,y
    # while gv.player.is_targeting:
    #     if not gv.player.is_targeting:
    #         print('Cancel')
    #         break