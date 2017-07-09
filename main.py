#! python3
''' A simple roguelike based on an online tutorial '''

import tdl
from random import randint
import colors
import settings
import global_vars as glob
from keyhandler import handle_keys
from entities import GameObject, Fighter,Item, place_objects
from map_util import GameMap,make_map, fov_recompute
from gui_util import render_all, inventory_menu, message

def player_move_or_attack(dx, dy):
    ''' Makes the glob.player character either move or attack '''

    #the coordinates the glob.player is moving to/attacking
    x = glob.player.x + dx
    y = glob.player.y + dy
 
    #try to find an attackable object there
    target = None
    for obj in glob.gameobjects:
        if obj.fighter and obj.x == x and obj.y == y:
            target = obj
            break
 
    #attack if target found, move otherwise
    if target is not None:
        glob.player.fighter.attack(target)
    else:
        glob.player.move(dx, dy)

def player_death(player):
    '''the game ended!'''
    message('You died!')

    #for added effect, transform the glob.player into a corpse!
    glob.player.char = '%'
    glob.player.color = colors.dark_red

    return 'dead'
    
def main_loop(con,root,panel):
    ''' begin main game loop '''
    game_state = 'playing'
    while not tdl.event.is_window_closed():
        render_all(con,root,panel)
        tdl.flush()

        for obj in glob.gameobjects:
            obj.clear(con)
        player_action = handle_keys(tdl.event.key_wait())
        
        if 'exit' in player_action:
            break
        elif 'fullscreen' in player_action:
            tdl.set_fullscreen(not tdl.get_fullscreen())
        elif game_state == 'playing' and player_action != 'pass':
            if 'move' in player_action:
                x,y = player_action['move']
                player_move_or_attack(x,y)
            elif 'get' in player_action:
                found_something = False
                for obj in glob.gameobjects:  #look for an item in the glob.player's tile
                    if obj.x == glob.player.x and obj.y == glob.player.y and obj.item:
                        obj.item.pick_up()
                        found_something = True
                        break
                if not found_something:
                    message('There is nothing to pick up here!')
            elif 'inventory' in player_action:
                #show the glob.inventory, pressing a key returns the corresponding item
                chosen_item = inventory_menu('Press the key next to an item to %s it, or any other to cancel.\n' % player_action['inventory'],root)
                if chosen_item is not None: #if an item was selected, call it's use or drop function
                    if (player_action['inventory'] == 'use'):
                        chosen_item.use()
                    elif (player_action['inventory'] == 'drop'):
                        chosen_item.drop()
            # AI takes turn
            for obj in glob.gameobjects:
                if obj.ai:
                    obj.ai.take_turn()

def initialize_game():
    ''' launches the game '''
    
    # Set custom font
    tdl.set_font('arial10x10.png', greyscale=True, altLayout=True)

    # initialize the window
    root = tdl.init(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
    con = tdl.Console(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    panel = tdl.Console(settings.SCREEN_WIDTH, settings.PANEL_HEIGHT)

    # create the player
    fighter_component = Fighter(hp=30, defense=2, power=5,death_function=player_death)
    glob.player = GameObject(randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),'player', '@', colors.white, blocks=True,fighter=fighter_component)

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