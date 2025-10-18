from sudoku import SudokuPuzzle, LockType
from sudoku_logger import log_step

class SudokuSolver:
    def __init__(self, puzzle: SudokuPuzzle):
        self.puzzle = puzzle
    
    def solve_singles(self):
        while True:
            singles = self.puzzle.get_singles()
            if len(singles) == 0: 
                break
            for cell in singles:
                cell.set_value(next(iter(cell.candidates)))     
                log_step(f"Solve Cell({cell.row}, {cell.col}) with single; Solution: {cell.value}", self.puzzle)        
            self.puzzle.populate_candidates()
            log_step(f"Update cell candidates", self.puzzle) 

    def eliminate_locked_candidates(self):
        eliminations = []
        for i in range(9):
            eliminations += self.puzzle.locked_candidates_for_box(i)
            eliminations += self.puzzle.locked_candidates_for_column(i)
            eliminations += self.puzzle.locked_candidates_for_row(i)

        for elimination in eliminations:
            box, row_or_col, candidate, lock_type = elimination
            if lock_type == LockType.ROW_LOCK:
                row = self.puzzle.row_at(row_or_col)
                cells = [cell for cell in row if cell.box != box and candidate in cell.candidates]
                for cell in cells:
                    cell.eliminate_candidate(candidate)
                    log_step(f"Eliminate candidate '{candidate}' from Cell({cell.row}, {cell.col})", self.puzzle)
            if lock_type == LockType.COL_LOCK:
                col = self.puzzle.col_at(row_or_col)
                cells = [cell for cell in col if cell.box != box and candidate in cell.candidates]
                for cell in cells:
                    cell.eliminate_candidate(candidate)
                    log_step(f"Eliminate candidate '{candidate}' from Cell({cell.row}, {cell.col})", self.puzzle)
            if lock_type == LockType.BOX_ROW_LOCK:
                box = self.puzzle.box_at(box)
                cells = [cell for cell in box if cell.row != row_or_col and candidate in cell.candidates]
                for cell in cells:
                    cell.eliminate_candidate(candidate)
                    log_step(f"Eliminate candidate '{candidate}' from Cell({cell.row}, {cell.col})", self.puzzle)
            if lock_type == LockType.BOX_COL_LOCK:
                box = self.puzzle.box_at(box)
                cells = [cell for cell in box if cell.col != row_or_col and candidate in cell.candidates]
                for cell in cells:
                    cell.eliminate_candidate(candidate)
                    log_step(f"Eliminate candidate '{candidate}' from Cell({cell.row}, {cell.col})", self.puzzle)

    
    def solve(self):
        log_step("Begin", self.puzzle)
        self.solve_singles()
        self.eliminate_locked_candidates()
        self.solve_singles()
        self.eliminate_locked_candidates()
        log_step("End", self.puzzle)

    