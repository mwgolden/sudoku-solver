from pathlib import Path
import numpy as np

from sudoku import Sudoku

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
    sudoku01 = puzzle_path / "sudoku01.txt"
    puzzle = read_file(sudoku01)
    np_puzzle = convert_to_np_array(puzzle)
    sudoku = Sudoku(np_puzzle)
    #print(np.union1d(np_puzzle[0], np_puzzle.transpose()[2]))
    #print(np_puzzle)
    pprint(sudoku.grid)
    
    # filter object array
    mask = np.vectorize(lambda cell: cell.box == 3)(sudoku.grid)
    print(sudoku.grid[mask])

if __name__ == "__main__":
    main()