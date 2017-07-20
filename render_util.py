import tdl
import tcod
from textwrap import wrap
from enum import Enum,auto

import settings
import colors
import global_vars as gv

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

    # Create panels
    stat_panel = tdl.Console(settings.SIDE_PANEL_WIDTH,settings.STAT_PANEL_HEIGHT)
    inv_panel = tdl.Console(settings.SIDE_PANEL_WIDTH,settings.INV_PANEL_HEIGHT)
    gamelog_panel = tdl.Console(settings.BOTTOM_PANEL_WIDTH, settings.BOTTOM_PANEL_HEIGHT)
    combat_panel = tdl.Console(settings.BOTTOM_PANEL_WIDTH, settings.BOTTOM_PANEL_HEIGHT)
    
    # Draw panels
    draw_stat_panel (stat_panel,root)
    draw_inv_panel (inv_panel,root)    # TODO: Fix bottom border
    draw_gamelog_panel(gamelog_panel,root)
    draw_combat_panel(combat_panel,root)

def draw_stat_panel(panel,root):
    ''' panel containing player stats & name '''

    panel.clear(fg=colors.white, bg=colors.black)

    # draw the panel's border
    draw_window_borders(panel)

    # Add the panel's caption
    panel.draw_str(2,0,'Player')
        
    # Show the player's name and stats
    panel.draw_str(1,2,'Name: %s' % gv.player.name, bg=None, fg=colors.gold)
    render_bar(1,4,panel,settings.BAR_WIDTH, 'HP', gv.player.hp, gv.player.max_hp,
        colors.light_red, colors.darker_red)
    render_bar(1,6,panel,settings.BAR_WIDTH, 'PWR', gv.player.power, gv.player.max_power,
        colors.black, colors.black)
    render_bar(1,8,panel,settings.BAR_WIDTH, 'DEF', gv.player.defense, gv.player.max_defense,
        colors.black, colors.black)

    root.blit(panel,settings.SIDE_PANEL_X,0, settings.SIDE_PANEL_WIDTH, settings.STAT_PANEL_HEIGHT)

def draw_inv_panel(panel,root):
    ''' panel containing the inventory '''

    panel.clear(fg=colors.white, bg=colors.black)

    # draw the panel's border
    draw_window_borders(panel)

    # Add the panel's caption
    panel.draw_str(2,0,'Inventory')
    
    if len(gv.inventory) > 0:
        y = 2   # Offset from the top of the panel
        for i in range(len(gv.inventory)):
            item = gv.inventory[i]
            text = wrap(item.name,settings.BAR_WIDTH-4)
            panel.draw_str(2,y,'- {0}'.format(text[0].title()))
            y += 1
            if len(text) > 1:
                for line in text[1:]:
                    panel.draw_str(2,y,line.title())
                    y += 1
            panel.draw_str(2,y,' ')
            y += 1
    
    root.blit(panel,settings.SIDE_PANEL_X,settings.STAT_PANEL_HEIGHT, settings.SIDE_PANEL_WIDTH, settings.INV_PANEL_HEIGHT)

def draw_stat_window(panel):
    ''' draw the player stats to a panel '''
    
    # draw the panel's border
    draw_window_borders(panel)

    # Add the panel's caption
    panel.draw_str(2,0,'Player')
        
    # Show the player's name and stats
    panel.draw_str(1,1,' ')
    panel.draw_str(1,2,'Name: %s' % gv.player.name, bg=None, fg=colors.gold)
    panel.draw_str(1,3,' ')
    render_bar(1,4,panel,settings.BAR_WIDTH-2, 'HP', gv.player.hp, gv.player.max_hp,
        colors.light_red, colors.darker_red)
    panel.draw_str(1,5,' ')
    render_bar(1,6,panel,settings.BAR_WIDTH-2, 'PWR', gv.player.power, gv.player.max_power,
        colors.black, colors.black)
    panel.draw_str(1,7,' ')
    render_bar(1,8,panel,settings.BAR_WIDTH-2, 'DEF', gv.player.defense, gv.player.max_defense,
        colors.black, colors.black)
    panel.draw_str(1,9,' ')

    return 9

def draw_gamelog_panel(panel,root):
    ''' draws the bottom (message) panel '''

    # prepare to render the bottom panel
    panel.clear(fg=colors.white, bg=colors.black)       
    
    # draw the panel's border
    draw_window_borders(panel)

    # draw the panenl's heading
    panel.draw_str(2,0,'Gamelog')

    #print the game messages, one line at a time
    y = 2
    for message in gv.game_log.messages:
        panel.draw_str(settings.MSG_X, y, message.text, bg=None, fg=message.color)
        y += 1
 
    #blit the contents of "panel" to the root console
    root.blit(panel, settings.BOTTOM_PANEL_WIDTH, settings.BOTTOM_PANEL_Y,settings.BOTTOM_PANEL_WIDTH,settings.BOTTOM_PANEL_HEIGHT)

def draw_combat_panel(panel,root):
    ''' draws the bottom (message) panel '''

    # prepare to render the bottom panel
    panel.clear(fg=colors.white, bg=colors.black)       
    
    # draw the panel's border
    draw_window_borders(panel)

    # draw the panenl's heading
    panel.draw_str(2,0,'Combatlog')

    #print the game messages, one line at a time
    y = 2
    for message in gv.combat_log.messages:
        panel.draw_str(settings.MSG_X, y, message.text, bg=None, fg=message.color)
        y += 1
 
    #blit the contents of "panel" to the root console
    root.blit(panel,0, settings.BOTTOM_PANEL_Y,settings.BOTTOM_PANEL_WIDTH, settings.BOTTOM_PANEL_HEIGHT)

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

def draw_window_borders(window,width=None,height=None):
    ''' draws an outline around the passed window. By default, the window's width & height will be used '''
    
    if width is None:
        width = window.width
    if height is None:
        height = window.height

    for x in range(width):
        window.draw_char(x,0,'196')
        window.draw_char(x,height-1,'196')

    for y in range(height):
        window.draw_char(0,y,'179')
        window.draw_char(width-1,y,'179')
    
    window.draw_char(0,0,'218')
    window.draw_char(width-1,0,'191')
    window.draw_char(0,height-1,'192')
    window.draw_char(width-1,height-1,'217')

def is_visible_tile(x, y):
    if x >= settings.MAP_WIDTH or x < 0:
        return False
    elif y >= settings.MAP_HEIGHT or y < 0:
        return False
    elif gv.game_map.transparent[x][y] == True:
        return True
    else:
        return False