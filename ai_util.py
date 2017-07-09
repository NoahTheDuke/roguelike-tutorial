''' All AI-related code '''

import global_vars as glob

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
            elif glob.player.fighter.hp > 0:
                monster.fighter.attack(glob.player)