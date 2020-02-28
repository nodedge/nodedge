# -*- encoding: utf-8 -*-
"""
Module with some helper functions
"""

import logging
import traceback
from pprint import PrettyPrinter

from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QApplication

pp = PrettyPrinter(indent=4).pprint


def dumpException(e):
    """
    Prints out Exception message with traceback to the console

    :param e: Exception to print out
    :type e: Exception
    """
    logging.warning(f"{e.__class__.__name__} Exception: {e}")
    traceback.print_tb(e.__traceback__)


def loadStyleSheet(fileName):
    """
    Loads an qss stylesheet to current QApplication instance

    :param fileName: Filename of qss stylesheet
    :type fileName: str
    """
    logging.info(f"Style loading: {fileName}")
    file = QFile(fileName)
    file.open(QFile.ReadOnly or QFile.Text)
    styleSheet = file.readAll()
    QApplication.instance().setStyleSheet(str(styleSheet, encoding="utf-8"))


def loadStyleSheets(*args):
    """
    Loads multiple qss stylesheets. Concats them together and applies the final stylesheet to current QApplication instance

    :param args: variable number of filenames of qss stylesheets
    :type args: str, str,...
    """
    res = ""
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly or QFile.Text)
        styleSheet = file.readAll()
        res = "\n" + str(styleSheet, encoding="utf-8")
    QApplication.instance().setStyleSheet(res)
