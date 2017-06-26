#! python 3
''' A simple roguelike based on an online tutorial '''

import tdl

# constants
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 45
color_dark_wall = (34, 49, 63)
color_dark_ground = (103, 128, 159)

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

    #create two rooms
    room1 = Rect(20, 15, 10, 15)
    room2 = Rect(50, 15, 10, 15)
    create_room(room1)
    create_room(room2)       

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

# Game setup


def initialize_game():
    ''' launches the game '''

    global objects, player, npc

    player = GameObject(25, 23, '@', (255,255,255))
    npc = GameObject(SCREEN_WIDTH//2 - 5, SCREEN_HEIGHT//2, 'H', (255,255,0))
    objects = [npc,player]
    make_map()

    ''' begin main game loop '''
    while not tdl.event.is_window_closed():
        render_all(
        tdl.flush()

        for obj in objects:
            obj.clear()
        exit_game = handle_keys()
        if exit_game:
            break

initialize_game()