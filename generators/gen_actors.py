''' Generators for monster-type objects '''

import math
import random
from random import randint

import settings
import colors
import global_vars as gv

from classes.actors import Monster, Player
from classes.ai import BasicMonster


def gen_monsters():
    '''creates a new monster at the given position'''

    generators = {'orc': (80, gen_Orc), 'troll': (30, gen_Troll)}

    # loop through all rooms but the first one (the one the player starts in)
    for room in gv.game_map.rooms[1:]:
        for i in range(randint(1, settings.MAX_ROOM_MONSTERS)):  # place up as many monsters as the settings allow
            gen = random.choice(list(generators.keys()))  # Randomly pick a monster generator from the list
            while (randint(0, 100) > generators[gen][0]):
                gen = random.choice(list(generators.keys()))

            # Get a good position for the monster
            x, y = room.ranpos()
            i = 0
            while any([obj.x, obj.y] == [x, y] for obj in gv.actors):
                x, y = room.ranpos()
                i += 1  # WTF how do we escape this if it keeps climbing?
                if i == 0:
                    break

            # Place it
            m = generators[gen][1](x, y)


def gen_Player(x, y):
    name = 'Player'
    symbol = '@'
    color = colors.white
    hp = 30
    pwr = 5
    df = 2
    ent = Player(x, y, name, symbol, color, hp=hp, pwr=pwr, df=df)
    return ent


def gen_Orc(x, y):
    ''' generic orc'''

    name = 'Orc'
    descr = 'An Orc.'
    ent = Monster(
        x,
        y,
        name,
        'o',
        (0, randint(171, 191), 0),
        hp=randint(10, 12),
        pwr=3,
        df=0,
        ai=BasicMonster(),
        blurbs=(('The {} growls.'.format(name)),
                ('The {} screeches!'.format(name)),
                ('The {} screams in a strange language.'.format(name))),
        descr=descr)
    return ent


def gen_Troll(x, y):
    ''' generic Troll'''

    name = 'Troll'
    descr = 'A Troll, it is big.'
    ent = Monster(
        x,
        y,
        name,
        'T',
        (0, randint(70, 85), 0),
        hp=randint(16, 20),
        pwr=4,
        df=1,
        ai=BasicMonster(),
        blurbs=(('The {} stares at you.'.format(name)),
                ('The {} licks his lips.'.format(name))),
        descr=descr)
    return ent
