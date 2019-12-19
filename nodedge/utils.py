import traceback
import logging
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


def dumpException(e):
    logging.warning(f"Exception: {e}")
    traceback.print_tb(e.__traceback__)


def loadStyleSheet(fileName):
    print(f"Style loading: {fileName}")
    file = QFile(fileName)
    file.open(QFile.ReadOnly or QFile.Text)
    styleSheet = file.readAll()
    QApplication.instance().setStyleSheet(str(styleSheet, encoding="utf-8"))


def loadStyleSheets(*args):
    res = ''
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly or QFile.Text)
        styleSheet = file.readAll()
        res = "\n" + str(styleSheet, encoding="utf-8")
    QApplication.instance().setStyleSheet(res)
