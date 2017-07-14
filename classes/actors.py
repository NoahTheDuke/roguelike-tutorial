''' Actor-related classes '''
# TODO: split item-related code into own module

import math
from random import randint

import settings
import colors
import global_vars as gv

import item_use as iu
from gui_util import message
from render_util import fov_recompute

from classes.objects import GameObject
from classes.items import Item

class Fighter(GameObject):
    ''' combat-related properties and methods (monster, gv.player, NPC) '''
    def __init__(self, x, y,name,char,color,hp=10,pwr=5,df=2,blocks=False):
        super().__init__(x, y,name,char,color,blocks=True)
        self.hp, self.power, self.defense = hp, pwr, df
        self.max_hp = hp
        self.max_power = pwr
        self.max_defense = df
    
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

class Monster(Fighter):
    ''' base-class for all hostile mobs '''
    def __init__(self, x, y,name,char, color,hp=10,pwr=5,df=2,ai=None,blurbs=None):
        super().__init__(x, y,name,char,color,hp=hp,pwr=pwr,df=df)

        self.blurbs = blurbs
        self.ai = ai
        if self.ai: #let the AI component know who owns it
            self.ai.owner = self

    def death(self):
        ''' death for monster characters '''
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
        super().__init__(x, y,name,char,color,hp=hp,pwr=pwr,df=df)
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