''' functions related to all interactive menus '''

import tdl
import textwrap
import settings
import colors
import global_vars as gv

# GUI
from gui.render_main import render_all
from gui.windows import draw_item_window, draw_options_window
from gui.helpers import draw_window_borders
from gui.panels import setup_panel, draw_inv_panel
from gui.messages import Message

from game_states import GameStates


def item_selection_menu():

    # update the inventory panel's caption and border
    render_all()
    #draw_inv_panel(gv.inv_panel,gv.root)
    tdl.flush()

    item = None
    key = ' '

    # begin a loop waiting for input. the loop will only quit when ESC is pressed or an item is selected
    while key != 'ESCAPE':
        user_input = tdl.event.key_wait()
        key = user_input.key
        char = user_input.char
        if key == 'ESCAPE':
            break
        # elif it's an arrow key or pageup/pagedown, scroll the inventory:
        #
        # for any other key, check if a corresponding item exists in the player's inventory
        elif len(char) > 0:
            index = ord(char) - ord('a')
            if 0 <= index < len(gv.player.inventory):
                item = gv.player.inventory[index]
                break

    return item


def item_interaction_menu(item):
    ''' interaction menu for a single item '''

    panel = gv.inv_panel  # panel to draw the window over

    # draw the item's description window + options
    draw_item_window(item, settings.SIDE_PANEL_X, settings.STAT_PANEL_HEIGHT, panel.width, panel.height)
    tdl.flush()

    key = ' '
    # begin a loop waiting for a key. the loop will only quit when ESC is pressed or an item is selected
    while key != 'ESCAPE':
        print('item loop')
        user_input = tdl.event.key_wait()
        key = user_input.key
        text = user_input.char
        if key == 'ESCAPE':
            return None
            break
        if text == 'u':
            print(text)
            return 'use'
        elif text == 'd':
            print(text)
            return 'drop'
        elif text == 'e':
            print(text)
            return 'equip'


def inventory_popup_menu(caption='Select item:', filter=None):
    '''show a menu next to the player, with all or a filtered selection of items as options'''
    if filter is not None:  # if filter is set, only display items of a certain class
        inventory = [item for item in gv.player.inventory if type(item).__name__ == filter]
    else:
        inventory = gv.player.inventory

    options_list = [item.name for item in inventory]

    # draw a window with the options next to the player
    draw_options_window(caption, options_list, gv.player.x + 2, gv.player.y - 1)
    tdl.flush()

    item = None
    key = ' '

    # begin a loop waiting for input. the loop will only quit when ESC is pressed or an item is selected
    while key != 'ESCAPE':
        user_input = tdl.event.key_wait()
        key = user_input.key
        char = user_input.char
        if key == 'ESCAPE':
            break
        # elif it's an arrow key or pageup/pagedown, scroll the inventory:
        #
        # for any other key, check if a corresponding item exists in the player's inventory
        elif len(char) > 0:
            index = ord(char) - ord('a')
            if 0 <= index < len(inventory):
                item = inventory[index]
                break

    return item


def menu(header, options, width, wrap_header=True, options_sorted=True, text_color=colors.white):
    '''display a simple menu to the player'''
    '''NOTE: legacy function, needs to be updated'''

    if wrap_header:
        header_wrapped = textwrap.wrap(header, width)
    else:
        header_wrapped = header

    #calculate total height for the header (after textwrap) and one line per option
    header_height = len(header_wrapped)
    if header == '':
        header_height = 0
    height = len(options) + header_height + 3

    #create an off-screen console that represents the menu's window
    window = tdl.Console(width, height)

    #print the header, with wrapped text
    window.draw_rect(0, 0, width + 1, height + 1, None, fg=colors.white, bg=None)
    window.draw_str(0, 0, ' ')
    for i, line in enumerate(header_wrapped):
        window.draw_str(1, 1 + i, header_wrapped[i], fg=text_color)
    window.draw_str(0, header_height, ' ')

    y = header_height + 1
    if options_sorted:
        letter_index = ord('a')  #ord returns the ascii code for a string-letter
        for option_text in options:
            text = '(' + chr(letter_index) + ') ' + option_text
            window.draw_str(0, y, text, fg=text_color, bg=None)
            y += 1
            letter_index += 1  #by incrementing the ascii code for the letter, we go through the alphabet
    else:
        for option_text in options:
            window.draw_str(0, y, option_text, fg=text_color, bg=None)
            y += 1
    window.draw_str(0, y + 1, ' ')

    # Draw the window's borders
    draw_window_borders(window, color=settings.PANELS_BORDER_COLOR_ACTIVE)

    #blit the contents of "window" to the root console
    x = settings.SCREEN_WIDTH // 2 - width // 2
    y = settings.SCREEN_HEIGHT // 2 - height // 2
    gv.root.blit(window, x, y, width, height, 0, 0)

    #present the root console to the gv.player and wait for a key-press
    tdl.flush()
    key = tdl.event.key_wait()
    key_char = key.char
    if key_char == '':
        key_char = ' '  # placeholder
    if key.key == 'ENTER' and key.alt:  #(special case) Alt+Enter: toggle fullscreen
        tdl.set_fullscreen(not tdl.get_fullscreen())

    index = ord(key_char) - ord('a')
    if index >= 0 and index < len(options):
        return index
    return None
