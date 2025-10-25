import numpy.typing as npt
import numpy as np

from dataclasses import dataclass, field

from enums import LockType

@dataclass
class Cell:
    """
    Represents a single cell in a Sudoku grid.

    Attributes:
        row (int): Row index (0-8).
        col (int): Column index (0-8).
        box (int): Box index (0-8).
        value (int): Current value of the cell (0 if unsolved).
        candidates (set[int]): Possible candidate values for this cell.
        eliminated_candidates (set[int]): Candidates removed via solving techniques.
    """
    row: int
    col: int
    box: int
    value: int = 0
    candidates: set[int] = field(default_factory=lambda: set(range(1, 10)))
    eliminated_candidates: set[int] = field(default_factory=lambda: set())

    @property
    def is_solved(self) -> bool:
        """Returns True if the cell has a value assigned (i.e., is solved)."""
        return self.value > 0
    
    def eliminate_candidate(self, n: int) -> bool: 
        """
        Eliminates a candidate value from this cell.

        Args:
            n (int): The candidate to remove.

        Returns:
            bool: True if the candidate was removed, False if it was not present.

        Side Effects:
            - Adds the eliminated candidate to `eliminated_candidates`.
            - Does nothing if the candidate was already removed or cell is solved.
        """
        if n in self.candidates:
            self.candidates.remove(n)
            self.eliminated_candidates.add(n)
            return True
        return False
    
    def eliminate_candidates(self, s: set[int]) -> bool: 
        """
        Eliminates all candidate values in a set from this cell.

        Args:
            s (set[int]): Set of candidates to remove.

        Returns:
            bool: True if any candidate was removed, False if none were present.

        Side Effects:
            - Adds the eliminated candidates to `eliminated_candidates`.
            - Does nothing if the candidates were already removed or cell is solved.
        """
        has_eliminations = False
        for n in s:
            if n in self.candidates:
                self.candidates.remove(n)
                self.eliminated_candidates.add(n)
                has_eliminations =  True
        return has_eliminations
    
    def set_value(self, n: int):
        """
        Sets the value of the cell and clears its candidates.

        Args:
            n (int): Value to assign to the cell.

        Side Effects:
            - Clears all remaining candidates.
            - Clears all eliminated candidates
            - Does not propagate updates to other cells (caller must handle that).
        """
        self.value = n
        self.candidates = set()
        self.eliminated_candidates = set()

class SudokuPuzzle:
    """
    Represents a Sudoku puzzle and provides methods to help solve it
    using logical techniques like finding singles and locked candidates.

    Attributes:
        grid (np.ndarray): 9x9 array of Cell objects.
    """
    ALL_VALUES = set(range(1, 10))

    def __init__(self, arr: npt.NDArray[np.int8]):
        """
        Initializes a Sudoku puzzle from a 9x9 numpy array.

        Args:
            arr (np.ndarray): 9x9 integer array representing the puzzle
                              (0 indicates unsolved cells).

        Raises:
            ValueError: If the input array is not 9x9.
        """
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

    def is_solved(self) -> bool:
        """
        Returns a boolean value indicating whether all cells in the sudoku grid are solved.

        Returns:
            bool: True if all cells are solved, otherwise false
        """
        for row in self.grid:
            for cell in row:
                if not cell.is_solved:
                    return False
        return True
    
    def has_valid_solution(self) -> bool:
        """
        Returns a boolean value if all cells in the sodoku grid are solved and the solution is valid, 
        i.e. numbers 1 - 9 do not repeat for a given row, column or box. 

        Returns:
            bool: True if the grid has a valid solution, otherwise false
        """
        if not self.is_solved():
            return False
        
        for row in self.grid:
            for cell in row:
                r = {item.value for item in self.row_at(cell.row) if item != cell}
                c = {item.value for item in self.col_at(cell.col) if item != cell}
                b = {item.value for item in self.box_at(cell.box) if item != cell}
                if cell.value in r | b | c:
                    return False 

        return True

    def current_frame(self) -> npt.NDArray[np.int8]:
        """
        Returns the current numerical state of the puzzle as a 9x9 array.

        Returns:
            np.ndarray: 9x9 array of integers representing cell values (0 if unsolved).
        """
        frame = [[col.value for col in row] for row in self.grid]
        return np.array(frame, dtype=np.int8)
    
    def cell_at(self, row: int, col: int) -> Cell:
        """
        Returns the Cell object at a specific row and column.

        Args:
            row (int): Row index (0-8).
            col (int): Column index (0-8).

        Returns:
            Cell: The cell at the specified position.
        """
        return self.grid[row, col]
    
    def row_at(self, row: int) -> list[Cell]:
        """
        Returns all cells in a specific row.

        Args:
            row (int): Row index (0-8).

        Returns:
            list[Cell]: List of 9 cells in the row.
        """
        return list(self.grid[row, :])
    
    def col_at(self, col: int) -> list[Cell]:
        """
        Returns all cells in a specific column.

        Args:
            col (int): Column index (0-8).

        Returns:
            list[Cell]: List of 9 cells in the column.
        """
        return list(self.grid[:, col])
    
    def box_at(self, box: int) -> list[Cell]:
        """
        Returns all cells in a specific 3x3 box.

        Args:
            box (int): Box index (0-8).

        Returns:
            list[Cell]: List of 9 cells in the box.
        """
        r0, c0 = (box // 3) * 3, (box % 3) * 3
        return [self.grid[r, c] for r in range(r0, r0+3) for c in range(c0, c0+3)]
    
    def excluded_at(self, cell: Cell) -> set[int]:
        """
        Computes values that cannot appear in a given cell due to Sudoku rules.

        Args:
            cell (Cell): The cell for which to compute exclusions.

        Returns:
            set[int]: Set of values already used in the cell's row, column,
                      box, or previously eliminated from the cell.
        """
        r = set([c.value for c in self.row_at(cell.row) if c.is_solved])
        c = set([c.value for c in self.col_at(cell.col) if c.is_solved])
        box = set([c.value for c in self.box_at(cell.box) if c.is_solved])
        to_exclude = r | c | box | cell.eliminated_candidates
        return to_exclude
    
    def set_candidates(self, cell: Cell):
        """
        Updates the candidate set for a single cell based on current exclusions.

        Args:
            cell (Cell): The cell to update.
        """
        if cell.value == 0:
            exclusions = self.excluded_at(cell)
            cell.candidates = self.ALL_VALUES - exclusions
    
    def populate_candidates(self):
        """Populates candidates for all cells in the puzzle."""
        for row in self.grid:
            for cell in row:
                self.set_candidates(cell)
    
    def is_solved(self) -> bool:
        """
        Checks if the puzzle is completely solved.

        Returns:
            bool: True if all cells have a value assigned.
        """
        return all(cell.is_solved for row in self.grid for cell in row)

    def get_singles(self) -> list[Cell]:
        """
        Returns all cells that have only one remaining candidate.

        Returns:
            list[Cell]: List of cells that can be solved immediately.
        """
        return [cell for row in self.grid for cell in row if len(cell.candidates) == 1]
    
    def hidden_singles_for_group(self, group: list[Cell]) -> list[tuple[Cell, int]]:
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
    
    def hidden_singles_for_column(self, col: int) -> list[tuple[Cell, int]]:
        """
        Identifies hidden singles in a specific column.

        Args:
            col (int): Column index (0-8).

        Returns:
            list[tuple[Cell, int]]: List of hidden singles in the column.
        """
        group = self.col_at(col)
        return self.hidden_singles_for_group(group)

    def hidden_singles_for_row(self, row: int) -> list[tuple[Cell, int]]:
        """
        Identifies hidden singles in a specific row.

        Args:
            row (int): Row index (0-8).

        Returns:
            list[tuple[Cell, int]]: List of hidden singles in the row.
        """
        group = self.row_at(row)
        return self.hidden_singles_for_group(group)
    
    def hidden_singles_for_box(self, box: int) -> list[tuple[Cell, int]]:
        """
        Identifies hidden singles in a specific box.

        Args:
            box (int): Box index (0-8).

        Returns:
            list[tuple[Cell, int]]: List of hidden singles in the box.
        """
        group = self.box_at(box)
        return self.hidden_singles_for_group(group)
    
    def locked_candidates_for_box(self, box: int): 
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
                locked_candidates.append((box, next(iter(rows)), candidate, LockType.BOX_ROW_LOCK))
            if len(cols) == 1: # candidate is locked to column
                locked_candidates.append((box, next(iter(cols)), candidate, LockType.BOX_COL_LOCK))


        return locked_candidates
    
    def locked_candidates_for_column(self, col: int):
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
                locked_candidates.append((next(iter(boxes)), col, candidate, LockType.COL_LOCK))
        
        return locked_candidates
    
    def locked_candidates_for_row(self, row: int):
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
                locked_candidates.append((next(iter(boxes)), row, candidate, LockType.ROW_LOCK))
        
        return locked_candidates
    
    def naked_pairs_for_group(self, group: list[Cell]) -> list[tuple[Cell, Cell]]:
        """
        Identifies naked pairs in a row, column or box. 

        Candidates in a naked pair can be eliminated from other cells in the group. 

        Args:
            group list[Cell]:  group of cells from row, column or box

        Returns:
            list[tuple[Cell, Cell]]: Tuples of cells for each naked pair found in group
        """
        pairs = [cell for cell in group if len(cell.candidates) == 2]
        counts = dict()
        for cell in pairs:
            counts[tuple(sorted(cell.candidates))] = counts.get(tuple(sorted(cell.candidates)), 0) + 1

        valid_pairs = [set(candidates) for candidates, count in counts.items() if count == 2]

        naked_pairs = [
            tuple(c for c in group if c.candidates == p)
            for p in valid_pairs
        ]

        return naked_pairs

    def naked_pairs_for_row(self, row: int):
        group = self.row_at(row)
        return self.naked_pairs_for_group(group)
    
    def naked_pairs_for_col(self, col: int):
        group = self.col_at(col)
        return self.naked_pairs_for_group(group)
    
    def naked_pairs_for_box(self, box: int):
        group = self.box_at(box)
        return self.naked_pairs_for_group(group)

    def __str__(self) -> str:
        def cell_str(cell: Cell) -> list[str]:
            """Return 4 lines representing cell contents"""
            if cell.is_solved:
                val = str(cell.value)
                return [f" {val} ", "", "", "" ]  
            
            str_candidates = ",".join([str(val) for val in sorted(list(cell.candidates))])
            str_eliminated = ",".join([str(val) for val in sorted(list(cell.eliminated_candidates))])
            return ["   ", str_candidates, str_eliminated, f"({cell.row}, {cell.col})" ]  
        

        unsolved_str = "Cell:{coord}; Candidates: {candidates}; Eliminated: {eliminated}"
        # Unicode Box drawing characters
        V = "│"
        PV = "║"
        BH = "═"*3 
        H3 = "─"*3
        ROW_DIV = f"   ╟{H3}┼{H3}┼{H3}╫{H3}┼{H3}┼{H3}╫{H3}┼{H3}┼{H3}╢"
        BOX_DIV = f"   ╠{BH}╪{BH}╪{BH}╬{BH}╪{BH}╪{BH}╬{BH}╪{BH}╪{BH}╣"
        TC =  f"     0   1   2   3   4   5   6   7   8 "
        TOP = f"   ╔{BH}╤{BH}╤{BH}╦{BH}╤{BH}╤{BH}╦{BH}╤{BH}╤{BH}╗"
        BOT = f"   ╚{BH}╧{BH}╧{BH}╩{BH}╧{BH}╧{BH}╩{BH}╧{BH}╧{BH}╝" 

        # Draw grid
        lines_out = [TC]
        lines_out += [TOP]
        unsolved_details = []
        for i, row in enumerate(self.grid):
            cell_strs = [cell_str(cell) for cell in row]
            line = f"{ i }  ║"
            for j, cell in enumerate(cell_strs):
                if len(cell[0].strip()) == 0:
                    unsolved_details.append(unsolved_str.format(coord=cell[3], candidates=cell[1], eliminated=cell[2]))
                line += f"{cell[0]}"
                if j % 3 == 2:
                    line += PV
                else:
                    line += V
            lines_out += [line]
            if i == 8:
                lines_out += [BOT]
            elif i % 3 == 2:
                lines_out += [BOX_DIV]
            else:
                lines_out += [ROW_DIV]

        lines_out += ["\n\n"]
        lines_out += unsolved_details
        return "\n".join(lines_out)

        