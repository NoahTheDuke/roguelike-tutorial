''' All AI-related classes '''

import math
import random
from random import randint

import colors
import global_vars as gv
from gui_util import message

class BasicMonster:
    '''AI for a basic monster.'''

    def take_turn(self):
        '''let the monster take a turn'''
        monster = self.owner
        if gv.game_map.fov[monster.x, monster.y]:
 
            #move towards player if far away
            if monster.distance_to(gv.player) >= 2:
                self.move_towards(gv.player)
 
            #close enough, attack! (if the player is still alive.)
            elif gv.player.hp > 0:
                monster.attack(gv.player)
    
    def move(self, dx, dy):
        ''' Move the monster, after checking if the target space is legitimate '''

        x,y = self.owner.x, self.owner.y
        if gv.game_map.walkable[x+dx,y+dy]:
            check = True
            for obj in gv.gameobjects:
                target = None
                if [obj.x,obj.y] == [x+dx,y+dy] and obj.blocks:  # check if there is something in the way
                    check = False
                    if obj.is_player:                         # if it's the player, target him
                        target = obj
                    break
            if check and target == None:
                self.owner.x += dx
                self.owner.y += dy

            # if blocking object is an enemy target
            elif not check and target:
                self.attack(target)
        
        self.blurb()

    def move_towards(self, target):
        ''' Move Gameobject towards intended target '''
        #vector from this object to the target, and distance
        dx = target.x - self.owner.x
        dy = target.y - self.owner.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)
    
    def blurb(self):
        ''' make some sounds '''
        if not self.owner.blurbs == None:
            if randint(0,100) > 75:
                message(random.choice(self.owner.blurbs),colors.lightest_grey)

class ConfusedMonster:
    '''AI for a confused monster'''
    def __init__(self, old_ai, num_turns=5):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0:  #still confused...
                #move in a random direction, and decrease the number of turns confused
                self.move()
                self.num_turns -= 1
    
        else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', colors.red)

    def move(self):
        ''' Confused monsters stumble around and attack randomly '''
        x,y = self.owner.x, self.owner.y
        dx,dy = randint(-1, 1), randint(-1, 1)
        if gv.game_map.walkable[x+dx,y+dy]:
            check = True
            for obj in gv.gameobjects:
                target = None
                if [obj.x,obj.y] == [x+dx,y+dy] and obj.blocks:  # check if there is something in the way
                    check = False
                    if obj in gv.actors:
                        target = obj
                    break
            if check and target == None:
                self.owner.x += dx
                self.owner.y += dy
                message('The ' + self.owner.name + ' stumbles around.', colors.white)

            # if blocking object is an enemy target
            elif not check and target:
                self.owner.attack(target)
        else:
            message('The ' + self.owner.name + ' bumbs into a wall.', colors.white)