''' key input for the game '''

import colors
import global_vars as glob
from gui_util import message, inventory_menu

def handle_keys(user_input):
    ''' Handles all key input made by the player '''
    
    #print(user_input)

    if user_input.key == 'ENTER' and user_input.alt:
        #Alt+Enter: toggle fullscreen
        return {'fullscreen':None}
    elif user_input.key == 'ESCAPE':
        return {'exit':None}  #exit game
    elif user_input.key == 'F5':
        return {'restart'}

    # movement keys
    if user_input.key in ['UP','KP8']:
        return {'move':(0,-1)}

    elif user_input.key in ['DOWN','KP2']:
        return {'move':(0,1)}

    elif user_input.key in ['LEFT','KP4']:
        return {'move':(-1,0)}

    elif user_input.key in ['RIGHT','KP6']:
        return {'move':(1,0)}

    elif user_input.key in ['KP9']:
        return {'move':(1,-1)}

    elif user_input.key in ['KP7']:
        return {'move':(-1,-1)}    

    elif user_input.key in ['KP1']:
        return {'move':(-1,1)}    

    elif user_input.key in ['KP3']:
        return {'move':(1,1)}          

    elif user_input.key in ['KP5']:
        return {'move':(0,0)}

    elif user_input.text == 'r':
        return 'run'

    # looking and targeting
    elif user_input.text == 'l':
        return 'look'
    elif user_input.text == 't':
        return 'target'

    # item handling
    elif user_input.text == 'g':
        return 'get'

    elif user_input.text == 'i':
        return {'inventory':'use'}

    elif user_input.text == 'd':
        return {'inventory':'drop'}

    # other
    elif user_input.key in ['ENTER','KPENTER']:
        return 'confirm'

    else:
        return None

def process_input(action):
    ''' process key input into game actions '''
    if 'move' in action:
        x,y = action['move']
        if glob.cursor.is_active:
            glob.cursor.move(x,y)
            glob.player.is_active = False
        elif glob.player.is_active:
            glob.player.move(x,y,glob.player.is_running)          
    
    elif 'run' in action:
        if (glob.player.is_running):
            message('You stop running.')
            glob.player.is_running = False
        else:
            message('You start to run.')
            glob.player.is_running = True
        glob.player.is_active = False

    elif 'look' in action:
        if glob.player.is_looking:
            message('You stop looking around.')
            glob.player.is_active = False
            glob.player.is_looking = False
            glob.cursor.deactivate()
        else:
            message('You start looking around.')
            glob.player.is_active = False
            glob.player.is_looking = True
            glob.cursor.activate('.',colors.white)
    
    elif 'target' in action:
        if glob.player.is_targeting:
            message('You stop targeting.')
            glob.player.is_active = False
            glob.player.is_targeting = False
            glob.cursor.deactivate()
        else:
            message('You begin targeting.')
            glob.player.is_active = False
            glob.player.is_targeting = True
            glob.cursor.activate('X',colors.red)

    elif 'get' in action:
        found_something = False
        for obj in glob.gameobjects:  #look for an item in the player's tile
            if obj.x == glob.player.x and obj.y == glob.player.y and obj.is_item:
                obj.pick_up()
                found_something = True
                break
        if not found_something:
            message('There is nothing to pick up here!')

    elif 'inventory' in action:
        #show the glob.inventory, pressing a key returns the corresponding item
        chosen_item = inventory_menu('Press the key next to an item to %s it, or any other to cancel.\n' % action['inventory'])
        if chosen_item is not None: #if an item was selected, call it's use or drop function
            if (action['inventory'] == 'use'):
                chosen_item.use()
                glob.player.is_active = True
            elif (action['inventory'] == 'drop'):
                chosen_item.drop()
        glob.player.is_active = False
    
    elif 'confirm' in action:
        if glob.player.is_targeting:
            glob.player.is_active = False
            return {'target':(glob.cursor.x,glob.cursor.y)}