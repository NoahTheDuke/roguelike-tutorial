''' all GUI-related code '''

import tdl
import settings
import colors
import global_vars as glob
import textwrap
        
def render_all(con,root,panel):
    ''' draw all game objects '''
    for y in range(settings.MAP_HEIGHT):
        for x in range(settings.MAP_WIDTH):
            wall = not glob.game_map.transparent[x,y]
            if not glob.game_map.fov[x, y]:
                #it's out of the glob.player's FOV but explored
                if glob.game_map.explored[x][y]:
                    if wall:
                        con.draw_char(x, y, None, fg=None, bg=settings.color_dark_wall)
                    else:
                        con.draw_char(x, y, None, fg=None, bg=settings.color_dark_ground)
            else:
                #it's visible
                if wall:
                    con.draw_char(x, y, None, fg=None, bg=settings.color_light_wall)
                else:
                    con.draw_char(x, y, None, fg=None, bg=settings.color_light_ground)
                glob.game_map.explored[x][y] = True
    for obj in glob.gameobjects:
        if glob.game_map.fov[obj.x,obj.y]:
            obj.draw(con)
            #con.draw_char(obj.x, obj.y, obj.char, obj.color)
   # con.draw_char(obj.x, obj.y, obj.char, obj.color)
        
    root.blit(con , 0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, 0, 0)
    #prepare to render the GUI panel
    panel.clear(fg=colors.white, bg=colors.black)
 
    #show the glob.player's stats
    render_bar(panel,1, 1, settings.BAR_WIDTH, 'HP', glob.player.fighter.hp, glob.player.fighter.max_hp,
        colors.light_red, colors.darker_red)
    render_bar(panel,1, 2, settings.BAR_WIDTH, 'PWR', glob.player.fighter.power, glob.player.fighter.max_power,
        colors.black, colors.black)
    render_bar(panel,1, 3, settings.BAR_WIDTH, 'DEF', glob.player.fighter.defense, glob.player.fighter.max_defense,
        colors.black, colors.black)       
    
    #print the game messages, one line at a time
    y = 1
    for (line, color) in glob.game_msgs:
        panel.draw_str(settings.MSG_X, y, line, bg=None, fg=color)
        y += 1
 
    #blit the contents of "panel" to the root console
    root.blit(panel, 0, settings.PANEL_Y, settings.SCREEN_WIDTH, settings.PANEL_HEIGHT, 0, 0)

def inventory_menu(header,root):
    '''show a menu with each item of the inventory as an option'''
    if len(glob.inventory) == 0:
        message('Inventory is empty.')
    else:
        options = [item.name for item in glob.inventory]
        index = menu(header, options, settings.INVENTORY_WIDTH,root)
        #if an item was chosen, return it
        if index is None or len(glob.inventory) == 0:
            return None
        return glob.inventory[index].item

def menu(header, options, width,root):
    '''display a simple menu to the glob.player'''
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    #calculate total height for the header (after textwrap) and one line per option
    header_wrapped = textwrap.wrap(header, width)
    header_height = len(header_wrapped)
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
    
    index = ord(key_char) - ord('a')
    if index >= 0 and index < len(options):
        return index
    return None

def render_bar(panel,x, y, total_width, name, value, maximum, bar_color, back_color):
    '''render a bar (HP, experience, etc). first calculate the width of the bar'''
    bar_width = int(float(value) / maximum * total_width)
 
    #render the background first
    panel.draw_rect(x, y, total_width, 1, None, bg=back_color)
 
    #now render the bar on top
    if bar_width > 0:
        panel.draw_rect(x, y, bar_width, 1, None, bg=bar_color)
    
     #finally, some centered text with the values
    text = name + ': ' + str(value) + '/' + str(maximum)
    x_centered = x + (total_width-len(text))//2
    panel.draw_str(x_centered, y, text, fg=colors.white, bg=None)

def message(new_msg, color = colors.white):
    '''split the message if necessary, among multiple lines'''
    new_msg_lines = textwrap.wrap(new_msg, settings.MSG_WIDTH)
 
    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(glob.game_msgs) == settings.MSG_HEIGHT:
            del glob.game_msgs[0]
 
        #add the new line as a tuple, with the text and the color
        glob.game_msgs.append((line, color))