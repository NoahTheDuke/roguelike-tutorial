''' commonly used functions '''

from random import randint

# Constants and global variables
import global_vars as gv

def ran_room_pos(room):
    '''returns a random, walkable position within a room for an object'''
    x = randint(room.x1+1, room.x2-1)
    y = randint(room.y1+1, room.y2-1)
    while not gv.game_map.walkable[x,y]:
        x = randint(room.x1+1, room.x2-1)
        y = randint(room.y1+1, room.y2-1)
    return (x,y)