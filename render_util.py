import tdl
import tcod
from textwrap import wrap
from enum import Enum,auto

import settings
import colors
import global_vars as gv

from classes.messages import MessageLog

from game_states import GameStates

#from classes.messages import MessageLog

class RenderOrder(Enum):
    NONE = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()
    CURSOR = auto()

def render_all():
    ''' draw all game objects '''
    root = gv.root
    con = gv.con

    # render the dungeon map and it's objects
    px,py = gv.player.x, gv.player.y
    visible_tiles = (tdl.map.quick_fov(px, py,is_visible_tile,fov=settings.FOV_ALGO,radius=settings.TORCH_RADIUS,lightWalls=settings.FOV_LIGHT_WALLS))
    for y in range(settings.MAP_HEIGHT):
        for x in range(settings.MAP_WIDTH):
            wall = not gv.game_map.transparent[x][y]
            #if not gv.game_map.fov[x, y]:
            visible = (x, y) in visible_tiles
            
            #tdl.map.quick_fov(px, py,is_visible_tile,fov=settings.FOV_ALGO,radius=settings.TORCH_RADIUS,lightWalls=settings.FOV_LIGHT_WALLS)
            if not visible:
                #it's out of the gv.player's.visible[self.x + dx][self.y+dy]but explored
                if gv.game_map.explored[x][y]:
                    if wall:
                        con.draw_char(x, y,'#', fg=settings.COLOR_DARK_GROUND_fg, bg=settings.COLOR_DARK_GROUND)
                    else:
                        con.draw_char(x, y,'.', fg=settings.COLOR_DARK_WALL_fg, bg=settings.COLOR_DARK_WALL)
                gv.game_map.visible[x][y] = False
            else:
                #it's visible
                if gv.game_map.gibbed[x][y]:
                    fgcolor = colors.red
                else:
                    fgcolor = settings.COLOR_LIGHT_GROUND
                
                if wall:
                    con.draw_char(x, y,'#', fg=fgcolor, bg=colors.black)
                else:
                    con.draw_char(x, y,'.', fg=fgcolor, bg=colors.black)
                gv.game_map.explored[x][y] = True
                gv.game_map.visible[x][y] = True
    
    # sort the objects according to their render order
    sorted_objects = sorted(gv.gameobjects, key=lambda x: x.render_order.value)
    # then render them accordingly
    for obj in sorted_objects:
        if obj.render_order is not RenderOrder.NONE:
            if gv.game_map.visible[obj.x][obj.y]:
                obj.draw(con)
            elif not gv.game_map.visible[obj.x][obj.y] and gv.game_map.explored[obj.x][obj.y] and obj.always_visible: # if obj is not in FOV but should always be visible
                obj.draw(con,fgcolor=settings.COLOR_DARK_WALL_fg,bgcolor=settings.COLOR_DARK_GROUND)
    
    # Draw borders for console window
    draw_window_borders(con,width=settings.MAP_WIDTH,height=settings.MAP_HEIGHT)    

    root.blit(con, 0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, 0, 0)

    # render the panels containing the GUI
    render_panels(root)
    
def render_panels(root):
    ''' renders the GUI panels containing stats, logs etc. '''

    # Setup each panel by clearing it and drawing it's borders
    for panel in [gv.stat_panel,gv.inv_panel,gv.gamelog_panel,gv.combat_panel]:
        panel.clear(fg=colors.white, bg=colors.black)
        draw_window_borders(panel,color=panel.border_color)

    # call the individual function for each panel to draw it
    draw_stat_panel(gv.stat_panel,root)
    draw_inv_panel(gv.inv_panel,root)
    draw_gamelog_panel(gv.gamelog_panel,root)
    draw_combat_panel(gv.combat_panel,root)

def draw_stat_panel(panel,root):
    ''' panel containing player stats & name '''

    # Add the panel's caption
    panel.draw_str(2,0,'Status')
        
    # Show the player's name and stats
    panel.draw_str(1,2,'Name: %s' % gv.player.name, bg=None, fg=colors.gold)
    render_bar(1,4,panel,settings.BAR_WIDTH, 'HP', gv.player.hp, gv.player.max_hp,
        colors.light_red, colors.darker_red)
    render_bar(1,6,panel,settings.BAR_WIDTH, 'PWR', gv.player.power, gv.player.max_power,
        colors.black, colors.black)
    render_bar(1,8,panel,settings.BAR_WIDTH, 'DEF', gv.player.defense, gv.player.max_defense,
        colors.black, colors.black)

    draw_spotted_panel(panel)
    
    root.blit(panel,settings.SIDE_PANEL_X,0, panel.width, panel.height)

def draw_spotted_panel(panel):
    ''' draws spotted items and monsters on a panel '''
   
    # Draw what the player can see (either at his feet or at the cursor's position)
    if gv.gamestate == GameStates.CURSOR_ACTIVE:
        x,y = gv.cursor.pos()
    else:
        x,y = gv.player.pos()
    
    spotted = [obj.name for obj in gv.gameobjects if ([obj.x,obj.y] == [x,y] and not obj == gv.cursor and not obj == gv.player)]
    if len(spotted) > 0:    # if more than one object is present, output the names as a message
        y = settings.STAT_PANEL_HEIGHT//2
        panel.draw_str(1,settings.STAT_PANEL_HEIGHT//2,'I can see:', bg=None, fg=colors.white)
        y += 1
        for obj in spotted:    # Go through the object names and wrap them according to the panel's width
            line_wrapped = wrap(obj,panel.width - 3)
            if y + len(line_wrapped) < panel.height-1:  # As long as we don't exceed the panel's height, draw the items
                for text in line_wrapped:
                    panel.draw_str(2,y,text,bg=None, fg=colors.white)
                    y+=1
            else:   # otherwise draw a line to indicate there's more than can be displayed
                panel.draw_str(1,y,'~ ~ ~ more ~ ~ ~')
                break

def draw_inv_panel(panel,root):
    ''' panel containing the inventory '''

    # Add the panel's caption
    panel.draw_str(2,0,'Inventory {0}/26'.format(len(gv.inventory)))
    
    if len(gv.inventory) > 0:
        y = 2 # offset from the top of the panel
        x = 1 # offset from the left of the panel
        li = ord('a')   # index used to display the letters next to the inventory
        for i in range(len(gv.inventory)):
            item = gv.inventory[i]
            text = wrap(item.name,settings.BAR_WIDTH-4)
            panel.draw_str(x,y,'({0}) {1}'.format(chr(li),text[0].title()))
            y += 1
            li += 1
            if len(text) > 1:   # if the text was wrapped
                for line in text[1:]:   # draw subsequent lines in the following line (NOTE: should I add very long item names, this will need to be tweaked)
                    panel.draw_str(x,y,line.title())
                    y += 1
            panel.draw_str(x,y,' ')
            y += 1
            if y >= settings.INV_PANEL_HEIGHT - 2: # If the limit's of the panel are reached, cut the inventory off 
                panel.draw_str(x,y,'~ ~ ~ more ~ ~ ~')
                break
    
    root.blit(panel,settings.SIDE_PANEL_X,settings.STAT_PANEL_HEIGHT, panel.width, panel.height)


def draw_gamelog_panel(panel,root):
    ''' draws the bottom (message) panel '''

    # draw the panenl's heading
    panel.draw_str(2,0,'Gamelog')

    #print the game messages, one line at a time
    gv.game_log.display_messages(2,panel)
 
    #blit the contents of "panel" to the root console
    root.blit(panel, settings.BOTTOM_PANEL_WIDTH, settings.BOTTOM_PANEL_Y, panel.width, panel.height)

def draw_combat_panel(panel,root):
    ''' draws the bottom (message) panel '''

    # draw the panenl's heading
    panel.draw_str(2,0,'Combatlog')

    #print the game messages, one line at a time
    gv.combat_log.display_messages(2,panel)
 
    #blit the contents of "panel" to the root console
    root.blit(panel,0, settings.BOTTOM_PANEL_Y, panel.width, panel.height)

def render_bar(x, y, panel,total_width, name, value, maximum, bar_color, back_color):
    '''render a bar (HP, experience, etc).'''
    # first calculate the width of the bar
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

def is_visible_tile(x, y):
    if x >= settings.MAP_WIDTH or x < 0:
        return False
    elif y >= settings.MAP_HEIGHT or y < 0:
        return False
    elif gv.game_map.transparent[x][y] == True:
        return True
    else:
        return False