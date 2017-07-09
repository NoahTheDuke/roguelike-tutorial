''' Code related to entitity creation '''
# TODO: split item-related code into own module

import settings
import colors
import global_vars as glob
import math
from random import randint
import random
from map_util import fov_recompute
from gui_util import message
from ai_util import BasicMonster
import item_use as iu

# TODO transform these into proper generatos

class GameObject:
    ''' Main class of game objects'''
    def __init__(self, x, y,  name,char, color, blocks=False, fighter=None, ai=None,item=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.blocks = blocks
        self.name = name
        self.is_running = False

        self.fighter = fighter #let the fighter component know who owns it
        if self.fighter: #By default fighter is None thus this check only passes if a value for fighter has been set
            self.fighter.owner = self
        
        self.ai = ai #let the AI component know who owns it
        if self.ai:  
            self.ai.owner = self
        
        self.item = item
        if self.item:  #let the Item component know who owns it
            self.item.owner = self
        
        glob.gameobjects.append(self)
    
    def move(self, dx, dy,running=False):
        ''' Move the object, after checking if the target space is legitimate '''

        running = running

        if glob.game_map.walkable[self.x+dx,self.y+dy]:
            check = True
            for obj in glob.gameobjects:
                target = None
                if [obj.x,obj.y] == [self.x+dx,self.y+dy] and obj.blocks:  # check if there is something in the way
                    check = False
                    if obj.fighter:                         # if it's a hostile entity, target it
                        target = obj
                    break
            if check and target == None:
                self.x += dx
                self.y += dy
                if not self.ai: #if player has moved, recalculate FOV | NOTE: This should be eventually moved elsewhere
                    fov_recompute()
                
                # if entity is running, re-call the move function once
                if (running):

                    self.move(dx,dy,running=False)
            
            # if blocking object is an enemy target
            elif not check and not target == None:
                if running:
                    message('You bump into the ' + target.name,colors.red)
                    self.is_running = False
                else:
                    self.fighter.attack(target)
            
        elif running: # if the player crashes into a wall
                message('You run into something.',colors.red)
                self.is_running = False
                self.fighter.take_damage(1)
        
        else:
            message('Something blocks your way.')
    
    def draw(self,con):
        ''' Draw the object '''
        con.draw_char(self.x, self.y, self.char, self.color)

    def clear(self,con):
        ''' Clear the object '''
        con.draw_char(self.x, self.y, ' ', self.color, bg=None)
    
    def move_towards(self, target):
        ''' Move Gameobject towards intended target '''
        #vector from this object to the target, and distance
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
 
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)
    
    def distance_to(self, other):
        '''return the distance to another object'''
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
    
    def send_to_back(self):
        '''make this object be drawn first, so all others appear above it if they're in the same tile.'''
        glob.gameobjects.remove(self)
        glob.gameobjects.insert(0, self)

class Fighter:
    ''' combat-related properties and methods (monster, glob.player, NPC) '''
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.max_defense = defense
        self.defense = defense
        self.max_power = power
        self.power = power
    def take_damage(self, damage):
        '''apply damage if possible'''
        if damage > 0:
            self.hp -= damage
        if self.hp <= 0:
            if self.death_function:
                self.death_function(self.owner)
    def attack(self, target):
        '''a simple formula for attack damage'''
        # TODO: Check for friendly fire
        damage = self.power - target.fighter.defense
        if damage > 0:
            #make the target take some damage
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    def modpwr(self, amount):
        self.power += amount
        if self.power == 1:
            self.power = 1
    def death(self):
        if not self.ai:
            message('You died!')

            #for added effect, transform the glob.player into a corpse!
            glob.player.char = '%'
            glob.player.color = colors.dark_red

            game_state = 'ended' # TODO game needs to stop processing inputs after this
        else:
            message(monster.name.capitalize() + ' is dead!')
            item_component = Item(iu.eat_corpse,monster.name)
            item = GameObject(monster.x,monster.y, (monster.name + ' corpse'), '%', colors.dark_red,item=item_component)
            glob.gameobjects.remove(monster)
            item.send_to_back()

class Item:
    '''an item that can be picked up and used.'''
    def __init__(self, use_function=None,param1=None,param2=None):
        self.use_function = use_function
        self.param1 = param1
        self.param2 = param2
    def pick_up(self):
        '''add to the glob.player's glob.inventory and remove from the map'''
        if len(glob.inventory) >= 26:
            message('Your glob.inventory is full, cannot pick up ' + self.owner.name + '.', colors.red)
        else:
            glob.inventory.append(self.owner)
            glob.gameobjects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', colors.green)
    def use(self):
        '''just call the "use_function" if it is defined'''
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function(p1=self.param1,p2=self.param2) != 'cancelled': #the use_function is called and unless it isn't cancelled, True is returned
                glob.inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason

    def drop(self):
        '''add to the map and remove from the glob.player's glob.inventory. also, place it at the glob.player's coordinates'''
        glob.gameobjects.append(self.owner)
        glob.inventory.remove(self.owner)
        self.owner.x = glob.player.x
        self.owner.y = glob.player.y
        message('You dropped a ' + self.owner.name + '.', colors.yellow)


def ran_room_pos(room):
    '''returns a random position within a room for an object'''
    for i in range(room.w*room.h):
        x = randint(room.x1+1, room.x2-1)
        y = randint(room.y1+1, room.y2-1)
        if glob.game_map.walkable[x,y]:
            break
    return [x,y]

def place_objects():
    ''' place objects in room '''
    print(len(glob.game_map.rooms))
    for room in glob.game_map.rooms:
        num_monsters = randint(0, settings.MAX_ROOM_MONSTERS)
        for i in range(num_monsters):
            #choose random spot for this monster
            x,y = ran_room_pos(room)    
            place_monster(x,y)
        
        num_items = randint(0, settings.MAX_ROOM_ITEMS)
        for i in range(num_items):
            #choose random spot for this item
            x,y = ran_room_pos(room)
            place_item(x,y)

def place_monster(x,y):
    '''creates a new monster at the given position'''
    
    monsters = {
        'orc1':(80,'Orc','o',colors.desaturated_green,(10, 0, 3),BasicMonster()),
        'orc2':(80,'Orc','o',colors.desaturated_green,(12, 0, 3),BasicMonster()),
        'troll1':(20,'Troll','T',colors.darkest_green,(16, 1, 4),BasicMonster())
    }

    m = random.choice(list(monsters.keys()))
    while (randint(0,100) > monsters[m][0]):
        m = random.choice(list(monsters.keys()))
    name,symbol,color,stats,ai = monsters[m][1], monsters[m][2], monsters[m][3],monsters[m][4],monsters[m][5]
    fighter_component = Fighter(stats[0],stats[1],stats[2])
    monster = GameObject(x,y,name,symbol,color,blocks=True,fighter=fighter_component,ai=ai)

def place_item(x,y):
    '''creates a new item at the given position'''

    items = {
        'p_pwr':(70,'healing potion','!',colors.violet,iu.cast_heal,10,None),
        'p_pwr':(50,'power potion','!',colors.red,iu.cast_powerup,1,None),
        'p_pwr_cur':(20,'power potion','!',colors.red,iu.cast_powerup,-1,None),    #cursed
        'scr_lightning':(30,'scroll of lightning bolt','#',colors.light_yellow,iu.cast_lightning,20,5),
        'scr_lightning_cur':(10,'scroll of lightning bolt','#',colors.light_yellow,iu.cast_lightning,8,0),  #cursed
        'scr_conf':(100,'scroll of confusion','#',colors.light_yellow,iu.cast_confusion,10,5)
    }

    i = random.choice(list(items.keys()))
    while (randint(0,100) > items[i][0]):
        i = random.choice(list(items.keys()))
    name,symbol,color,use_function,param1,param2 = items[i][1], items[i][2], items[i][3],items[i][4],items[i][5],items[i][6]
    item_component = Item(use_function=use_function,param1=param1,param2=param2)
    item = GameObject(x,y, name, symbol, color,item=item_component)
    item.send_to_back()  #items appear below other objects

# def monster_death(monster):
#     '''transform it into a nasty corpse! it doesn't block, can't be
#     attacked and doesn't move'''
#     message(monster.name.capitalize() + ' is dead!')
#     item_component = Item(iu.eat_corpse,monster.name)
#     item = GameObject(monster.x,monster.y, (monster.name + ' corpse'), '%', colors.dark_red,item=item_component)
#     glob.gameobjects.remove(monster)
#     item.send_to_back()