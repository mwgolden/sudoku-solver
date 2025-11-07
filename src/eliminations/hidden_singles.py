from sudoku import SudokuPuzzle
from sudoku_cell import Cell
from sudoku_logger import log_step
from enums import GroupType


def eliminate_hidden_singles(puzzle: SudokuPuzzle):
    """
    Eliminates hidden singles from a row, column or box.
    """
    group_types = [GroupType.ROW, GroupType.COL, GroupType.BOX]
    hidden_singles = []
    for i in range(9):
         for group_type in group_types:
            group = puzzle.group_for_loc(i, group_type)
            hidden_singles += hidden_singles_for_group(group)

    if not hidden_singles:
        return False

    changed = False
    for cell, candidate in hidden_singles:
        to_keep = {candidate}
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
