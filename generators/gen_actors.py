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
        'goblin':(80,gen_Goblin),
        'orc':(80,gen_Orc),
        'troll':(30,gen_Troll)
    }

    # loop through all rooms but the first one (the one the player starts in)
    for room in gv.game_map.rooms[1:]:
        for i in range(randint(1,settings.MAX_ROOM_MONSTERS)): # place up as many monsters as the settings allow
            gen = random.choice(list(generators.keys())) # Randomly pick a monster generator from the list
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
    descr = 'The most generic of monsters you could imagine. Thankfully, it will probably kill you before you become bored to death.'
    ent = Monster (
        x,y,
        name,
        'o',
        (0,randint(171,191),0),
        hp = randint(10,12),
        pwr = 3,
        df = 0,
        ai = BasicMonster(),
        barks = (
            ('The ' + name + ' growls.'),
            ('The ' + name + ' screeches!'),
            ('The ' + name + ' screams in a strange language.')
        ),
        descr = descr
    )
    return ent

def gen_Troll(x,y):
    ''' generic Troll'''

    name = 'Troll'
    descr = 'There are many different and imaginative interpretations of what a Troll could look like. This is not one of them. It is big, ugly and strong.'
    ent = Monster (
        x,y,
        name,
        'T',
        (0,randint(70,85),0),
        hp = randint(16,20),
        pwr = 4,
        df = 1,
        ai = BasicMonster(),
        barks = (
            ('The ' + name + ' stares at you.'),
            ('The ' + name + ' licks his lips.')
        ),
        descr = descr
    )
    return ent

def gen_Goblin(x,y):
    ''' generic Troll'''

    name = 'Goblin'
    descr = 'The Goblin is just as generic as an orc but smaller.'
    ent = Monster (
        x,y,
        name,
        'g',
        colors.lighter_green,
        hp = randint(6,8),
        pwr = 1,
        df = 0,
        ai = BasicMonster(),
        barks = (
            ('The {0} is visibly agitated'.format(name)),
            ('The {0} does a generic thing.'.format(name))
        ),
        descr = descr
    )
    return ent