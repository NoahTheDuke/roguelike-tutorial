#! python3
''' module containing all map related code'''

import settings
from objects import GameObject

class Tile:
    ''' a map tile '''
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        self.explored = False
 
        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight# Wall colors

class Rect:
    ''' a rectangle on the map. used to characterize a room. '''
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        ''' returns center '''
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)
 
    def intersect(self, other):
        ''' returns true if this rectangle intersects with another one '''
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)

def make_map():
    ''' Sets up the game's map '''
    #fill map with "unblocked" tiles
    my_map = [[Tile(True)
    for y in range(settings.MAP_HEIGHT)]
        for x in range(settings.MAP_WIDTH)]

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
                #this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y
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
                
                #Fill room with monsters
                place_objects(new_room)

        #finally, append the new room to the list
        rooms.append(new_room)
        num_rooms += 1

        return my_map

def create_room(room):
    ''' Create a room in the dungeon '''
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1, room.x2 + 1):
        for y in range(room.y1, room.y2 + 1):
            my_map[x][y].blocked = False
            my_map[x][y].block_sight = False
 
def create_h_tunnel(x1, x2, y):
    global my_map
    for x in range(min(x1, x2), max(x1, x2) + 1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False
 
def create_v_tunnel(y1, y2, x):
    global my_map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        my_map[x][y].blocked = False
        my_map[x][y].block_sight = False        

def place_objects(room):
    ''' choose random number of monsters '''
    num_monsters = randint(0, settings.MAX_ROOM_MONSTERS)
 
    for i in range(num_monsters):
        #choose random spot for this monster
        x = randint(room.x1, room.x2)
        y = randint(room.y1, room.y2)
        while is_blocked(x, y):
            x = randint(room.x1, room.x2)
            y = randint(room.y1, room.y2)
 
        if randint(0, 100) < 80:  #80% chance of getting an orc
            #create an orc
            monster = GameObject(x, y,'Orc', 'o', colors.desaturated_green,blocks=True)
        else:
            #create a troll
            monster = GameObject(x, y,'Troll','T', colors.darker_green,blocks=True)
 
        gameobjects.append(monster)