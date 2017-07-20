import textwrap
import colors

import global_vars as gv

class Message:
    def __init__(self, text,color=colors.white,log=None):
        self.text = text
        self.color = color

        if log is None:
            log = gv.game_log
        
        # Add the new message to the specified log
        log.add_message(self)

class MessageLog:
    def __init__(self, x, width, height):
        self.messages = []
        self.x = x
        self.width = width
        self.height = height

    def add_message(self,message):
        # Split the message if necessary, among multiple lines
        new_msg_lines = textwrap.wrap(message.text, self.width)

        for line in new_msg_lines:
            # If the buffer is full, remove the first line to make room for the new one
            if len(self.messages) == self.height:
                del self.messages[0]

            # Add the new line as a Message object, with the text and the color
            self.messages.append(message)