''' Actor-related classes '''

import math
from random import randint

import settings
import colors
import global_vars as gv


from gui.messages import Message,msgbox
from gui.render_main import RenderOrder

from classes.objects import GameObject

from generators.gen_items import gen_Corpse,gen_Corpsebits

import item_use as iu
from game_states import GameStates

class Fighter(GameObject):
    ''' combat-related properties and methods (monster, gv.player, NPC) '''
    def __init__(self, x, y,name,char,color,hp=10,pwr=5,df=2,inventory=[],blocks=False):
        super().__init__(x, y,name,char,color,blocks=True,render_order=RenderOrder.ACTOR)
        self.hp, self.power, self.defense = hp, pwr, df
        self.max_hp = hp
        self.max_power = pwr
        self.max_defense = df
        
        self.inventory = inventory
        
        self.description = 'It is you.'
    
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
            Message(self.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.',log=gv.combat_log)
            target.take_damage(damage)
        else:
            Message(self.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!',log=gv.combat_log)
    
    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    
    def modpwr(self, amount):
        self.power += amount
        if self.power == 1:
            self.power = 1

    def get_health_as_string_and_color(self):
        ''' returns the actor's hp as a tuple containing a descriptive string and an associated color'''

        percentage = self.hp/self.max_hp * 100
        if 86 <= percentage <= 100:
            return ('healthy',colors.dark_green)
        elif 71 <= percentage <= 85:
            return ('scratched',colors.light_green)
        elif 25 <= percentage <= 70:
            return  ('wounded',colors.light_red)
        else:
            return ('nearly dead',colors.dark_red)

    def death(self):
        ''' Generic death for all actors '''
        Message('The ' + self.name.capitalize() + ' is dead!',log=gv.combat_log,color=colors.green)
        x,y = (self.x,self.y)
        item = gen_Corpse(x,y,self)
        #item = Useable(self.x,self.y, (self.name + ' corpse'), '%', colors.dark_red,use_function=iu.eat_corpse,params=self.name)
        gv.game_map.gibbed[x][y] = True # Set the tile to 'gibbed' (will be rendered red)
        for i in range(1,randint(3,5)):
            x,y = (randint(x-1,x+1),randint(y-1,y+1))
            gv.game_map.gibbed[x][y] = True
        for i in range(1,randint(1,3)):
            x,y = (randint(x-2,x+2),randint(y-2,y+2))
            if randint(0,100) < 40:
                item = gen_Corpsebits(x,y,self)
                #item = Useable(x,y,(self.name + ' bits'), '~', colors.darker_red,use_function=iu.eat_corpse,params=self.name)
        self.delete()

class Monster(Fighter):
    ''' base-class for all hostile mobs '''
    def __init__(self, x, y,name,char, color,hp=10,pwr=5,df=2,ai=None,blurbs=None,descr = None):
        super().__init__(x, y,name,char,color,hp=hp,pwr=pwr,df=df)

        self.blurbs = blurbs

        self.description = descr

        self.ai = ai
        if self.ai: #let the AI component know who owns it
            self.ai.owner = self

class Player(Fighter):
    ''' Class for the player object '''
    def __init__(self, x, y,name,char, color,hp=10,pwr=5,df=2):
        super().__init__(x, y,name,char,color,hp=hp,pwr=pwr,df=df)
        self.is_running = False
        self.is_dead = False
      
    def move(self, dx, dy,running=False):
        ''' Move the player, after checking if the target space is legitimate'''

        running = running

        if gv.game_map.walkable[self.x+dx][self.y+dy]:
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
                
                # if entity is running, re-call the move function once
                if (running):

                    self.move(dx,dy,running=False)
            
            # if blocking object is an enemy target
            elif not check and not target == None:
                if running:
                    Message('You bump into the ' + target.name,colors.red)
                    self.is_running = False
                else:
                    self.attack(target)
            
        elif running: # if the player crashes into a wall
                Message('You run into something.',colors.red)
                self.is_running = False
                self.take_damage(1)
        
        else:
            Message('Something blocks your way.')
    
    def death(self):
        '''specific player death function'''
        msgbox('You died!',width=10,text_color=colors.red)

        #for added effect, transform the gv.player into a corpse!
        gv.player.char = '%'
        gv.player.color = colors.dark_red
        for i in range(1,randint(1,5)):
            x,y = (randint(self.x-2, self.x+2),randint(self.y-2, self.y+2))
            if randint(0,100) < 40:
                item = gen_Corpsebits(x,y,self)
            else:
                gv.game_map.gibbed[x][y] = True

        gv.gamestate = GameStates.PLAYER_DEAD