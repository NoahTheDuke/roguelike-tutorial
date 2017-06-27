#! python 3
''' A simple roguelike based on an online tutorial '''

import tdl
from random import randint

# Constants
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 45
color_dark_wall = (34, 49, 63)
color_dark_ground = (103, 128, 159)
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

# Set custom font
tdl.set_font('arial10x10.png', greyscale=True, altLayout=True)

# initialize the window
ROOT = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
CON = tdl.Console(SCREEN_WIDTH, SCREEN_HEIGHT)

# Classes

class GameObject:
    ''' Main class of game objects'''
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
    
    def move(self, dx, dy):
        ''' Move the object '''
        if not my_map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy
    
    def draw(self):
        ''' Draw the object '''
        CON.draw_char(self.x, self.y, self.char, self.color)

    def clear(self):
        ''' Clear the object '''
        CON.draw_char(self.x, self.y, ' ', self.color, bg=None)


class Tile:
    ''' a map tile '''
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
 
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

def handle_keys():
    ''' Handles all key input made by the player '''
 
    # turn-based
    user_input = tdl.event.key_wait()

    '''
    #realtime (delete line above)
    keypress = False
    for event in tdl.event.get():
        if event.type == 'KEYDOWN':
           user_input = event
           keypress = True
    if not keypress:
        return
    '''
 
    #movement keys
    if user_input.key in ['UP','KP8']:
        player.move(0,-1)
 
    elif user_input.key in ['DOWN','KP2']:
        player.move(0,1)
 
    elif user_input.key in ['LEFT','KP4']:
        player.move(-1,0)
 
    elif user_input.key in ['RIGHT','KP6']:
        player.move(1,0)

    elif user_input.key in ['KP9']:
        player.move(1,-1)

    elif user_input.key in ['KP7']:
        player.move(-1,-1)    

    elif user_input.key in ['KP1']:
        player.move(-1,1)    

    elif user_input.key in ['KP3']:
        player.move(1,1)           

    elif user_input.key in ['KP5']:
        player.move(0,0)

    elif user_input.key in ['q','0']:
        return True

def make_map():
    ''' Sets up the game's map '''
    global my_map
    #fill map with "unblocked" tiles
    my_map = [[Tile(True)
    for y in range(MAP_HEIGHT)]
        for x in range(MAP_WIDTH)]

    rooms = []
    num_rooms = 0
 
    for r in range(MAX_ROOMS):
        #random width and height
        w = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = randint(0, MAP_WIDTH-w-1)
        y = randint(0, MAP_HEIGHT-h-1)

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

        #finally, append the new room to the list
        rooms.append(new_room)
        num_rooms += 1

def render_all():
    ''' draw all game objects '''

    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = my_map[x][y].block_sight
            if wall:
                CON.draw_char(x, y, None, fg=None, bg=color_dark_wall)
            else:
                CON.draw_char(x, y, '.', fg=(255,255,0), bg=color_dark_ground)
    
    for obj in objects:
        obj.draw()
        
    ROOT.blit(CON , 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)        

def create_room(room):
    ''' Create a room in the dungeon '''
    global my_map
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

def main_loop():
    ''' begin main game loop '''
    while not tdl.event.is_window_closed():
        render_all()
        tdl.flush()

        for obj in objects:
            obj.clear()
        exit_game = handle_keys()
        if exit_game:
            break

def initialize_game():
    ''' launches the game '''

    global objects, player, npc

    player = GameObject(25, 23, '@', (255,255,255))
    #npc = GameObject(SCREEN_WIDTH//2 - 5, SCREEN_HEIGHT//2, 'H', (255,255,0))
    objects = [player]
    make_map()
    main_loop()

initialize_game()