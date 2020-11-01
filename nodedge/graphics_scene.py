# -*- coding: utf-8 -*-
"""
Graphics scene module containing :class:`~nodedge.graphics_scene.GraphicsScene` class.
"""

import logging
from math import ceil, floor, log
from typing import Optional

from PySide2.QtCore import QLine, Qt, Signal
from PySide2.QtGui import QColor, QMatrix, QPen, QTransform
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsItemGroup,
    QGraphicsScene,
    QGraphicsSceneDragDropEvent,
    QGraphicsSceneMouseEvent,
    QWidget,
)


class GraphicsScene(QGraphicsScene):
    """:class:`~nodedge.scene.Scene` class

    The graphics scene contains the background grid."""

    #: Signal emitted when some item is selected in the `Scene`
    itemSelected = Signal()
    #: Signal emitted when items are deselected in the `Scene`
    itemsDeselected = Signal()

    itemsPressed = Signal(list)

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
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._colorBackground = QColor("#363A46")
        self._colorLight = QColor("#666666")
        self._colorDark = QColor("#999999")

        self._penSmallSquares = QPen(self._colorLight, 0.3, Qt.DotLine)

        self._penBigSquares = QPen(self._colorDark, 0.6)
        self._penBigSquares.setDashPattern([2, 6])

    # noinspection PyAttributeOutsideInit
    def initSizes(self) -> None:
        """Set up internal attributes like `gridSize`, `sceneWidth` and
        `sceneHeight`. """
        self.gridSize = 15
        self.gridSquares = 4
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
        left = int(floor(rectangle.left()))
        right = int(ceil(rectangle.right()))
        top = int(floor(rectangle.top()))
        bottom = int(ceil(rectangle.bottom()))

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
        painter.setPen(self._penSmallSquares)
        painter.drawLines(linesLight)

        painter.setPen(self._penBigSquares)
        painter.drawLines(linesDark)

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
            and not event.modifiers() & Qt.ShiftModifier
        ):
            self.__logger.debug(f"Pressed item: {item}")
            self.__logger.debug(f"Pressed parent item: {item.parentItem()}")
            self.__logger.debug(
                f"Selected items in graphics scene: {self.selectedItems()}"
            )
            for item in self.selectedItems():
                if item is not None:
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

    def fitInView(self):
        """

        :return:
        """
        if len(self.scene.nodes) <= 1:
            return

        nodes = self.scene.nodes
        items = [node.graphicsNode for node in nodes]
        group = QGraphicsItemGroup()
        for item in items:
            group.addToGroup(item)

        zoomInFactor = self.scene.graphicsView.zoomInFactor
        maxZoomLevel = self.scene.graphicsView.zoomRange[1]

        # Get current scale factor.
        oldMatrix: QMatrix = self.scene.graphicsView.matrix()
        oldScaleFactor = oldMatrix.m11()
        oldZoomLevel = maxZoomLevel + round(log(oldScaleFactor) / log(zoomInFactor))

        # Fit in view and estimate new scale factor.
        self.scene.graphicsView.fitInView(group, Qt.KeepAspectRatio)
        newMatrix = self.scene.graphicsView.matrix()
        newScaleFactor = newMatrix.m11()
        newZoomLevel = min(
            maxZoomLevel, maxZoomLevel + floor(log(newScaleFactor) / log(zoomInFactor))
        )

        # Restore old scale factor.
        self.scene.graphicsView.setMatrix(oldMatrix)

        # Apply new scale factor properly.
        self.scene.graphicsView.zoom = newZoomLevel
        newScale = pow(zoomInFactor, newZoomLevel - oldZoomLevel)
        self.scene.graphicsView.scale(newScale, newScale)

        # Center on nodes.
        self.scene.graphicsView.centerOn(group)

        for item in items:
            group.removeFromGroup(item)
            self.scene.graphicsScene.addItem(item)
