#! python3
''' A simple roguelike based on an online tutorial '''
# TODO: adding ,con,root,panel where relevant

import tdl
from random import randint
import colors
import settings
import math
import textwrap
import random
from keyhandler import handle_keys
from map_util import GameMap,make_map
#from gameobjects import GameObject, Fighter

# Global variables | NOTE: These need to be moved into the relevant functions and passed around as arguments
game_state = 'idle'
player_action = None
gameobjects = []
inventory = []
game_msgs = []

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
    
    def move(self, dx, dy,game_map):
        ''' Move the object '''
        if game_map.walkable[self.x+dx,self.y+dy]:
            self.x += dx
            self.y += dy
            if not self.ai: #if the player has moved, recalculate FOV | NOTE: This should be moved elsewhere
                fov_recompute(self,game_map)
    
    def draw(self):
        ''' Draw the object '''
        con.draw_char(self.x, self.y, self.char, self.color)

    def clear(self):
        ''' Clear the object '''
        con.draw_char(self.x, self.y, ' ', self.color, bg=None)
    
    def move_towards(self, target_x, target_y,game_map):
        ''' Move Gameobject towards intended target '''
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
 
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy,game_map)
    
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
    def take_turn(self,game_map,player):
        '''let the monster take a turn'''
        monster = self.owner
        if game_map.fov[monster.x, monster.y]:
 
            #move towards player if far away
            if monster.distance_to(player) >= 2:
                monster.move_towards(player.x, player.y,game_map)
 
            #close enough, attack! (if the player is still alive.)
            elif player.fighter.hp > 0:
                monster.fighter.attack(player)

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
      
def ran_room_pos(room,game_map):
    '''returns a random position within a room for an object'''
    for i in range(room.w*room.h):
        x = randint(room.x1+1, room.x2-1)
        y = randint(room.y1+1, room.y2-1)
        if game_map.walkable[x,y]:
            break
    return [x,y]

def place_objects(game_map):
    ''' place objects in room '''
    print(len(game_map.rooms))
    for room in game_map.rooms:
        num_monsters = randint(0, settings.MAX_ROOM_MONSTERS)
        for i in range(num_monsters):
            #choose random spot for this monster
            x,y = ran_room_pos(room,game_map)    
            place_monster(x,y)
        
        num_items = randint(0, settings.MAX_ROOM_ITEMS)
        for i in range(num_items):
            #choose random spot for this item
            x,y = ran_room_pos(room,game_map)
            place_item(x,y)

def place_monster(x,y):
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
    name,symbol,color,stats,ai = monsters[m][1], monsters[m][2], monsters[m][3],monsters[m][4],monsters[m][5]
    fighter_component = Fighter(stats[0],stats[1],stats[2],stats[3])
    monster = GameObject(x,y,name,symbol,color,blocks=True,fighter=fighter_component,ai=ai)

def place_item(x,y):
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
    item_component = Item(use_function=use_function,param1=param1,param2=param2)
    item = GameObject(x,y, name, symbol, color,item=item_component)
    item.send_to_back()  #items appear below other objects

def render_all(game_map,player,con,root,panel):
    ''' draw all game objects '''
    for y in range(settings.MAP_HEIGHT):
        for x in range(settings.MAP_WIDTH):
            wall = not game_map.transparent[x,y]
            if not game_map.fov[x, y]:
                #it's out of the player's FOV but explored
                if game_map.explored[x][y]:
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
                game_map.explored[x][y] = True
    for obj in gameobjects:
        if obj != player and game_map.fov[obj.x,obj.y]:
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

def fov_recompute(player,game_map):
    ''' Recomputes the player's FOV '''
    game_map.compute_fov(player.x, player.y,fov=settings.FOV_ALGO,radius=settings.TORCH_RADIUS,light_walls=settings.FOV_LIGHT_WALLS)

def player_move_or_attack(player,dx, dy,game_map):
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
        player.move(dx, dy,game_map)

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
    
def closest_monster(max_range,game_map):
    '''find closest enemy, up to a maximum range, and in the player's FOV'''
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range
 
    for obj in gameobjects:
        if obj.fighter and not obj == player and game_map.fov[obj.x, obj.y]:
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
    

def main_loop(game_map,player,con,root,panel):
    ''' begin main game loop '''
    game_state = 'playing'
    while not tdl.event.is_window_closed():
        render_all(game_map,player,con,root,panel)
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
                player_move_or_attack(player,x,y,game_map)
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
                    obj.ai.take_turn(game_map,player)

def initialize_game():
    ''' launches the game '''
    
    # Set custom font
    tdl.set_font('arial10x10.png', greyscale=True, altLayout=True)

    # initialize the window
    root = tdl.init(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
    con = tdl.Console(settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    panel = tdl.Console(settings.SCREEN_WIDTH, settings.PANEL_HEIGHT)

    # create the player
    fighter_component = Fighter(hp=30, defense=2, power=5,death_function=player_death)
    player = GameObject(randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),randint(settings.MAP_HEIGHT,settings.MAP_WIDTH),'player', '@', colors.white, blocks=True,fighter=fighter_component)
    
    # create the map
    game_map = GameMap(settings.MAP_WIDTH,settings.MAP_HEIGHT)
    make_map(game_map,player)
    
    # place objects in the map
    place_objects(game_map)

    # initialize FOV
    fov_recompute(player,game_map)
    
    # a warm welcoming message!
    message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', colors.red)
    
    # begin the main game loop
    main_loop(game_map,player,con,root,panel)

initialize_game()