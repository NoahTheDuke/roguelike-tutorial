import settings
import colors
import global_vars as gv
import math
from random import randint
import random
from gui_util import message
import item_use as iu
from entities import GameObject,Fighter,Item
from ai_util import BasicMonster

def ran_room_pos(room):
    '''returns a random position within a room for an object'''
    for i in range(room.w*room.h):
        check = True
        while check:
            x = randint(room.x1+1, room.x2-1)
            y = randint(room.y1+1, room.y2-1)
            if gv.game_map.walkable[x,y]:
                #count = lambda obj,x,y : [obj.x,obj.y] == [x,y]
                if sum([obj.x,obj.y] == [x,y] for obj in gv.actors) <= 0:
                    check = False
                    break
    return [x,y]

def place_objects():
    ''' place objects in room '''
    for room in gv.game_map.rooms:
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
    
    monsters = {
        'orc1':(80,'Orc','o',colors.desaturated_green,(10, 0, 3),BasicMonster()),
        'orc2':(80,'Orc','o',colors.desaturated_green,(12, 0, 3),BasicMonster()),
        'troll1':(20,'Troll','T',colors.darkest_green,(16, 1, 4),BasicMonster())
    }

    m = random.choice(list(monsters.keys()))
    while (randint(0,100) > monsters[m][0]):
        m = random.choice(list(monsters.keys()))
    name,symbol,color,stats,ai = monsters[m][1], monsters[m][2], monsters[m][3],monsters[m][4],monsters[m][5] 
    monster = Fighter(x,y,name,symbol,color,stats=(stats[0],stats[1],stats[2]),blocks=True,ai=ai)

def place_item(x,y):
    '''creates a new item at the given position'''

    items = {
        # 'p_heal':(70,'healing potion','!',colors.violet,iu.cast_heal,10,None),
        # 'p_pwr':(50,'power potion','!',colors.red,iu.cast_powerup,1,None),
        # 'p_pwr_cur':(20,'power potion','!',colors.red,iu.cast_powerup,-1,None),    #cursed
        #'scr_lightning':(30,'scroll of lightning bolt','#',colors.light_yellow,iu.cast_lightning,20,5),
        #'scr_lightning_cur':(10,'scroll of lightning bolt','#',colors.light_yellow,iu.cast_lightning,8,0),  #cursed
        #'scr_conf':(30,'scroll of confusion','#',colors.light_yellow,iu.cast_confusion,10,8),
        #'scr_conf_cur':(10,'scroll of confusion','#',colors.light_yellow,iu.cast_confusion,0,3),
        'scr_frb':(100,'scroll of fireball','#',colors.light_yellow,iu.cast_fireball,10,10)
    }

    i = random.choice(list(items.keys()))
    while (randint(0,100) > items[i][0]):
        i = random.choice(list(items.keys()))
    name,symbol,color,use_function,param1,param2 = items[i][1], items[i][2], items[i][3],items[i][4],items[i][5],items[i][6]
    item = Item(x,y, name, symbol, color,use_function=use_function,param1=param1,param2=param2)
    item.send_to_back()  #items appear below other objects