''' Code related to entitity creation '''

import math
from random import randint

import settings
import colors
import global_vars as gv

from gui.render_main import RenderOrder
from gui.messages import Message

import item_use as iu
from classes.objects import GameObject


class Item(GameObject):
    '''an item that can be picked up and used.'''

    def __init__(self, x, y, name, char, color, description=None):
        super().__init__(x, y, name, char, color, blocks=False, item=True, render_order=RenderOrder.ITEM, always_visible=True)

        self.description = description
        if description == None:
            description = '{0} lacks a description!'.format[str(self.name)]
            print(str(self.name) + ' lacks a description!')

    def pick_up(self, actor):
        '''add to the gv.player's inventory and remove from the map'''
        if len(actor.inventory) >= 26:
            Message('Your gv.player.inventory is full, cannot pick up ' + self.name + '.', colors.red)
        else:
            actor.inventory.append(self)
            gv.gameobjects.remove(self)

    def drop(self):
        '''add to the map and remove from the gv.player's gv.player.inventory. also, place it at the gv.player's coordinates'''
        gv.gameobjects.append(self)
        gv.player.inventory.remove(self)
        self.x = gv.player.x
        self.y = gv.player.y
        Message('You dropped ' + self.name.title() + '.', colors.yellow)

    def examine(self):
        '''examines the given'''
        # TODO: Pass description from generator; possibly open small menu instead of message to display longer texts
        Message('This is a ' + self.name + '.')

    def use(self):
        Message('The ' + self.name + ' cannot be used.')

    def equip(self):
        Message('The ' + self.name + ' cannot be equipped.')


class Useable(Item):
    '''an useable item (e.g. scroll, potion,wand)'''

    def __init__(self, x, y, name, char, color, description=None, use_function=None, params=None):
        super().__init__(x, y, name, char, color, description=description)

        self.use_function = use_function
        self.params = params

    def use(self):
        '''just call the "use_function" if it is defined'''
        #the use_function is called and unless it isn't cancelled, True is returned
        if self.use_function(params=self.params) != 'cancelled':
            gv.player.inventory.remove(self)  #destroy after use, unless it was cancelled for some reason


class Equipment(Item):
    '''an equipable item (e.g. armor, weapon)'''

    def __init__(self, x, y, name, char, color, description=None, equips_to=None, params=None):
        super().__init__(x, y, name, char, color, description=description)

        self.equips_to = equips_to
        self.params = params

    def equip(self):
        if not self.equips_to is None:
            print('equip item' + item.name)
