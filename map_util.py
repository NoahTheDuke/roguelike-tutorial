'''map-creation related code for the roguelike tutorial'''

# Third-party modules
from random import choice as ranchoice
from random import randint
from tdl.map import Map

# Constants and global variables
import global_vars as gv
import settings

class GameMap(Map):
    ''' the basic game map '''
    def __init__(self, width, height,rooms=[]):
        super().__init__(width, height)
        self.rooms = rooms
        self.explored = [[False for y in range(height)] for x in range(width)] # This loops through a list of range (width), for every step looping through a list of range (height), filling every index with a False value. Eg: [[False,False],[False,False]]
        self.gibbed = [[False for y in range(height)] for x in range(width)]

class Rect:
    ''' a rectangle on the map. used to characterize a room. '''
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.w = w
        self.h = h

    def center(self):
        ''' returns center '''
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)
 
    def intersect(self, other):
        ''' returns true if this rectangle intersects with another one '''
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

def create_room(room):
    ''' Create a room in the dungeon '''
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1, room.x2 + 1):
        for y in range(room.y1, room.y2 + 1):
            gv.game_map.walkable[x,y] = True
            gv.game_map.transparent[x,y] = True
 
def create_h_tunnel(x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        gv.game_map.walkable[x,y] = True
        gv.game_map.transparent[x,y] = True
 
def create_v_tunnel(y1, y2, x):
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        gv.game_map.walkable[x,y] = True
        gv.game_map.transparent[x,y] = True

def ran_room_pos(room):
    '''returns a random, walkable position within a room for an object'''
    x = randint(room.x1+1, room.x2-1)
    y = randint(room.y1+1, room.y2-1)
    while not gv.game_map.walkable[x,y]:
        x = randint(room.x1+1, room.x2-1)
        y = randint(room.y1+1, room.y2-1)
    return (x,y)