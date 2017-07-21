''' Generators for monster-type objects '''

import math
import random
from random import randint

import settings
import colors
import global_vars as gv

from classes.actors import Monster,Player
from classes.ai import BasicMonster

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
        x,y = room.ranpos()
        i = 0
        while sum([obj.x,obj.y] == [x,y] for obj in gv.actors) > 0:
            x,y = room.ranpos()
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
    ''' generic orc'''

    name = 'Orc'
    ent = Monster (
        x,y,
        name,
        'o',
        (0,randint(171,191),0),
        hp = randint(10,12),
        pwr = 3,
        df = 0,
        ai = BasicMonster(),
        blurbs = (
            ('The ' + name + ' growls.'),
            ('The ' + name + ' screeches!'),
            ('The ' + name + ' screams in a strange language.')
        )
    )
    return ent

def gen_Troll(x,y):
    ''' generic Troll'''

    name = 'Troll'
    ent = Monster (
        x,y,
        name,
        'T',
        (0,randint(70,85),0),
        hp = randint(16,20),
        pwr = 4,
        df = 1,
        ai = BasicMonster(),
        blurbs = (
            ('The ' + name + ' stares at you.'),
            ('The ' + name + ' licks his lips.')
        )
    )
    return ent