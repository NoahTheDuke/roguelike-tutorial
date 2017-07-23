''' main function for drawing all objects in the game '''

import tdl
#import tcod
#from textwrap import wrap
from enum import Enum,auto

import settings
import colors
import global_vars as gv

from gui.panels import render_panels, draw_panel_borders
from gui.windows import draw_spotted_window

from game_states import GameStates

class RenderOrder(Enum):
    ''' the RenderOrder class is a component of all objects and determines their render priority '''

    NONE = auto()
    CORPSE = auto()
    ITEM = auto()
    ACTOR = auto()
    CURSOR = auto()

def initialize_window():
    ''' initializes & launches the game '''
    
    # Set custom font
    tdl.set_font('resources/terminal12x12_gs_ro.png', greyscale=True)

    # initialize the main console
    gv.root = tdl.init(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, title=settings.DUNGEONNAME, fullscreen=False)
    gv.con = tdl.Console(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

    # initialize the panels
    gv.stat_panel = tdl.Console(settings.SIDE_PANEL_WIDTH,settings.STAT_PANEL_HEIGHT)
    gv.inv_panel = tdl.Console(settings.SIDE_PANEL_WIDTH,settings.INV_PANEL_HEIGHT)
    gv.gamelog_panel = tdl.Console(settings.BOTTOM_PANEL_WIDTH, settings.BOTTOM_PANEL_HEIGHT)
    gv.combat_panel = tdl.Console(settings.COMBAT_PANEL_WIDTH, settings.BOTTOM_PANEL_HEIGHT)

    # set the default captions for all panels
    gv.stat_panel.caption = 'Status'
    gv.inv_panel.caption = 'Inventory'
    gv.gamelog_panel.caption = 'Gamelog'
    gv.combat_panel.caption = 'Enemies'

    # set the default border color and mode for all panels
    for panel in [gv.stat_panel,gv.inv_panel,gv.gamelog_panel,gv.combat_panel]:
        panel.mode = 'default'
        panel.border_color = settings.PANELS_BORDER_COLOR

def render_all():
    ''' draw all game objects '''
    root = gv.root
    con = gv.con

    # clear the console of all temporary windows
    con.clear(fg=colors.white, bg=colors.black)

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
    
    # Draw borders for the map window
    if gv.gamestate in [GameStates.PLAYERS_TURN,GameStates.CURSOR_ACTIVE]:
        map_border = settings.PANELS_BORDER_COLOR_ACTIVE
    else:
        map_border = settings.PANELS_BORDER_COLOR

    draw_panel_borders(con,width=settings.MAP_WIDTH,height=settings.MAP_HEIGHT,color=map_border)    

    root.blit(con, 0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, 0, 0)

    # render the panels containing the GUI
    render_panels(root,visible_tiles)

    # If the cursor is active, draw the spotted window
    if gv.gamestate == GameStates.CURSOR_ACTIVE:
        draw_spotted_window()
    
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