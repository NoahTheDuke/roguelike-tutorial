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
from classes.actors import Player
# Classes
from classes.objects import Cursor
# Generators
from generators.gen_actors import gen_monsters, gen_Player
from generators.gen_items import gen_inventory, gen_items
from gui_util import menu, message
# Game-related modules
from input_util import handle_keys, process_input
from map_util import GameMap, make_map
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
            new_game()
        elif choice == 2:  #quit
            break

def new_game():
    ''' sets up a new game '''
    # reset other global variables
    gv.gameobjects = []
    gv.actors = []
    gv.game_msgs = []
    gv.inventory = []

    # create the player & cursor
    player_stats = (30,2,5) # hp/defense/power
    gv.player = gen_Player(randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),randint(settings.MAP_HEIGHT,settings.MAP_WIDTH))
    #Player(randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),'player', '@', colors.white, stats=player_stats,blocks=True)
    gv.cursor = Cursor(0,0)

    # setup an initial inventory
    gen_inventory()

    # create the map
    gv.game_map = GameMap(settings.MAP_WIDTH,settings.MAP_HEIGHT)
    make_map()
    
    # fill the map with content
    gen_monsters()
    gen_items()

    # initialize FOV
    fov_recompute()
    
    # clear the old console
    gv.con.clear()
    
    # a warm welcoming message!
    message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', colors.red)
    
    # begin the main game loop
    tdl.setFPS(settings.LIMIT_FPS)
    main_loop()

def main_loop():
    ''' begin main game loop '''
    while not tdl.event.is_window_closed():
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
                
                #AI takes turn, if player is not considered inactive
                if gv.player.is_active:
                    for obj in gv.actors:
                        if not obj.is_player and gv.game_map.fov[obj.x, obj.y]:
                            obj.ai.take_turn()

if __name__ == '__main__':
    initialize_window()
