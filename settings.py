#! python3
''' Settings for the tutorial roguelike '''

import colors

# Constants
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 45
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_ROOM_MONSTERS = 3

# FOV
FOV_ALGO = 'SHADOW'
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

# Dungeon colors
color_dark_wall = colors.darkest_gray
color_light_wall = colors.gray
color_dark_ground = colors.dark_grey
color_light_ground = colors.dark_amber