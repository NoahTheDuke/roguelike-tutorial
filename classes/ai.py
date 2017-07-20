''' All AI-related classes '''

import tcod as libtcod
import math
import random
from random import randint

from classes.messages import Message

import colors
import settings
import global_vars as gv

class BasicMonster:
    '''AI for a basic monster.'''

    def take_turn(self):
        '''let the monster take a turn'''
        monster = self.owner
        if gv.game_map.visible[monster.x][monster.y]:
 
            #move towards player if far away
            if monster.distance_to(gv.player) >= 2:
                self.move_astar(gv.player)
 
            #close enough, attack! (if the player is still alive.)
            elif gv.player.hp > 0:
                monster.attack(gv.player)
            
            # 25% chance to produce a sound
            if randint(0,100) > 75:
                self.blurb()
    
    def move(self, dx, dy):
        ''' Move the monster, after checking if the target space is legitimate '''

        x,y = self.owner.x, self.owner.y
        if gv.game_map.walkable[x+dx][y+dy]:
            if sum([obj.x,obj.y] == [x+dx,y+dy] for obj in gv.actors)==0:
                self.owner.x += dx
                self.owner.y += dy

    def move_astar(self,target):
        '''A* pathfinding'''

        #Create a FOV map that has the dimensions of the map
        fov = libtcod.map_new(settings.MAP_WIDTH, settings.MAP_HEIGHT)
 
        #Scan the current map each turn and set all the walls as unwalkable
        for y1 in range(settings.MAP_HEIGHT):
            for x1 in range(settings.MAP_WIDTH):
                libtcod.map_set_properties(fov, x1, y1, gv.game_map.transparent[x1][y1], gv.game_map.walkable[x1][y1])
 
        #Scan all the objects to see if there are objects that must be navigated around
        #Check also that the object isn't self or the target (so that the start and the end points are free)
        #The AI class handles the situation if self is next to the target so it will not use this A* function anyway   
        for obj in gv.gameobjects:
            if obj.blocks and obj != self and obj != target:
                #Set the tile as a wall so it must be navigated around
                libtcod.map_set_properties(fov, obj.x, obj.y, True, False)
 
        #Allocate a A* path
        #The 1.41 is the normal diagonal cost of moving, it can be set as 0.0 if diagonal moves are prohibited
        my_path = libtcod.path_new_using_map(fov, 1.41)
 
        #Compute the path between self's coordinates and the target's coordinates
        libtcod.path_compute(my_path, self.owner.x, self.owner.y, target.x, target.y)
 
        #Check if the path exists, and in this case, also the path is shorter than 25 tiles
        #The path size matters if you want the monster to use alternative longer paths (for example through other rooms) if for example the player is in a corridor
        #It makes sense to keep path size relatively low to keep the monsters from running around the map if there's an alternative path really far away        
        if not libtcod.path_is_empty(my_path) and libtcod.path_size(my_path) < 25:
            #Find the next coordinates in the computed full path
            x, y = libtcod.path_walk(my_path, True)
            if x or y:
                #Set self's coordinates to the next path tile
                self.owner.x = x
                self.owner.y = y
        else:
            #Keep the old move function as a backup so that if there are no paths (for example another monster blocks a corridor)
            #it will still try to move towards the player (closer to the corridor opening)
            self.move_towards(target)  
 
        #Delete the path to free memory
        libtcod.path_delete(my_path)


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
            Message(random.choice(self.owner.blurbs),colors.desaturated_red)

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
            Message('The ' + self.owner.name + ' is no longer confused!', colors.red)

    def move(self):
        ''' Confused monsters stumble around and attack randomly '''
        x,y = self.owner.x, self.owner.y
        dx,dy = randint(-1, 1), randint(-1, 1)
        if gv.game_map.walkable[x+dx][y+dy]:
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
                Message('The ' + self.owner.name + ' stumbles around.', colors.white)

            # if blocking object is an enemy target
            elif not check and target:
                self.owner.attack(target)
        else:
            Message('The ' + self.owner.name + ' bumbs into a wall.', colors.white)