import numpy.typing as npt
import numpy as np

from enums import GroupType

from sudoku_cell import Cell

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
    
    def group_for_loc(self, loc: int, group_type: GroupType) -> list[Cell]:
        if group_type == GroupType.ROW:
            return self.row_at(loc)
        elif group_type == GroupType.COL:
            return self.col_at(loc)
        elif group_type == GroupType.BOX:
            return self.box_at(loc)
        else:
            raise ValueError(f"Invalid group_type: {group_type}")


    def group_for_cell(self, cell: Cell, group_type: GroupType) -> list[Cell]:
        if group_type == GroupType.ROW:
            return self.row_at(cell.row)
        elif group_type == GroupType.COL:
            return self.col_at(cell.col)
        elif group_type == GroupType.BOX:
            return self.box_at(cell.box)
        else:
            raise ValueError(f"Invalid group_type: {group_type}")

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

        