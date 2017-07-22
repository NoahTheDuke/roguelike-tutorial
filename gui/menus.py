''' functions related to all interactive menus '''

import tdl
import textwrap
import settings
import colors
import global_vars as gv

# GUI
from gui.render_main import render_all
from gui.panels import draw_panel_borders
from gui.messages import Message

def inventory_menu(header,filter=None):
    '''show a menu with each item of the inventory as an option'''
    if filter is not None:  # if filter is set, only display items of a certain class
        inventory = [item for item in gv.player.inventory if type(item).__name__ == filter]
    else:
        inventory = gv.player.inventory
    if len(inventory) == 0:
        Message('Your Inventory is empty.')
    options = [item.name for item in inventory]
    index = menu(header, options, settings.INVENTORY_WIDTH)
    #if an item was chosen, return it
    if index is None or len(gv.player.inventory) == 0:
        return None
    return gv.player.inventory[index]

def interactive_inventory_panel():
    '''show a menu with each item of the inventory as an option'''
    gv.inv_panel.border_color = settings.PANELS_BORDER_COLOR_ACTIVE

def item_menu(item):
    '''displays an item's descriptions and related options '''
    render_all()    # Re-render the screen so the menus wont overlap

    width = 30
    header = [(item.name).title(),' ']+(textwrap.wrap(item.description,width)+[' ']) # Construct a header out of the item's name and description
    menu(header,['(u)se','(e)quip','(d)rop',' ','Any other key to cancel.'],width,wrap_header=False,options_sorted=False)

    # Wait for the player make a selection
    key = tdl.event.key_wait()

    # After the player has made his choice (or canceled), game play resumes
    if key.char == 'u':
        gv.gamestate = GameStates.ENEMY_TURN
        item.use()
    elif key.char == 'e':
        gv.gamestate = GameStates.PLAYERS_TURN
        item.equip()
    elif key.char == 'd':
        gv.gamestate = GameStates.PLAYERS_TURN
        item.drop()
    else:
        gv.gamestate = GameStates.PLAYERS_TURN
        pass

def menu(header, options, width,wrap_header=True,options_sorted=True,text_color=colors.white):
    '''display a simple menu to the player'''
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    
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
    window.draw_rect(0, 0, width+1, height+1, None, fg=colors.white, bg=None)
    window.draw_str(0,0,' ')
    for i, line in enumerate(header_wrapped):
        window.draw_str(1,1+i, header_wrapped[i],fg=text_color)
    window.draw_str(0,header_height,' ')

    y = header_height+1
    if options_sorted:
        letter_index = ord('a') #ord returns the ascii code for a string-letter
        for option_text in options:
            text = '(' + chr(letter_index) + ') ' + option_text
            window.draw_str(0, y, text,fg=text_color, bg=None)
            y += 1
            letter_index += 1 #by incrementing the ascii code for the letter, we go through the alphabet
    else:
        for option_text in options:
            window.draw_str(0, y, option_text,fg=text_color, bg=None)
            y += 1
    window.draw_str(0,y+1,' ')

    # Draw the window's borders
    draw_panel_borders(window)

    #blit the contents of "window" to the root console
    x = settings.SCREEN_WIDTH//2 - width//2
    y = settings.SCREEN_HEIGHT//2 - height//2
    gv.root.blit(window, x, y, width, height, 0, 0)

    #present the root console to the gv.player and wait for a key-press
    tdl.flush()
    key = tdl.event.key_wait()
    key_char = key.char
    if key_char == '':
        key_char = ' ' # placeholder
    if key.key == 'ENTER' and key.alt:  #(special case) Alt+Enter: toggle fullscreen
        tdl.set_fullscreen(not tdl.get_fullscreen())

    index = ord(key_char) - ord('a')
    if index >= 0 and index < len(options):
        return index
    return None