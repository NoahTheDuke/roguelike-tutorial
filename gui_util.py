''' all GUI-related code '''

import tdl
import settings
import colors
import global_vars as glob
import textwrap
        
def inventory_menu(header):
    '''show a menu with each item of the inventory as an option'''
    if len(glob.inventory) == 0:
        message('Inventory is empty.')
    else:
        options = [item.name for item in glob.inventory]
        index = menu(header, options, settings.INVENTORY_WIDTH)
        #if an item was chosen, return it
        if index is None or len(glob.inventory) == 0:
            return None
        return glob.inventory[index]

def menu(header, options, width):
    '''display a simple menu to the glob.player'''
    root = glob.root
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    #calculate total height for the header (after textwrap) and one line per option
    header_wrapped = textwrap.wrap(header, width)
    header_height = len(header_wrapped)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #create an off-screen console that represents the menu's window
    window = tdl.Console(width, height)
 
    #print the header, with wrapped text
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    for i, line in enumerate(header_wrapped):
        window.draw_str(0, 0+i, header_wrapped[i])

    y = header_height
    letter_index = ord('a') #ord returns the ascii code for a string-letter
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        window.draw_str(0, y, text, bg=None)
        y += 1
        letter_index += 1 #by incrementing the ascii code for the letter, we go through the alphabet

    #blit the contents of "window" to the root console
    x = settings.SCREEN_WIDTH//2 - width//2
    y = settings.SCREEN_HEIGHT//2 - height//2
    root.blit(window, x, y, width, height, 0, 0)

    #present the root console to the glob.player and wait for a key-press
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
        if len(glob.game_msgs) == settings.MSG_HEIGHT:
            del glob.game_msgs[0]
 
        #add the new line as a tuple, with the text and the color
        glob.game_msgs.append((line, color))