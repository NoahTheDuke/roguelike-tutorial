''' Generators for monster-type objects '''

import math
import random
from random import randint

import settings
import colors
import global_vars as gv

from classes.actors import Fighter,Player
from classes.ai import BasicMonster
from map_util import ran_room_pos

def gen_monsters():
    '''creates a new monster at the given position'''
    
    generators = {
        'orc':(80,gen_Orc),
        'troll':(30,gen_Troll)
    }

    # Randomly pick a monster from the list
    for room in gv.game_map.rooms:
        gen = random.choice(list(generators.keys()))
        while (randint(0,100) > generators[gen][0]):
            gen = random.choice(list(generators.keys()))
    
        # Get a good position for the monster
        x,y = ran_room_pos(room)
        i = 0
        while not gv.game_map.walkable[x,y] or sum([obj.x,obj.y] == [x,y] for obj in gv.actors) > 0:
            x,y = ran_room_pos(room)
            i += 1
            if i == 0:
                break
        
        # Place it
        m = generators[gen][1](x,y)

def gen_Player(x,y):
    name='Player'
    symbol = '@'
    color = colors.white
    hp = 30
    pwr = 5
    df = 2
    ent = Player(x,y,name,symbol,color,hp=hp,pwr=pwr,df=df)
    return ent

def gen_Orc(x,y):
    name='Orc'
    symbol = 'o'
    color = colors.desaturated_green
    hp = randint(10,12)
    pwr = 3
    df = 0
    ai = BasicMonster()
    ent = Fighter(x,y,name,symbol,color,hp=hp,pwr=pwr,df=df,ai=ai)
    return ent

def gen_Troll(x,y):
    name='Troll'
    symbol = 'T'
    color = colors.darkest_green
    hp = randint(16,20)
    pwr = 4
    df = 1
    ai = BasicMonster()
    ent = Fighter(x,y,name,symbol,color,hp=hp,pwr=pwr,df=df,ai=ai)
    return ent