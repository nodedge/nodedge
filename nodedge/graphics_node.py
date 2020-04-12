# -*- coding: utf-8 -*-
"""
Graphics node module containing :class:`~nodedge.graphics_node.GraphicsNode` class.
"""

import logging
from typing import Optional

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainterPath, QPen
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
)

from nodedge.graphics_node_content import GraphicsNodeContentProxy
from nodedge.graphics_node_title_item import GraphicsNodeTitleItem


class GraphicsNode(QGraphicsItem):
    """:class:`~nodedge.node.Node` class

    The graphics node is the graphical representation of a node.
    """

    def __init__(self, node: "Node", parent: Optional[QGraphicsItem] = None) -> None:  # type: ignore
        """
        :param node: reference to :class:`~nodedge.node.Node`
        :type node: :class:`~nodedge.node.Node`
        :param parent: parent widget
        :type parent: ``Optional[QGraphicsItem]``
        """
        super().__init__(parent)
        self.node = node
        self.content = self.node.content

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.initUI()
        self._wasMoved = False
        self._lastSelectedState = False
        self.hovered = False

    @property
    def title(self):
        """
        Title of this graphical node.

        :getter: Return current Graphics Node title
        :setter: Store and make visible the new title
        :type: ``str``
        """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.titleItem.setPlainText(self._title)

    @property
    def selectedState(self):
        return self._lastSelectedState

    @selectedState.setter
    def selectedState(self, value):
        self._lastSelectedState = value

    def initUI(self) -> None:
        """
        Set up this ``QGraphicsItem``.
        """
        self.initSizes()
        self.initStyle()
        self.initTitle()
        self.initContent()

        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    # noinspection PyAttributeOutsideInit
    def initStyle(self) -> None:
        """
        Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``.
        """
        self._titleColor: QColor = QColor(Qt.white)
        self._colorHovered: QColor = QColor("#FF37A6FF")

        self._titleFont: QFont = QFont("Ubuntu", 10)

        self._penDefault: QPen = QPen(QColor("#7F000000"))
        self._penDefault.setWidthF(2.0)
        self._penSelected: QPen = QPen(QColor("#FFFFA637"))
        self._penSelected.setWidthF(2.0)

        self._penHovered: QPen = QPen(self._colorHovered)
        self._penHovered.setWidthF(3.0)

        self._brushTitle: QBrush = QBrush(QColor("#FF313131"))
        self._brushBackground: QBrush = QBrush(QColor("#E3212121"))

    # noinspection PyAttributeOutsideInit
    def initSizes(self) -> None:
        """
        Set up internal attributes like `width`, `height`, etc.
        """
        self.width: int = 180
        self.height: int = 240
        self.edgeRoundness: float = 5.0
        self.edgePadding: float = 10.0
        self.titleHeight: float = 24.0
        self.titleHorizontalPadding: float = 4.0
        self.titleVerticalPadding: float = 4.0

    # noinspection PyAttributeOutsideInit
    def initTitle(self) -> None:
        """
        Set up the title Graphics representation: font, color, position, etc.
        """
        self.titleItem: GraphicsNodeTitleItem = GraphicsNodeTitleItem(self)
        self.titleItem.setDefaultTextColor(self._titleColor)
        self.titleItem.setFont(self._titleFont)
        self.titleItem.setPos(self.titleHorizontalPadding, 0)
        self.titleItem.setTextWidth(self.width - 2 * self.titleHorizontalPadding)

        self.title = self.node.title

    # noinspection PyAttributeOutsideInit
    def initContent(self) -> None:
        """
        Set up the `grContent` - ``QGraphicsProxyWidget`` to have a container for `GraphicsContent`.
        """

        self.content.setGeometry(
            int(self.edgePadding),
            int(self.titleHeight + self.edgePadding),
            int(self.width - 2 * self.edgePadding),
            int(self.height - 2 * self.edgePadding - self.titleHeight),
        )
        self.graphicsContentProxy = GraphicsNodeContentProxy(self)
        self.graphicsContentProxy.setWidget(self.content)

    def boundingRect(self):
        """
        Define Qt' bounding rectangle.
        """
        return QRectF(0, 0, self.width, self.height).normalized()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """
        Paint the rounded rectangular `Node`.
        """
        # title
        pathTitle = QPainterPath()
        pathTitle.setFillRule(Qt.WindingFill)
        pathTitle.addRoundedRect(
            0, 0, self.width, self.titleHeight, self.edgeRoundness, self.edgeRoundness
        )
        maxTopRect = max(self.titleHeight - self.edgeRoundness, self.titleHeight / 2.0)
        maxHeightRect = min(self.edgeRoundness, self.titleHeight / 2.0)
        pathTitle.addRect(0, maxTopRect, self.edgeRoundness, maxHeightRect)
        pathTitle.addRect(
            self.width - self.edgeRoundness,
            maxTopRect,
            self.edgeRoundness,
            maxHeightRect,
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brushTitle)
        painter.drawPath(pathTitle.simplified())

        # content
        pathContent = QPainterPath()
        pathContent.setFillRule(Qt.WindingFill)
        pathContent.addRoundedRect(
            0,
            self.titleHeight,
            self.width,
            self.height - self.titleHeight,
            self.edgeRoundness,
            self.edgeRoundness,
        )
        maxHeightRect = min(self.edgeRoundness, self.height / 2)
        pathContent.addRect(0, self.titleHeight, self.edgeRoundness, maxHeightRect)
        pathContent.addRect(
            self.width - self.edgeRoundness,
            self.titleHeight,
            self.edgeRoundness,
            maxHeightRect,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brushBackground)
        painter.drawPath(pathContent.simplified())

        # outline
        pathOutline = QPainterPath()
        pathOutline.addRoundedRect(
            -1,
            -1,
            self.width + 2,
            self.height + 2,
            self.edgeRoundness,
            self.edgeRoundness,
        )
        painter.setBrush(Qt.NoBrush)

        if self.hovered:
            painter.setPen(self._penHovered)
            painter.drawPath(pathOutline.simplified())

        painter.setPen(self._penDefault if not self.isSelected() else self._penSelected)
        painter.drawPath(pathOutline.simplified())

    def mouseMoveEvent(self, event):
        """
        Override Qt's event to detect that we moved this graphical node.
        """
        super().mouseMoveEvent(event)

        # TODO: Optimize this condition. Just update the selected blocks.
        for node in self.scene().scene.nodes:
            if node.graphicsNode.isSelected():
                node.updateConnectedEdges()

        self._wasMoved = True

    def mouseReleaseEvent(self, event):
        """
        Handle Qt's event when we move, select or deselect this graphical node.
        """
        super().mouseReleaseEvent(event)

        # Handle when node moved
        if self._wasMoved:
            self._wasMoved = False
            self.node.scene.history.store("Move a node")

            self.node.scene.resetLastSelectedStates()
            self.selectedState = True

            # Store the last selected, because moving does also select the blocks.
            self.node.scene.lastSelectedItems = self.node.scene.selectedItems

            # Skip storing selection as it has just been done.
            return

        # Handle when node was clicked on
        isSelected = self.isSelected()
        if (
            self._lastSelectedState != isSelected
            or self.node.scene.lastSelectedItems != self.node.scene.selectedItems
        ):
            self.node.scene.resetLastSelectedStates()
            self._lastSelectedState = isSelected
            self.onSelected()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """
        Handle Qt's hover event.
        It adds a highlighting boundary around the graphical node.
        """
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """
        Handle Qt's hover effect.
        """
        self.hovered = False
        self.update()

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        """
        Qt's overridden event for doubleclick.
        Resend to :func:`~nodedge.node.Node.onDoubleClicked`
        """
        self.node.onDoubleClicked(event)

    def onSelected(self):
        """
        Handle when the node has been selected.
        """
        self.node.scene.graphicsScene.itemSelected.emit()
