''' code related to item usage'''

from random import randint

import settings
import colors
import global_vars as gv

from gui.messages import Message
from gui.menus import menu

from target_util import target_tile
from classes.ai import ConfusedMonster


def cast_heal(params=0):
    '''heal the player'''
    hp = params
    if gv.player.hp == gv.player.max_hp:
        Message('You are already at full health.', colors.red)
        return 'cancelled'

    Message('Your wounds start to feel better!', colors.light_violet)
    gv.player.heal(hp)


def cast_powerup(params=0):
    '''modify characters power'''
    pwr = params
    if pwr:
        Message('Your power has been increased!', colors.light_violet)
    else:
        Message('The potion of power was cursed!', colors.light_violet)

    gv.player.modpwr(pwr)


def cast_lightning(params=(0, 0)):
    '''zap something'''
    pwr, spell_range = params
    #find closest enemy (inside a maximum range) and damage it
    if spell_range:
        monster = closest_monster(spell_range)

        if monster is None:  #no enemy found within maximum range
            Message('No enemy is close enough to strike.', colors.red)
            return 'cancelled'
    else:
        monster = gv.player
        Message('The scroll of lightning was cursed!', colors.light_violet)

    #zap it!
    Message('A lighting bolt strikes the {} with a loud thunder! The damage is {} hit points.'.format(
        monster.name, str(pwr)), colors.light_blue)
    monster.take_damage(pwr)


def cast_confusion(params=(6, 3)):
    '''find closest enemy in-range and confuse it'''  #TODO: Make confused monster attack random monsters
    dur, spell_range = params
    monster = None
    if spell_range:
        monster = closest_monster(spell_range)

        if monster is None:  #no enemy found within maximum range
            Message('No enemy is close enough to confuse.', colors.red)
            return 'cancelled'
        else:
            old_ai = monster.ai
            monster.ai = ConfusedMonster(old_ai, num_turns=dur)
            monster.ai.owner = monster  #tell the new component who owns it
            Message('The eyes of the {} look vacant, as he starts to stumble around!'.format(monster.name),
                    colors.light_green)
    else:
        Message('The scroll of confusion was cursed!')
        gv.player.confused = True  # Placeholder


def cast_fireball(params=(10, 3)):
    '''ask the player for a target tile to throw a fireball at'''
    pwr, radius = params
    target = target_tile()
    if target is None:
        Message('Your spell fizzles.')
    else:
        x, y = target
        check = True  # Choice is True by default, but can be set to False if the player decided not to hit him-/herself
        if gv.player.distance_to_coord(x, y) <= radius:
            check = menu('The spell would hit you as well. Proceed?', ['No', 'Yes'], 40)
        if check:
            Message('The fireball explodes, burning everything within {} tiles!'.format(str(radius)), colors.orange)
            for obj in gv.actors:  #damage every actor in range, including the player
                if obj.distance_to_coord(x, y) <= radius:
                    dmg = randint(pwr / 2, pwr)
                    Message('The {} gets burned for {} hit points.'.format(obj.name, str(dmg)), colors.orange)
                    obj.take_damage(dmg)
        else:
            Message('Your spell fizzles.')


def cast_magicmissile(params=(10, 3)):
    '''ask the player for a target tile to throw a magic missile at it'''
    pwr, radius = params
    target = target_tile()
    monster = next(obj for obj in gv.actors if (obj.x, obj.y) == target)
    if not monster:  # if no actor is at the selected location, the spell fails
        Message('There is no target at the position and your spell fizzles.')
    else:
        Message('Your magical projectile hits the {} for {} damage!'.format(
            monster.name, str(pwr)), colors.turquoise)
        monster.take_damage(pwr)


def eat_corpse(params=''):
    Message('You eat the corpse of a ' + params + '. It is disgusting!')


def closest_monster(max_range):
    '''find closest enemy, up to a maximum range, and in the gv.player's FOV'''
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range

    for obj in gv.actors:
        if gv.game_map.visible[obj.x][obj.y] and (not obj == gv.player):
            #calculate distance between this object and the gv.player
            dist = gv.player.distance_to(obj)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = obj
                closest_dist = dist
    return closest_enemy
