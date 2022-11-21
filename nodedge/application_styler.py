# -*- coding: utf-8 -*-
"""
Application styler module containing
:class:`~nodedge.application_styler.ApplicationStyler` class.
"""

import logging
import os

import yaml
from PySide6.QtGui import QColor, QGuiApplication, QPalette
from PySide6.QtWidgets import QApplication

from nodedge.logger import logger


class ApplicationStyler:
    """:class:`~nodedge.application_styler.ApplicationStyler` class ."""

    def __init__(self):
        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        app = QGuiApplication.instance()

        QApplication.setStyle("Fusion")
        logger.debug(os.getcwd())

        with open("resources/palette/dark_palette.yml", "r") as file:
            colors = yaml.safe_load(file)
        p = QApplication.palette()
        dark = QColor(colors["dark"])
        midLight = QColor(colors["midLight"])
        mid = QColor(colors["mid"])
        base = QColor(colors["base"])
        light = QColor(colors["light"])
        text = QColor(colors["text"])
        highlight = QColor(colors["highlight"])
        link = QColor(colors["link"])
        visitedLink = QColor(colors["visitedLink"])
        p.setColor(QPalette.AlternateBase, highlight)
        p.setColor(QPalette.Base, base)
        p.setColor(QPalette.BrightText, highlight)
        p.setColor(QPalette.Button, dark)
        p.setColor(QPalette.ButtonText, text)
        p.setColor(QPalette.Dark, dark)
        p.setColor(QPalette.Highlight, highlight)
        p.setColor(QPalette.HighlightedText, text)
        p.setColor(QPalette.Light, light)
        p.setColor(QPalette.Link, link)
        p.setColor(QPalette.LinkVisited, visitedLink)
        p.setColor(QPalette.Mid, mid)
        p.setColor(QPalette.Midlight, midLight)
        p.setColor(QPalette.Shadow, light)
        p.setColor(QPalette.Text, text)
        p.setColor(QPalette.Window, base)
        p.setColor(QPalette.WindowText, text)
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
