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

# GUI
from gui.render_main import render_all, initialize_window
from gui.menus import menu
from gui.messages import MessageLog, Message, msgbox
from gui.manual import display_manual

# Generators
from generators.gen_game import gen_game

# Game-related modules
from game_states import GameStates
from input_util import handle_keys, process_input


def main_menu():
    img = image_load('resources\menu_background3.png')

    while not tdl.event.is_window_closed():
        #show the background image, at twice the regular console resolution
        img.blit_2x(gv.root, 0, 0)

        #show the game's title, and some credits!
        title = 'THE PITS BELOW'
        center = (settings.SCREEN_WIDTH - len(title)) // 2
        gv.root.draw_str(center, settings.SCREEN_HEIGHT // 2 - 4, title, bg=None, fg=colors.light_yellow)

        title = 'By Wolfenswan'
        center = (settings.SCREEN_WIDTH - len(title)) // 2
        gv.root.draw_str(center, settings.SCREEN_HEIGHT - 2, title, bg=None, fg=colors.light_yellow)

        #show options and wait for the player's choice
        #choice = menu('', ['Play a new game', 'Continue last game', 'Quit'], 24)
        choice = menu('', ['Play a new game', 'Quit'], 24)

        if choice == 0:  # new game:
            gen_game(True)
            main_loop()
        # elif choice == 1:
        #     try:
        #         load_game()
        #         main_loop()
        #     except:
        #         msgbox('\n No saved game to load.\n', 24)
        elif choice == 1:  #quit
            break


def main_loop():
    ''' begin main game loop '''

    # limit the game's FPS
    tdl.setFPS(settings.LIMIT_FPS)

    # set the gamestate to the player's turn
    gv.gamestate = GameStates.PLAYERS_TURN
    turnnumber = 0

    while not tdl.event.is_window_closed():
        turnnumber += 1
        if gv.stairs_down.descended:
            #msgbox('You descend further downwards %s' % settings.DUNGEONNAME,colors.dark_red)
            gen_game(newgame=False)

        render_all()
        tdl.flush()
        for obj in gv.gameobjects:
            obj.clear(gv.con)

        #gv.player.is_active = True # Player is considered active by default
        print('main loop waiting on input in turn {0}!'.format(turnnumber))
        player_action = handle_keys(tdl.event.key_wait())
        #print('Gamestate: %s' % gv.gamestate)

        # if the action is recognized, proceed
        if not player_action == None:
            if 'exit' in player_action:
                # if the player action is exit, prompt if he wants to quit the game
                if gv.gamestate == GameStates.PLAYERS_TURN:
                    choice = menu('Save & Quit the %s' % settings.DUNGEONNAME + ' ?', ['Yes', 'No'], 24)
                    if choice == 0:
                        save_game()
                        break

                elif gv.gamestate == GameStates.PLAYER_DEAD:
                    choice = menu('Quit the %s' % settings.DUNGEONNAME + ' ?', ['Yes', 'No'], 24)
                    if choice == 0:
                        break

            # Esc cancels inventory interaction or cursor mode
            elif 'cancel' in player_action and gv.gamestate in [GameStates.INVENTORY_ACTIVE, GameStates.CURSOR_ACTIVE]:
                gv.gamestate = GameStates.PLAYERS_TURN

            elif 'fullscreen' in player_action:
                tdl.set_fullscreen(not tdl.get_fullscreen())

            elif 'manual' in player_action:
                display_manual()

            else:
                if gv.gamestate in [GameStates.PLAYERS_TURN, GameStates.CURSOR_ACTIVE, GameStates.INVENTORY_ACTIVE]:
                    print('Gamestate: %s, should be PLAYER_ACTIVE or CURSOR_ACTIVE' % gv.gamestate)
                    process_input(player_action)

                # If player has done an active turn
                if gv.gamestate == GameStates.ENEMY_TURN:
                    #AI takes turn, if player is not considered inactive and is roughly in FOV
                    for obj in gv.actors:
                        if (obj.distance_to(gv.player) <= settings.TORCH_RADIUS + 2) and obj is not gv.player:
                            obj.ai.take_turn()
                    if gv.gamestate is not GameStates.PLAYER_DEAD:
                        gv.gamestate = GameStates.PLAYERS_TURN


def save_game():
    ''' open a new empty shelve (possibly overwriting an old one) to write the game data '''
    with shelve.open('savegames/savegame', 'n') as savefile:
        savefile['map'] = gv.game_map
        savefile['objects'] = gv.gameobjects
        savefile['actors'] = gv.actors
        savefile['inventory'] = gv.player.inventory

        # TODO: message logs

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

        Message(
            'Welcome back stranger to %s! You are on level %s.' % (settings.DUNGEONNAME, gv.dungeon_level),
            color=colors.red)


if __name__ == '__main__':
    initialize_window()
    main_menu()
