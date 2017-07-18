''' all GUI-related code '''

import tdl
import textwrap
import settings
import colors
import global_vars as gv

from render_util import render_all

def inventory_menu(header,filter=None):
    '''show a menu with each item of the inventory as an option'''
    if filter is not None:  # if filter is set, only display items of a certain class
        inventory = [item for item in gv.inventory if type(item).__name__ == filter]
    else:
        inventory = gv.inventory
    if len(inventory) == 0:
        message('Your Inventory is empty.')
    options = [item.name for item in inventory]
    index = menu(header, options, settings.INVENTORY_WIDTH)
    #if an item was chosen, return it
    if index is None or len(gv.inventory) == 0:
        return None
    return gv.inventory[index]

def item_menu(item):
    '''displays an item's descriptions and related options '''
    render_all()    # Re-render the screen so the menus wont overlap

    header = [(item.name).title(),' ']+(textwrap.wrap(item.description,30)) # Construct a header out of the item's name and description
    menu(header,['(u)se','(e)quip','(d)rop',' ','Any other key to cancel.'],30,wrap_header=False,options_sorted=False)
    key = tdl.event.key_wait()

    if key.key == 'ENTER' and key.alt:  #(special case) Alt+Enter: toggle fullscreen
        tdl.set_fullscreen(not tdl.get_fullscreen())

    if key.char == 'u':
        item.use()
    elif key.char == 'e':
        item.equip()
    elif key.char == 'd':
        item.drop()

def display_manual():
    '''displays the game's manual'''
    man = open('resources/manual.txt','r')
    man = man.read().split('\n')
    print(man)
    menu(man,[],40,wrap_header=False,options_sorted=False)

def msgbox(text, width=50):
    '''display a simple message box'''
    menu(text, [], width)  #use menu() as a sort of "message box"

def menu(header, options, width,wrap_header=True,options_sorted=True):
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
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    for i, line in enumerate(header_wrapped):
        window.draw_str(0, 0+i, header_wrapped[i])
    window.draw_str(0,header_height,' ')

    y = header_height+1
    if options_sorted:
        letter_index = ord('a') #ord returns the ascii code for a string-letter
        for option_text in options:
            text = '(' + chr(letter_index) + ') ' + option_text
            window.draw_str(0, y, text, bg=None)
            y += 1
            letter_index += 1 #by incrementing the ascii code for the letter, we go through the alphabet
    else:
        for option_text in options:
            window.draw_str(0, y, option_text, bg=None)
            y += 1
    window.draw_str(0,y+1,' ')

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

def message(new_msg, color = colors.white):
    '''split the message if necessary, among multiple lines'''
    new_msg_lines = textwrap.wrap(new_msg, settings.MSG_WIDTH)
 
    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(gv.game_msgs) == settings.MSG_HEIGHT:
            del gv.game_msgs[0]
 
        #add the new line as a tuple, with the text and the color
        gv.game_msgs.append((line, color))