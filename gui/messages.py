''' all code related to handling messages in-game '''

import tdl
import textwrap
import colors
import settings

import global_vars as gv

from gui.helpers import draw_window_borders, center_x_for_text

class Message:
    def __init__(self,text,color=colors.white,log=None):
        self.text = text
        self.color = color

        if log is None:
            log = gv.game_log

        # Format the passed text according to the intended log's width
        self.lines = textwrap.wrap(self.text, log.width)

        # Add the new message to the specified log
        log.add_message(self)

class MessageLog:
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self,message):
        ''' add a message to the log, deleting earlier message if necessary '''   
              
        if len(self.messages) == self.height:
            del self.messages[0]

        # Add the Message to the messages list
        self.messages.append(message)
    
    def display_messages(self,y,panel):
        ''' draws the messages to the indicated panel at height y'''
        for message in self.messages:
            if y + len(message.lines) < panel.height:   # If the current height + upcoming lines wouldn't exceed the log's height, draw the lines
                for line in message.lines:
                    panel.draw_str(settings.MSG_X, y, line, bg=None, fg=message.color)
                    y += 1
            else:   # Otherwise delete the earliest message to make room
                del self.messages[0]

def msgbox(text,title=None,width=0,text_color=colors.white,border_color=settings.PANELS_BORDER_COLOR_ACTIVE):
    '''display a simple message box'''

    # if width wasn't set, it's automatically length of text + padding
    if width == 0:
        width = len(text) + 4

    text_wrapped = textwrap.wrap(text,width-2) # Calculate how many lines are required

    # Set up the panel
    panel = tdl.Console(width,len(text_wrapped)+4)
    panel.clear(fg=colors.white, bg=colors.black)
    draw_window_borders(panel,color=border_color)

    # Draw the panel title (if passed)
    if title is not None:
        panel.draw_str(2,0,title,fg=text_color)
    
    # Draw the panel's contents
    y = 2
    for line in text_wrapped:
        panel.draw_str(2,y,line,fg=text_color)
        y += 1
    
    panel.draw_str(center_x_for_text(panel,'<CONTINUE>'),panel.height-1,'<CONTINUE>',fg=text_color)
    
    # Blit the box to the root window, flush the console to display it and wait for a key input to remove it
    gv.root.blit(panel,settings.SCREEN_WIDTH//2 - panel.width//2,settings.SCREEN_HEIGHT//2 - panel.height//2, panel.width, panel.height)
    tdl.flush()
    # Mesagebox waits for enter to proceed
    key = ''
    while key not in ['ENTER','KPENTER','SPACE','ESCAPE']:
        key = tdl.event.key_wait().key
