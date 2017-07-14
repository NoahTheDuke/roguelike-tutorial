#! python3
''' A simple roguelike based on an online tutorial '''

# Other libraries
import tdl
from tcod import image_load
from random import randint

# Constants and global varialbes
import colors
import global_vars as gv
import settings

# Generators
from generators.gen_game import gen_game

# Game-related modules
from gui_util import menu, message
from input_util import handle_keys, process_input
from render_util import fov_recompute, render_all
from target_util import look_at_ground

def initialize_window():
    ''' initializes & launches the game '''
    
    # Set custom font
    tdl.set_font('resources/arial10x10.png', greyscale=True, altLayout=True)

    # initialize the window
    gv.root = tdl.init(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
    gv.con = tdl.Console(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    gv.panel = tdl.Console(settings.SCREEN_WIDTH, settings.PANEL_HEIGHT)

    # begin the main game loop
    tdl.setFPS(settings.LIMIT_FPS)

    main_menu()

def main_menu():
    img = image_load('resources\menu_background2.png')

    while not tdl.event.is_window_closed():
        #show the background image, at twice the regular console resolution
        img.blit_2x(gv.root, 0, 0)

        #show the game's title, and some credits!
        title = 'THE PITS BELOW'
        center = (settings.SCREEN_WIDTH - len(title)) // 2
        gv.root.draw_str(center, settings.SCREEN_HEIGHT//2-4, title, bg=None, fg=colors.light_yellow)

        title = 'By Wolfenswan'
        center = (settings.SCREEN_WIDTH - len(title)) // 2
        gv.root.draw_str(center, settings.SCREEN_HEIGHT-2, title, bg=None, fg=colors.light_yellow)
 
        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)
 
        if choice == 0:  #new game
            gen_game()
            main_loop()
        elif choice == 2:  #quit
            break

def main_loop():
    ''' begin main game loop '''
    while not tdl.event.is_window_closed():
        if gv.stairs_down.descended:
            gen_game(newgame=False)

        render_all()
        tdl.flush()
        for obj in gv.gameobjects:
            obj.clear(gv.con)
        
        gv.player.is_active = True # Player is considered active by default
        player_action = handle_keys(tdl.event.key_wait())

        if not player_action == None:
            if 'exit' in player_action:
                break
            elif 'fullscreen' in player_action:
                tdl.set_fullscreen(not tdl.get_fullscreen())
                gv.player.is_active = False
            else:              
                if not gv.player.is_dead:
                    process_input(player_action)

                if gv.cursor.is_active:
                    look_at_ground(gv.cursor.x,gv.cursor.y)
                
                # If player has done an active turn
                if gv.player.is_active:
                    look_at_ground(gv.player.x,gv.player.y) # check ground for stuff
                    #AI takes turn, if player is not considered inactive
                    for obj in gv.actors:
                        if gv.game_map.fov[obj.x, obj.y] and (not obj == gv.player):
                            obj.ai.take_turn()

if __name__ == '__main__':
    initialize_window()
