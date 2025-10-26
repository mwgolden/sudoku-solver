from collections import defaultdict

from sudoku import SudokuPuzzle, Cell
from sudoku_logger import log_step

def hidden_singles_for_group(group: list[Cell]) -> list[tuple[Cell, int]]:
        """
        Identifies hidden singles in a group of cells (row, column, or box).
        A hidden single is a candidate that appears only once among the candidates
        of all cells in the group.
        Args:
            group (list[Cell]): List of cells in the group.
        Returns:
            list[tuple[Cell, int]]: List of tuples (cell, candidate) where
                                     candidate is a hidden single in that cell.
        """
        counts: dict[int, int] = dict()
        for cell in group:
            for candidate in cell.candidates:
                counts[candidate] = counts.get(candidate, 0) + 1
        
        hidden_singles = {candidate for candidate, count in counts.items() if count == 1}

        return [
            (cell, next(iter(cell.candidates & hidden_singles)))
            for cell in group if cell.candidates & hidden_singles
        ]
    
def hidden_singles_for_column(puzzle: SudokuPuzzle, col: int) -> list[tuple[Cell, int]]:
    """
    Identifies hidden singles in a specific column.
    Args:
        col (int): Column index (0-8).
    Returns:
        list[tuple[Cell, int]]: List of hidden singles in the column.
    """
    group = puzzle.col_at(col)
    return hidden_singles_for_group(group)

def hidden_singles_for_row(puzzle: SudokuPuzzle, row: int) -> list[tuple[Cell, int]]:
    """
    Identifies hidden singles in a specific row.
    Args:
        row (int): Row index (0-8).
    Returns:
        list[tuple[Cell, int]]: List of hidden singles in the row.
    """
    group = puzzle.row_at(row)
    return hidden_singles_for_group(group)

def hidden_singles_for_box(puzzle: SudokuPuzzle, box: int) -> list[tuple[Cell, int]]:
    """
    Identifies hidden singles in a specific box.
    Args:
        box (int): Box index (0-8).
    Returns:
        list[tuple[Cell, int]]: List of hidden singles in the box.
    """
    group = puzzle.box_at(box)
    return hidden_singles_for_group(group)