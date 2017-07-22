''' code related to the manual display '''

from gui.menus import menu

def display_manual():
    '''displays the game's manual'''
    manfile = open('resources/manual.txt','r')   
    man = manfile.read().split('\n')
    manfile.close()
    menu(man,[],(settings.SCREEN_WIDTH//2),wrap_header=False,options_sorted=False)