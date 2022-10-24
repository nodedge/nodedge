import logging
import sys
import traceback

from PySide6.QtWidgets import QApplication

from tools.log_analyzer.log_analyzer_window import LogAnalyzerWindow
from tools.log_analyzer.main_window import MainWindow


def dumpException(e=None, file=None):
    """
    Print out an exception message with the traceback to the console.


    :param e: Exception to print out
    :type e: Exception
    :param file: optional, file where the exception is dumped
    :type file: ``str``
    """
    logging.warning(f"{e.__class__.__name__} Exception: {e}")
    if file is not None:
        traceback.print_tb(e.__traceback__, file=file)
    else:
        traceback.print_exc()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = LogAnalyzerWindow()
    window.showMaximized()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
