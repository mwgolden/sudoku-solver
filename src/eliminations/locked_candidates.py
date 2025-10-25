from sudoku import SudokuPuzzle
from enums import LockType
from sudoku_logger import log_step



def eliminate_locked_candidates(puzzle: SudokuPuzzle) -> bool:
        changes = False
        eliminations = []
        for i in range(9):
            eliminations += puzzle.locked_candidates_for_box(i)
            eliminations += puzzle.locked_candidates_for_column(i)
            eliminations += puzzle.locked_candidates_for_row(i)

        for elimination in eliminations:
            box, row_or_col, candidate, lock_type = elimination
            if lock_type == LockType.BOX_ROW_LOCK:
                row = puzzle.row_at(row_or_col)
                cells = [cell for cell in row if cell.box != box and candidate in cell.candidates]
                for cell in cells:
                    has_change = cell.eliminate_candidate(candidate)
                    changes = changes or has_change
                    log_step(f"'{candidate}' is locked to row {row_or_col}  inside box {box}. Eliminate candidate from Cell({cell.row}, {cell.col})")
            if lock_type == LockType.BOX_COL_LOCK:
                col = puzzle.col_at(row_or_col)
                cells = [cell for cell in col if cell.box != box and candidate in cell.candidates]
                for cell in cells:
                    has_change = cell.eliminate_candidate(candidate)
                    changes = changes or has_change
                    log_step(f"'{candidate}' is locked to column {row_or_col} inside box {box}. Eliminate candidate from Cell({cell.row}, {cell.col})")
            if lock_type == LockType.ROW_LOCK:
                bx = puzzle.box_at(box)
                cells = [cell for cell in bx if cell.row != row_or_col and candidate in cell.candidates]
                for cell in cells:
                    has_change = cell.eliminate_candidate(candidate)
                    changes = changes or has_change
                    log_step(f"'{candidate}' is locked to row {row_or_col}. Eliminate candidate '{candidate}' from Cell({cell.row}, {cell.col})")
            if lock_type == LockType.COL_LOCK:
                bx = puzzle.box_at(box)
                cells = [cell for cell in bx if cell.col != row_or_col and candidate in cell.candidates]
                for cell in cells:
                    has_change = cell.eliminate_candidate(candidate)
                    changes = changes or has_change
                    log_step(f"'{candidate}' is locked to column {row_or_col}. Eliminate candidate '{candidate}' from Cell({cell.row}, {cell.col})")

        return changes