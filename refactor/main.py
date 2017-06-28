#! python3
''' The main module for the roguelike tutorial roguelike '''

import tdl
import settings
import package.dungeon
from package.objects import GameObject

# Set custom font
tdl.set_font('arial10x10.png', greyscale=True, altLayout=True)

# initialize the window
ROOT = tdl.init(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
CON = tdl.Console(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

def handle_keys():
    ''' Handles all key input made by the player '''
 
    # turn-based
    user_input = tdl.event.key_wait()

    '''
    #realtime (delete line above)
    keypress = False
    for event in tdl.event.get():
        if event.type == 'KEYDOWN':
           user_input = event
           keypress = True
    if not keypress:
        return
    '''

    if user_input.key == 'ENTER' and user_input.alt:
        #Alt+Enter: toggle fullscreen
        tdl.set_fullscreen(not tdl.get_fullscreen())
    elif user_input.key == 'ESCAPE':
        return 'exit'  #exit game

    if game_state == 'playing':
        #movement keys
        if user_input.key in ['UP','KP8']:
            player_move_or_attack(0,-1)
    
        elif user_input.key in ['DOWN','KP2']:
            player_move_or_attack(0,1)
    
        elif user_input.key in ['LEFT','KP4']:
            player_move_or_attack(-1,0)
    
        elif user_input.key in ['RIGHT','KP6']:
            player_move_or_attack(1,0)

        elif user_input.key in ['KP9']:
            player_move_or_attack(1,-1)

        elif user_input.key in ['KP7']:
            player_move_or_attack(-1,-1)    

        elif user_input.key in ['KP1']:
            player_move_or_attack(-1,1)    

        elif user_input.key in ['KP3']:
            player_move_or_attack(1,1)           

        elif user_input.key in ['KP5']:
            player_move_or_attack(0,0)
            return 'pass'

        else:
            return 'pass'

def fov_recompute():
    ''' Recomputes the player's FOV '''
    global visible_tiles
    visible_tiles = tdl.map.quickFOV(player.x, player.y,
                                        is_visible_tile,
                                        fov=settings.FOV_ALGO,
                                        radius=settings.TORCH_RADIUS,
                                        lightWalls=settings.FOV_LIGHT_WALLS)

def is_visible_tile(x, y):
    ''' Determine whether a tile is visibile or not '''

    if x >= settings.MAP_WIDTH or x < 0:
        return False
    elif y >= settings.MAP_HEIGHT or y < 0:
        return False
    elif my_map[x][y].blocked == True:
        return False
    elif my_map[x][y].block_sight == True:
        return False
    else:
        return True

def is_blocked(x, y):
    '''first test the map tile'''
    if my_map[x][y].blocked:
        return True
 
    #now check for any blocking objects
    for obj in objects.gameobjects:
        if obj.blocks and obj.x == x and obj.y == y:
            return True
 
    return False

def main_loop():
    ''' begin main game loop '''
    global game_state, player_action
    game_state = 'playing'
    while not tdl.event.is_window_closed():
        render_all()
        tdl.flush()

        for obj in objects.gameobjects:
            obj.clear()
        player_action = handle_keys()
        if player_action == 'exit':
            break
        if game_state == 'playing' and player_action != 'pass':
            for obj in objects.gameobjects:
                if obj != player:
                    print('The ' + obj.name + ' growls!')

def initialize_game():
    ''' launches the game '''

    global player

    player = GameObject(randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),'player', '@', colors.white, blocks=True)
    #npc = GameObject(settings.SCREEN_WIDTH//2 - 5, settings.SCREEN_HEIGHT//2, 'H', (255,255,0))
    my_map = dungeon.make_map()
    fov_recompute()
    main_loop()

initialize_game()