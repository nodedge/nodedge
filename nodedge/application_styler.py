# -*- coding: utf-8 -*-
"""
Application styler module containing
:class:`~nodedge.application_styler.ApplicationStyler` class.
"""

import logging

# import pyqtconsole.highlighter as hl
from PySide6.QtGui import QColor, QGuiApplication, QPalette
from PySide6.QtWidgets import QApplication


class ApplicationStyler:
    """:class:`~nodedge.application_styler.ApplicationStyler` class ."""

    def __init__(self):
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
        app.setPalette(p)

        # self.consoleStyle = {
        #     "keyword": hl.format("blue", "bold"),
        #     "operator": hl.format("white"),
        #     "brace": hl.format("lightGray"),
        #     "defclass": hl.format("white", "bold"),
        #     "string": hl.format("magenta"),
        #     "string2": hl.format("lightMagenta"),
        #     "comment": hl.format("lightGreen", "italic"),
        #     "self": hl.format("white", "italic"),
        #     "numbers": hl.format("white"),
        #     "inprompt": hl.format("lightBlue", "bold"),
        #     "outprompt": hl.format("white", "bold"),
        # }
