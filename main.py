#! python3
''' A simple roguelike based on an online tutorial '''

import tdl
from tcod import image_load
from random import randint
import colors
import settings
import global_vars as glob
from input_util import handle_keys, process_input
from map_util import GameMap,make_map
from render_util import render_all, fov_recompute
from gui_util import message, menu
from entities import Player, Cursor
from generators import place_objects
from target_util import look_at_ground

def initialize_window():
    ''' initializes & launches the game '''
    
    # Set custom font
    tdl.set_font('resources/arial10x10.png', greyscale=True, altLayout=True)

    # initialize the window
    glob.root = tdl.init(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
    glob.con = tdl.Console(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    glob.panel = tdl.Console(settings.SCREEN_WIDTH, settings.PANEL_HEIGHT)

    main_menu()

def main_menu():
    img = image_load('resources\menu_background2.png')

    while not tdl.event.is_window_closed():
        #show the background image, at twice the regular console resolution
        img.blit_2x(glob.root, 0, 0)

        #show the game's title, and some credits!
        title = 'THE PITS BELOW'
        center = (settings.SCREEN_WIDTH - len(title)) // 2
        glob.root.draw_str(center, settings.SCREEN_HEIGHT//2-4, title, bg=None, fg=colors.light_yellow)

        title = 'By Wolfenswan'
        center = (settings.SCREEN_WIDTH - len(title)) // 2
        glob.root.draw_str(center, settings.SCREEN_HEIGHT-2, title, bg=None, fg=colors.light_yellow)
 
        #show options and wait for the player's choice
        choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)
 
        if choice == 0:  #new game
            new_game()
        elif choice == 2:  #quit
            break

def new_game():
    ''' sets up a new game '''
    # reset other global variables
    glob.gameobjects = []
    glob.actors = []
    glob.game_msgs = []
    glob.inventory = []

    # create the player & cursor
    player_stats = (30,2,5) # hp/defense/power
    glob.player = Player(randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),'player', '@', colors.white, stats=player_stats,blocks=True)
    glob.cursor = Cursor(0,0)

    # create the map
    glob.game_map = GameMap(settings.MAP_WIDTH,settings.MAP_HEIGHT)
    make_map()
    
    # place objects in the map
    place_objects()

    # initialize FOV
    fov_recompute()
    
    # clear the old console
    glob.con.clear()
    
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
        for obj in glob.gameobjects:
            obj.clear(glob.con)
        
        glob.player.is_active = True # Player is considered active by default
        player_action = handle_keys(tdl.event.key_wait())

        if not player_action == None:
            if 'exit' in player_action:
                break
            elif 'fullscreen' in player_action:
                tdl.set_fullscreen(not tdl.get_fullscreen())
                glob.player.is_active = False
            else:              
                if not glob.player.is_dead:
                    process_input(player_action)
                
                if glob.cursor.is_active:
                    look_at_ground()
                
                #TODO: Get targeting to work
                #IDEA: suspend all input processing above, while is_targeting
                # if glob.player.is_targeting:
                #     target_tile()

                #AI takes turn, if player is not considered inactive
                if glob.player.is_active:
                    for obj in glob.actors:
                        if obj.ai and glob.game_map.fov[obj.x, obj.y]:
                            obj.ai.take_turn()

initialize_window()