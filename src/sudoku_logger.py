import logging
from pprint import pformat

logging.basicConfig(
    filename="sudoku_steps.log",
    filemode="w",
    level=logging.INFO,
    format="%(message)s"
)

def log_step(step_description, puzzle=None):
    logging.info(step_description)
    if puzzle:
        logging.info(puzzle)
    logging.info("\n" + "-"*40 + "\n")
