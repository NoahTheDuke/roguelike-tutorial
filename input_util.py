''' key handling & input processing '''

import colors
import global_vars as gv

from game_states import GameStates
from gui_util import message, menu, inventory_menu, item_menu

def handle_keys(user_input):
    ''' Handles all key input made by the player '''
    
    print(user_input)

    if user_input.key == 'ENTER' and user_input.alt:
        #Alt+Enter: toggle fullscreen
        return {'fullscreen':None}
    elif user_input.key == 'ESCAPE':
        return {'exit':None}  #exit game
    elif user_input.text == '?':
        return 'manual'
    
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

    elif user_input.key in ['KP5','.']:
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
        return {'inventory':'interact'}

    elif user_input.text == 'u':
        return {'inventory':'use'}

    # elif user_input.text == 'd':
    #     return {'inventory':'drop'}

    # elif user_input.text == 'e':
    #     return {'inventory':'equip'}

    # elif user_input.text == 'x':
    #     return {'inventory':'examine'}

    # other
    elif user_input.key in ['ENTER','KPENTER']:
        return 'confirm'

    else:
        return None

def process_input(action):
    ''' process key input into game actions '''
    if 'move' in action:
        x,y = action['move']
        if gv.gamestate == GameStates.CURSOR_ACTIVE:
            gv.cursor.move(x,y)
        elif gv.gamestate == GameStates.PLAYERS_TURN:
            gv.player.move(x,y,gv.player.is_running)
            gv.gamestate = GameStates.ENEMY_TURN          
    
    elif 'run' in action:
        if (gv.player.is_running):
            message('You stop runningv.')
            gv.player.is_running = False
        else:
            message('You start to run.')
            gv.player.is_running = True

    elif 'look' in action:
        if gv.gamestate == GameStates.CURSOR_ACTIVE:
            message('You stop looking around.')
            gv.cursor.deactivate()
            gv.gamestate = GameStates.PLAYERS_TURN
        else:
            message('You start looking around.')
            gv.gamestate = GameStates.CURSOR_ACTIVE
            gv.cursor.activate('*',colors.white)
    
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
        item = None
        # get all items at the player's feet
        items = [obj for obj in gv.gameobjects if [obj.x,obj.y] == [gv.player.x, gv.player.y] and obj.is_item]
        if len(items) == 0:
            message('There is nothing to pick up here!')
        elif len(items) == 1:
            item = 0
        else:
            item = menu('What do you want to pick up?',[item.name for item in items],24)
        if not item == None:
            items[item].pick_up()
            message('You picked up a ' + items[item].name + '!', colors.green)

    elif 'inventory' in action:
        #show the gv.inventory, pressing a key returns the corresponding item
        #if chosen_item is not None:
        if (action['inventory'] == 'interact'):
            chosen_item = inventory_menu('Select the item to interact with:')
            if chosen_item is not None:
                item_menu(chosen_item)
        elif (action['inventory'] == 'use'):
            chosen_item = inventory_menu('Select the item to use:',filter='Useable')
            if chosen_item is not None:
                chosen_item.use()
    
    elif 'stairs' in action:
        if (action['stairs'] == '<' and gv.player.pos() == gv.stairs_down.pos()):
            message('You descend further into the dark abyss.')
            gv.stairs_down.descended = True
        elif (action['stairs'] == '>' and gv.player.pos() == gv.stairs_up.pos()):
            message('A heavy trap door has fallen shut on the staircase. You can only go further down.')
        else:
            message('There are no stairs here.')
    
    # elif 'confirm' in action:
    #     if gv.player.is_targeting:
    #         gv.player.fire_weapon(gv.cursor.x,gv.cursor.y)
    #     gv.player.is_active = False