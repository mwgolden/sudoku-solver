from sudoku import SudokuPuzzle, Cell
from sudoku_logger import log_step
from collections import defaultdict
from pprint import pprint
from enums import GroupType, LockType

class SudokuSolver:
    def __init__(self, puzzle: SudokuPuzzle):
        self.puzzle = puzzle
    
    def solve_singles(self):
        singles = self.puzzle.get_singles()
        for cell in singles:
            cell.set_value(next(iter(cell.candidates)))     
            log_step(f"Solve Cell({cell.row}, {cell.col}) with single; Solution: {cell.value}")        
            self.eliminate_candidate_for_group(cell.row, cell.value, GroupType.ROW)
            self.eliminate_candidate_for_group(cell.col, cell.value, GroupType.COL)
            self.eliminate_candidate_for_group(cell.box, cell.value, GroupType.BOX)
        return len(singles) > 0

    def eliminate_candidate_for_group(self, r: int, candidate: int, group_type: GroupType):
        group = self.group_for_loc(r, group_type)
        for cell in group:
            if candidate in cell.candidates:
                cell.eliminate_candidate(candidate)
                log_step(f"Cell ({cell.row}, {cell.col}): Eliminate candidate '{candidate}'")

    def eliminate_locked_candidates(self) -> bool:
        changes = False
        eliminations = []
        for i in range(9):
            eliminations += self.puzzle.locked_candidates_for_box(i)
            eliminations += self.puzzle.locked_candidates_for_column(i)
            eliminations += self.puzzle.locked_candidates_for_row(i)

        for elimination in eliminations:
            box, row_or_col, candidate, lock_type = elimination
            if lock_type == LockType.BOX_ROW_LOCK:
                row = self.puzzle.row_at(row_or_col)
                cells = [cell for cell in row if cell.box != box and candidate in cell.candidates]
                for cell in cells:
                    has_change = cell.eliminate_candidate(candidate)
                    changes = changes or has_change
                    log_step(f"'{candidate}' is locked to row {row_or_col}  inside box {box}. Eliminate candidate from Cell({cell.row}, {cell.col})")
            if lock_type == LockType.BOX_COL_LOCK:
                col = self.puzzle.col_at(row_or_col)
                cells = [cell for cell in col if cell.box != box and candidate in cell.candidates]
                for cell in cells:
                    has_change = cell.eliminate_candidate(candidate)
                    changes = changes or has_change
                    log_step(f"'{candidate}' is locked to column {row_or_col} inside box {box}. Eliminate candidate from Cell({cell.row}, {cell.col})")
            if lock_type == LockType.ROW_LOCK:
                bx = self.puzzle.box_at(box)
                cells = [cell for cell in bx if cell.row != row_or_col and candidate in cell.candidates]
                for cell in cells:
                    has_change = cell.eliminate_candidate(candidate)
                    changes = changes or has_change
                    log_step(f"'{candidate}' is locked to row {row_or_col}. Eliminate candidate '{candidate}' from Cell({cell.row}, {cell.col})")
            if lock_type == LockType.COL_LOCK:
                bx = self.puzzle.box_at(box)
                cells = [cell for cell in bx if cell.col != row_or_col and candidate in cell.candidates]
                for cell in cells:
                    has_change = cell.eliminate_candidate(candidate)
                    changes = changes or has_change
                    log_step(f"'{candidate}' is locked to column {row_or_col}. Eliminate candidate '{candidate}' from Cell({cell.row}, {cell.col})")

        return changes
    
    def group_for_loc(self, n: int, group_type: GroupType) -> list[Cell]:
        if group_type == GroupType.ROW:
            return self.puzzle.row_at(n)
        if group_type == GroupType.COL:
            return self.puzzle.col_at(n)
        if group_type == GroupType.BOX:
            return self.puzzle.box_at(n)


    def group_for_cell(self, cell: Cell, group_type: GroupType) -> list[Cell]:
        if group_type == GroupType.ROW:
            return self.puzzle.row_at(cell.row)
        if group_type == GroupType.COL:
            return self.puzzle.col_at(cell.col)
        if group_type == GroupType.BOX:
            return self.puzzle.box_at(cell.box)
        
    def naked_pairs_for_group(self, group_type, n):
        if group_type == GroupType.ROW:
            return self.puzzle.naked_pairs_for_row(n)
        if group_type == GroupType.COL:
            return self.puzzle.naked_pairs_for_col(n)
        if group_type == GroupType.BOX:
            return self.puzzle.naked_pairs_for_box(n)
        
    def eliminate_candidates_from_group(self, eliminations: tuple[GroupType, list[Cell], list[Cell], set[int]]) -> bool:
        changed = False
        group_type, cells_to_keep, group, candidates = eliminations
        for cell in group:
            if cell not in cells_to_keep:
                to_remove =  candidates & cell.candidates
                if to_remove:
                    log_step(f"Naked Pair ({group_type.name}): Eliminate candidates {candidates} from Cell({cell.row}, {cell.col}){{{cell.candidates}}}")
                    cell.eliminate_candidates(candidates)
                    changed = True
        return changed
                

    def eliminate_naked_pairs(self) -> bool:
        group_types = [GroupType.ROW, GroupType.COL, GroupType.BOX]
        naked_pairs = defaultdict(list)
        for i in range(9):
            for group_type in group_types:
                naked_pairs[group_type] += self.naked_pairs_for_group(group_type, i)

        changed = False
        for group_type, pairs in naked_pairs.items():
            for cell1, cell2 in pairs:
                group = self.group_for_cell(cell1, group_type)
                has_change = self.eliminate_candidates_from_group((group_type, [cell1, cell2], group, cell1.candidates))
                changed = changed or has_change
        return changed
    
    def solve(self):
        log_step("Begin", self.puzzle)
        changed = True
        while changed:
            log_step("Resolve Singles")
            solved_singles = self.solve_singles()
            
            log_step("Eliminate Locked Candidates")
            eliminated_locked_candidates = self.eliminate_locked_candidates()
            
            log_step("Eliminate Naked Pairs")
            eliminated_naked_pairs = self.eliminate_naked_pairs()
            changed = solved_singles or eliminated_locked_candidates or eliminated_naked_pairs

            log_step("Current State", self.puzzle)

        log_step("End", self.puzzle)
        log_step(f"The puzzle is {'solved' if self.puzzle.is_solved() else 'not solved'}")
        log_step(f"The puzzle solution is {'valid' if self.puzzle.has_valid_solution() else 'invalid'}")

    