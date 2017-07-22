''' code related to all windows, i.e. temporary panels and popups '''

import tdl
import textwrap

import colors

from gui.panels import draw_panel_borders

import global_vars as gv

def draw_spotted_window(root):
    ''' draws a window next to the cursor if any objects are in the area '''

    cx,cy = gv.cursor.pos()

    spotted = [obj for obj in gv.gameobjects if ([obj.x,obj.y] == [cx,cy] and not obj == gv.cursor and not obj == gv.player)]

    if len(spotted) > 0:    # if more than one object is present, output the names as a message
        lines = []
        #gv.cursor.color = colors.yellow
        width = max([len(obj.name) for obj in spotted]) + 6 # Window width is adapted to longest object name in list
        for obj in spotted:    # Go through the object names and wrap them according to the panel's width
            line_wrapped = textwrap.wrap(obj.name,width)
            for text in line_wrapped:
                lines.append(text)

        panel = tdl.Window(gv.con,cx+2,cy-2,width,4 + len(lines))
        panel.border_color=colors.white
        panel.clear(fg=colors.white, bg=colors.black)
        draw_panel_borders(panel,color=panel.border_color)
        
        panel.draw_str(1,0,'I spot:')
        y = 2
        for text in lines:
            panel.draw_str(1,y,text.title(),bg=None, fg=colors.white)
            y += 1

        root.blit(panel,cx+2,cy-2, panel.width, panel.height)

        #if there is an actor amongst the spotted objects:
            # switch the "enemies" panel to a "description" panel
        if len([obj for obj in spotted if obj in gv.actors]) > 0:
            gv.combat_panel.caption = 'Description'
            gv.combat_panel.mode = 'description'
    else:
        gv.combat_panel.caption = 'Enemies'
        gv.combat_panel.mode = 'default'