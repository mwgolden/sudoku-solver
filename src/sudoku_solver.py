from sudoku import SudokuPuzzle
from sudoku_logger import log_step
from enums import GroupType
from eliminations.locked_candidates import eliminate_locked_candidates
from eliminations.hidden_singles import eliminate_hidden_singles
from eliminations.naked_subsets import eliminate_naked_pairs, eliminate_naked_triples, eliminate_naked_quads
from eliminations.utils import eliminate_candidate_for_group
import copy

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
    
    def backtrack(self, cell):
        if self.puzzle.is_solved():
            return True
        
        for candidate in cell.candidates:
            new_puzzle = copy.deepcopy(self.puzzle)
            new_puzzle.cell_at(cell.row, cell.col).set_value(candidate)
            new_solver = SudokuSolver(new_puzzle)
            log_step(f"Try candidate {candidate} in Cell:({cell.row}, {cell.col})")
            new_solver.solve()
            if new_puzzle.is_solved() and new_puzzle.has_valid_solution():
                self.puzzle.grid = new_puzzle.grid
                return True
            log_step(f"Backtracking from Cell:({cell.row}, {cell.col}) = {candidate}")
            
        return False

        

    def solve(self):
        log_step("Begin", self.puzzle)
        changed = True
        while changed:
            log_step("Find and Resolve Singles")
            solved_singles = self.solve_singles()

            log_step("Find and Eliminate Hidden Singles")
            eliminated_hidden_singles = eliminate_hidden_singles(self.puzzle)
            
            log_step("Find and Eliminate Locked Candidates")
            eliminated_locked_candidates = eliminate_locked_candidates(self.puzzle)
            
            log_step("Find and Eliminate Naked Pairs")
            eliminated_naked_pairs = eliminate_naked_pairs(self.puzzle)

            log_step("Find and Eliminate Naked Triples")
            eliminated_naked_triples = eliminate_naked_triples(self.puzzle)

            log_step("Find and Eliminate Naked Quads")
            eliminated_naked_quads = eliminate_naked_quads(self.puzzle)
            

            changed = solved_singles or eliminated_locked_candidates or eliminated_hidden_singles or eliminated_naked_pairs or eliminated_naked_triples or eliminated_naked_quads
            log_step("Current State", self.puzzle)
        
        solved = self.puzzle.is_solved()
        log_step(f"The puzzle is {'solved' if solved else 'not solved'}")
        if not solved:
            unsolved_cells = [cell for row in self.puzzle.grid for cell in row if not cell.is_solved]
            log_step("Begin backtracking")
            for cell in unsolved_cells:
                self.backtrack(cell)


        log_step("End", self.puzzle)
        
        log_step(f"The puzzle solution is {'valid' if self.puzzle.has_valid_solution() else 'invalid'}")

    