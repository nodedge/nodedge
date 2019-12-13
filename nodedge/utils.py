import traceback
import logging


def dumpException(e):
    logging.warning(f"Exception: {e}")
    traceback.print_tb(e.__traceback__)
