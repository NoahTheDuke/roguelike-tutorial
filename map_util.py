'''map-creation related code for the roguelike tutorial'''

import settings
import global_vars as glob
from random import randint
from tdl.map import Map

class GameMap(Map):
    def __init__(self, width, height,rooms=[]):
        super().__init__(width, height)
        self.rooms = rooms
        self.explored = [[False for y in range(height)] for x in range(width)]

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
            glob.game_map.walkable[x,y] = True
            glob.game_map.transparent[x,y] = True
 
def create_h_tunnel(x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        glob.game_map.walkable[x,y] = True
        glob.game_map.transparent[x,y] = True
 
def create_v_tunnel(y1, y2, x):
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        glob.game_map.walkable[x,y] = True
        glob.game_map.transparent[x,y] = True

def make_map():
    ''' Sets up the game's map '''

    rooms = []
    num_rooms = 0
 
    for r in range(settings.MAX_ROOMS):
        #random width and height
        w = randint(settings.ROOM_MIN_SIZE, settings.ROOM_MAX_SIZE)
        h = randint(settings.ROOM_MIN_SIZE, settings.ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = randint(0, settings.MAP_WIDTH-w-1)
        y = randint(0, settings.MAP_HEIGHT-h-1)

        #"Rect" class makes rectangles easier to work with
        new_room = Rect(x, y, w, h)
 
        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
        if not failed:
            #this means there are no intersections, so this room is valid

            #"paint" it to the map's tiles
            create_room(new_room)

            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                #this is the first room, where the glob.player starts at
                glob.player.x = new_x
                glob.player.y = new_y
            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel

                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms-1].center()

                #toss a coin (random number that is either 0 or 1)
                if randint(0, 1):
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)

            #append the new room to the list
            rooms.append(new_room)
            num_rooms += 1
    
    glob.game_map.rooms = rooms

def fov_recompute():
    ''' Recomputes the glob.player's FOV '''
    glob.game_map.compute_fov(glob.player.x, glob.player.y,fov=settings.FOV_ALGO,radius=settings.TORCH_RADIUS,light_walls=settings.FOV_LIGHT_WALLS)