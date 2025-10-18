from pathlib import Path
import numpy as np

from sudoku import SudokuPuzzle
from sudoku_solver import SudokuSolver

from pprint import pprint

def  read_file(path: Path):
    rows = []
    with open(path, "r") as file:
        for line in file:
            rows.append(line.strip().split(","))
    return rows

def convert_to_np_array(l_puzzle):
    arr = np.array(l_puzzle, dtype=object)
    arr[arr == ''] = 0
    return arr.astype(np.int8)



def main():
    project_root = Path(__file__).resolve().parent.parent
    puzzle_path = project_root / "puzzles"
    #sudoku01 = puzzle_path / "sudoku01.txt"
    sudoku01 = puzzle_path / "hard-sudoku.txt"
    puzzle = read_file(sudoku01)
    np_puzzle = convert_to_np_array(puzzle)
    sudoku_puzzle = SudokuPuzzle(np_puzzle)
    sudoku_solver = SudokuSolver(sudoku_puzzle)

    #print(sudoku_puzzle.box_at(8))
    #print(sudoku_puzzle.hidden_singles_for_box(8))

    sudoku_solver.solve()
    #print(np_puzzle)
    #print(sudoku_puzzle.current_frame())
    #print(sudoku_puzzle.locked_candidates_for_box(0))
    #print(sudoku_puzzle.box_at(0))
    #pprint(sudoku_puzzle.locked_candidates_for_box(1))
    #pprint(sudoku_puzzle.locked_candidates_for_column(1))
    #pprint(sudoku_puzzle.locked_candidates_for_row(1))
    

if __name__ == "__main__":
    main()