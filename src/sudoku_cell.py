from dataclasses import dataclass, field


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
