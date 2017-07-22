''' all code relevant to rendering the info panels '''

import tdl
from textwrap import wrap

import settings
import colors
import global_vars as gv

def render_panels(root,visible_tiles):
    ''' renders the GUI panels containing stats, logs etc. '''

    # Setup each panel by clearing it and drawing it's borders
    for panel in [gv.stat_panel,gv.inv_panel,gv.gamelog_panel,gv.combat_panel,gv.spotted_window]:
        panel.clear(fg=colors.white, bg=colors.black)
        draw_panel_borders(panel,color=panel.border_color)

    # call the individual function for each panel to draw it
    draw_stat_panel(gv.stat_panel,root)
    draw_inv_panel(gv.inv_panel,root)
    draw_gamelog_panel(gv.gamelog_panel,root)
    draw_combat_panel(gv.combat_panel,root,visible_tiles)

def draw_stat_panel(panel,root):
    ''' panel containing player stats & name '''

    # Add the panel's caption
    panel.draw_str(2,0,panel.caption)
        
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
                panel.draw_str(x,y+1,'~ ~ ~ ~ MORE ~ ~ ~ ~')
                break

def draw_inv_panel(panel,root):
    ''' panel containing the inventory '''

    # Add the panel's caption
    if panel.caption == 'Inventory':
        panel.draw_str(2,0,'Inventory {0}/26'.format(len(gv.player.inventory)))
    
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
                panel.draw_str(x,y,'~ ~ ~ more ~ ~ ~')
                break
    
    root.blit(panel,settings.SIDE_PANEL_X,settings.STAT_PANEL_HEIGHT, panel.width, panel.height)

def draw_gamelog_panel(panel,root):
    ''' draws the bottom (message) panel '''

    # draw the panenl's heading
    panel.draw_str(2,0,panel.caption)

    #print the game messages, one line at a time
    gv.game_log.display_messages(2,panel)
 
    #blit the contents of "panel" to the root console
    root.blit(panel, settings.COMBAT_PANEL_WIDTH, settings.BOTTOM_PANEL_Y, panel.width, panel.height)

def draw_combatlog_panel(panel,root):
    ''' (OBSOLETE) draws the bottom (message) panel '''

    # draw the panenl's heading
    panel.draw_str(2,0,panel.caption)

    #print the game messages, one line at a time
    gv.combat_log.display_messages(2,panel)
 
    #blit the contents of "panel" to the root console
    root.blit(panel,0, settings.BOTTOM_PANEL_Y, panel.width, panel.height)

def draw_combat_panel(panel,root,visible_tiles):
    ''' draws the bottom left panel '''

    # draw the panenl's heading
    panel.draw_str(2,0,panel.caption)

    # check for monsters in FOV
    spotted = [ent for ent in gv.actors if (ent.x,ent.y) in visible_tiles and ent is not gv.player]

    if len(spotted) > 0:
        x = 2
        y = 2
        for ent in spotted:    # Go through the object names and wrap them according to the panel's width
            panel.draw_str(x,y,'{0}:'.format(ent.name),bg=None, fg=colors.white)
            wounded = ent.get_health_as_string_and_color()
            panel.draw_str(len(ent.name)+4,y,'{0}'.format(wounded[0].title()),bg=None, fg=wounded[1])
            y += 2
            if y >= panel.height - 2: # If the limit's of the panel are reached, cut the panel off
                panel.draw_str(x,y,'~ ~ ~ ~ MORE ~ ~ ~ ~')
                break
 
    #blit the contents of "panel" to the root console
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

def draw_panel_borders(window,width=None,height=None,color=colors.dark_grey):
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