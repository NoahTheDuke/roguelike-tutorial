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

# Classes
from classes.messages import MessageLog

# Generators
from generators.gen_game import gen_game

# Game-related modules
from game_states import GameStates
from gui_util import menu, msgbox
from input_util import handle_keys, process_input
from render_util import render_all
from target_util import look_at_ground
from gui_util import display_manual

def initialize_window():
    ''' initializes & launches the game '''
    
    # Set custom font
    tdl.set_font('resources/terminal12x12_gs_ro.png', greyscale=True)

    # initialize the window
    gv.root = tdl.init(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, title=settings.DUNGEONNAME, fullscreen=False)
    gv.con = tdl.Console(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

    # initialize the panels
    gv.stat_panel = tdl.Console(settings.SIDE_PANEL_WIDTH,settings.STAT_PANEL_HEIGHT)
    gv.inv_panel = tdl.Console(settings.SIDE_PANEL_WIDTH,settings.INV_PANEL_HEIGHT)
    gv.gamelog_panel = tdl.Console(settings.BOTTOM_PANEL_WIDTH, settings.BOTTOM_PANEL_HEIGHT)
    gv.combat_panel = tdl.Console(settings.COMBAT_PANEL_WIDTH, settings.BOTTOM_PANEL_HEIGHT)

    # set the default captions for all panels
    gv.stat_panel.caption = 'Status'
    gv.inv_panel.caption = 'Inventory'
    gv.gamelog_panel.caption = 'Gamelog'
    gv.combat_panel.caption = 'Enemies'

    # set the default border color for all panels
    for panel in [gv.stat_panel,gv.inv_panel,gv.gamelog_panel,gv.combat_panel]:
        panel.border_color = settings.PANELS_BORDER_COLOR

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
            #msgbox('Welcome stranger! Prepare to perish in %s.' % settings.DUNGEONNAME,width=30,text_color=colors.red)
            gen_game(True)
            
            #Message('Press ? to open the manual.')
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
        savefile['inventory'] = gv.player.inventory
        #savefile['messages']=gv.game_msgs

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
        gv.player.inventory = savefile['inventory']
        #gv.game_msgs = savefile['messages']

        # Restore special objects
        gv.player = gv.gameobjects[savefile['p_index']]
        print('{0} is new gv.player'.format(gv.player.name))
        gv.cursor = gv.gameobjects[savefile['c_index']]
        gv.stairs_down = gv.gameobjects[savefile['sd_index']]
        gv.stairs_up = gv.gameobjects[savefile['su_index']]

        Message('Welcome back stranger to %s! You are on level %s.' % (settings.DUNGEONNAME,gv.dungeon_level), color=colors.red)

def main_loop():
    ''' begin main game loop '''
    gv.gamestate = GameStates.PLAYERS_TURN

    while not tdl.event.is_window_closed():
        if gv.stairs_down.descended:
            #msgbox('You descend further downwards %s' % settings.DUNGEONNAME,colors.dark_red)
            gen_game(newgame=False)

        render_all()
        tdl.flush()
        for obj in gv.gameobjects:
            obj.clear(gv.con)
        
        #gv.player.is_active = True # Player is considered active by default
        #print('main loop waiting again!')
        player_action = handle_keys(tdl.event.key_wait())
        #print('Gamestate: %s' % gv.gamestate)
        if not player_action == None:
            if 'exit' in player_action:
                # if the player is exit, prompt if he wants to quit the game
                if gv.gamestate == GameStates.PLAYERS_TURN:
                    choice = menu('Save & Quit the %s' % settings.DUNGEONNAME + ' ?',['Yes','No'],24)
                    if choice == 0:
                        save_game()
                        break

                elif gv.gamestate == GameStates.PLAYER_DEAD:
                    choice = menu('Quit the %s' % settings.DUNGEONNAME + ' ?',['Yes','No'],24)
                    if choice == 0:
                        break    
            
                # if the cursor is active, deactivate it
                elif gv.gamestate == GameStates.CURSOR_ACTIVE:
                    gv.cursor.deactivate()
                    gv.gamestate = GameStates.PLAYERS_TURN
                    
            elif 'fullscreen' in player_action:
                tdl.set_fullscreen(not tdl.get_fullscreen())
            elif 'manual' in player_action:
                display_manual()

            else:              
                if gv.gamestate is GameStates.PLAYERS_TURN or gv.gamestate is GameStates.CURSOR_ACTIVE:
                    print('Gamestate: %s, should be PLAYER_ACTIVE or CURSOR_ACTIVE' % gv.gamestate)
                    #print('processing input!')
                    process_input(player_action)
                
                # If player has done an active turn
                if gv.gamestate == GameStates.ENEMY_TURN:
                    #AI takes turn, if player is not considered inactive and is roughly in FOV
                    for obj in gv.actors:
                        if (obj.distance_to(gv.player) <= settings.TORCH_RADIUS + 2) and obj is not gv.player:
                            obj.ai.take_turn()
                    if gv.gamestate is not GameStates.PLAYER_DEAD:
                        gv.gamestate = GameStates.PLAYERS_TURN

if __name__ == '__main__':
    initialize_window()
