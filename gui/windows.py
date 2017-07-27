''' code related to all windows, i.e. temporary panels and popups '''

import tdl
import textwrap

import settings
import colors

from gui.panels import setup_panel
from gui.helpers import center_x_for_text

import global_vars as gv


def draw_spotted_window():
    ''' draws a window next to the cursor if any objects are in the area '''

    cx, cy = gv.cursor.pos()

    spotted = [
        obj for obj in gv.gameobjects
        if [obj.x, obj.y] == [cx, cy] and not obj == gv.cursor and not obj == gv.player]

    if spotted:  # if more than one object is present, output the names as a message
        lines = []
        #gv.cursor.color = colors.yellow
        width = max(len(obj.name) for obj in spotted) + 6  # Window width is adapted to longest object name in list
        for obj in spotted:  # Go through the object names and wrap them according to the window's width
            line_wrapped = textwrap.wrap(obj.name, width)
            for text in line_wrapped:
                lines.append(text)

        window = tdl.Window(gv.root, cx + 2, cy - 2, width, 4 + len(lines))
        window.caption = 'I spot:'
        window.border_color = settings.PANELS_BORDER_COLOR
        setup_panel(window)

        y = 2
        for text in lines:
            window.draw_str(1, y, text.title(), bg=None, fg=colors.white)
            y += 1

        #gv.root.blit(window,cx+2,cy-2, window.width, window.height)


def draw_item_window(item, px, py, width, height):
    ''' draws a window containing an item's description and related options '''

    window = tdl.Window(gv.root, px, py, width, height)
    window.caption = item.name.title()
    window.border_color = settings.PANELS_BORDER_COLOR_ACTIVE
    setup_panel(window)

    wrapped_descr = textwrap.wrap(item.description, window.width - 2)
    y = 2
    for line in wrapped_descr:
        window.draw_str(1, y, line, bg=None, fg=colors.white)
        y += 1

    y += 2
    window.draw_str(1, y, '(u)se?', bg=None, fg=colors.white)
    y += 2
    window.draw_str(1, y, '(e)quip?', bg=None, fg=colors.white)
    y += 2
    window.draw_str(1, y, '(d)rop?', bg=None, fg=colors.white)
    y += 2
    window.draw_str(center_x_for_text(window, '<ESC TO CANCEL>'), y, '<ESC TO CANCEL>')

    #gv.root.blit(window,px,py,window.width,window.height)


def draw_options_window(caption, options, x, y):
    ''' draws a window listing the passed options '''

    width = max(len(option) for option in options) + 7
    height = len(options) + 4

    window = tdl.Window(gv.root, x, y, width, height)
    window.caption = caption
    window.border_color = settings.PANELS_BORDER_COLOR_ACTIVE
    setup_panel(window)

    y = 2
    letter_index = ord('a')  #ord returns the ascii code for a string-letter
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        window.draw_str(1, y, text, fg=colors.white, bg=None)
        y += 1
        letter_index += 1  #by incrementing the ascii code for the letter, we go through the alphabet

    window.draw_str(center_x_for_text(window, '<ESC TO CANCEL>'), window.height - 1, '<ESC TO CANCEL>')
