import settings
import colors
import global_vars as gv

def render_all():
    ''' draw all game objects '''
    root = gv.root
    con = gv.con
    panel = gv.panel
    for y in range(settings.MAP_HEIGHT):
        for x in range(settings.MAP_WIDTH):
            wall = not gv.game_map.transparent[x,y]
            if not gv.game_map.fov[x, y]:
                #it's out of the gv.player's FOV but explored
                if gv.game_map.explored[x][y]:
                    if wall:
                        con.draw_char(x, y,'#', fg=colors.grey, bg=colors.darkest_gray)
                    else:
                        con.draw_char(x, y,'.', fg=colors.grey, bg=colors.darkest_grey)
            else:
                #it's visible
                if gv.game_map.gibbed[x][y]:
                    fgcolor = colors.red
                else:
                    fgcolor = colors.white
                
                if wall:
                    con.draw_char(x, y,'#', fg=fgcolor, bg=colors.black)
                else:
                    con.draw_char(x, y,'.', fg=fgcolor, bg=colors.black)
                gv.game_map.explored[x][y] = True
    for obj in gv.gameobjects:
        if gv.game_map.fov[obj.x,obj.y]:
            obj.draw(con)
    
    root.blit(con , 0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, 0, 0)
    #prepare to render the GUI panel
    panel.clear(fg=colors.white, bg=colors.black)
 
    #show the gv.player's stats
    render_bar(1, 1, settings.BAR_WIDTH, 'HP', gv.player.hp, gv.player.max_hp,
        colors.light_red, colors.darker_red)
    render_bar(1,2, settings.BAR_WIDTH, 'PWR', gv.player.power, gv.player.max_power,
        colors.black, colors.black)
    render_bar(1, 3, settings.BAR_WIDTH, 'DEF', gv.player.defense, gv.player.max_defense,
        colors.black, colors.black)       
    
    #print the game messages, one line at a time
    y = 1
    for (line, color) in gv.game_msgs:
        panel.draw_str(settings.MSG_X, y, line, bg=None, fg=color)
        y += 1
 
    #blit the contents of "panel" to the root console
    root.blit(panel, 0, settings.PANEL_Y, settings.SCREEN_WIDTH, settings.PANEL_HEIGHT, 0, 0)

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    '''render a bar (HP, experience, etc). first calculate the width of the bar'''
    panel = gv.panel
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

def fov_recompute():
    ''' Recomputes the gv.player's FOV '''
    gv.game_map.compute_fov(gv.player.x, gv.player.y,fov=settings.FOV_ALGO,radius=settings.TORCH_RADIUS,light_walls=settings.FOV_LIGHT_WALLS)