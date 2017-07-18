''' Generators for item-type objects '''

import math
import random
from random import randint

import settings
import colors
import global_vars as gv

import item_use as iu
from classes.items import Useable,Equipment

# Constants for item generation
CHAR_POTION = '!'
CHAR_SCROLL = '='

COLOR_SCROLL = colors.light_yellow

def gen_items():
    '''creates a new item at the given position'''
    
    generators = {
        'p_heal':(70,gen_P_Heal),
        'p_pwr':(50,gen_P_Power),
        'scr_frb':(30,gen_Scr_Frb),
        'scr_ltng':(30,gen_Scr_Ltng),
        'scr_conf':(30,gen_Scr_Conf),
        'scr_mm': (30,gen_Scr_Mami)
    }

    # Randomly pick an item from the list
    for room in gv.game_map.rooms:
        gen = random.choice(list(generators.keys()))
        while (randint(0,100) > generators[gen][0]):
            gen = random.choice(list(generators.keys()))
    
        # Get a good position for the item
        x,y = room.ranpos()

        # Place it  
        i = generators[gen][1](x,y)

def gen_inventory():
    ''' creates an initial inventory (PLACEHOLDER) '''
    gen_P_Heal(0,0).pick_up()
    gen_Scr_Mami(0,0).pick_up()
    gen_Scr_Frb(0,0).pick_up()

#    ____       _   _                 
#  |  _ \ ___ | |_(_) ___  _ __  ___ 
#  | |_) / _ \| __| |/ _ \| '_ \/ __|
#  |  __/ (_) | |_| | (_) | | | \__ \
#  |_|   \___/ \__|_|\___/|_| |_|___/
                                    
def gen_P_Heal(x,y):
    ''' basic healing potion '''

    name = 'healing potion'
    pwr = randint(6,10)
    descr = 'This potion will heal you for a small amount.'

    i = Useable(
        x,y,
        name,
        CHAR_POTION,
        colors.violet,
        description = descr,
        use_function=iu.cast_heal,
        params= pwr
    )
    return i

def gen_P_Power(x,y):
    ''' basic power potion - can be cursed '''

    name = 'potion of power'
    descr = 'A potion of power will heighten your strength.'

    if randint(0,100) > 20: 
        pwr = 1
    else:   # 20% chance of being cursed
        pwr = -1

    i = Useable(
        x,y,
        name,
        CHAR_POTION,
        colors.red,
        description = descr,
        use_function=iu.cast_powerup,
        params=pwr
    )
    return i

#   ____                 _ _     
#  / ___|  ___ _ __ ___ | | |___ 
#  \___ \ / __| '__/ _ \| | / __|
#   ___) | (__| | | (_) | | \__ \
#  |____/ \___|_|  \___/|_|_|___/
                               
def gen_Scr_Ltng(x,y):
    name = 'scroll of lightning bolt'
    descr = 'A scroll of lightning bolt. It will strike one of the nearest enemies.'
    pwr = randint(8,10)
    range = 3
    i = Useable(
        x,y,
        name,
        CHAR_SCROLL,
        COLOR_SCROLL,
        description = descr,
        use_function=iu.cast_lightning,
        params=(pwr,range) # power/radius
    )
    return i

def gen_Scr_Frb(x,y):
    name = 'scroll of fireball'
    pwr = 12
    range = 3
    i = Useable(
        x,y,
        name,
        CHAR_SCROLL,
        COLOR_SCROLL,
        description = 'A scroll of fireball. It will burn anything in a small radius.',
        use_function=iu.cast_fireball,
        params=(pwr,range) # power/radius
    )
    return i

def gen_Scr_Conf(x,y):
    name = 'scroll of confusion'
    pwr = randint(4,6)
    if randint(0,100) > 85: # 15% chance to be cursed
        range = -1
    else:
        range = 3
    i = Useable(
        x,y,
        name,
        CHAR_SCROLL,
        COLOR_SCROLL,
        description = 'A scroll of confusion. It will turn a foes brain into mush temporarily.',
        use_function=iu.cast_confusion,
        params=(pwr,range) # power/radius
    )
    return i

def gen_Scr_Mami(x,y):
    name = 'scroll of magic missile'
    pwr = randint(4,8)
    range = 6
    i = Useable(
        x,y,
        name,
        CHAR_SCROLL,
        COLOR_SCROLL,
        description = 'A scroll of magic missile. Inflicts direct damage on a single enemy.',
        use_function=iu.cast_magicmissile,
        params=(pwr,range) # power/radius
    )
    return i