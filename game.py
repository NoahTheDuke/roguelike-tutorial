#! python3
''' A simple roguelike based on an online tutorial '''

import tdl
from random import randint
import colors
import settings
import math
import textwrap
import random
from keyhandler import handle_keys

# Global variables
game_state = 'idle'
player_action = None
gameobjects = []
inventory = []
my_map = []
game_msgs = []

# Set custom font
tdl.set_font('arial10x10.png', greyscale=True, altLayout=True)

# initialize the window
root = tdl.init(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
con = tdl.Console(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
panel = tdl.Console(settings.SCREEN_WIDTH, settings.PANEL_HEIGHT)

class GameObject:
    ''' Main class of game objects'''
    def __init__(self, x, y,  name,char, color, blocks=False, fighter=None, ai=None,item=None):
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
        
        self.item = item
        if self.item:  #let the Item component know who owns it
            self.item.owner = self
        
        gameobjects.append(self)
    
    def move(self, dx, dy):
        ''' Move the object '''
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
    
    def draw(self):
        ''' Draw the object '''
        if (self.x, self.y) in visible_tiles:
            con.draw_char(self.x, self.y, self.char, self.color)

    def clear(self):
        ''' Clear the object '''
        con.draw_char(self.x, self.y, ' ', self.color, bg=None)
    
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
    
    def send_to_back(self):
        '''make this object be drawn first, so all others appear above it if they're in the same tile.'''
        gameobjects.remove(self)
        gameobjects.insert(0, self)

class Fighter:
    ''' combat-related properties and methods (monster, player, NPC) '''
    def __init__(self, hp, defense, power,death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.max_defense = defense
        self.defense = defense
        self.max_power = power
        self.power = power
        self.death_function = death_function
    def take_damage(self, damage):
        '''apply damage if possible'''
        if damage > 0:
            self.hp -= damage
        if self.hp <= 0:
            if self.death_function:
                self.death_function(self.owner)
    def attack(self, target):
        '''a simple formula for attack damage'''
        damage = self.power - target.fighter.defense

        if damage > 0:
            #make the target take some damage
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')
    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp
    def modpwr(self, amount):
        self.power += amount
        if self.power == 1:
            self.power = 1    

class BasicMonster:
    '''AI for a basic monster.'''
    def take_turn(self):
        '''let the monster take a turn'''
        monster = self.owner
        if (monster.x, monster.y) in visible_tiles:
 
            #move towards player if far away
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y)
 
            #close enough, attack! (if the player is still alive.)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)

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

class Item:
    '''an item that can be picked up and used.'''
    def __init__(self, use_function=None,param1=None,param2=None):
        self.use_function = use_function
        self.param1 = param1
        self.param2 = param2
    def pick_up(self):
        '''add to the player's inventory and remove from the map'''
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', colors.red)
        else:
            inventory.append(self.owner)
            gameobjects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', colors.green)
    def use(self):
        '''just call the "use_function" if it is defined'''
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function(self.param1,self.param2) != 'cancelled': #the use_function is called and unless it isn't cancelled, True is returned
                inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason

    def drop(self):
        '''add to the map and remove from the player's inventory. also, place it at the player's coordinates'''
        gameobjects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', colors.yellow)


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

def ran_room_pos(room,check_block=True):
    '''returns a random position within a room for an object'''
    x = randint(room.x1+1, room.x2-1)
    y = randint(room.y1+1, room.y2-1)
    if check_block:
        while is_blocked(x, y):
            x = randint(room.x1+1, room.x2-1)
            y = randint(room.y1+1, room.y2-1)
    return [x,y]
def place_objects(room):
    ''' place objects in room '''
    num_monsters = randint(0, settings.MAX_ROOM_MONSTERS)
    for i in range(num_monsters):
        #choose random spot for this monster
        pos = ran_room_pos(room)    
        place_monster(pos)
    
    num_items = randint(0, settings.MAX_ROOM_ITEMS)
    for i in range(num_items):
        #choose random spot for this item
        pos = ran_room_pos(room)
        place_item(pos)

def place_monster(pos):
    '''creates a new monster at the given position'''
    # list of possible monsters
    # index:(chance,name,symbol,color,fighter values(tuple),AI class)
    monsters = {
            'orc1':(80,'Orc','o',colors.desaturated_green,(10, 0, 3,monster_death),BasicMonster()),
            'orc2':(80,'Orc','o',colors.desaturated_green,(12, 0, 3,monster_death),BasicMonster()),
            'troll1':(20,'Troll','T',colors.darkest_green,(16, 1, 4,monster_death),BasicMonster())
        }
    m = random.choice(list(monsters.keys()))
    while (randint(0,100) > monsters[m][0]):
        m = random.choice(list(monsters.keys()))
    fighter_component = Fighter(monsters[m][4][0],monsters[m][4][1],monsters[m][4][2],monsters[m][4][3])
    monster = GameObject(pos[0], pos[1],monsters[m][1], monsters[m][2], monsters[m][3],blocks=True,fighter=fighter_component,ai=monsters[m][5])

def place_item(pos):
    '''creates a new item at the given position'''
    # list of possible items
    # index:(chance,name,symbol,color,use_function(can be empty),param1,param2)
    items = {
        'heal1':(70,'healing potion','!',colors.violet,cast_heal,10,None),
        'power1':(50,'power potion','!',colors.red,cast_powerup,1,None),
        'power2':(20,'power potion','!',colors.red,cast_powerup,-1,None),    #cursed
        'scroll1':(30,'scroll of lightning bolt','#',colors.light_yellow,cast_lightning,20,5),
        'scroll2':(10,'scroll of lightning bolt','#',colors.light_yellow,cast_lightning,8,0)  #cursed
    }
    i = random.choice(list(items.keys()))
    while (randint(0,100) > items[i][0]):
        i = random.choice(list(items.keys()))
    name,symbol,color,use_function,param1,param2 = items[i][1], items[i][2], items[i][3],items[i][4],items[i][5],items[i][6]
    item_component = Item(use_function=items[i][4],param1=items[i][5],param2=items[i][6])
    item = GameObject(pos[0], pos[1], items[i][1], items[i][2], items[i][3],item=item_component)
    item.send_to_back()  #items appear below other objects

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
                        con.draw_char(x, y, None, fg=None, bg=settings.color_dark_wall)
                    else:
                        con.draw_char(x, y, None, fg=None, bg=settings.color_dark_ground)
            else:
                #it's visible
                if wall:
                    con.draw_char(x, y, None, fg=None, bg=settings.color_light_wall)
                else:
                    con.draw_char(x, y, None, fg=None, bg=settings.color_light_ground)
                my_map[x][y].explored = True
    for obj in gameobjects:
        if obj != player:
            obj.draw()
    player.draw()
        
    root.blit(con , 0, 0, settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, 0, 0)
    #prepare to render the GUI panel
    panel.clear(fg=colors.white, bg=colors.black)
 
    #show the player's stats
    render_bar(1, 1, settings.BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
        colors.light_red, colors.darker_red)
    render_bar(1, 2, settings.BAR_WIDTH, 'PWR', player.fighter.power, player.fighter.max_power,
        colors.black, colors.black)
    render_bar(1, 3, settings.BAR_WIDTH, 'DEF', player.fighter.defense, player.fighter.max_defense,
        colors.black, colors.black)       
    
    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        panel.draw_str(settings.MSG_X, y, line, bg=None, fg=color)
        y += 1
 
    #blit the contents of "panel" to the root console
    root.blit(panel, 0, settings.PANEL_Y, settings.SCREEN_WIDTH, settings.PANEL_HEIGHT, 0, 0)     

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
        if obj.fighter and obj.x == x and obj.y == y:
            target = obj
            break
 
    #attack if target found, move otherwise
    if target is not None:
        player.fighter.attack(target)
    else:
        player.move(dx, dy)
        fov_recompute()

def player_death(player):
    '''the game ended!'''
    global game_state
    message('You died!')
    game_state = 'dead'
 
    #for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = colors.dark_red
 
def monster_death(monster):
    '''transform it into a nasty corpse! it doesn't block, can't be
    attacked and doesn't move'''
    message(monster.name.capitalize() + ' is dead!')
    item_component = Item(eat_corpse,monster.name)
    item = GameObject(monster.x,monster.y, (monster.name + ' corpse'), '%', colors.dark_red,item=item_component)
    gameobjects.remove(monster)
    item.send_to_back()

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    '''render a bar (HP, experience, etc). first calculate the width of the bar'''
    bar_width = int(float(value) / maximum * total_width)
 
    #render the background first
    panel.draw_rect(x, y, total_width, 1, None, bg=back_color)
 
    #now render the bar on top
    if bar_width > 0:
        panel.draw_rect(x, y, bar_width, 1, None, bg=bar_color)
    
     #finally, some centered text with the values
    text = name + ': ' + str(value) + '/' + str(maximum)
    x_centered = x + (total_width-len(text))//2
    panel.draw_str(x_centered, y, text, fg=colors.white, bg=None)

def message(new_msg, color = colors.white):
    '''split the message if necessary, among multiple lines'''
    new_msg_lines = textwrap.wrap(new_msg, settings.MSG_WIDTH)
 
    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == settings.MSG_HEIGHT:
            del game_msgs[0]
 
        #add the new line as a tuple, with the text and the color
        game_msgs.append((line, color))

def menu(header, options, width):
    '''display a simple menu to the player'''
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
    #calculate total height for the header (after textwrap) and one line per option
    header_wrapped = textwrap.wrap(header, width)
    header_height = len(header_wrapped)
    height = len(options) + header_height

    #create an off-screen console that represents the menu's window
    window = tdl.Console(width, height)
 
    #print the header, with wrapped text
    window.draw_rect(0, 0, width, height, None, fg=colors.white, bg=None)
    for i, line in enumerate(header_wrapped):
        window.draw_str(0, 0+i, header_wrapped[i])

    y = header_height
    letter_index = ord('a') #ord returns the ascii code for a string-letter
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        window.draw_str(0, y, text, bg=None)
        y += 1
        letter_index += 1 #by incrementing the ascii code for the letter, we go through the alphabet

    #blit the contents of "window" to the root console
    x = settings.SCREEN_WIDTH//2 - width//2
    y = settings.SCREEN_HEIGHT//2 - height//2
    root.blit(window, x, y, width, height, 0, 0)

    #present the root console to the player and wait for a key-press
    tdl.flush()
    key = tdl.event.key_wait()
    key_char = key.char
    if key_char == '':
        key_char = ' ' # placeholder
    
    index = ord(key_char) - ord('a')
    if index >= 0 and index < len(options):
        return index
    return None

def cast_heal(hp,range):
    '''heal the player'''
    if range == None:
        if player.fighter.hp == player.fighter.max_hp:
            message('You are already at full health.', colors.red)
            return 'cancelled'

        message('Your wounds start to feel better!', colors.light_violet)
        player.fighter.heal(hp)

def cast_powerup(pwr,range):
    '''modify characters power'''
    if range == None:
        if (pwr > 0):
            message('Your power has been increased!', colors.light_violet)
        else:
            message('The potion of power was cursed!', colors.light_violet)

    player.fighter.modpwr(pwr)

def cast_lightning(pwr,range):
    '''zap something'''
    #find closest enemy (inside a maximum range) and damage it
    if range == 0:
        monster = player
        message('The scroll of lightning was cursed!', colors.light_violet)
    else:
        monster = closest_monster(range)

    if monster is None:  #no enemy found within maximum range
        message('No enemy is close enough to strike.', colors.red)
        return 'cancelled'

    #zap it!
    message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
        + str(pwr) + ' hit points.', colors.light_blue)
    monster.fighter.take_damage(pwr)
    
def closest_monster(max_range):
    '''find closest enemy, up to a maximum range, and in the player's FOV'''
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
    for obj in gameobjects:
        if obj.fighter and not obj == player and (obj.x, obj.y) in visible_tiles:
            #calculate distance between this object and the player
            dist = player.distance_to(obj)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = obj
                closest_dist = dist
    return closest_enemy

def eat_corpse(name,pwr):
    message('You eat the corpse of a ' + name + '. It is disgusting!')

def inventory_menu(header):
    '''show a menu with each item of the inventory as an option'''
    if len(inventory) == 0:
        message('Inventory is empty.')
    else:
        options = [item.name for item in inventory]
        index = menu(header, options, settings.INVENTORY_WIDTH)
        #if an item was chosen, return it
        if index is None or len(inventory) == 0:
            return None
        return inventory[index].item
    

def main_loop():
    ''' begin main game loop '''
    game_state = 'playing'
    while not tdl.event.is_window_closed():
        render_all()
        tdl.flush()

        for obj in gameobjects:
            obj.clear()
        player_action = handle_keys(tdl.event.key_wait())
        if 'exit' in player_action:
            break
        elif 'fullscreen' in player_action:
            tdl.set_fullscreen(not tdl.get_fullscreen())
        elif game_state == 'playing' and player_action != 'pass':
            if 'move' in player_action:
                x,y = player_action['move']
                player_move_or_attack(x,y)
            elif 'get' in player_action:
                found_something = False
                for obj in gameobjects:  #look for an item in the player's tile
                    if obj.x == player.x and obj.y == player.y and obj.item:
                        obj.item.pick_up()
                        found_something = True
                        break
                if not found_something:
                    message('There is nothing to pick up here!')
            elif 'inventory' in player_action:
                #show the inventory, pressing a key returns the corresponding item
                chosen_item = inventory_menu('Press the key next to an item to %s it, or any other to cancel.\n' % player_action['inventory'])
                if chosen_item is not None: #if an item was selected, call it's use or drop function
                    if (player_action['inventory'] == 'use'):
                        chosen_item.use()
                    elif (player_action['inventory'] == 'drop'):
                        chosen_item.drop()
            # AI takes turn
            for obj in gameobjects:
                if obj.ai:
                    obj.ai.take_turn()

def initialize_game():
    ''' launches the game '''
    global player
    fighter_component = Fighter(hp=30, defense=2, power=5,death_function=player_death)
    player = GameObject(randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),'player', '@', colors.white, blocks=True,fighter=fighter_component)
    #npc = GameObject(settings.SCREEN_WIDTH//2 - 5, settings.SCREEN_HEIGHT//2, 'H', (255,255,0))
    make_map()
    fov_recompute()
    #a warm welcoming message!
    message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', colors.red)
    main_loop()

initialize_game()