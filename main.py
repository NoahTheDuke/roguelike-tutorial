#! python3
''' A simple roguelike based on an online tutorial '''

import tdl
from random import randint
import colors
import settings
import global_vars as glob
from input_util import handle_keys, process_input
from map_util import GameMap,make_map, fov_recompute
from gui_util import render_all, inventory_menu, message
from entities import GameObject, Fighter, Player, Item, place_objects

def main_loop(con,root,panel):
    ''' begin main game loop '''
    while not tdl.event.is_window_closed():
        render_all(con,root,panel)
        tdl.flush()
        for obj in glob.gameobjects:
            obj.clear(con)
        
        game_state = 'playing'  # Game state is set to playing by default
        player_action = handle_keys(tdl.event.key_wait())

        if not player_action == None:
            if 'exit' in player_action:
                break
            elif 'fullscreen' in player_action:
                tdl.set_fullscreen(not tdl.get_fullscreen())
                game_state = 'paused'
            
            else:
                if not glob.player.is_dead:
                    game_state = process_input(player_action,game_state,root)
            
                #AI takes turn, if game_state is not set to pause
                if game_state == 'playing':
                    for obj in glob.actors:
                        if obj.ai and glob.game_map.fov[obj.x, obj.y]:
                            obj.ai.take_turn()

def initialize_game():
    ''' initializes & launches the game '''
    
    # Set custom font
    tdl.set_font('resources/arial10x10.png', greyscale=True, altLayout=True)

    # initialize the window
    root = tdl.init(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
    con = tdl.Console(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    panel = tdl.Console(settings.SCREEN_WIDTH, settings.PANEL_HEIGHT)

    # create the player
    player_stats = (30,2,5) # hp/defense/power
    glob.player = Player(randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),'player', '@', colors.white, stats=player_stats,blocks=True)

    # create the map
    glob.game_map = GameMap(settings.MAP_WIDTH,settings.MAP_HEIGHT)
    make_map()
    
    # place objects in the map
    place_objects()

    # initialize FOV
    fov_recompute()
    
    # a warm welcoming message!
    message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', colors.red)
    
    # begin the main game loop
    main_loop(con,root,panel)

initialize_game()