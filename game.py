#! python3
''' A simple roguelike based on an online tutorial '''

import tdl
from random import randint
import colors
import settings
import math

# Global variablesgam
game_state = 'idle'
player_action = None
gameobjects = []
my_map = []

# Set custom font
tdl.set_font('arial10x10.png', greyscale=True, altLayout=True)

# initialize the window
ROOT = tdl.init(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
CON = tdl.Console(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)

class GameObject:
    ''' Main class of game objects'''
    global gameobjects

    def __init__(self, x, y,  name,char, color, blocks=False, fighter=None, ai=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.blocks = blocks
        self.name = name

        self.fighter = fighter #let the fighter component know who owns it
        if self.fighter: #By default fighter is None thus this check only passes if a value for fighter has been set
            self.fighter.owner = self
        
        self.ai = ai #let the AI component know who owns it
        if self.ai:  
            self.ai.owner = self

        gameobjects.append(self)
    
    def move(self, dx, dy):
        ''' Move the object '''
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
    
    def draw(self):
        ''' Draw the object '''
        if (self.x, self.y) in visible_tiles:
            CON.draw_char(self.x, self.y, self.char, self.color)

    def clear(self):
        ''' Clear the object '''
        CON.draw_char(self.x, self.y, ' ', self.color, bg=None)
    
    def move_towards(self, target_x, target_y):
        ''' Move Gameobject towards intended target '''
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
 
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)
    
    def distance_to(self, other):
        '''return the distance to another object'''
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

class Fighter:
    #combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

class BasicMonster:
    #AI for a basic monster. 
    def take_turn(self):
        monster = self.owner
        if (monster.x, monster.y) in visible_tiles:
 
            #move towards player if far away
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)
 
            #close enough, attack! (if the player is still alive.)
            elif player.fighter.hp > 0:
                print('The attack of the ' + monster.name + ' bounces off your shiny metal armor!')

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

    if user_input.key == 'ENTER' and user_input.alt:
        #Alt+Enter: toggle fullscreen
        tdl.set_fullscreen(not tdl.get_fullscreen())
    elif user_input.key == 'ESCAPE':
        return 'exit'  #exit game

    if game_state == 'playing':
        #movement keys
        if user_input.key in ['UP','KP8']:
            player_move_or_attack(0,-1)
    
        elif user_input.key in ['DOWN','KP2']:
            player_move_or_attack(0,1)
    
        elif user_input.key in ['LEFT','KP4']:
            player_move_or_attack(-1,0)
    
        elif user_input.key in ['RIGHT','KP6']:
            player_move_or_attack(1,0)

        elif user_input.key in ['KP9']:
            player_move_or_attack(1,-1)

        elif user_input.key in ['KP7']:
            player_move_or_attack(-1,-1)    

        elif user_input.key in ['KP1']:
            player_move_or_attack(-1,1)    

        elif user_input.key in ['KP3']:
            player_move_or_attack(1,1)           

        elif user_input.key in ['KP5']:
            player_move_or_attack(0,0)
            return 'pass'

        else:
            return 'pass'

def make_map():
    ''' Sets up the game's map '''
    global my_map

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
            fighter_component = Fighter(hp=10, defense=0, power=3)
            ai_component = BasicMonster()
            monster = GameObject(x, y,'Orc', 'o', colors.desaturated_green,blocks=True,fighter=fighter_component,ai=BasicMonster())
        else:
            #create a troll
            fighter_component = Fighter(hp=16, defense=1, power=4)
            ai_component = BasicMonster()
            monster = GameObject(x, y,'Troll','T', colors.darker_green,blocks=True,fighter=fighter_component,ai=BasicMonster())
 
        gameobjects.append(monster)

def render_all():
    ''' draw all game objects '''
    for y in range(settings.MAP_HEIGHT):
        for x in range(settings.MAP_WIDTH):
            visible = (x, y) in visible_tiles
            wall = my_map[x][y].block_sight
            if not visible:
                #it's out of the player's FOV but explored
                if my_map[x][y].explored:
                    if wall:
                        CON.draw_char(x, y, None, fg=None, bg=settings.color_dark_wall)
                    else:
                        CON.draw_char(x, y, None, fg=None, bg=settings.color_dark_ground)
            else:
                #it's visible
                if wall:
                    CON.draw_char(x, y, None, fg=None, bg=settings.color_light_wall)
                else:
                    CON.draw_char(x, y, None, fg=None, bg=settings.color_light_ground)
                my_map[x][y].explored = True
    for obj in gameobjects:
        obj.draw()
        
    ROOT.blit(CON , 0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, 0, 0)        

def fov_recompute():
    ''' Recomputes the player's FOV '''
    global visible_tiles
    visible_tiles = tdl.map.quickFOV(player.x, player.y,
                                        is_visible_tile,
                                        fov=settings.FOV_ALGO,
                                        radius=settings.TORCH_RADIUS,
                                        lightWalls=settings.FOV_LIGHT_WALLS)

def is_blocked(x, y):
    '''first test the map tile'''
    if my_map[x][y].blocked:
        return True
 
    #now check for any blocking objects
    for obj in gameobjects:
        if obj.blocks and obj.x == x and obj.y == y:
            return True
 
    return False

def is_visible_tile(x, y):
    ''' Determine whether a tile is visibile or not '''

    if x >= settings.MAP_WIDTH or x < 0:
        return False
    elif y >= settings.MAP_HEIGHT or y < 0:
        return False
    elif my_map[x][y].blocked == True:
        return False
    elif my_map[x][y].block_sight == True:
        return False
    else:
        return True

def player_move_or_attack(dx, dy):
    ''' Makes the player character either move or attack '''

    #the coordinates the player is moving to/attacking
    x = player.x + dx
    y = player.y + dy
 
    #try to find an attackable object there
    target = None
    for obj in gameobjects:
        if obj.x == x and obj.y == y:
            target = obj
            break
 
    #attack if target found, move otherwise
    if target is not None:
        print('The ' + target.name + ' laughs at your puny efforts to attack him!')
    else:
        player.move(dx, dy)
        fov_recompute()

def main_loop():
    ''' begin main game loop '''
    global game_state, player_action
    game_state = 'playing'
    while not tdl.event.is_window_closed():
        render_all()
        tdl.flush()

        for obj in gameobjects:
            obj.clear()
        player_action = handle_keys()
        if player_action == 'exit':
            break
        if game_state == 'playing' and player_action != 'pass':
            for obj in gameobjects:
                if obj.ai:
                    obj.ai.take_turn()

def initialize_game():
    ''' launches the game '''

    global player
    fighter_component = Fighter(hp=30, defense=2, power=5)
    player = GameObject(randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),'player', '@', colors.white, blocks=True,fighter=fighter_component)
    #npc = GameObject(settings.SCREEN_WIDTH//2 - 5, settings.SCREEN_HEIGHT//2, 'H', (255,255,0))
    make_map()
    fov_recompute()
    main_loop()

initialize_game()