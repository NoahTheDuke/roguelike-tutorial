import tdl
from textwrap import wrap
from enum import Enum,auto

import settings
import colors
import global_vars as gv

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
    bottom_panel = gv.bottom_panel
    side_panel = gv.side_panel
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
    
    root.blit(con , 0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, 0, 0)

    # Draw panels
    draw_side_panel(side_panel,root)
    draw_bottom_panel(bottom_panel,root)    

def draw_side_panel(panel,root):
    ''' draws the right (GUI) panel '''

    # prepare to render the GUI panel
    panel.clear(fg=colors.white, bg=colors.black)

    # draw the panel's border
    for y in range(settings.SCREEN_HEIGHT):
        panel.draw_char(0,y,None,bg=colors.darker_grey)
        
    # Show the player's name and stats
    panel.draw_str((settings.BAR_WIDTH-len(gv.player.name))//2,1,gv.player.name, bg=None, fg=colors.gold)
    panel.draw_str(1,2,' ')
    render_bar(1,3,panel,settings.BAR_WIDTH, 'HP', gv.player.hp, gv.player.max_hp,
        colors.light_red, colors.darker_red)
    panel.draw_str(2,4,' ')
    render_bar(1,5,panel,settings.BAR_WIDTH, 'PWR', gv.player.power, gv.player.max_power,
        colors.black, colors.black)
    panel.draw_str(2,6,' ')
    render_bar(1,7,panel,settings.BAR_WIDTH, 'DEF', gv.player.defense, gv.player.max_defense,
        colors.black, colors.black)
    panel.draw_str(1,8,' ')
    
    # Draw the inventory below the stats
    if len(gv.inventory) > 0:
        y = 9
        panel.draw_str((settings.BAR_WIDTH-len(gv.player.name))//2,y,'Inventory', bg=None, fg=colors.gold)
        panel.draw_str(2,y+1,' ')
        y += 2
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

    # # Blit the content to root
    # blit(source, x=0, y=0, width=None, height=None, srcX=0, srcY=0, fg_alpha=1.0, bg_alpha=1.0)
    root.blit(panel, settings.SIDE_PANEL_X,0, settings.SIDE_PANEL_WIDTH, settings.SCREEN_HEIGHT)

def draw_bottom_panel(panel,root):
    ''' draws the bottom (message) panel '''

    # prepare to render the bottom panel
    panel.clear(fg=colors.white, bg=colors.black)       
    
    # draw the panel's border
    for x in range(settings.SCREEN_WIDTH):
        panel.draw_char(x,0,None,bg=colors.darker_grey)

    #print the game messages, one line at a time
    y = 2
    for (line, color) in gv.game_msgs:
        panel.draw_str(settings.MSG_X, y, line, bg=None, fg=color)
        y += 1
 
    #blit the contents of "panel" to the root console
    root.blit(panel, 0, settings.BOTTOM_PANEL_Y, settings.SCREEN_WIDTH-settings.SIDE_PANEL_WIDTH, settings.BOTTOM_PANEL_HEIGHT)

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

def is_visible_tile(x, y):
    if x >= settings.MAP_WIDTH or x < 0:
        return False
    elif y >= settings.MAP_HEIGHT or y < 0:
        return False
    elif gv.game_map.transparent[x][y] == True:
        return True
    else:
        return False