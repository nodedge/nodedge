# -*- coding: utf-8 -*-
"""
Graphics scene module containing :class:`~nodedge.graphics_scene.GraphicsScene` class.
"""
import logging
from math import ceil, floor, log
from typing import Optional

from PySide6.QtCore import QCoreApplication, QLine, QPointF, Qt, Signal
from PySide6.QtGui import QPen, QTransform
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsItemGroup,
    QGraphicsScene,
    QGraphicsSceneDragDropEvent,
    QGraphicsSceneMouseEvent,
    QWidget,
)

logger = logging.getLogger(__name__)


class GraphicsScene(QGraphicsScene):
    """:class:`~nodedge.scene.Scene` class

    The graphics scene contains the background grid."""

    #: Signal emitted when some item is selected in the `Scene`
    itemSelected = Signal()
    #: Signal emitted when items are deselected in the `Scene`
    itemsDeselected = Signal()

    itemsPressed = Signal(list)

    mouseMoved = Signal(QPointF)

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

        app: Optional[QCoreApplication] = QApplication.instance()
        app.paletteChanged.connect(self.updateColors)  # type: ignore

        self.scene = scene
        self.initUI()

    def updateColors(self):
        self.initUI()
        self.drawBackground()

    def initUI(self) -> None:
        """Set up this ``QGraphicsScene``"""
        self.initSizes()
        self.initStyle()
        self.setBackgroundBrush(self._colorBackground)

    # noinspection PyAttributeOutsideInit
    def initStyle(self) -> None:
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        p = QApplication.palette()
        self._colorBackground = p.dark().color()
        self._colorSmallSquares = p.linkVisited().color()
        self._colorBigSquares = p.link().color()

        self._penSmallSquares = QPen(self._colorSmallSquares, 0.1)

        self._penBigSquares = QPen(self._colorBigSquares, 0.2)
        # self._penBigSquares.setDashPattern([2, 6])

    # noinspection PyAttributeOutsideInit
    def initSizes(self) -> None:
        """Set up internal attributes like `gridSize`, `sceneWidth` and
        `sceneHeight`."""
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
        Handle Qt mouse's drag move event.

        :param event: Mouse release event
        :type event: ``QGraphicsSceneDragDropEvent.py``
        """
        pass

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().mouseDoubleClickEvent(event)
        logger.debug("Double click in graphics scene")

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """
        Handle Qt mouse's button press event.

        :param event: Mouse release event
        :type event: ``QGraphicsSceneMouseEvent.py``
        """
        super().mousePressEvent(event)

        item: Optional[QGraphicsItem] = self.itemAt(event.scenePos(), QTransform())
        logger.debug(f"item: {item}")

        if not event.modifiers() & Qt.ShiftModifier:
            self.scene.doDeselectItems(silent=True)
            # for item in self.selectedItems():
            #     if item is not None:
            #         item.setSelected(False)
            # self.itemsDeselected.emit()

        if (
            item is not None
            and item not in self.selectedItems()
            and item.parentItem() not in self.selectedItems()
            and not event.modifiers() & Qt.ShiftModifier
        ):
            logger.debug(f"Pressed item: {item}")
            logger.debug(f"Pressed parent item: {item.parentItem()}")

        if item is not None:
            if item.parentItem() is not None:
                item.parentItem().setSelected(True)
            else:
                item.setSelected(True)

        self.itemSelected.emit()

        logger.debug(f"Selected items in graphics scene: {self.selectedItems()}")
        logger.debug(f"Last selected item: {self.scene.lastSelectedItems}")

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """
        Handle Qt mouse's button release event.

        :param event: Mouse release event
        :type event: ``QGraphicsSceneMouseEvent.py``
        """
        item = self.itemAt(event.scenePos(), QTransform())

        if item is not None:
            pass
            # item.setSelected(True)

        super().mouseReleaseEvent(event)

        logger.debug(f"Last selected item: {self.scene.lastSelectedItems}")

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.mouseMoved.emit(event.scenePos())
        super().mouseMoveEvent(event)

    def fitToView(self):
        """

        :return:
        """
        if len(self.scene.nodes) + len(self.scene.elements) <= 1:
            return

        nodes = self.scene.nodes
        items = [node.graphicsNode for node in nodes]
        elements = [element.graphicsElement for element in self.scene.elements]
        items = items + elements
        group = QGraphicsItemGroup()
        for item in items:
            group.addToGroup(item)

        zoomInFactor = self.scene.graphicsView.zoomInFactor
        maxZoomLevel = self.scene.graphicsView.zoomRange[1]

        # Get current scale factor.
        oldMatrix: QTransform = self.scene.graphicsView.transform()
        oldScaleFactor = oldMatrix.m11()
        oldZoomLevel = maxZoomLevel + round(log(oldScaleFactor) / log(zoomInFactor))

        # Fit in view and estimate new scale factor.
        self.scene.graphicsView.fitInView(group, Qt.KeepAspectRatio)
        newMatrix = self.scene.graphicsView.transform()
        newScaleFactor = newMatrix.m11()
        newZoomLevel = min(
            maxZoomLevel, maxZoomLevel + floor(log(newScaleFactor) / log(zoomInFactor))
        )

        # Restore old scale factor.
        self.scene.graphicsView.setTransform(oldMatrix)

        # Apply new scale factor properly.
        self.scene.graphicsView.zoom = newZoomLevel
        newScale = pow(zoomInFactor, newZoomLevel - oldZoomLevel)
        self.scene.graphicsView.scale(newScale, newScale)

        # Center on nodes.
        self.scene.graphicsView.centerOn(group)

        for item in items:
            group.removeFromGroup(item)
            self.scene.graphicsScene.addItem(item)
