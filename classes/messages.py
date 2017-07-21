import textwrap
import colors
import settings

import global_vars as gv

class Message:
    def __init__(self,text,lines=None,color=colors.white,log=None):
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