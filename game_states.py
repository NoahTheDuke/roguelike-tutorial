from enum import Enum, auto

class GameStates(Enum):
    PLAYERS_TURN = auto()
    CURSOR_ACTIVE = auto()
    ENEMY_TURN = auto()