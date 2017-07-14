''' Code related to entitity creation '''
# TODO: split item-related code into own module

import math
from random import randint

import settings
import colors
import global_vars as gv

import item_use as iu
from classes.objects import GameObject
from gui_util import message

class Item(GameObject):
    '''an item that can be picked up and used.'''
    def __init__(self, x, y,name,char, color,description=None):
        super().__init__(x, y,name,char, color,blocks=False,item=True)
        
        self.description = description
        if description == None:
            print(str(self) + ' lacks a description!')
    
    def pick_up(self):
        '''add to the gv.player's gv.inventory and remove from the map'''
        if len(gv.inventory) >= 26:
            message('Your gv.inventory is full, cannot pick up ' + self.name + '.', colors.red)
        else:
            gv.inventory.append(self)
            gv.gameobjects.remove(self)
            message('You picked up a ' + self.name + '!', colors.green)
    
    def drop(self):
        '''add to the map and remove from the gv.player's gv.inventory. also, place it at the gv.player's coordinates'''
        gv.gameobjects.append(self)
        gv.inventory.remove(self)
        self.x = gv.player.x
        self.y = gv.player.y
        message('You dropped a ' + self.name + '.', colors.yellow)

    def examine(self):
        '''examines the given'''
        # TODO: Pass description from generator; possibly open small menu instead of message to display longer texts
        message('This is a ' + self.name + '.')

    def use(self):
        message('The ' + self.name + ' cannot be used.')

    def equip(self):
        message('The ' + self.name + ' cannot be equipped.')
    
class Useable(Item):
    '''an useable item (e.g. scroll, potion,wand)'''
    def __init__(self, x, y,name,char, color,description=None,use_function=None,params=None):
        super().__init__(x, y,name,char, color,description=description)
        
        self.use_function = use_function
        self.params = params

    def use(self):
        '''just call the "use_function" if it is defined'''
        if self.use_function(params = self.params) != 'cancelled': #the use_function is called and unless it isn't cancelled, True is returned
            gv.inventory.remove(self)  #destroy after use, unless it was cancelled for some reason

class Equipment(Item):
    '''an equipable item (e.g. armor, weapon)'''
    def __init__(self, x, y,name,char, color,description=None,equips_to=None,stats=None):
        super().__init__(x, y,name,char, color,description=description)
        
        self.equips_to = equips_to
        self.stats = stats

    def equip(self):
        if not self.equips_to is None:
            print('equip item' + item.name)