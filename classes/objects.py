''' Classes for basic objects '''

import math
from random import randint

import settings
import colors
import global_vars as gv

from gui.render_main import RenderOrder

class GameObject:
    ''' Main class of game objects'''
    def __init__(self, x, y,name,char,color,blocks=False, item=False,always_visible=False,render_order=RenderOrder.CORPSE):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.blocks = blocks
        self.name = name
        self.is_item = item
        self.always_visible = always_visible

        self.render_order = render_order
        
        gv.gameobjects.append(self)

    def draw(self,con,fgcolor=None,bgcolor = colors.black):
        ''' Draw the object '''
        if fgcolor == None:
            fgcolor = self.color
        if gv.player.opponent == self: # if the object is locked in combat with the player, change it's background color
            bgcolor = colors.darker_crimson
        con.draw_char(self.x, self.y, self.char, fgcolor,bgcolor)

    def clear(self,con):
        ''' Clear the object '''
        con.draw_char(self.x, self.y, ' ', self.color, bg=None)

    def pos(self):
        ''' Returns the x,y coordinates of the object '''
        return (self.x,self.y)

    def is_player(self):
        ''' returns true if the object is the player '''
        return (self == gv.player)

    def direction_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return(dx,dy)

    def distance_to(self, other):
        '''return the distance to another object'''
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance_to_coord(self, x, y):
        ''' return the distance to some coordinates '''
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2) 
    
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
        super().__init__(x, y,'cursor',None,None)

    def move (self,dx,dy):
        if gv.game_map.visible[self.x + dx][self.y + dy]:
            self.x += dx
            self.y += dy
    
    def draw(self,con):
        ''' Draw the object '''
        if not self.color == None:
            con.draw_char(self.x, self.y, self.char,self.color)
    
    def activate(self,char,color):
        self.char = char
        self.color = color
        self.x = gv.player.x
        self.y = gv.player.y
        self.render_order = RenderOrder.CURSOR
    
    def deactivate(self):
        self.char = None
        self.render_order = RenderOrder.NONE

class Stairs(GameObject):
    '''stair object '''
    def __init__(self, x, y,down=True):
        if down:
            name = 'downward stairs'
            char = '<'
            self.descended = False
        else:
            name = 'upward stairs'
            char = '>'

        super().__init__(x, y,name,char,colors.white,always_visible=True)
        self.down = down