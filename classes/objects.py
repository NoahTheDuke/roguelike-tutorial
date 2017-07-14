''' Classes for basic objects '''

import math
from random import randint

import settings
import colors
import global_vars as gv

from render_util import fov_recompute

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

    def pos(self):
        ''' Returns the x,y coordinates of the object '''
        return (self.x,self.y)

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
        super().__init__(x, y,'cursor',None,None)
        self.is_active = False

    def move (self,dx,dy):
        if gv.game_map.fov[self.x + dx,self.y + dy]:
            self.x += dx
            self.y += dy
            #look_at_ground(self.x,self.y)
    
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

        super().__init__(x, y,name,char,colors.white)
        self.down = down
        self.send_to_back()