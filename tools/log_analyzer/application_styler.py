# -*- coding: utf-8 -*-
"""
Application styler module containing
:class:`~nodedge.application_styler.ApplicationStyler` class.
"""

import logging
import os

# import pyqtconsole.highlighter as hl
from PySide6.QtCore import QFile, QTimer
from PySide6.QtGui import QColor, QGuiApplication, QPalette, Qt
from PySide6.QtWidgets import QApplication


class ApplicationStyler:
    """:class:`~nodedge.application_styler.ApplicationStyler` class ."""

    def __init__(self, iconPath: str = "", qssPath: str = ""):
        self.iconPath = iconPath
        self.qssPath = qssPath

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        app = QGuiApplication.instance()

        QApplication.setStyle("Fusion")
        p = QApplication.palette()
        raisinBlackDark = QColor("#1B1D23")
        raisinBlackLight = QColor("#272C36")
        raisinBlackMid = QColor("#23252E")
        charCoal = QColor("#363A46")
        independence = QColor("#464B5B")
        white = QColor("#DDFFFFFF")
        blue = QColor("#007BFF")
        spanishGray = QColor("#8791AF")
        dimGray = QColor("#6C748C")
        p.setColor(QPalette.AlternateBase, blue)
        p.setColor(QPalette.Base, charCoal)
        p.setColor(QPalette.BrightText, blue)
        p.setColor(QPalette.Button, raisinBlackDark)
        p.setColor(QPalette.ButtonText, white)
        p.setColor(QPalette.Dark, raisinBlackDark)
        p.setColor(QPalette.Highlight, blue)
        p.setColor(QPalette.HighlightedText, white)
        p.setColor(QPalette.Light, independence)
        p.setColor(QPalette.Link, spanishGray)
        p.setColor(QPalette.LinkVisited, dimGray)
        p.setColor(QPalette.Mid, raisinBlackMid)
        p.setColor(QPalette.Midlight, raisinBlackLight)
        p.setColor(QPalette.Shadow, independence)
        p.setColor(QPalette.Text, white)
        p.setColor(QPalette.Window, charCoal)
        p.setColor(QPalette.WindowText, white)
        if app is not None:
            app.setPalette(p)  # type: ignore

        self.styleSheetFilename = os.path.join(os.path.dirname(__file__), self.qssPath)
        loadStyleSheets(self.styleSheetFilename)

        self.stylesheetLastModified: float = 0.0
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.checkStylesheet)  # type: ignore
        self.timer.start()

    def checkStylesheet(self) -> None:
        """
        Helper function which checks if the stylesheet exists and has changed.
        """
        try:
            modTime = os.path.getmtime(self.styleSheetFilename)
        except FileNotFoundError:
            self.__logger.warning("Stylesheet was not found")
            return

        if modTime != self.stylesheetLastModified:
            self.stylesheetLastModified = modTime
            loadStyleSheets(self.styleSheetFilename)


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
    Load multiple qss stylesheets. It concatenates them together and applies the final
    stylesheet to current QApplication instance.

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
