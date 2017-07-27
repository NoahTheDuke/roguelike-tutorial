''' key handling & input processing '''

import colors
import global_vars as gv

from gui.messages import Message
from gui.menus import menu, inventory_popup_menu, item_selection_menu, item_interaction_menu

from game_states import GameStates


def handle_keys(user_input):
    ''' Handles all key input made by the player '''

    print(user_input)

    #Alt+Enter: toggle fullscreen
    if user_input.key == 'ENTER' and user_input.alt:
        return 'fullscreen'
    # escape cancels menus
    elif user_input.key == 'ESCAPE':
        return 'cancel'
    # control-q exists the game
    elif user_input.char == 'q' and user_input.leftCtrl:
        return 'exit'
    # '?' opens the manual
    elif user_input.char == '?':
        return 'manual'

    # movement keys
    elif user_input.key in ['UP', 'KP8']:
        return {'move': (0, -1)}

    elif user_input.key in ['DOWN', 'KP2']:
        return {'move': (0, 1)}

    elif user_input.key in ['LEFT', 'KP4']:
        return {'move': (-1, 0)}

    elif user_input.key in ['RIGHT', 'KP6']:
        return {'move': (1, 0)}

    elif user_input.key in ['KP9']:
        return {'move': (1, -1)}

    elif user_input.key in ['KP7']:
        return {'move': (-1, -1)}

    elif user_input.key in ['KP1']:
        return {'move': (-1, 1)}

    elif user_input.key in ['KP3']:
        return {'move': (1, 1)}

    elif user_input.key in ['KP5', '.']:
        return {'move': (0, 0)}

    elif user_input.char == 'r':
        return 'run'

    elif user_input.char in ['<', '>']:
        return {'stairs': user_input.char}

    # looking and targeting
    if user_input.char == 'l':
        return 'look'
    # elif user_input.char == 't':
    #     return 'target'

    # item handling
    if user_input.char == 'g':
        return 'get'

    elif user_input.char == 'i':
        return {'inventory': 'interact'}

    elif user_input.char == 'u':
        return {'inventory': 'use'}

    # elif user_input.char == 'd':
    #     return {'inventory':'drop'}

    # elif user_input.char == 'e':
    #     return {'inventory':'equip'}

    # elif user_input.char == 'x':
    #     return {'inventory':'examine'}

    # other
    elif user_input.key in ['ENTER', 'KPENTER']:
        return 'confirm'

    else:
        return None


def process_input(action):
    ''' process key input into game actions '''

    print('Processing {0}'.format(action))

    if 'move' in action:
        x, y = action['move']
        if gv.gamestate == GameStates.CURSOR_ACTIVE:
            gv.cursor.move(x, y)
        elif gv.gamestate == GameStates.PLAYERS_TURN:
            gv.player.move(x, y, gv.player.is_running)
            gv.gamestate = GameStates.ENEMY_TURN

    elif 'run' in action:
        if (gv.player.is_running):
            Message('You stop runningv.')
            gv.player.is_running = False
        else:
            Message('You start to run.')
            gv.player.is_running = True

    elif 'look' in action:
        if gv.gamestate is GameStates.CURSOR_ACTIVE:
            Message('You stop looking around.')
            gv.cursor.deactivate()
            gv.gamestate = GameStates.PLAYERS_TURN
        else:
            Message('You start looking around.')
            gv.cursor.activate('*', colors.white)
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
        items = [obj for obj in gv.gameobjects if [obj.x, obj.y] == [gv.player.x, gv.player.y] and obj.is_item]
        if not items:
            Message('There is nothing to pick up here!')
        elif len(items) == 1:
            item = 0
        else:
            item = menu('What do you want to pick up?', [item.name for item in items], 40)
        if item is not None:
            items[item].pick_up(gv.player)
            Message('You picked up ' + items[item].name.title() + '!', colors.green)

    elif 'inventory' in action:
        if not gv.player.inventory:
            Message('Your inventory is empty!')

        # Display the inventory, if it is not already active
        elif gv.gamestate is not GameStates.INVENTORY_ACTIVE:  # if the inventory isn't already active
            if (action['inventory'] == 'interact'):
                gv.gamestate = GameStates.INVENTORY_ACTIVE
                chosen_item = item_selection_menu()  # first, pick an item from the inventory

                while chosen_item is not None:
                    item_action = item_interaction_menu(chosen_item)  # then decide what to do with it
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
                if chosen_item is None:  # if inventory interaction was canceled, return to normal
                    gv.gamestate = GameStates.PLAYERS_TURN

            elif (action['inventory'] == 'use'):
                chosen_item = inventory_popup_menu(caption='Select item to use:', filter='Useable')
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
