from sudoku import SudokuPuzzle
from sudoku_logger import log_step
from enums import GroupType

def eliminate_candidate_for_group(puzzle: SudokuPuzzle, r: int, candidate: int, group_type: GroupType):
        group = puzzle.group_for_loc(r, group_type)
        for cell in group:
            if candidate in cell.candidates:
                cell.eliminate_candidate(candidate)
                log_step(f"Cell ({cell.row}, {cell.col}): Eliminate candidate '{candidate}'")