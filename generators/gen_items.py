''' Generators for item-type objects '''

import math
import random
from random import randint

import settings
import colors
import global_vars as gv

import item_use as iu
from entities import Item
from map_util import ran_room_pos

def gen_items():
    '''creates a new item at the given position'''
    
    generators = {
        'p_heal':(70,gen_P_Heal),
        'p_pwr':(50,gen_P_Power),
        'scr_frb':(30,gen_Scr_Frb)
        # 'scr_lightning':(30,'scroll of lightning bolt','#',colors.light_yellow,iu.cast_lightning,20,5),
        # 'scr_lightning_cur':(10,'scroll of lightning bolt','#',colors.light_yellow,iu.cast_lightning,8,0),  #cursed
        # 'scr_conf':(30,'scroll of confusion','#',colors.light_yellow,iu.cast_confusion,10,8),
        # 'scr_conf_cur':(10,'scroll of confusion','#',colors.light_yellow,iu.cast_confusion,0,3),
        # 'scr_frb':(100,'scroll of fireball','#',colors.light_yellow,iu.cast_fireball,10,10)
    }

    # Randomly pick an item from the list
    for room in gv.game_map.rooms:
        gen = random.choice(list(generators.keys()))
        while (randint(0,100) > generators[gen][0]):
            gen = random.choice(list(generators.keys()))
    
        # Get a good position for the item
        x,y = ran_room_pos(room)
        i = 0
        while not gv.game_map.walkable[x,y]:
            x,y = ran_room_pos(room)
            i += 1
            if i == 0:
                break
        # Place it  
        i = generators[gen][1](x,y)

def gen_inventory():
    ''' creates an initial inventory (PLACEHOLDER) '''
    i = gen_P_Heal(0,0)
    i.pick_up()

# Potions

def gen_P_Heal(x,y):
    ''' basic healing potion '''

    name = 'healing potion'
    symbol = '!'
    color = colors.violet
    pwr = randint(6,10)
    on_use = iu.cast_heal

    i = Item(x,y, name, symbol, color,use_function=on_use,params=pwr)
    i.send_to_back()
    return i

def gen_P_Power(x,y):
    ''' basic power potion - can be cursed '''

    name = 'potion of power'
    symbol = '!'
    color = colors.red
    if randint(0,100) > 20: 
        pwr = 1
    else:   # 20% chance of being cursed
        pwr = -1
    on_use = iu.cast_powerup

    i = Item(x,y, name, symbol, color,use_function=on_use,params=pwr)
    i.send_to_back()
    return i

# Scrolls

def gen_Scr_Frb(x,y):
    break