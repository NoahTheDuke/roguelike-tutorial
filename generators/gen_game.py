''' functions related to generating the game's basic structure itself '''

# Third-party modules
import tdl
from random import choice as ranchoice
from random import randint

# Constants and global variables
import global_vars as gv
import settings
import colors

# Classes
from classes.objects import Cursor, Stairs

# Generators
from generators.gen_actors import gen_monsters, gen_Player
from generators.gen_items import gen_inventory, gen_items

# Other game-related functions
from map_util import GameMap,Rect,create_room, create_h_tunnel,create_v_tunnel,ran_room_pos
from gui_util import message
from render_util import fov_recompute

def gen_map(width,height):
    ''' Sets up the game's map '''

    rooms = []
    num_rooms = 0

    # create the map
    gv.game_map = GameMap(width,height)
 
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

            if num_rooms > 0:
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
    
    gv.game_map.rooms = rooms

def gen_map_content():
    
    rooms = gv.game_map.rooms
    x,y = ran_room_pos(ranchoice(gv.game_map.rooms))
    gv.player.x,gv.player.y = x,y
    # Place player and upwards stairs in random room
    x,y = ran_room_pos(ranchoice(rooms))
    gv.player.x,gv.player.y = x,y
    #gv.stairs_up = Stairs(x,y,False)
    gv.stairs_down = Stairs(x,y)

    # Create downward stairs in a random room
    # x,y = ran_room_pos(ranchoice(rooms))
    # while ((x,y) == gv.stairs_up.pos()):
    #     x,y = ran_room_pos(ranchoice(rooms))
    gv.stairs_down = Stairs(x,y)

    # fill the map with content
    gen_monsters()
    gen_items()


def gen_game(newgame=True):
    ''' sets up a new game '''

    if newgame:
        # reset other global variables
        gv.gameobjects = []
        gv.actors = []
        gv.game_msgs = []
        gv.inventory = []
        #gv.cursor = Cursor(0,0)

        # create the player & cursor
        gv.player = gen_Player(0,0)
        gv.cursor = Cursor(0,0)
        
        # Setup an initial inventory
        gen_inventory()

        # a warm welcoming message!
        message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', colors.red)
    else:
        for obj in gv.gameobjects:
            if not obj == gv.player:
                obj.delete()

    # Generate a new map
    gen_map(settings.MAP_WIDTH,settings.MAP_HEIGHT)

    # Generate map content
    gen_map_content()

    # initialize FOV
    fov_recompute()
    
    # clear the old console
    gv.con.clear()