''' code related to item usage'''

#from main import message
import settings
import colors
import global_vars as glob
from gui_util import message
from ai_util import ConfusedMonster

def cast_heal(p1=0,p2=None,**kwargs):
    '''heal the player'''
    hp = p1
    range = p2
    if range == None:
        if glob.player.hp == glob.player.max_hp:
            message('You are already at full health.', colors.red)
            return 'cancelled'

        message('Your wounds start to feel better!', colors.light_violet)
        glob.player.heal(hp)

def cast_powerup(p1=0,**kwargs):
    '''modify characters power'''
    pwr = p1
    if (pwr > 0):
        message('Your power has been increased!', colors.light_violet)
    else:
        message('The potion of power was cursed!', colors.light_violet)

    glob.player.modpwr(pwr)

def cast_lightning(p1=0,p2=0):
    '''zap something'''
    pwr = p1
    range = p2
    #find closest enemy (inside a maximum range) and damage it
    if range == 0:
        monster = glob.player
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

def cast_confusion(p1=5,p2=10,**kwargs):
    '''find closest enemy in-range and confuse it''' #TODO: Make confused monster attack random monsters
    range = p1
    dur = p2
    monster = closest_monster(range)
    if monster is None:  #no enemy found within maximum range
        message('No enemy is close enough to confuse.', colors.red)
        return 'cancelled'
    else:
        old_ai = monster.ai
        monster.ai = ConfusedMonster(old_ai,num_turns=dur)
        monster.ai.owner = monster  #tell the new component who owns it
        message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', colors.light_green)

def eat_corpse(p1='',**kwargs):
    message('You eat the corpse of a ' + p1 + '. It is disgusting!')

def closest_monster(max_range):
    '''find closest enemy, up to a maximum range, and in the glob.player's FOV'''
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
    for obj in glob.actors:
        if not obj.is_player and glob.game_map.fov[obj.x, obj.y]:
            #calculate distance between this object and the glob.player
            dist = glob.player.distance_to(obj)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = obj
                closest_dist = dist
    return closest_enemy