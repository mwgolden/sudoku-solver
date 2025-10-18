import logging
from pprint import pformat

logging.basicConfig(
    filename="sudoku_steps.log",
    filemode="w",
    level=logging.INFO,
    format="%(message)s"
)

def log_step(step_description, sudoku_grid):
    logging.info(step_description)
    logging.info(pformat(sudoku_grid))
    logging.info("\n" + "-"*40 + "\n")