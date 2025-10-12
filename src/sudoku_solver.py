from sudoku import SudokuPuzzle

class SudokuSolver:
    def __init__(self, puzzle: SudokuPuzzle):
        self.puzzle = puzzle
    
    def solve_singles(self):
        while True:
            singles = self.puzzle.get_singles()
            if len(singles) == 0: 
                break
            for cell in singles:
                cell.set_value(cell.candidates.pop())             
            self.puzzle.populate_candidates()

    