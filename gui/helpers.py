''' helper functions for the gui '''

import tdl
import colors

def draw_window_borders(window,width=None,height=None,color=colors.dark_grey):
    ''' draws an outline around the passed window. By default, the window's width & height will be used '''
    
    if width is None:
        width = window.width
    if height is None:
        height = window.height

    for x in range(width):
        window.draw_char(x,0,'196',bg=None,fg=color)
        window.draw_char(x,height-1,'196',bg=None,fg=color)

    for y in range(height):
        window.draw_char(0,y,'179',bg=None,fg=color)
        window.draw_char(width-1,y,'179',bg=None,fg=color)
    
    window.draw_char(0,0,'218',bg=None,fg=color)
    window.draw_char(width-1,0,'191',bg=None,fg=color)
    window.draw_char(0,height-1,'192',bg=None,fg=color)
    window.draw_char(width-1,height-1,'217',bg=None,fg=color)

def center_x_for_text(window,text,padding=0):
    '''returns the x for a text centered in the passed window'''
    x = padding+(window.width-len(text))//2
    return x
    
def is_visible_tile(x, y):
    ''' a helper function to determine whether a tile is in within the game's playing field '''

    if x >= settings.MAP_WIDTH or x < 0:
        return False
    elif y >= settings.MAP_HEIGHT or y < 0:
        return False
    elif gv.game_map.transparent[x][y] == True:
        return True
    else:
        return False