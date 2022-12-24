# -*- coding: utf-8 -*-
import os
import sys

import yaml
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QApplication,
    QColorDialog,
    QInputDialog,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from nodedge.application_styler import ApplicationStyler
from nodedge.flow_layout import FlowLayout

# from components.flow_layout import FlowLayout

os.environ["QT_API"] = "pyside6"

WIDGET_WIDTH = 60


class ColorButton(QWidget):
    def __init__(self, text, color, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)
        self.colorLabel = QLabel("", self)
        self.colorLabel.setFixedWidth(WIDGET_WIDTH)
        self.colorLabel.setFixedHeight(WIDGET_WIDTH)
        self.colorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.textLabel = QLabel(text)
        self.textLabel.setFixedWidth(WIDGET_WIDTH)
        self.textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.colorLabel)
        self.layout.addWidget(self.textLabel)
        self._color = color
        self.setButtonColor(self._color)

    def setButtonColor(self, color):
        self._color = color
        borderColor = QApplication.palette().text().color().name()
        self.colorLabel.setStyleSheet(
            f"background-color: {self._color};" f"border: 1px solid {borderColor};"
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            QApplication.clipboard().setText(self._color)
        elif event.button() == Qt.MouseButton.RightButton:
            color = QColorDialog.getColor(self._color).name()
            self.setButtonColor(color)


class PaletteViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Palette Viewer")
        # self.setMinimumSize(800, 600)
        self.centralWidget = QWidget()
        self.centralWidget.setMinimumWidth(4 * WIDGET_WIDTH)
        self.centralWidget.setMinimumHeight(4 * WIDGET_WIDTH)
        self.setCentralWidget(self.centralWidget)
        self.layout = FlowLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.centralWidget.setLayout(self.layout)

        self.initializeColorWidgets()

    def initializeColorWidgets(self):
        with open("resources/palette/dark_palette.yml", "r") as file:
            colors = yaml.safe_load(file)

        for index, (key, value) in enumerate(colors.items()):
            w = ColorButton(key, value)

            self.layout.addWidget(w)

        self.newColorButton = QPushButton("Add\nColor")
        self.newColorButton.clicked.connect(self.newColorButtonClicked)
        self.newColorButton.setFixedHeight(WIDGET_WIDTH)
        self.newColorButton.setFixedWidth(WIDGET_WIDTH)

        self.layout.addWidget(self.newColorButton)

    def newColorButtonClicked(self):
        text, ok = QInputDialog.getText(self, "New Color", "Color Name")
        if not ok:
            return
        color = QColorDialog.getColor().name()

        w = ColorButton(text, color)
        self.layout.removeWidget(self.newColorButton)
        self.layout.addWidget(w)
        self.layout.addWidget(self.newColorButton)


def main():
    app: QApplication = QApplication(sys.argv)
    styler = ApplicationStyler()

    window = PaletteViewerWindow()
    window.show()
    window.adjustSize()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
