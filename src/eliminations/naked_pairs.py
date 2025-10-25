from collections import defaultdict

from sudoku import SudokuPuzzle, Cell
from sudoku_logger import log_step
from enums import GroupType


def eliminate_naked_pairs(puzzle: SudokuPuzzle) -> bool:
    group_types = [GroupType.ROW, GroupType.COL, GroupType.BOX]
    naked_pairs = defaultdict(list)
    for i in range(9):
        for group_type in group_types:
            naked_pairs[group_type] += puzzle.naked_pairs_for_group(group_type, i)
    changed = False
    for group_type, pairs in naked_pairs.items():
        for cell1, cell2 in pairs:
            group = puzzle.group_for_cell(cell1, group_type)
            has_change = eliminate_candidates_from_group((group_type, [cell1, cell2], group, cell1.candidates))
            changed = changed or has_change
    return changed

def eliminate_candidates_from_group( eliminations: tuple[GroupType, list[Cell], list[Cell], set[int]]) -> bool:
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