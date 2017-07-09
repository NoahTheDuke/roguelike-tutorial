''' key input for the game '''

def handle_keys(user_input):
    ''' Handles all key input made by the player '''
 
    if user_input.key == 'ENTER' and user_input.alt:
        #Alt+Enter: toggle fullscreen
        return {'fullscreen':None}
    elif user_input.key == 'ESCAPE':
        return {'exit':None}  #exit game

    # movement keys
    if user_input.key in ['UP','KP8']:
        return {'move':(0,-1)}

    elif user_input.key in ['DOWN','KP2']:
        return {'move':(0,1)}

    elif user_input.key in ['LEFT','KP4']:
        return {'move':(-1,0)}

    elif user_input.key in ['RIGHT','KP6']:
        return {'move':(1,0)}

    elif user_input.key in ['KP9']:
        return {'move':(1,-1)}

    elif user_input.key in ['KP7']:
        return {'move':(-1,-1)}    

    elif user_input.key in ['KP1']:
        return {'move':(-1,1)}    

    elif user_input.key in ['KP3']:
        return {'move':(1,1)}          

    elif user_input.key in ['KP5']:
        return {'wait'}

    elif user_input.text == 'r':
        return {'running':None}

    # item handling
    elif user_input.text == 'g':
        return {'get':None}

    elif user_input.text == 'i':
        return {'inventory':'use'}

    elif user_input.text == 'd':
        return {'inventory':'drop'}

    else:
        return 'pass'