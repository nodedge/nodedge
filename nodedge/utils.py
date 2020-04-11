# -*- encoding: utf-8 -*-
"""
Utils module with some helper functions.
"""

import logging
import traceback
from pprint import PrettyPrinter

from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QApplication

pp = PrettyPrinter(indent=4).pprint


def dumpException(e=None, file=None):
    """
    Print out an exception message with the traceback to the console.


    :param e: Exception to print out
    :type e: Exception
    :param file: optional, file where the expection is dumped
    :type file: ``str``
    """
    logging.warning(f"{e.__class__.__name__} Exception: {e}")
    if file is not None:
        traceback.print_tb(e.__traceback__, file=file)
    else:
        traceback.print_exc()


def loadStyleSheet(fileName):
    """
    Load an qss stylesheet to current QApplication instance.

    :param fileName: filename of qss stylesheet
    :type fileName: ``str``
    """
    logging.info(f"Style loading: {fileName}")
    file = QFile(fileName)
    file.open(QFile.ReadOnly or QFile.Text)
    styleSheet = file.readAll()
    QApplication.instance().setStyleSheet(str(styleSheet, encoding="utf-8"))


def loadStyleSheets(*args):
    """
    Load multiple qss stylesheets.
    It concats them together and applies the final stylesheet to current QApplication instance.

    :param args: variable number of filenames of qss stylesheets
    :type args: ``str``, ``str``,...
    """
    res = ""
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly or QFile.Text)
        styleSheet = file.readAll()
        res = "\n" + str(styleSheet, encoding="utf-8")
    QApplication.instance().setStyleSheet(res)
