import numpy.typing as npt
import numpy as np

from dataclasses import dataclass, field

from enum import Enum

class LockType(Enum):
    ROW_LOCK = 1
    COL_LOCK = 2
    BOX_ROW_LOCK = 3
    BOX_COL_LOCK = 4

@dataclass
class Cell:
    row: int
    col: int
    box: int
    value: int = 0
    candidates: set[int] = field(default_factory=lambda: set(range(1, 10)))
    eliminated_candidates: set[int] = field(default_factory=lambda: set())

    @property
    def is_solved(self) -> bool:
        return self.value > 0
    
    def eliminate_candidate(self, n: int) -> bool: 
        if n in self.candidates:
            self.candidates.remove(n)
            self.eliminated_candidates.add(n)
            return True
        return False
    
    def set_value(self, n: int):
        self.value = n
        self.candidates = set()

class SudokuPuzzle:
    ALL_VALUES = set(range(1, 10))

    def __init__(self, arr: npt.NDArray[np.int8]):
        if arr.shape != (9, 9):
            raise ValueError("Sudoku grid must be 9x9")
        self.grid = np.empty((9, 9), dtype=object)
        for row in range(9):
            for col in range(9):
                box = (row // 3) * 3 + (col // 3)
                val = int(arr[row, col])
                cell = Cell(row=row, col=col, box=box)
                if val > 0:
                    cell.set_value(val)
                self.grid[row, col] = cell
        self.populate_candidates()

    def current_frame(self) -> npt.NDArray[np.int8]:
        frame = [[col.value for col in row] for row in self.grid]
        return np.array(frame, dtype=np.int8)
    
    def cell_at(self, row: int, col: int) -> Cell:
        return self.grid[row, col]
    
    def row_at(self, row: int) -> list[Cell]:
        return list(self.grid[row, :])
    
    def col_at(self, col: int) -> list[Cell]:
        return list(self.grid[:, col])
    
    def box_at(self, box: int) -> list[Cell]:
        r0, c0 = (box // 3) * 3, (box % 3) * 3
        return [self.grid[r, c] for r in range(r0, r0+3) for c in range(c0, c0+3)]
    
    def excluded_at(self, cell: Cell) -> set[int]:
        r = set([c.value for c in self.row_at(cell.row) if c.is_solved])
        c = set([c.value for c in self.col_at(cell.col) if c.is_solved])
        box = set([c.value for c in self.box_at(cell.box) if c.is_solved])
        to_exclude = r | c | box | cell.eliminated_candidates
        return to_exclude
    
    def set_candidates(self, cell: Cell):
        if cell.value == 0:
            exclusions = self.excluded_at(cell)
            cell.candidates = self.ALL_VALUES - exclusions
    
    def populate_candidates(self):
        for row in self.grid:
            for cell in row:
                self.set_candidates(cell)
    
    def is_solved(self) -> bool:
        return all(cell.is_solved for row in self.grid for cell in row)

    def get_singles(self) -> list[Cell]:
        return [cell for row in self.grid for cell in row if len(cell.candidates) == 1]
    
    def hidden_singles_for_group(self, group: list[Cell]) -> list[tuple[Cell, int]]:
        counts: dict[int, int] = dict()
        for cell in group:
            for candidate in cell.candidates:
                counts[candidate] = counts.get(candidate, 0) + 1
        
        hidden_singles = {candidate for candidate, count in counts.items() if count == 1}

        return [
            (cell, next(iter(cell.candidates & hidden_singles)))
            for cell in group if cell.candidates & hidden_singles
        ]
    
    def hidden_singles_for_column(self, col: int) -> list[tuple[Cell, int]]:
        group = self.col_at(col)
        return self.hidden_singles_for_group(group)

    def hidden_singles_for_row(self, row: int) -> list[tuple[Cell, int]]:
        group = self.row_at(row)
        return self.hidden_singles_for_group(group)
    
    def hidden_singles_for_box(self, box: int) -> list[tuple[Cell, int]]:
        group = self.box_at(box)
        return self.hidden_singles_for_group(group)
    
    def locked_candidates_for_box(self, box: int): 
        """
            Identify candidates confined to a single row or column inside a box.
            Elimination happens outside the box for a row or column, i.e. the 
            candidate can be eliminated from other cells in the same row or 
            column outside the given box.

            Returns a list of tuples describing box-row or box-column locks:
            (box, row_or_col, candidate, "row_lock" | "col_lock")
        """
        cells = self.box_at(box)
        all_candidates = set()

        for cell in cells:
            all_candidates |= cell.candidates

        locked_candidates = []
        for candidate in all_candidates:
            cells_with_candidate = [cell for cell in cells if candidate in cell.candidates]
            rows = {cell.row for cell in cells_with_candidate}
            cols = {cell.col for cell in cells_with_candidate}
            if len(rows) == 1: #candidate is locked to row
                locked_candidates.append((box, next(iter(rows)), candidate, LockType.ROW_LOCK))
            if len(cols) == 1: # candidate is locked to column
                locked_candidates.append((box, next(iter(cols)), candidate, LockType.COL_LOCK))


        return locked_candidates
    
    def locked_candidates_for_column(self, col: int):
        """
            Identify candidates in a column confined to a single box.
            Elimination happens inside the box for a column, i.e. the 
            candidate can be eliminated from other cells in the same 
            column within the same box. 

            Returns a list of tuples describing box-column locks:
            (box, col, candidate, "box_col_lock")
        """
        cells = self.col_at(col)
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
                locked_candidates.append((next(iter(boxes)), col, candidate, LockType.BOX_COL_LOCK))
        
        return locked_candidates
    
    def locked_candidates_for_row(self, row: int):
        """
            Identify candidates in a row confined to a single box.
            Elimination happens outside the box for a row, i.e. the 
            candidate can be eliminated from other cells in the same 
            row within the same box. 


            Returns a list of tuples describing box-column locks:
            (box, row, candidate, "box_row_lock")
        """
        cells = self.row_at(row)
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
                locked_candidates.append((next(iter(boxes)), row, candidate, LockType.BOX_ROW_LOCK))
        
        return locked_candidates
        
