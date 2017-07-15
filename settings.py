#! python3
''' Constant variables for the tutorial roguelike '''

import colors

# Game
DUNGEONNAME = 'The Fiendish Abyss'

# Console
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 30
MAP_WIDTH = 80
MAP_HEIGHT = 43
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

# Map
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 2
INVENTORY_WIDTH = 50

# FOV
FOV_ALGO = 'SHADOW'
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 6

# Dungeon colors
COLOR_DARK_WALL = colors.darkest_gray
COLOR_DARK_WALL_fg = colors.dark_grey
COLOR_DARK_GROUND = colors.darkest_gray
COLOR_DARK_GROUND_fg = colors.dark_grey
COLOR_LIGHT_WALL = colors.lighter_grey
COLOR_LIGHT_GROUND = colors.lighter_grey