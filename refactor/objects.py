#! python3
''' objects related code '''

import settings
import main

gameobjects = []

class GameObject:
    ''' Main class of game objects'''

    def __init__(self, x, y, name, char,color,blocks=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.blocks = blocks
        self.name = name
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