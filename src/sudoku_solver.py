from sudoku import SudokuPuzzle, LockType
from sudoku_logger import log_step

class SudokuSolver:
    def __init__(self, puzzle: SudokuPuzzle):
        self.puzzle = puzzle
    
    def solve_singles(self):
        singles = self.puzzle.get_singles()
        for cell in singles:
            cell.set_value(next(iter(cell.candidates)))     
            log_step(f"Solve Cell({cell.row}, {cell.col}) with single; Solution: {cell.value}")        
            self.eliminate_candidates_for_row(cell.row, cell.value)
            self.eliminate_candidates_for_col(cell.col, cell.value)
            self.eliminate_candidates_for_box(cell.box, cell.value)
        return len(singles) > 0


    def eliminate_candidates_for_row(self, r: int, candidate: int):
        row = self.puzzle.row_at(r)
        for cell in row:
            if candidate in cell.candidates:
                cell.eliminate_candidate(candidate)  
                log_step(f"Cell ({cell.row}, {cell.col}): Eliminate candidate '{candidate}'")

    def eliminate_candidates_for_col(self, c: int, candidate: int):
        col = self.puzzle.col_at(c)
        for cell in col:
            if candidate in cell.candidates:
                cell.eliminate_candidate(candidate)
                log_step(f"Cell ({cell.row}, {cell.col}): Eliminate candidate '{candidate}'")  

    def eliminate_candidates_for_box(self, b: int, candidate: int):
        box = self.puzzle.box_at(b)
        for cell in box:
            if candidate in cell.candidates:
                cell.eliminate_candidate(candidate)  
                log_step(f"Cell ({cell.row}, {cell.col}): Eliminate candidate '{candidate}'")

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
                    log_step(f"Eliminate candidate '{candidate}' from Cell({cell.row}, {cell.col})")
            if lock_type == LockType.COL_LOCK:
                col = self.puzzle.col_at(row_or_col)
                cells = [cell for cell in col if cell.box != box and candidate in cell.candidates]
                for cell in cells:
                    cell.eliminate_candidate(candidate)
                    log_step(f"Eliminate candidate '{candidate}' from Cell({cell.row}, {cell.col})")
            if lock_type == LockType.BOX_ROW_LOCK:
                box = self.puzzle.box_at(box)
                cells = [cell for cell in box if cell.row != row_or_col and candidate in cell.candidates]
                for cell in cells:
                    cell.eliminate_candidate(candidate)
                    log_step(f"Eliminate candidate '{candidate}' from Cell({cell.row}, {cell.col})")
            if lock_type == LockType.BOX_COL_LOCK:
                box = self.puzzle.box_at(box)
                cells = [cell for cell in box if cell.col != row_or_col and candidate in cell.candidates]
                for cell in cells:
                    cell.eliminate_candidate(candidate)
                    log_step(f"Eliminate candidate '{candidate}' from Cell({cell.row}, {cell.col})")

    
    def solve(self):
        log_step("Begin", self.puzzle)
        changed = True
        while changed:
            changed = self.solve_singles()
            log_step("Singles Updated", self.puzzle)
            self.eliminate_locked_candidates()
            log_step("Eliminations Completed", self.puzzle)
        log_step("End", self.puzzle)
        log_step(f"The puzzle is {'solved' if self.puzzle.is_solved() else 'not solved'}")
        log_step(f"The puzzle solution is {'valid' if self.puzzle.has_valid_solution() else 'invalid'}")

    