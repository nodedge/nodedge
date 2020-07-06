# -*- coding: utf-8 -*-
"""
Graphics scene module containing :class:`~nodedge.graphics_scene.GraphicsScene` class.
"""

import logging
import math
from typing import Optional

from PyQt5.QtCore import QLine, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPen, QTransform
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsScene,
    QGraphicsSceneDragDropEvent,
    QGraphicsSceneMouseEvent,
    QWidget,
)


class GraphicsScene(QGraphicsScene):
    """:class:`~nodedge.scene.Scene` class

    The graphics scene contains the background grid."""

    #: pyqtSignal emitted when some item is selected in the `Scene`
    itemSelected = pyqtSignal()
    #: pyqtSignal emitted when items are deselected in the `Scene`
    itemsDeselected = pyqtSignal()

    itemsPressed = pyqtSignal(list)

    def __init__(
        self, scene: "Scene", parent: Optional[QWidget] = None  # type: ignore
    ) -> None:
        """
        :param scene: reference to the :class:`~nodedge.scene.Scene`
        :type scene: :class:`~nodedge.scene.Scene`
        :param parent: parent widget
        :type parent: QWidget
        """

        super().__init__(parent)

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.scene = scene
        self.initUI()

    def initUI(self) -> None:
        """Set up this ``QGraphicsScene``"""
        self.initSizes()
        self.initStyle()
        self.setBackgroundBrush(self._colorBackground)

    # noinspection PyAttributeOutsideInit
    def initStyle(self) -> None:
        """Initialize ``QObjects`` like ``QColor``, ``QPten`` and ``QBrush``"""
        self._colorBackground = QColor("#DFE0DC")
        self._colorLight = QColor("#ffffff")
        self._colorDark = QColor("#ffffff")

        self._penLight = QPen(self._colorLight)
        self._penLight.setWidth(1)

        self._penDark = QPen(self._colorDark)
        self._penDark.setWidth(2)

    # noinspection PyAttributeOutsideInit
    def initSizes(self) -> None:
        """Set up internal attributes like `grid_size`, `scene_width` and
        `scene_height`. """
        self.gridSize = 20
        self.gridSquares = 5
        self.sceneWidth = 64000
        self.sceneHeight = 64000

    def setScene(self, width, height) -> None:
        """
        Set `width` and `height` of the graphics scene.
        """
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter, rectangle) -> None:
        """
        Draw background scene grid.
        """
        super().drawBackground(painter, rectangle)

        # Create the background grid
        left = int(math.floor(rectangle.left()))
        right = int(math.ceil(rectangle.right()))
        top = int(math.floor(rectangle.top()))
        bottom = int(math.ceil(rectangle.bottom()))

        firstLeft = left - (left % self.gridSize)
        first_top = top - (top % self.gridSize)

        # Compute all lines to be drawn
        linesLight, linesDark = [], []
        for x in range(firstLeft, right, self.gridSize):
            line = QLine(x, top, x, bottom)
            if (x // self.gridSize) % self.gridSquares == 0:
                linesDark.append(line)
            else:
                linesLight.append(line)

        for y in range(first_top, bottom, self.gridSize):
            line = QLine(left, y, right, y)
            if (y // self.gridSize) % self.gridSquares == 0:
                linesDark.append(line)
            else:
                linesLight.append(line)

        # Draw the lines
        painter.setPen(self._penLight)
        painter.drawLines(*linesLight)

        painter.setPen(self._penDark)
        painter.drawLines(*linesDark)

    def dragMoveEvent(self, event: QGraphicsSceneDragDropEvent) -> None:
        """
        Handle Qt's mouse's drag move event.

        :param event: Mouse release event
        :type event: ``QGraphicsSceneDragDropEvent.py``
        """
        pass

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """
        Handle Qt's mouse's button press event.

        :param event: Mouse release event
        :type event: ``QGraphicsSceneMouseEvent.py``
        """
        item: Optional[QGraphicsItem] = self.itemAt(event.scenePos(), QTransform())

        if (
            item is not None
            and item not in self.selectedItems()
            and item.parentItem() not in self.selectedItems()
            and not int(event.modifiers()) & Qt.ShiftModifier
        ):
            self.__logger.debug(f"Pressed item: {item}")
            self.__logger.debug(f"Pressed parent item: {item.parentItem()}")
            self.__logger.debug(
                f"Selected items in graphics scene: {self.selectedItems()}"
            )
            for item in self.selectedItems():
                item.setSelected(False)

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """
        Handle Qt's mouse's button release event.

        :param event: Mouse release event
        :type event: ``QGraphicsSceneMouseEvent.py``
        """
        item = self.itemAt(event.scenePos(), QTransform())

        if item is not None:
            item.setSelected(True)

        super().mouseReleaseEvent(event)
