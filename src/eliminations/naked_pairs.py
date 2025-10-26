from collections import defaultdict

from sudoku import SudokuPuzzle
from sudoku_cell import Cell
from sudoku_logger import log_step
from enums import GroupType


def eliminate_naked_pairs(puzzle: SudokuPuzzle) -> bool:
    group_types = [GroupType.ROW, GroupType.COL, GroupType.BOX]
    naked_pairs = defaultdict(list)
    for i in range(9):
        for group_type in group_types:
            naked_pairs[group_type] += naked_pairs_for_group(puzzle, group_type, i)
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


def find_naked_pairs_for_group(group: list[Cell]) -> list[tuple[Cell, Cell]]:
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

def naked_pairs_for_group(puzzle, group_type: GroupType, loc: int):
        if group_type == GroupType.ROW:
            group = puzzle.group_for_loc(loc, group_type)
        elif group_type == GroupType.COL:
            group = puzzle.group_for_loc(loc, group_type)
        elif group_type == GroupType.BOX:
            group = puzzle.group_for_loc(loc, group_type)
        else:
            raise ValueError(f"Invalid group_type: {group_type}")
        
        return find_naked_pairs_for_group(group)