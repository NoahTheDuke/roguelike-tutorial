''' code related to item usage'''

from random import randint

import settings
import colors
import global_vars as gv

from gui_util import message, menu
from target_util import target_tile
from classes.ai import ConfusedMonster

def cast_heal(params=0):
    '''heal the player'''
    hp = params
    if gv.player.hp == gv.player.max_hp:
        message('You are already at full health.', colors.red)
        return 'cancelled'

    message('Your wounds start to feel better!', colors.light_violet)
    gv.player.heal(hp)

def cast_powerup(params=0):
    '''modify characters power'''
    pwr = params
    if (pwr > 0):
        message('Your power has been increased!', colors.light_violet)
    else:
        message('The potion of power was cursed!', colors.light_violet)

    gv.player.modpwr(pwr)

def cast_lightning(params=(0,0)):
    '''zap something'''
    pwr,range = params
    #find closest enemy (inside a maximum range) and damage it
    if range == 0:
        monster = gv.player
        message('The scroll of lightning was cursed!', colors.light_violet)
    else:
        monster = closest_monster(range)

    if monster is None:  #no enemy found within maximum range
        message('No enemy is close enough to strike.', colors.red)
        return 'cancelled'

    #zap it!
    message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
        + str(pwr) + ' hit points.', colors.light_blue)
    monster.take_damage(pwr)

def cast_confusion(params = (6,3)):
    '''find closest enemy in-range and confuse it''' #TODO: Make confused monster attack random monsters
    dur,range = params
    monster = None
    if (range > 0):
        monster = closest_monster(range)

        if monster is None:  #no enemy found within maximum range
            message('No enemy is close enough to confuse.', colors.red)
            return 'cancelled'
        else:
            old_ai = monster.ai
            monster.ai = ConfusedMonster(old_ai,num_turns=dur)
            monster.ai.owner = monster  #tell the new component who owns it
            message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', colors.light_green)
    else:
        message('The scroll of confusion was cursed!')
        gv.player.confused = True # Placeholder    
    

def cast_fireball(params = (10,3)):
    '''ask the player for a target tile to throw a fireball at'''
    pwr,radius = params
    target = target_tile()
    if target is None:
        message('Your spell fizzles.')
    else:
        x,y = target
        check = True # Choice is True by default, but can be set to False if the player decided not to hit him-/herself
        if gv.player.distance_to_coord(x,y) <= radius:
            check = menu('The spell would hit you as well. Proceed?',['No','Yes'],24)
        if check:
            message('The fireball explodes, burning everything within ' + str(radius) + ' tiles!', colors.orange)
            for obj in gv.actors:  #damage every actor in range, including the player
                if obj.distance_to_coord(x, y) <= radius:
                    dmg = randint(pwr/2,pwr)
                    message('The ' + obj.name + ' gets burned for ' + str(dmg) + ' hit points.', colors.orange)
                    obj.take_damage(dmg)
        else:
            message('Your spell fizzles.')

def cast_magicmissile(params = (10,3)):
    '''ask the player for a target tile to throw a magic missile at it'''
    pwr,radius = params
    target = target_tile()
    monster = [obj for obj in gv.actors if (obj.x,obj.y) == target]
    if len(monster) == 0: # if no actor is at the selected location, the spell fails
        message('There is no target at the position and your spell fizzles.')
    else: 
        message('Your magical projectile hits the ' + monster[0].name + ' for ' + str(pwr) + ' damage!', colors.turquoise)
        monster[0].take_damage(pwr)

def eat_corpse(params = ''):
    message('You eat the corpse of a ' + params + '. It is disgusting!')

def closest_monster(max_range):
    '''find closest enemy, up to a maximum range, and in the gv.player's FOV'''
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
    for obj in gv.actors:
        if gv.game_map.visible[x][y] and (not obj == gv.player):
            #calculate distance between this object and the gv.player
            dist = gv.player.distance_to(obj)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = obj
                closest_dist = dist
    return closest_enemy