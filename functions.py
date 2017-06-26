#! python3
# Functions module for roguelike tutorial

# Movement function
def handle_keys():

    global playerx, playery
 
    # turn-based
    user_input = tdl.event.key_wait()

    '''
    #realtime (delete line above)
    keypress = False
    for event in tdl.event.get():
        if event.type == 'KEYDOWN':
           user_input = event
           keypress = True
    if not keypress:
        return
    '''
 
    #movement keys
    if user_input.key in ['UP','KP8']:
        player.move(0,-1)
 
    elif user_input.key in ['DOWN','KP2']:
        player.move(0,1)
 
    elif user_input.key in ['LEFT','KP4']:
        player.move(-1,0)
 
    elif user_input.key in ['RIGHT','KP6']:
        player.move(1,0)

    elif user_input.key in ['KP9']:
        player.move(1,-1)

    elif user_input.key in ['KP7']:
        player.move(-1,-1)    

    elif user_input.key in ['KP1']:
        player.move(-1,1)    

    elif user_input.key in ['KP3']:
        player.move(1,1)           

    elif user_input.key in ['KP5']:
        player.move(0,0)