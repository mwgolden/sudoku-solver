import numpy.typing as npt
import numpy as np

from dataclasses import dataclass, field

@dataclass
class Cell:
    row: int
    col: int
    box: int
    value: int = 0
    candidates: set[int] = field(default_factory=lambda: set(range(1, 10)))

    @property
    def is_solved(self) -> bool:
        return self.value > 0
    
    def eliminate_candidate(self, n: int) -> bool: 
        if n in self.candidates:
            self.candidates.remove(n)
            return True
        return False
    
    def set_value(self, n: int):
        self.value = n
        self.candidates = set()

class SudokuPuzzle:
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
    
    def cell_at(self, row: int, col: int) -> Cell:
        return self.grid[row, col]
    
    def row_at(self, row: int) -> list[Cell]:
        return list(self.grid[row, :])
    
    def col_at(self, col: int) -> list[Cell]:
        return list(self.grid[:, col])
    
    def box_at(self, box: int) -> list[Cell]:
        r0, c0 = (box // 3) * 3, (box % 3) * 3
        return [self.grid[r, c] for r in range(r0, r0+3) for c in range(c0, c0+3)]
    
    def excluded_at(self, cell: Cell) -> set:
        r = set([c.value for c in self.row_at(cell.row) if c.value > 0])
        c = set([c.value for c in self.col_at(cell.col) if c.value > 0])
        box = set([c.value for c in self.box_at(cell.box) if c.value > 0])
        to_exclude = r | c | box
        return to_exclude
    
    def set_candidates(self, cell: Cell):
        if cell.value == 0:
            exclusions = self.excluded_at(cell)
            candidates = set([1, 2, 3, 4, 5, 6, 7, 8, 9])
            cell.candidates = candidates - exclusions
    
    def populate_candidates(self):
        for row in self.grid:
            for cell in row:
                self.set_candidates(cell)
    
    def is_solved(self):
        mask = np.vectorize(lambda cell: not cell.is_solved)(self.grid)
        unsolved = self.grid[mask]
        return len(unsolved) == 0

    def get_singles(self):
        mask = np.vectorize(lambda cell: len(cell.candidates) == 1)(self.grid)
        return self.grid[mask]