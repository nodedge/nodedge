# -*- coding: utf-8 -*-
"""
Graphics node module containing :class:`~nodedge.graphics_node.GraphicsNode` class.
"""

import logging
from typing import Optional, cast

from PySide2.QtCore import QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QFont, QPainterPath, QPen
from PySide2.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
    QVBoxLayout,
    QWidget,
)

from nodedge.graphics_node_content import GraphicsNodeContent, GraphicsNodeContentProxy
from nodedge.graphics_node_title_label import GraphicsNodeTitleLabel
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
        pass

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
            self.titleLabel = GraphicsNodeTitleLabel(self.title, widget)
            layout.addWidget(self.titleLabel)
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
        pass

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
