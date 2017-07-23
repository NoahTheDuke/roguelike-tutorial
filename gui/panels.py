''' all code relevant to rendering the info panels '''

import tdl
from textwrap import wrap

import settings
import colors
import global_vars as gv

from gui.helpers import draw_window_borders as draw_panel_borders

from game_states import GameStates

def render_panels(root,visible_tiles):
    ''' renders the GUI panels containing stats, logs etc. '''

    # call the individual function for each panel to draw it
    draw_stat_panel(gv.stat_panel,root)
    draw_inv_panel(gv.inv_panel,root)
    draw_gamelog_panel(gv.gamelog_panel,root)
    draw_combat_panel(gv.combat_panel,root,visible_tiles)
    
    # if the cursor is active, try drawing the description panel
    if gv.gamestate == GameStates.CURSOR_ACTIVE:
        try:
            gv.combat_panel.caption = 'Description'
            draw_description_panel(gv.combat_panel,root)
        except:
            gv.combat_panel.caption = 'Enemies'
            draw_combat_panel(gv.combat_panel,root,visible_tiles)       

def setup_panel(panel):
    panel.clear(fg=colors.white, bg=colors.black)
    draw_panel_borders(panel,color=panel.border_color)
    panel.draw_str(2,0,panel.caption)

def draw_stat_panel(panel,root):
    ''' panel containing player stats & name '''
    
    # sets up the panel's basic functionality
    setup_panel(panel)

    # Show the player's name and stats
    panel.draw_str(1,2,'Name: %s' % gv.player.name, bg=None, fg=colors.gold)
    render_bar(1,4,panel,settings.BAR_WIDTH, 'HP', gv.player.hp, gv.player.max_hp,
        colors.light_red, colors.darker_red)
    render_bar(1,6,panel,settings.BAR_WIDTH, 'PWR', gv.player.power, gv.player.max_power,
        colors.black, colors.black)
    render_bar(1,8,panel,settings.BAR_WIDTH, 'DEF', gv.player.defense, gv.player.max_defense,
        colors.black, colors.black)

    draw_spotteditems_panel(panel)
    
    root.blit(panel,settings.SIDE_PANEL_X,0, panel.width, panel.height)
    
def draw_spotteditems_panel(panel):
    ''' draws items below the player a panel '''
   
    # Draw what the player can see at his feet

    spotted = [obj.name for obj in gv.gameobjects if (obj.x,obj.y) == gv.player.pos() and obj.is_item]
    if len(spotted) > 0:    # if more than one object is present, output the names as a message
        x = 2
        y = settings.STAT_PANEL_HEIGHT//2
        panel.draw_str(x,settings.STAT_PANEL_HEIGHT//2,'At your feet:', bg=None, fg=colors.white)
        y += 2
        for obj in spotted:    # Go through the object names and wrap them according to the panel's width
            line_wrapped = wrap(obj,panel.width - 3)
            if y + len(line_wrapped) < panel.height-2:  # As long as we don't exceed the panel's height, draw the items
                for text in line_wrapped:
                    panel.draw_str(x,y,text.title(),bg=None, fg=colors.white)
                    y+=1
            else:   # otherwise draw a line to indicate there's more than can be displayed
                panel.draw_str((panel.width-6)//2,panel.height-1,'< MORE >')
                break

def draw_inv_panel(panel,root):
    ''' panel containing the inventory '''

    if gv.gamestate == GameStates.INVENTORY_ACTIVE:
        panel.border_color = settings.PANELS_BORDER_COLOR_ACTIVE
        panel.caption = 'Select item:'
    else:
        panel.border_color = settings.PANELS_BORDER_COLOR
        panel.caption = 'Inventory {0}/26:'.format(len(gv.player.inventory))

    # sets up the panel's basic functionality
    setup_panel(panel)   
    
    if len(gv.player.inventory) > 0:
        y = 2 # offset from the top of the panel
        x = 1 # offset from the left of the panel
        li = ord('a')   # index used to display the letters next to the inventory
        for i in range(len(gv.player.inventory)):
            item = gv.player.inventory[i]
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
            
            if y >= panel.height - 2: # If the limit's of the panel are reached, cut the inventory off 
                panel.draw_str((panel.width-6)//2,panel.height-1,'< MORE >')
                break
        
                
    
    root.blit(panel,settings.SIDE_PANEL_X,settings.STAT_PANEL_HEIGHT, panel.width, panel.height)

def draw_gamelog_panel(panel,root):
    ''' draws the bottom (message) panel '''

    # sets up the panel's basic functionality
    setup_panel(panel)

    #print the game messages, one line at a time
    gv.game_log.display_messages(2,panel)
 
    #blit the contents of "panel" to the root console
    root.blit(panel, settings.COMBAT_PANEL_WIDTH, settings.BOTTOM_PANEL_Y, panel.width, panel.height)

def draw_combatlog_panel(panel,root):
    ''' (OBSOLETE) draws the bottom (message) panel '''

    #print the game messages, one line at a time
    gv.combat_log.display_messages(2,panel)
 
    #blit the contents of "panel" to the root console
    root.blit(panel,0, settings.BOTTOM_PANEL_Y, panel.width, panel.height)

def draw_combat_panel(panel,root,visible_tiles):
    ''' draws the bottom left panel '''

    # sets up the panel's basic functionality
    setup_panel(panel)

    # check for monsters in FOV
    spotted = [ent for ent in gv.actors if (ent.x,ent.y) in visible_tiles and ent is not gv.player]

    if len(spotted) > 0:
        x = 2
        y = 2
        spotted.sort(key=gv.player.distance_to) # sort the spotted array by distance to player
        for ent in spotted:    # Go through the object names and wrap them according to the panel's width
            panel.draw_str(x,y,'{0}:'.format(ent.name),bg=None, fg=colors.white)
            status = ent.get_health_as_string_and_color()
            panel.draw_str(len(ent.name)+4,y,'{0}'.format(status[0].title()),bg=None, fg=status[1])
            y += 2
            if y >= panel.height - 2: # If the limit's of the panel are reached, cut the panel off
                panel.draw_str(x,y,'~ ~ ~ ~ MORE ~ ~ ~ ~')
                break
 
    #blit the contents of "panel" to the root console
    root.blit(panel,0, settings.BOTTOM_PANEL_Y, panel.width, panel.height)

def draw_description_panel(panel,root):
    ''' shows a monster's description in the combat panel '''

    # sets up the panel's basic functionality
    setup_panel(panel)

    # get the first entity from the actors array under the cursor position
    # (if this fails, the except in render_panels() catches it)
    ent = next(ent for ent in gv.actors if (ent.x,ent.y)==(gv.cursor.pos()))
    
    x = 2
    y = 2
    panel.draw_str(x,y,'{0}:'.format(ent.name),bg=None, fg=colors.white)
    status = ent.get_health_as_string_and_color()
    panel.draw_str(len(ent.name)+4,y,'{0}'.format(status[0].title()),bg=None, fg=status[1])

    text_wrapped = wrap(ent.description,settings.BAR_WIDTH-4)
    y += 2
    for line in text_wrapped:
        panel.draw_str(x,y,line,bg=None, fg=colors.white)
        y += 1

    root.blit(panel,0, settings.BOTTOM_PANEL_Y, panel.width, panel.height)

def render_bar(x, y, panel,total_width, name, value, maximum, bar_color, back_color):
    '''render a status bar (HP, experience, etc).'''
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

