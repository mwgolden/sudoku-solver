from enum import Enum

class GroupType(Enum):
    """
        Enumerate types of groups in a sudoku grid
    """
    ROW = 1
    COL = 2
    BOX = 3

class LockType(Enum):
    """Enumeration of locked candidate types used in Sudoku solving."""
    ROW_LOCK = 1
    COL_LOCK = 2
    BOX_ROW_LOCK = 3
    BOX_COL_LOCK = 4