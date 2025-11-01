from sudoku import SudokuPuzzle
from sudoku_cell import Cell
from enums import GroupType, NakedSubsetType
from sudoku_logger import log_step
from itertools import combinations
from typing import Union, TypeAlias

NakedSubset: TypeAlias = Union[
    tuple[Cell, Cell],
    tuple[Cell, Cell, Cell],
    tuple[Cell, Cell, Cell, Cell],
]

def eliminate_naked_pairs(puzzle: SudokuPuzzle):
    """
        Eliminate candidates from cells identified as naked triples in the same group. 
    """
    changed = False
    group_types = [GroupType.ROW, GroupType.COL, GroupType.BOX]
    for i in range(9):
        for group_type in group_types:
            group = puzzle.group_for_loc(i, group_type)
            pairs = find_naked_pairs_for_group(group)
            if pairs:
                if eliminate_candidates_for_group(group, pairs, NakedSubsetType.PAIR, group_type):
                    changed = True
                                
    return changed

def eliminate_naked_triples(puzzle: SudokuPuzzle):
    """
        Eliminate candidates from cells identified as naked triples in the same group. 
    """
    changed = False
    group_types = [GroupType.ROW, GroupType.COL, GroupType.BOX]
    for i in range(9):
        for group_type in group_types:
            group = puzzle.group_for_loc(i, group_type)
            triples = find_naked_triples_for_group(group)
            if triples:
                if eliminate_candidates_for_group(group, triples, NakedSubsetType.TRIPLE, group_type):
                    changed = True
                                
    return changed

def eliminate_naked_quads(puzzle: SudokuPuzzle):
    """
        Eliminate candidates from cells identified as naked triples in the same group. 
    """
    changed = False
    group_types = [GroupType.ROW, GroupType.COL, GroupType.BOX]
    for i in range(9):
        for group_type in group_types:
            group = puzzle.group_for_loc(i, group_type)
            quads = find_naked_quads_for_group(group)
            if quads:
                if  eliminate_candidates_for_group(group, quads, NakedSubsetType.QUAD, group_type):
                    changed = True
                                
    return changed

def eliminate_candidates_for_group(group: list[Cell], naked_subsets: NakedSubset, elimination_type: NakedSubsetType, group_type: GroupType) -> bool:
    """
        Eliminate candidates from a group of cells.
    """
    changed = False
    for cells in naked_subsets:
        eliminations = set().union(*(cell.candidates for cell in cells))
        for cell in group:
            if cell not in cells and eliminations & cell.candidates:
                log_step(f"Naked {elimination_type} ({group_type.name}): Eliminate candidates {eliminations} from Cell({cell.row}, {cell.col}){{{cell.candidates}}}")
                changed = cell.eliminate_candidates(eliminations)

    return changed



def find_naked_subsets_for_group(group: list[Cell], n: int) -> list[NakedSubset]:
    """
        Identifies naked subsets in a row, column or box. The candidates themselves are 
        confined to n cells. For naked pairs, candidates are confined to two cells. For
        naked triples, candidates are confined to 3 cells. For naked quads, candidates are 
        confiend to 4 cells within a group. 

        Candidates in a naked subset can be eliminated from other cells in the group. 

        Args:
            group list[Cell]:  group of cells from row, column or box

        Returns: list[tuple[Cell]]
    """
    # There must be n cells in a group with n or less candidates
    possible_subsets = [cell for cell in group if not cell.is_solved and len(cell.candidates) <= n]

    if len(possible_subsets) < n:
        return []
    
    # find all subset cell combinations
    subset_combinations = []
    for combination in combinations(possible_subsets, n):
        union_of_candidates = set()
        for cell in combination:
            union_of_candidates |= cell.candidates
        if len(union_of_candidates) == n:
            # Ensure only these three cells in the group have these candidates
            matching_cells = [c for c in group if c.candidates <= union_of_candidates and not c.is_solved]
            if len(matching_cells) == n:
                subset_combinations.append(combination)

    return subset_combinations
    
def find_naked_pairs_for_group(group: list[Cell]) -> list[NakedSubset]:
    """
        Identifies naked pairs in a row, column or box. 

        Candidates in a naked pair can be eliminated from other cells in the group. 

        Args:
            group list[Cell]:  group of cells from row, column or box
            n int: number of cells in a subset combination

        Returns:
            list[tuple[Cell]]: Tuples of cells for each naked pair found in group
        """
    pairs = find_naked_subsets_for_group(group, 2)

    return pairs

def find_naked_triples_for_group(group: list[Cell]) -> list[NakedSubset]:
    """
        Identifies naked triples in a row, column or box. 
        A naked triple occurs when three cells in a unit contain only three digits between them, 
        and no other cells in that unit can contain those digits.

        Candidates in a naked triple can be eliminated from other cells in the group. 

        Args:
            group list[Cell]:  group of cells from row, column or box
            n int: number of cells in a subset combination

        Returns: list[tuple[Cell]]
            
    """
    triples = find_naked_subsets_for_group(group, 3)

    return triples

def find_naked_quads_for_group(group: list[Cell]) -> list[NakedSubset]:
    """
        Identifies naked quads in a row, column or box. 
        A naked quad occurs when three cells in a unit contain only four digits between them, 
        and no other cells in that unit can contain those digits.

        Candidates in a naked quad can be eliminated from other cells in the group. 

        Args:
            group list[Cell]:  group of cells from row, column or box
            n int: number of cells in a subset combination

        Returns: list[tuple[Cell]]
            
    """
    quads = find_naked_subsets_for_group(group, 4)

    return quads

