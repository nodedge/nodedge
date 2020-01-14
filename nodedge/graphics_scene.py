import logging
import math

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class GraphicsScene(QGraphicsScene):
    itemSelected = pyqtSignal()
    itemsDeselected = pyqtSignal()

    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.scene = scene

        # Settings
        self.grid_size = 20
        self.grid_squares = 5
        self.scene_width = 64000
        self.scene_height = 64000

        self._color_background = QColor("#ffffff")
        self._color_light = QColor("#ffffff")
        self._color_dark = QColor("#ffffff")

        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)

        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)

        self.setBackgroundBrush(self._color_background)

    def dragMoveEvent(self, event: "QGraphicsSceneDragDropEvent") -> None:
        # Drag events won't be allowed until dragMoveEvent is overridden.
        pass

    def setScene(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter, rectangle):
        super().drawBackground(painter, rectangle)

        # Create the background grid
        left = int(math.floor(rectangle.left()))
        right = int(math.ceil(rectangle.right()))
        top = int(math.floor(rectangle.top()))
        bottom = int(math.ceil(rectangle.bottom()))

        first_left = left - (left % self.grid_size)
        first_top = top - (top % self.grid_size)

        # Compute all lines to be drawn
        lines_light, lines_dark = [], []
        for x in range(first_left, right, self.grid_size):
            line = QLine(x, top, x, bottom)
            if (x // self.grid_size) % self.grid_squares == 0:
                lines_dark.append(line)
            else:
                lines_light.append(line)

        for y in range(first_top, bottom, self.grid_size):
            line = QLine(left, y, right, y)
            if (y // self.grid_size) % self.grid_squares == 0:
                lines_dark.append(line)
            else:
                lines_light.append(line)

        # Draw the lines
        painter.setPen(self._pen_light)
        painter.drawLines(*lines_light)

        painter.setPen(self._pen_dark)
        painter.drawLines(*lines_dark)
