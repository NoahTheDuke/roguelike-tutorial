#! python3
''' A simple roguelike based on an online tutorial '''

import tdl
from random import randint
import colors
import settings
import global_vars as glob
import math
import random
import textwrap
from keyhandler import handle_keys
from entities import GameObject, Fighter, BasicMonster, Item
from map_util import GameMap,make_map, fov_recompute
from gui_util import render_all, inventory_menu, message
import item_use as iu

def ran_room_pos(room):
    '''returns a random position within a room for an object'''
    for i in range(room.w*room.h):
        x = randint(room.x1+1, room.x2-1)
        y = randint(room.y1+1, room.y2-1)
        if glob.game_map.walkable[x,y]:
            break
    return [x,y]

def place_objects():
    ''' place objects in room '''
    print(len(glob.game_map.rooms))
    for room in glob.game_map.rooms:
        num_monsters = randint(0, settings.MAX_ROOM_MONSTERS)
        for i in range(num_monsters):
            #choose random spot for this monster
            x,y = ran_room_pos(room)    
            place_monster(x,y)
        
        num_items = randint(0, settings.MAX_ROOM_ITEMS)
        for i in range(num_items):
            #choose random spot for this item
            x,y = ran_room_pos(room)
            place_item(x,y)

def place_monster(x,y):
    '''creates a new monster at the given position'''
    # list of possible monsters
    # index:(chance,name,symbol,color,fighter values(tuple),AI class)
    monsters = {
            'orc1':(80,'Orc','o',colors.desaturated_green,(10, 0, 3,monster_death),BasicMonster()),
            'orc2':(80,'Orc','o',colors.desaturated_green,(12, 0, 3,monster_death),BasicMonster()),
            'troll1':(20,'Troll','T',colors.darkest_green,(16, 1, 4,monster_death),BasicMonster())
        }
    m = random.choice(list(monsters.keys()))
    while (randint(0,100) > monsters[m][0]):
        m = random.choice(list(monsters.keys()))
    name,symbol,color,stats,ai = monsters[m][1], monsters[m][2], monsters[m][3],monsters[m][4],monsters[m][5]
    fighter_component = Fighter(stats[0],stats[1],stats[2],stats[3])
    monster = GameObject(x,y,name,symbol,color,blocks=True,fighter=fighter_component,ai=ai)

def place_item(x,y):
    '''creates a new item at the given position'''
    # list of possible items
    # index:(chance,name,symbol,color,use_function(can be empty),param1,param2)
    items = {
        'heal1':(70,'healing potion','!',colors.violet,iu.cast_heal,10,None),
        'power1':(50,'power potion','!',colors.red,iu.cast_powerup,1,None),
        'power2':(20,'power potion','!',colors.red,iu.cast_powerup,-1,None),    #cursed
        'scroll1':(30,'scroll of lightning bolt','#',colors.light_yellow,iu.cast_lightning,20,5),
        'scroll2':(10,'scroll of lightning bolt','#',colors.light_yellow,iu.cast_lightning,8,0)  #cursed
    }
    i = random.choice(list(items.keys()))
    while (randint(0,100) > items[i][0]):
        i = random.choice(list(items.keys()))
    name,symbol,color,use_function,param1,param2 = items[i][1], items[i][2], items[i][3],items[i][4],items[i][5],items[i][6]
    item_component = Item(use_function=use_function,param1=param1,param2=param2)
    item = GameObject(x,y, name, symbol, color,item=item_component)
    item.send_to_back()  #items appear below other objects


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
 
def monster_death(monster):
    '''transform it into a nasty corpse! it doesn't block, can't be
    attacked and doesn't move'''
    message(monster.name.capitalize() + ' is dead!')
    item_component = Item(iu.eat_corpse,monster.name)
    item = GameObject(monster.x,monster.y, (monster.name + ' corpse'), '%', colors.dark_red,item=item_component)
    glob.gameobjects.remove(monster)
    item.send_to_back()
    
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