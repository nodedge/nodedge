# -*- coding: utf-8 -*-
"""
Application styler module containing
:class:`~nodedge.application_styler.ApplicationStyler` class.
"""

import logging
import os

import yaml
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QGuiApplication, QPalette, Qt
from PySide6.QtWidgets import QApplication

from nodedge.utils import loadStyleSheet

logger = logging.getLogger(__name__)

darkPaletteFilePath = os.path.join(
    os.path.dirname(__file__), "../resources/palette/dark_palette.yml"
).replace("\\", "/")

lightPaletteFilePath = os.path.join(
    os.path.dirname(__file__), "../resources/palette/light_palette.yml"
).replace("\\", "/")

blackIconsFilePath = os.path.join(
    os.path.dirname(__file__), "../resources/black_icons/"
).replace("\\", "/")

whiteIconsFilePath = os.path.join(
    os.path.dirname(__file__), "../resources/white_icons/"
).replace("\\", "/")


class ApplicationStyler:
    """:class:`~nodedge.application_styler.ApplicationStyler` class ."""

    def __init__(self, palette="Dark"):

        self.styleSheetFilename = os.path.join(
            os.path.dirname(__file__), "../resources/qss/nodedge_style.qss"
        )

        self.setCustomPalette(palette)

        self.stylesheetLastModified: float = 0.0
        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.checkStylesheet)

        self.palette = "Dark"

        logger.debug("Application styler set up.")
        # self.timer.start()

    def setCustomPalette(self, palette="Dark", font="14"):
        app = QGuiApplication.instance()
        self.palette = palette
        if palette == "Dark":
            with open(darkPaletteFilePath, "r") as file:
                colors = yaml.safe_load(file)
            iconPath = whiteIconsFilePath
        else:
            with open(lightPaletteFilePath, "r") as file:
                colors = yaml.safe_load(file)
            iconPath = blackIconsFilePath

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
        extraLight = QColor(colors["extraLight"])
        brightText = QColor(colors["brightText"])
        p.setColor(QPalette.AlternateBase, highlight)
        p.setColor(QPalette.Base, base)
        p.setColor(QPalette.BrightText, brightText)
        p.setColor(QPalette.Button, mid)
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
        p.setColor(QPalette.PlaceholderText, light)
        app.setPalette(p)
        QApplication.setStyle("Fusion")

        loadStyleSheet(
            # os.path.join(os.path.dirname(__file__), "qss/calculator-dark.qss"),
            self.styleSheetFilename,
            iconPath=iconPath,
            fontSize=font,
        )

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

    def checkStylesheet(self) -> None:
        """
        Helper function which checks if the stylesheet exists and has changed.
        """
        try:
            modTime = os.path.getmtime(self.styleSheetFilename)
        except FileNotFoundError:
            logger.warning("Stylesheet was not found")
            return

        if modTime != self.stylesheetLastModified:
            pass
        self.stylesheetLastModified = modTime
        loadStyleSheet(self.styleSheetFilename)

    def setFontSize(self, size: str) -> None:
        self.setCustomPalette(self.palette, size)
