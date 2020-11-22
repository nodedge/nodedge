# -*- coding: utf-8 -*-
"""
Graphics node module containing :class:`~nodedge.graphics_node.GraphicsNode` class.
"""

import logging
from typing import Optional, cast

from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QFont, QPainterPath, QPen
from PySide2.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsItem,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from nodedge.graphics_node_content import GraphicsNodeContentProxy
from nodedge.graphics_node_title_label import (
    GraphicsNodeTitleLabel,
    GraphicsNodeTypeLabel,
)
from nodedge.graphics_scene import GraphicsScene


class GraphicsNode(QGraphicsItem):
    """:class:`~nodedge.node.Node` class

    The graphics node is the graphical representation of a node.
    """

    def __init__(
        self, node: "Node", parent: Optional[QGraphicsItem] = None  # type: ignore
    ) -> None:
        """
        :param node: reference to :class:`~nodedge.node.Node`
        :type node: :class:`~nodedge.node.Node`
        :param parent: parent widget
        :type parent: ``Optional[QGraphicsItem]``
        """
        super().__init__(parent)
        self.node: "Node" = node  # type: ignore

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self._title: str = "Unnamed"

        self.initUI()
        self._wasMoved: bool = False
        self._lastSelectedState: bool = False
        self.hovered: bool = False

    @property
    def title(self):
        """
        Title of this :class:`~nodedge.graphics_node.GraphicsNode`.

        :getter: Return current :class:`~nodedge.graphics_node.GraphicsNode` title
        :setter: Store and make visible the new title
        :type: ``str``
        """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.titleLabel.setText(self._title)

    @property
    def type(self):
        return (
            self.node.__class__.operationTitle
            if "Block" in self.node.__class__.__name__
            else "undefined"
        )

    @property
    def selectedState(self):
        return self._lastSelectedState

    @selectedState.setter
    def selectedState(self, value):
        self._lastSelectedState = value

    @property
    def content(self):
        """

        :getter: Return reference to
            :class:`~nodedge.graphics_node_content.GraphicsNodeContent`

        :rtype: :class:`~nodedge.graphics_node_content.GraphicsNodeContent`
        """
        return self.node.content if self.node else None

    def initUI(self) -> None:
        """
        Set up this ``QGraphicsItem``.
        """
        self.initSizes()
        self.initStyle()
        self.initContent()

        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    # noinspection PyAttributeOutsideInit
    def initStyle(self) -> None:
        """
        Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``.
        """
        p = QApplication.palette()
        self._titleColor: QColor = QColor(Qt.white)
        self._colorHovered: QColor = p.alternateBase().color()

        self._titleFont: QFont = QFont("Ubuntu", 10)

        self._penDefault: QPen = QPen(QColor("#7F000000"))
        self._penDefault.setWidthF(2.0)
        self._penSelected: QPen = QPen(p.highlight().color())
        self._penSelected.setWidthF(2.0)

        self._penHovered: QPen = QPen(self._colorHovered)
        self._penHovered.setWidthF(2.0)

        self._brushTitle: QBrush = QBrush(QColor("#FF313131"))
        self._brushBackground: QBrush = QBrush(QColor("#E3212121"))

    # noinspection PyAttributeOutsideInit
    def initSizes(self) -> None:
        """
        Set up internal attributes like `width`, `height`, etc.
        """
        self.width: int = 180
        self.height: int = 240
        self.edgeRoundness: float = 0.0
        self.edgePadding: float = 0.0
        self.titleHeight: float = 24.0
        self.titleHorizontalPadding: float = 4.0
        self.titleVerticalPadding: float = 4.0

    # noinspection PyAttributeOutsideInit
    def initContent(self) -> None:
        """
        Set up the
        :class:`~nodedge.graphics_node_content.GraphicsNodeContentProxy`
        to have a container for
        :class:`~nodedge.graphics_node_content.GraphicsNodeContent`.
        """

        if self.content is not None:
            self.content.setGeometry(0, 0, self.width, self.height)
            self.graphicsContentProxy = GraphicsNodeContentProxy(self)
            widget = GraphicsNodeWidget()
            widget.setGeometry(0, 0, self.width, self.height)
            layout = GraphicsNodeVBoxLayout()
            widget.setLayout(layout)

            titleFrame = GraphicsNodeTitleFrame(widget)
            titleFrame.setMaximumHeight(30)
            titleLayout = QHBoxLayout()
            titleLayout.setMargin(0)
            titleFrame.setLayout(titleLayout)
            self.titleLabel = GraphicsNodeTitleLabel(self.title, widget)
            self.titleLabel.setSizePolicy(
                QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            )
            self.typeLabel = GraphicsNodeTypeLabel(self.type, widget)
            self.statusLabel = GraphicsNodeStatusLabel()
            titleLayout.addWidget(self.titleLabel)
            titleLayout.addWidget(self.typeLabel)
            titleLayout.addWidget(self.statusLabel)
            layout.addWidget(titleFrame)
            layout.addWidget(self.content)
            self.graphicsContentProxy.setWidget(widget)

    def boundingRect(self):
        """
        Define Qt' bounding rectangle.
        """
        return QRectF(0, 0, self.width, self.height).normalized()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """
        Paint the rounded rectangular :class:`~nodedge.node.Node`.
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
        Override Qt's event to detect that we moved this .
        """
        super().mouseMoveEvent(event)

        # TODO: Optimize this condition. Just update the selected blocks.
        graphicsScene: GraphicsScene = cast(GraphicsScene, self.scene())
        for node in graphicsScene.scene.nodes:
            if node.graphicsNode.isSelected():
                node.updateConnectedEdges()

        self._wasMoved = True

    def mouseReleaseEvent(self, event):
        """
        Handle Qt's event when we move, select or deselect this
        :class:`~nodedge.graphics_node.GraphicsNode`.
        """
        super().mouseReleaseEvent(event)

        # Handle when node moved
        if self._wasMoved:
            clipSize = self.node.scene.graphicsScene.gridSize
            pos = event.scenePos() - event.pos()
            newX = pos.x() - pos.x() % clipSize
            newY = pos.y() - pos.y() % clipSize

            self.setPos(newX, newY)
            graphicsScene: GraphicsScene = cast(GraphicsScene, self.scene())
            for node in graphicsScene.scene.nodes:
                if node.graphicsNode.isSelected():
                    node.updateConnectedEdges()

            self.__logger.debug(f"Current graphics node pos: {self.pos()}")
            self.__logger.debug(f"Event pos: {event.scenePos()}")

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
        It adds a highlighting boundary around this
        :class:`~nodedge.graphics_node.GraphicsNode`.
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


class GraphicsNodeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


class GraphicsNodeVBoxLayout(QVBoxLayout):
    def __init__(self, parent=None):
        super(GraphicsNodeVBoxLayout, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)


class GraphicsNodeTitleFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)


class GraphicsNodeStatusLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
