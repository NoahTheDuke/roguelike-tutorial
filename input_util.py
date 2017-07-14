''' key handling & input processing '''

import colors
import global_vars as gv

from gui_util import message, inventory_menu

def handle_keys(user_input):
    ''' Handles all key input made by the player '''
    
    print(user_input)

    if user_input.key == 'ENTER' and user_input.alt:
        #Alt+Enter: toggle fullscreen
        return {'fullscreen':None}
    elif user_input.key == 'ESCAPE':
        return {'exit':None}  #exit game
    
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

    elif user_input.text in ['<','>']:
        return {'stairs':user_input.text}

    # looking and targeting
    if user_input.text == 'l':
        return 'look'
    # elif user_input.text == 't':
    #     return 'target'

    # item handling
    if user_input.text == 'g':
        return 'get'

    elif user_input.text == 'i':
        return {'inventory':'use'}

    elif user_input.text == 'd':
        return {'inventory':'drop'}

    elif user_input.text == 'e':
        return {'inventory':'equip'}

    elif user_input.text == 'x':
        return {'inventory':'examine'}

    # other
    elif user_input.key in ['ENTER','KPENTER']:
        return 'confirm'

    else:
        return None

def process_input(action):
    ''' process key input into game actions '''
    if 'move' in action:
        x,y = action['move']
        if gv.cursor.is_active:
            gv.cursor.move(x,y)
            gv.player.is_active = False
        elif gv.player.is_active:
            gv.player.move(x,y,gv.player.is_running)          
    
    elif 'run' in action:
        if (gv.player.is_running):
            message('You stop runningv.')
            gv.player.is_running = False
        else:
            message('You start to run.')
            gv.player.is_running = True
        gv.player.is_active = False

    elif 'look' in action:
        if gv.player.is_looking:
            message('You stop looking around.')
            gv.player.is_looking = False
            gv.cursor.deactivate()
        else:
            message('You start looking around.')
            gv.player.is_looking = True
            gv.cursor.activate('*',colors.white)
        gv.player.is_active = False
    
    # elif 'target' in action:
    #     if gv.player.is_targeting:
    #         message('You stop targeting.')
    #         gv.player.is_targeting = False
    #         gv.cursor.deactivate()
    #     else:
    #         message('You begin targeting.')
    #         gv.player.is_targeting = True
    #         gv.cursor.activate('X',colors.red)
    #     gv.player.is_active = False

    elif 'get' in action:
        found_something = False
        for obj in gv.gameobjects:  #look for an item in the player's tile
            if [obj.x,obj.y] == [gv.player.x, gv.player.y] and obj.is_item:
                obj.pick_up()
                found_something = True
                break
        if not found_something:
            message('There is nothing to pick up here!')
            gv.player.is_active = False

    elif 'inventory' in action:
        #show the gv.inventory, pressing a key returns the corresponding item
        chosen_item = inventory_menu('Press the key next to an item to %s it, or any other to cancel.\n' % action['inventory'])
        if chosen_item is not None: #if an item was selected, call it's use or drop function
            if (action['inventory'] == 'use'):
                chosen_item.use()
            elif (action['inventory'] == 'equip'):
                chosen_item.equip()
            elif (action['inventory'] == 'drop'):
                chosen_item.drop()
            elif (action['inventory'] == 'examine'):
                chosen_item.examine()
        gv.player.is_active = False
    
    elif 'stairs' in action:
        if (action['stairs'] == '<' and gv.player.pos() == gv.stairs_down.pos()):
            message('You descend further into the dark abyss.')
            gv.stairs_down.descended = True
        elif (action['stairs'] == '>' and gv.player.pos() == gv.stairs_up.pos()):
            message('A heavy trap door has fallen shut on the stairs. You can only go further down.')
        else:
            message('There a no stairs here.')
        gv.player.is_active = False
    
    # elif 'confirm' in action:
    #     if gv.player.is_targeting:
    #         gv.player.fire_weapon(gv.cursor.x,gv.cursor.y)
    #     gv.player.is_active = False