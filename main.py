#! python3
''' A simple roguelike based on an online tutorial '''

# Other libraries
import tdl
import shelve
from tcod import image_load
from random import randint

# Constants and global varialbes
import colors
import global_vars as gv
import settings

# Generators
from generators.gen_game import gen_game

# Game-related modules
from gui_util import menu, message, msgbox
from input_util import handle_keys, process_input
from render_util import render_all
from target_util import look_at_ground
from gui_util import display_manual

def initialize_window():
    ''' initializes & launches the game '''
    
    # Set custom font
    tdl.set_font('resources/arial10x10.png', greyscale=True, altLayout=True)

    # initialize the window
    gv.root = tdl.init(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, title=settings.DUNGEONNAME, fullscreen=False)
    gv.con = tdl.Console(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    gv.panel = tdl.Console(settings.SCREEN_WIDTH, settings.PANEL_HEIGHT)

    # begin the main game loop
    tdl.setFPS(settings.LIMIT_FPS)

    main_menu()

def main_menu():
    img = image_load('resources\menu_background3.png')

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
        #choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)
        choice = menu('', ['Play a new game', 'Quit'], 24)

        if choice == 0: # new game:
            gen_game(True)
            #message('Press ? to open the manual.')
        # elif choice == 1:
        #     try:
        #         load_game()
        #     except:
        #         msgbox('\n No saved game to load.\n', 24)
        else: #quit
            break

        main_loop()

def save_game():
    ''' open a new empty shelve (possibly overwriting an old one) to write the game data '''
    with shelve.open('savegames/savegame', 'n') as savefile:
        savefile['map'] = gv.game_map
        savefile['objects'] = gv.gameobjects
        savefile['actors'] = gv.actors
        savefile['inventory'] = gv.inventory
        savefile['messages']=gv.game_msgs

        # Store the index of special objects, so they can be later restored from the gv.gameobjects array
        savefile['p_index'] = gv.gameobjects.index(gv.player)
        savefile['c_index'] = gv.gameobjects.index(gv.cursor)
        savefile['sd_index'] = gv.gameobjects.index(gv.stairs_down)
        savefile['su_index'] = gv.gameobjects.index(gv.stairs_up)
        
        savefile.close()

def load_game():
    ''' load an existing savegame '''
    with shelve.open('savegames/savegame', 'r') as savefile:
        gv.game_map = savefile['map']
        gv.gameobjects = savefile['objects']
        gv.actors = savefile['actors']
        #gv.actors = [obj for obj in gameobjects if ]
        gv.inventory = savefile['inventory']
        gv.game_msgs = savefile['messages']

        # Restore special objects
        gv.player = gv.gameobjects[savefile['p_index']]
        print('{0} is new gv.player'.format(gv.player.name))
        gv.cursor = gv.gameobjects[savefile['c_index']]
        gv.stairs_down = gv.gameobjects[savefile['sd_index']]
        gv.stairs_up = gv.gameobjects[savefile['su_index']]

        message('Welcome back stranger to %s! You are on level %s.' % (settings.DUNGEONNAME,gv.dungeon_level), colors.red)

def main_loop():
    ''' begin main game loop '''
    while not tdl.event.is_window_closed():
        if gv.stairs_down.descended:
            msgbox('You descend further downwards the %s' % settings.DUNGEONNAME)
            gen_game(newgame=False)

        render_all()
        tdl.flush()
        for obj in gv.gameobjects:
            obj.clear(gv.con)
        
        gv.player.is_active = True # Player is considered active by default
        player_action = handle_keys(tdl.event.key_wait())
        print(player_action)

        if not player_action == None:
            if 'exit' in player_action:
                choice = menu('Save & Quit the %s' % settings.DUNGEONNAME + ' ?',['Yes','No'],24)
                if choice == 0:
                    save_game()
                    break
            elif 'fullscreen' in player_action:
                tdl.set_fullscreen(not tdl.get_fullscreen())
                gv.player.is_active = False
            elif 'manual' in player_action:
                display_manual()
  
            else:              
                if not gv.player.is_dead:
                    process_input(player_action)

                if gv.cursor.is_active:
                    look_at_ground(gv.cursor.x,gv.cursor.y)
                
                # If player has done an active turn
                if gv.player.is_active:
                    look_at_ground(gv.player.x,gv.player.y) # check ground for stuff
                    #AI takes turn, if player is not considered inactive and is roughly in FOV
                    for obj in gv.actors:
                        if (obj.distance_to(gv.player) <= settings.TORCH_RADIUS + 2) and obj is not gv.player:
                            obj.ai.take_turn()

if __name__ == '__main__':
    initialize_window()
