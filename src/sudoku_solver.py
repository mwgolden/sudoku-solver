from sudoku import SudokuPuzzle
from sudoku_logger import log_step
from pprint import pprint
from enums import GroupType, LockType
from eliminations.naked_pairs import eliminate_naked_pairs
from eliminations.locked_candidates import eliminate_locked_candidates
from eliminations.utils import eliminate_candidate_for_group

class SudokuSolver:
    def __init__(self, puzzle: SudokuPuzzle):
        self.puzzle = puzzle
    
    def solve_singles(self):
        singles = self.puzzle.get_singles()
        for cell in singles:
            cell.set_value(next(iter(cell.candidates)))     
            log_step(f"Solve Cell({cell.row}, {cell.col}) with single; Solution: {cell.value}")        
            eliminate_candidate_for_group(self.puzzle, cell.row, cell.value, GroupType.ROW)
            eliminate_candidate_for_group(self.puzzle, cell.col, cell.value, GroupType.COL)
            eliminate_candidate_for_group(self.puzzle, cell.box, cell.value, GroupType.BOX)
        return len(singles) > 0
    
    def solve(self):
        log_step("Begin", self.puzzle)
        changed = True
        while changed:
            log_step("Resolve Singles")
            solved_singles = self.solve_singles()
            
            log_step("Eliminate Locked Candidates")
            eliminated_locked_candidates = eliminate_locked_candidates(self.puzzle)
            
            log_step("Eliminate Naked Pairs")
            eliminated_naked_pairs = eliminate_naked_pairs(self.puzzle)
            changed = solved_singles or eliminated_locked_candidates or eliminated_naked_pairs

            log_step("Current State", self.puzzle)

        log_step("End", self.puzzle)
        log_step(f"The puzzle is {'solved' if self.puzzle.is_solved() else 'not solved'}")
        log_step(f"The puzzle solution is {'valid' if self.puzzle.has_valid_solution() else 'invalid'}")

    