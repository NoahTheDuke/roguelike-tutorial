''' code related to all windows, i.e. temporary panels and popups '''

import tdl
import colors

import global_vars as gv

def draw_spotted_window(root):
    ''' draws a window next to the cursor if any objects are in the area '''

    panel = gv.spotted_window
    cx,cy = gv.cursor.pos()

    spotted = [obj for obj in gv.gameobjects if ([obj.x,obj.y] == [cx,cy] and not obj == gv.cursor and not obj == gv.player)]

    if len(spotted) > 0:    # if more than one object is present, output the names as a message
        lines = []
        gv.cusor.color = colors.light_yellow
        width = max([len(obj.name) for obj in spotted]) + 3 # Window width is adapted to longest object name in list
        for obj in spotted:    # Go through the object names and wrap them according to the panel's width
            line_wrapped = wrap(obj.name,width)
            for text in line_wrapped:
                lines.append(text)

        (panel.width,panel.height) = (width,4 + len(lines))
        panel.clear(fg=colors.white, bg=colors.black)
        draw_panel_borders(panel,color=panel.border_color)
        
        panel.draw_str(1,0,'I spot:')
        y = 2
        for text in lines:
            panel.draw_str(1,y,text.title(),bg=None, fg=colors.white)
            y += 1

        root.blit(panel,cx+2,cy-2, panel.width, panel.height)