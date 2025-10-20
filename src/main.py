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
    sudoku01 = puzzle_path / "hard-sudoku03.txt" # hard-sudoku03.txt cannot be solved with singles and locked singles alone
    puzzle = read_file(sudoku01)
    np_puzzle = convert_to_np_array(puzzle)
    sudoku_puzzle = SudokuPuzzle(np_puzzle)
    sudoku_solver = SudokuSolver(sudoku_puzzle)
    sudoku_solver.solve()


if __name__ == "__main__":
    main()