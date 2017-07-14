''' Code related to entitity creation '''
# TODO: split item-related code into own module

import math
from random import randint

import settings
import colors
import global_vars as gv
import item_use as iu
from gui_util import message
from render_util import fov_recompute
from target_util import look_at_ground

class GameObject:
    ''' Main class of game objects'''
    def __init__(self, x, y,name,char,color,blocks=False, item=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.blocks = blocks
        self.name = name
        self.is_item = item
        
        gv.gameobjects.append(self)

    def draw(self,con):
        ''' Draw the object '''
        con.draw_char(self.x, self.y, self.char, self.color)

    def clear(self,con):
        ''' Clear the object '''
        con.draw_char(self.x, self.y, ' ', self.color, bg=None)  
    def distance_to(self, other):
        '''return the distance to another object'''
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)
    def distance_to_coord(self, x, y):
        ''' return the distance to some coordinates '''
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2) 
    def send_to_back(self):
        '''make this object be drawn first, so all others appear above it if they're in the same tile.'''
        gv.gameobjects.remove(self)
        gv.gameobjects.insert(0, self)
    def send_to_front(self):
        gv.gameobjects.remove(self)
        gv.gameobjects.insert(len(gv.gameobjects), self)
    def delete(self):
        '''remove the object from the game'''
        if self in gv.gameobjects:
            gv.gameobjects.remove(self)
        if self in gv.actors:
            gv.actors.remove(self)
        del self

class Cursor(GameObject):
    '''cursor object '''
    def __init__(self, x, y):
        GameObject.__init__(self, x, y,'cursor',None,None)
        self.is_active = False

    def move (self,dx,dy):
        if gv.game_map.fov[self.x + dx,self.y + dy]:
            self.x += dx
            self.y += dy
            look_at_ground(self.x,self.y)
    
    def draw(self,con):
        ''' Draw the object '''
        if not self.color == None:
            con.draw_char(self.x, self.y, self.char,self.color)
    
    def activate(self,char,color):
        self.char = char
        self.color = color
        self.is_active = True
        self.x = gv.player.x
        self.y = gv.player.y
        self.send_to_front()
    
    def deactivate(self):
        self.color = None
        self.char = None
        self.is_active = False
        self.send_to_back()

class Fighter(GameObject):
    ''' combat-related properties and methods (monster, gv.player, NPC) '''
    def __init__(self, x, y,name,char,color,hp=10,pwr=5,df=2,blocks=False, ai=None):
        GameObject.__init__(self, x, y,name,char,color,blocks=True)
        self.hp, self.power, self.defense = hp, pwr, df
        self.max_hp = hp
        self.max_power = pwr
        self.max_defense = df
    
        self.ai = ai #let the AI component know who owns it
        if self.ai:  
            self.ai.owner = self
        
        gv.actors.append(self)

    def take_damage(self, damage):
        '''apply damage if possible'''
        if damage > 0:
            self.hp -= damage
        if self.hp <= 0:
            self.death()
    
    def attack(self, target):
        '''a simple formula for attack damage'''
        damage = self.power - target.defense
        if damage > 0:
            #make the target take some damage
            message(self.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.take_damage(damage)
        else:
            message(self.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
    
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
        message('The ' + self.name.capitalize() + ' is dead!',colors.green)
        item = Item(self.x,self.y, (self.name + ' corpse'), '%', colors.dark_red,iu.eat_corpse,self.name)
        item.send_to_back()
        for i in range(1,randint(1,5)):
            x,y = (randint(self.x-2, self.x+2),randint(self.y-2, self.y+2))
            if randint(0,100) < 40:
                item = Item(x,y,(self.name + ' bits'), '~', colors.darker_red,iu.eat_corpse,self.name)
                item.send_to_back()
            else:
                gv.game_map.gibbed[x][y] = True
        self.delete()

class Player(Fighter):
    ''' Class for the player object '''
    def __init__(self, x, y,name,char, color,hp=10,pwr=5,df=2):
        Fighter.__init__(self, x, y,name,char,color,hp=hp,pwr=pwr,df=df)
        self.is_running = False
        self.is_looking = False
        self.is_targeting = False
        self.is_active = True
        self.is_dead = False
      
    def move(self, dx, dy,running=False):
        ''' Move the player, after checking if the target space is legitimate'''

        running = running

        if gv.game_map.walkable[self.x+dx,self.y+dy]:
            check = True
            for obj in gv.gameobjects:
                target = None
                if [obj.x,obj.y] == [self.x+dx,self.y+dy] and obj.blocks:  # check if there is something in the way
                    check = False
                    if obj in gv.actors  and (not obj == gv.player):                         # if it's another actor, target it
                        target = obj
                    break
            if check and target == None:
                self.x += dx
                self.y += dy
                if not self.ai: #if player has moved, recalculate FOV | NOTE: This should be eventually moved elsewhere
                    fov_recompute()
                    look_at_ground(self.x,self.y)
                
                # if entity is running, re-call the move function once
                if (running):

                    self.move(dx,dy,running=False)
            
            # if blocking object is an enemy target
            elif not check and not target == None:
                if running:
                    message('You bump into the ' + target.name,colors.red)
                    self.is_running = False
                else:
                    self.attack(target)
            
        elif running: # if the player crashes into a wall
                message('You run into something.',colors.red)
                self.is_running = False
                self.take_damage(1)
        
        else:
            message('Something blocks your way.')
    
    def death(self):
        message('You died!')

        #for added effect, transform the gv.player into a corpse!
        gv.player.char = '%'
        gv.player.color = colors.dark_red
        for i in range(1,randint(1,5)):
            x,y = (randint(self.x-2, self.x+2),randint(self.y-2, self.y+2))
            if randint(0,100) < 40:
                item = Item(x,y,(self.name + ' bits'), '~', colors.darker_red,iu.eat_corpse,self.name)
                item.send_to_back()
            else:
                gv.game_map.gibbed[x][y] = True

        self.is_dead = True

class Item(GameObject):
    '''an item that can be picked up and used.'''
    def __init__(self, x, y,name,char, color, use_function=None,params=None):
        GameObject.__init__(self, x, y,name,char, color,blocks=False,item=True)
        self.use_function = use_function
        self.params = params
    def pick_up(self):
        '''add to the gv.player's gv.inventory and remove from the map'''
        if len(gv.inventory) >= 26:
            message('Your gv.inventory is full, cannot pick up ' + self.name + '.', colors.red)
        else:
            gv.inventory.append(self)
            gv.gameobjects.remove(self)
            message('You picked up a ' + self.name + '!', colors.green)
    def use(self):
        '''just call the "use_function" if it is defined'''
        if self.use_function is None:
            message('The ' + self.name + ' cannot be used.')
        else:
            if self.use_function(params = self.params) != 'cancelled': #the use_function is called and unless it isn't cancelled, True is returned
                gv.inventory.remove(self)  #destroy after use, unless it was cancelled for some reason

    def drop(self):
        '''add to the map and remove from the gv.player's gv.inventory. also, place it at the gv.player's coordinates'''
        gv.gameobjects.append(self)
        gv.inventory.remove(self)
        self.x = gv.player.x
        self.y = gv.player.y
        message('You dropped a ' + self.name + '.', colors.yellow)