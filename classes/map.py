''' map-related classes '''

# Third-party modules
from random import randint

# Constants and global variables
import global_vars as gv
import settings


class GameMap:
    ''' the basic game map '''

    def __init__(self, width, height, rooms=None):
        self.width = width
        self.height = height
        #super().__init__(width, height)
        self.rooms = list() if rooms is None else rooms
        # This loops through a list of range (width), for every step looping through a list of range (height), filling every index with a False value. Eg: [[False,False],[False,False]]
        self.explored = [[False for y in range(height)] for x in range(width)]
        self.gibbed = [[False for y in range(height)] for x in range(width)]
        self.transparent = [[False for y in range(height)] for x in range(width)]
        self.walkable = [[False for y in range(height)] for x in range(width)]
        self.visible = [[False for y in range(height)] for x in range(width)]

    def create_room(self, room):
        ''' Create a room in the dungeon '''
        #go through the tiles in the rectangle and make them passable
        for x in range(room.x1, room.x2 + 1):
            for y in range(room.y1, room.y2 + 1):
                self.walkable[x][y] = True
                self.transparent[x][y] = True  # transparent is an attribute inherited from parent class 'Map'

    def create_h_tunnel(self, x1, x2, y):
        ''' create a horizontal tunnel between x1 & x2 '''
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.walkable[x][y] = True
            self.transparent[x][y] = True

    def create_v_tunnel(self, y1, y2, x):
        ''' create a vertical tunnel between y1 & y2 '''
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.walkable[x][y] = True
            self.transparent[x][y] = True

    # def create_d_tunnel(self,(x1,y1),(x2,y2)):
    #     ''' create a diagonal tunnel between (x1,y1) & (x2,y2) '''


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
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)

    def ranpos(self):
        '''returns a random, walkable position within the room'''
        x = randint(self.x1 + 1, self.x2 - 1)
        y = randint(self.y1 + 1, self.y2 - 1)
        while not gv.game_map.walkable[x][y]:
            x = randint(self.x1 + 1, self.x2 - 1)
            y = randint(self.y1 + 1, self.y2 - 1)
        return (x, y)
