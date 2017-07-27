''' commonly used functions '''

# Constants and global variables
import global_vars as gv


def same_pos(obj1, obj2):
    if (obj1.pos() == obj2.pos()):
        return True
    else:
        return False
