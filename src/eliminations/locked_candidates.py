from sudoku import SudokuPuzzle
from enums import LockType
from sudoku_logger import log_step



def eliminate_locked_candidates(puzzle: SudokuPuzzle) -> bool:
        changes = False
        eliminations = []
        for i in range(9):
            eliminations += locked_candidates_for_box(puzzle, i)
            eliminations += locked_candidates_for_column(puzzle, i)
            eliminations += locked_candidates_for_row(puzzle, i)

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

def locked_candidates_for_box(puzzle: SudokuPuzzle, box: int): 
        """
        Identifies candidates confined to a single row or column inside a box (pointing).

        Candidates restricted to a row/column within a box can be eliminated
        from other cells in that row/column outside the box.

        Args:
            box (int): Box index (0-8).

        Returns:
            list[tuple[int, int, int, LockType]]: Tuples describing locked candidates:
                (box, row_or_col, candidate, LockType.ROW_LOCK | LockType.COL_LOCK)
        """
        cells = puzzle.box_at(box)
        all_candidates = set()

        for cell in cells:
            all_candidates |= cell.candidates

        locked_candidates = []
        for candidate in all_candidates:
            cells_with_candidate = [cell for cell in cells if candidate in cell.candidates]
            rows = {cell.row for cell in cells_with_candidate}
            cols = {cell.col for cell in cells_with_candidate}
            if len(rows) == 1: #candidate is locked to row
                locked_candidates.append((box, next(iter(rows)), candidate, LockType.BOX_ROW_LOCK))
            if len(cols) == 1: # candidate is locked to column
                locked_candidates.append((box, next(iter(cols)), candidate, LockType.BOX_COL_LOCK))


        return locked_candidates
    
def locked_candidates_for_column(puzzle: SudokuPuzzle, col: int):
        """
        Identifies candidates in a column confined to a single box (claiming).

        Candidates restricted to a box within a column can be eliminated from
        other cells in that box.

        Args:
            col (int): Column index (0-8).

        Returns:
            list[tuple[int, int, int, LockType]]: Tuples describing locked candidates:
                (box, col, candidate, LockType.BOX_COL_LOCK)
        """
        cells = puzzle.col_at(col)
        all_candidates = set()

        # get all candidates in a column
        for cell in cells:
            all_candidates |= cell.candidates

        locked_candidates = []
        for candidate in all_candidates:
            # filter all cells for a candidate
            cells_with_candidate = [cell for cell in cells if candidate in cell.candidates]
            # find which boxes these cells belong to
            boxes = {cell.box for cell in cells_with_candidate}
            if len(boxes) == 1: 
                locked_candidates.append((next(iter(boxes)), col, candidate, LockType.COL_LOCK))
        
        return locked_candidates
    
def locked_candidates_for_row(puzzle: SudokuPuzzle, row: int):
        """
        Identifies candidates in a row confined to a single box (claiming).

        Candidates restricted to a box within a row can be eliminated from
        other cells in that box.

        Args:
            row (int): Row index (0-8).

        Returns:
            list[tuple[int, int, int, LockType]]: Tuples describing locked candidates:
                (box, row, candidate, LockType.BOX_ROW_LOCK)
        """
        cells = puzzle.row_at(row)
        all_candidates = set()

        # get all candidates in a column
        for cell in cells:
            all_candidates |= cell.candidates

        locked_candidates = []
        for candidate in all_candidates:
            # filter all cells for a candidate
            cells_with_candidate = [cell for cell in cells if candidate in cell.candidates]
            # find which boxes these cells belong to
            boxes = {cell.box for cell in cells_with_candidate}
            if len(boxes) == 1: 
                locked_candidates.append((next(iter(boxes)), row, candidate, LockType.ROW_LOCK))
        
        return locked_candidates