''' All AI-related code '''

import colors
import global_vars as glob
from random import randint
from gui_util import message

class BasicMonster:
    '''AI for a basic monster.'''
    def take_turn(self):
        '''let the monster take a turn'''
        monster = self.owner
        if glob.game_map.fov[monster.x, monster.y]:
 
            #move towards glob.player if far away
            if monster.distance_to(glob.player) >= 2:
                monster.move_towards(glob.player)
 
            #close enough, attack! (if the glob.player is still alive.)
            elif glob.player.hp > 0:
                monster.attack(glob.player)

class ConfusedMonster:
    '''AI for a confused monster'''
    def __init__(self, old_ai, num_turns=5):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0:  #still confused...
                #move in a random direction, and decrease the number of turns confused
                self.owner.move(randint(-1, 1), randint(-1, 1))
                self.num_turns -= 1
    
        else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', colors.red)