from sudoku import SudokuPuzzle
from sudoku_cell import Cell
from sudoku_logger import log_step


def eliminate_hidden_singles(puzzle: SudokuPuzzle):
    """
    Eliminates hidden singles from a row, column or box.
    """
    hidden_singles = []
    for i in range(9):
         hidden_singles += hidden_singles_for_row(puzzle, i)
         hidden_singles += hidden_singles_for_column(puzzle, i)
         hidden_singles += hidden_singles_for_box(puzzle, i)

    changed = False
    if hidden_singles:
         for cell, candidate in hidden_singles:
            to_keep = set()
            to_keep.add(candidate)
            if to_keep != cell.candidates:
                to_eliminate = cell.candidates - to_keep
                log_step(f"Hidden Single {candidate}: Eliminate candidates {to_eliminate} from Cell({cell.row}, {cell.col}){{{cell.candidates}}}")
                changed = cell.eliminate_candidates(to_eliminate)

    return changed

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