''' key handling & input processing '''

import colors
import global_vars as gv

from gui.messages import LogLevel, Message
from gui.menus import menu, inventory_popup_menu, item_selection_menu,item_interaction_menu

from game_states import GameStates

MOVE_PATTERNS = {
    # arrow keys
    'UP':(0,-1),'DOWN':(0,1),'LEFT':(-1,0),'RIGHT':(-1,0),

    # Numpad
    'KP7':(-1,-1),'KP8':(0,-1),'KP9':(1,-1),
    'KP4':(-1,0),'KP5':(0,0),'KP6':(1,0),
    'KP1':(-1,1),'KP2':(0,1),'KP3':(1,1)

    # TODO VIM keys
}

def handle_keys(user_input):
    ''' Handles all key input made by the player '''
    
    print(user_input)
    key = user_input.key
    char = user_input.char

    #Alt+Enter: toggle fullscreen
    if key == 'ENTER' and user_input.alt:
        return 'fullscreen'
    # escape cancels menus
    elif key == 'ESCAPE':
        return 'cancel'
    # control-q exists the game
    elif char == 'q' and user_input.leftCtrl:
        return 'exit'
    # '?' opens the manual
    elif char == '?':
        return 'manual'
    
    # directional keys
    if key in MOVE_PATTERNS.keys():
        if user_input.shift:
            return {'attention':MOVE_PATTERNS[key]}
        elif user_input.control:
            # force attack
            pass
        else:
            return {'move':MOVE_PATTERNS[key]}

    # running
    elif char == 'r':
        return 'run'

    # stair usage
    elif char in ['<','>']:
        return {'stairs':char}

    # looking and targeting
    elif char == 'l':
        return 'look'
    # elif char == 't':
    #     return 'target'

    # item handling
    elif char == 'g':
        return 'get'

    elif char == 'i':
        return {'inventory':'interact'}

    elif char == 'u':
        return {'inventory':'use'}

    # elif char == 'd':
    #     return {'inventory':'drop'}

    # elif char == 'e':
    #     return {'inventory':'equip'}

    # elif char == 'x':
    #     return {'inventory':'examine'}

    # other
    elif key in ['ENTER','KPENTER']:
        return 'confirm'

    else:
        return None

def process_input_noncombat(action):
    ''' process key input into game actions outside of combat'''

    print('Processing {0}'.format(action))

    if 'move' in action:
        x,y = action['move']
        if gv.gamestate == GameStates.CURSOR_ACTIVE:
            gv.cursor.move(x,y)
        elif gv.gamestate == GameStates.PLAYERS_TURN:
            gv.player.move(x,y,gv.player.is_running)
            gv.gamestate = GameStates.ENEMY_TURN          
    
    elif 'run' in action:
        if (gv.player.is_running):
            Message('You stop running.')
            gv.player.is_running = False
        else:
            Message('You start to run.')
            gv.player.is_running = True

    elif 'look' in action:
        if gv.gamestate == GameStates.CURSOR_ACTIVE:
            Message('You stop looking around.')
            gv.cursor.deactivate()
            gv.gamestate = GameStates.PLAYERS_TURN
        else:
            Message('You start looking around.')
            gv.cursor.activate('*',colors.white)
            gv.gamestate = GameStates.CURSOR_ACTIVE
    
    # elif 'target' in action:
    #     if gv.player.is_targeting:
    #         Message('You stop targeting.')
    #         gv.player.is_targeting = False
    #         gv.cursor.deactivate()
    #     else:
    #         Message('You begin targeting.')
    #         gv.player.is_targeting = True
    #         gv.cursor.activate('X',colors.red)
    #     gv.player.is_active = False

    elif 'get' in action:
        item = None
        # get all items at the player's feet
        items = [obj for obj in gv.gameobjects if [obj.x,obj.y] == [gv.player.x, gv.player.y] and obj.is_item]
        if len(items) == 0:
            Message('There is nothing to pick up here!')
        elif len(items) == 1:
            item = 0
        else:
            item = menu('What do you want to pick up?',[item.name for item in items],40)
        if not item == None:
            items[item].pick_up(gv.player)
            Message('You picked up ' + items[item].name.title() + '!', colors.green)

    elif 'inventory' in action:
        if len(gv.player.inventory) == 0:
            Message('Your inventory is empty!')
            
        # Display the inventory, if it is not already active
        elif gv.gamestate is not GameStates.INVENTORY_ACTIVE: # if the inventory isn't already active
            if (action['inventory'] == 'interact'):         
                if gv.player.opponent is None:
                    gv.gamestate = GameStates.INVENTORY_ACTIVE
                    chosen_item = item_selection_menu() # first, pick an item from the inventory
            
                    while chosen_item is not None:
                        item_action = item_interaction_menu(chosen_item) # then decide what to do with it
                        if item_action is None:  # if player cancels, let him/her pick another item (if he cancels here, the entire loop quits)
                            chosen_item = item_selection_menu()
                        elif item_action == 'use':
                            chosen_item.use()
                            gv.gamestate = GameStates.ENEMY_TURN
                            break
                        elif item_action == 'drop':
                            chosen_item.drop()
                            gv.gamestate = GameStates.PLAYERS_TURN
                            break
                        elif item_action == 'equip':
                            chosen_item.equip()
                            gv.gamestate = GameStates.PLAYERS_TURN
                            break
                    if chosen_item is None: # if inventory interaction was canceled, return to normal
                        gv.gamestate = GameStates.PLAYERS_TURN         
                else:
                    # Being locked in combat prevents the player from more complex inventory interaction
                    Message('You are locked in combat!')

            elif (action['inventory'] == 'use'):
                chosen_item = inventory_popup_menu(caption='Select item to use:',filter='Useable')
                if chosen_item is not None:
                    chosen_item.use()
                    gv.gamestate = GameStates.ENEMY_TURN
                else:
                    gv.gamestate = GameStates.PLAYERS_TURN
    
    elif 'stairs' in action:
        if (action['stairs'] == '<' and gv.player.pos() == gv.stairs_down.pos()):
            Message('You descend further into the dark abyss.')
            gv.stairs_down.descended = True
        elif (action['stairs'] == '>' and gv.player.pos() == gv.stairs_up.pos()):
            Message('A heavy trap door has fallen shut on the staircase. You can only go further down.')
        else:
            Message('There are no stairs here.')
    
    # elif 'confirm' in action:
    #     if gv.player.is_targeting:
    #         gv.player.fire_weapon(gv.cursor.x,gv.cursor.y)
    #     gv.player.is_active = False

def process_input_combat(action):
    ''' input processing while the player is locked in combat '''

    opponent = gv.player.opponent

    if 'move' in action:
        x,y = action['move']
        if (x,y) == (0,0) or gv.player.direction_to(opponent) == (x,y):
            gv.player.move(x,y,False)
            gv.gamestate = GameStates.ENEMY_TURN
        else:
            Message('You are locked in combat!',log_level = LogLevel.COMBAT)
    
    elif 'look' in action:
        if gv.gamestate == GameStates.CURSOR_ACTIVE:
            Message('You stop looking around.',log_level = LogLevel.COMBAT)
            gv.cursor.deactivate()
            gv.gamestate = GameStates.PLAYERS_TURN
        else:
            Message('You start looking around.',log_level = LogLevel.COMBAT)
            gv.cursor.activate('*',colors.white)
            gv.gamestate = GameStates.CURSOR_ACTIVE

    if 'inventory' in action:
        if (action['inventory'] == 'use'):
            chosen_item = inventory_popup_menu(caption='Select item to use:',filter='Useable')
            if chosen_item is not None:
                chosen_item.use()
                gv.gamestate = GameStates.ENEMY_TURN
            else:
                gv.gamestate = GameStates.PLAYERS_TURN
        else:
            Message('You are locked in combat!',log_level = LogLevel.COMBAT)

    else:
        Message('You are locked in combat!',log_level = LogLevel.COMBAT)
