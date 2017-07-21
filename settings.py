#! python3
''' Constant variables for the tutorial roguelike '''

import colors

# Game
DUNGEONNAME = 'The Fiendish Abyss'

# Console
SCREEN_WIDTH = 95
SCREEN_HEIGHT = 70
MAP_WIDTH = 70  # Should be at least 20 less than SCREEN_WIDTH
MAP_HEIGHT = 55
LIMIT_FPS = 30

# GUI panels
SIDE_PANEL_WIDTH = SCREEN_WIDTH - MAP_WIDTH         # Difference between screen and map width
SIDE_PANEL_X = SCREEN_WIDTH - SIDE_PANEL_WIDTH
STAT_PANEL_HEIGHT = SCREEN_HEIGHT//3
INV_PANEL_HEIGHT = SCREEN_HEIGHT - STAT_PANEL_HEIGHT
BAR_WIDTH = SIDE_PANEL_WIDTH - 2    # Width for the bars displaying health etc

PANELS_BORDER_COLOR = colors.dark_grey
PANELS_BORDER_COLOR_ACTIVE = colors.darker_red

# Message panels
BOTTOM_PANEL_HEIGHT = SCREEN_HEIGHT - MAP_HEIGHT    # Difference between screen and map height
BOTTOM_PANEL_Y = SCREEN_HEIGHT - BOTTOM_PANEL_HEIGHT
BOTTOM_PANEL_WIDTH = (SCREEN_WIDTH - SIDE_PANEL_WIDTH)//2
MSG_X = 2
MSG_WIDTH = BOTTOM_PANEL_WIDTH - 2
MSG_HEIGHT = BOTTOM_PANEL_HEIGHT - 4

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
INVENTORY_WIDTH = 30

# FOV
FOV_ALGO = 'SHADOW'
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 6