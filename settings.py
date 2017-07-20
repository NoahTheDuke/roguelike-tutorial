#! python3
''' Constant variables for the tutorial roguelike '''

import colors

# Game
DUNGEONNAME = 'The Fiendish Abyss'

# Console
SCREEN_WIDTH = 120
SCREEN_HEIGHT = 80
MAP_WIDTH = 95
MAP_HEIGHT = 60

# GUI panels
SIDE_PANEL_WIDTH = SCREEN_WIDTH - MAP_WIDTH         # Difference between screen and map width
SIDE_PANEL_X = SCREEN_WIDTH - SIDE_PANEL_WIDTH
STAT_PANEL_HEIGHT = 20
INV_PANEL_HEIGHT = 40

# Message panel
BOTTOM_PANEL_HEIGHT = SCREEN_HEIGHT - MAP_HEIGHT    # Difference between screen and map height
BOTTOM_PANEL_WIDTH = SCREEN_WIDTH - SIDE_PANEL_WIDTH
BOTTOM_PANEL_Y = SCREEN_HEIGHT - BOTTOM_PANEL_HEIGHT
BAR_WIDTH = SIDE_PANEL_WIDTH
MSG_X = 5
MSG_WIDTH = SCREEN_WIDTH - 2
MSG_HEIGHT = BOTTOM_PANEL_HEIGHT - 3
LIMIT_FPS = 30

# Map
ROOM_MAX_SIZE = 18
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 2

# Dungeon colors
COLOR_DARK_WALL = colors.darkest_gray
COLOR_DARK_WALL_fg = colors.dark_grey
COLOR_DARK_GROUND = colors.darkest_gray
COLOR_DARK_GROUND_fg = colors.dark_grey
COLOR_LIGHT_WALL = colors.lighter_grey
COLOR_LIGHT_GROUND = colors.lighter_grey

# Interaction
INVENTORY_WIDTH = 50

# FOV
FOV_ALGO = 'SHADOW'
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 6