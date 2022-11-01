# -*- coding: utf-8 -*-
"""
Graphics edge module containing :class:`~nodedge.graphics_edge.GraphicsEdge`,
:class:`~nodedge.graphics_edge.GraphicsEdgeDirect` and
:class:`~nodedge.graphics_edge.GraphicsEdgeBezier` classes.
"""

import logging
import math
from typing import Optional, Union

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
)

from nodedge.graphics_socket import getSocketColor
from nodedge.utils import dumpException


class GraphicsEdge(QGraphicsPathItem):
    """:class:`~nodedge.graphics_edge.GraphicsEdge` class

    The graphics edge is the graphical representation of the
    :class:`~nodedge.edge.Edge`.
    """

    def __init__(
        self, edge: "Edge", parent: Optional[QGraphicsItem] = None  # type: ignore
    ) -> None:
        """
        :param edge: reference to :class:`~nodedge.edge.Edge`
        :type edge: :class:`~nodedge.edge.Edge`
        :param parent: parent widget
        :type parent: ``Optional[QGraphicsItem]``
        """

        super().__init__(parent)
        self.edge = edge

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self._sourcePos: QPointF = QPointF(0.0, 0.0)
        self._targetPos: QPointF = QPointF(200.0, 200.0)

        self._lastSelectedState: bool = False
        self.hovered: bool = False

        self.initUI()

    @property
    def selectedState(self):
        """

        :getter: Return whether the edge is selected or not.
        :setter: Set the selection state of the edge.
        :type: ``bool``
        """
        return self._lastSelectedState

    @selectedState.setter
    def selectedState(self, value):
        self._lastSelectedState = value

    @property
    def sourcePos(self):
        """

        :getter: Return the edge's source position.
        :setter: Set the edge's source position.
        :type: ``QPointF``
        """
        return self._sourcePos

    @sourcePos.setter
    def sourcePos(self, value: QPointF):
        self._sourcePos = value

    @property
    def targetPos(self):
        """

        :getter: Return the edge's target position.
        :setter: Set the edge's target position.
        :type: ``QPointF``
        """
        return self._targetPos

    @targetPos.setter
    def targetPos(self, value: QPointF):
        self._targetPos = value

    def initUI(self):
        """
        Set up this ``QGraphicsPathItem``
        """
        self.initStyle()
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    # noinspection PyAttributeOutsideInit
    def initStyle(self):
        """
        Initialize ``QObject`` like ``QColor``, ``QPen`` and ``QBrush``
        """
        p = QApplication.palette()
        self._defaultColor: QColor = p.dark().color()
        self._color: QColor = self._defaultColor
        self._colorSelected: QColor = QColor("#00ff00")

        self._pen: QPen = QPen(self._color)
        self._pen.setWidthF(2.0)

        self._penSelected: QPen = QPen(self._colorSelected)
        self._penSelected.setWidthF(3.0)

        self._penDragging: QPen = QPen(self._color)
        self._penDragging.setWidthF(2.0)
        self._penDragging.setStyle(Qt.DashLine)

        self.setZValue(-1)

        #: Bezier control point distance on the line
        self._controlPointRoundness: float = 100.0

    def boundingRect(self):
        """
        Define Qt' bounding rectangle
        """
        return self.shape().boundingRect()

    def onSelected(self):
        """
        Slot called when the edge has just been selected.
        """
        self.edge.scene.graphicsScene.itemSelected.emit()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """
        Overridden Qt slot to handle mouse release on the edge.

        :param event: Qt mouse release event
        :type event: ``QGraphicsSceneMouseEvent``
        """
        super().mouseReleaseEvent(event)
        isSelected = self.isSelected()
        if self._lastSelectedState != isSelected:
            self.edge.scene.resetLastSelectedStates()
            self._lastSelectedState = isSelected
            self.onSelected()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """
        Overridden Qt slot to handle mouse hovering on the edge.

        :param event: Qt mouse hover event
        :type event: ``QGraphicsSceneHoverEvent``
        """
        p = QApplication.palette()
        self.hovered = True
        self._pen.setColor(p.highlight().color())
        self.update()

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """
        Overridden Qt slot to handle mouse hovering's end on the edge.

        :param event: Qt mouse hover event
        :type event: ``QGraphicsSceneHoverEvent``
        """
        self.hovered = False
        p = QApplication.palette()
        self._pen.setColor(p.dark().color())
        self.update()

    def shape(self) -> QPainterPath:
        """Returns ``QPainterPath`` representation of the edge.

        :return: graphical path
        :rtype: ``QPainterPath``
        """

        return self.calcPath()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """
        Qt overridden method to paint the edge.

        .. note:: The path is calculated in
            :func:`~nodedge.graphics_edge.GraphicsEdge.calcPath` method.
        """
        self.setPath(self.calcPath())

        painter.setBrush(Qt.NoBrush)

        if self.edge.targetSocket is None:
            painter.setPen(self._penDragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._penSelected)

        painter.drawPath(self.path())

    def calcPath(self) -> QPainterPath:
        """Compute the graphical path between
        :attr:`~nodedge.graphics_edge.GraphicsEdge.sourcePos` and
        `~nodedge.graphics_edge.GraphicsEdge.targetPos`.

        .. warning::
            This method needs to be overridden.

        :returns: The computed path
        :rtype: ``QPainterPath``
        """
        raise NotImplementedError("This method needs to be overridden in a child class")

    def intersectsWith(self, p1: QPointF, p2: QPointF) -> bool:
        """
        Compute if the edge's path intersects with line between points given as
        argument.

        :param p1: first point
        :type p1: ``QPointF``
        :param p2: second point
        :type p2: ``QPointF``
        :return: ``True`` if this edge's path intersects with the line between p1 and p2
        :rtype: ``bool``
        """
        cutpath: QPainterPath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)

    # noinspection PyAttributeOutsideInit
    def changeColor(self, color: Union[str, QColor]):
        """Change color of the edge from string hex value '#00ff00'"""

        newColor = color if isinstance(color, QColor) else QColor(color)

        self.__logger.debug(
            "Change color to:",
            newColor.red(),
            newColor.green(),
            newColor.blue(),
            "on edge:",
            self.edge,
        )

        self._color = newColor
        self._pen = QPen(self._color)
        self._pen.setWidthF(3.0)

    def setColorFromSockets(self) -> bool:
        """
        Change color according to connected sockets.
        Returns ``True`` if color can be determined.
        """
        try:
            if self.edge is None:
                return False

            if self.edge.sourceSocket is None:
                return False

            if self.edge.targetSocket is None:
                return False

            sourceSocketType = self.edge.sourceSocket.socketType
            targetSocketType = self.edge.targetSocket.socketType
            if sourceSocketType != targetSocketType:
                return False
            self.changeColor(getSocketColor(sourceSocketType.value))
        except Exception as e:
            dumpException(e)
        return True

    def makeUnselectable(self):
        """
        Used for :class:`~nodedge.edge_dragging.EdgeDragging` to disable click
        detection over this graphics item.
        """
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setAcceptHoverEvents(False)


class GraphicsEdgeDirect(GraphicsEdge):
    """
    Graphics Edge Direct class, with straight line path between
    :attr:`~nodedge.graphics_edge.GraphicsEdge.sourcePos` and
    :attr:`~nodedge.graphics_edge.GraphicsEdge.targetPos`
    """

    def calcPath(self) -> QPainterPath:
        """Compute a straight line path between
        :attr:`~nodedge.graphics_edge.GraphicsEdge.sourcePos` and
        `~nodedge.graphics_edge.GraphicsEdge.targetPos`.

        :returns: The computed path
        :rtype: ``QPainterPath``
        """
        path = QPainterPath(self._sourcePos)
        path.lineTo(self._targetPos)
        return path


class GraphicsEdgeBezier(GraphicsEdge):
    """
    Graphics Edge Bezier class, with Bezier line path between
    :attr:`~nodedge.graphics_edge.GraphicsEdge.sourcePos` and
    :attr:`~nodedge.graphics_edge.GraphicsEdge.targetPos`
    """

    def calcPath(self) -> QPainterPath:
        """
        Compute a Bezier curve path between
        :attr:`~nodedge.graphics_edge.GraphicsEdge.sourcePos` and
        :attr:`~nodedge.graphics_edge.GraphicsEdge.targetPos`.

        :returns: The computed path
        :rtype: ``QPainterPath``
        """
        sx = self._sourcePos.x()
        sy = self._sourcePos.y()
        dx = self._targetPos.x()
        dy = self._targetPos.y()

        dist = (dx - sx) * 0.5

        cpx_s: float = dist
        cpx_d: float = -dist
        cpy_s: float = 0
        cpy_d: float = 0

        if self.edge.sourceSocket is not None:
            sourceSocketIsInput = self.edge.sourceSocket.isInput

            if (sx > dx and not sourceSocketIsInput) or (
                sx < dx and sourceSocketIsInput
            ):
                cpx_d *= -1.0
                cpx_s *= -1.0

                verticalDistance = sx - dx
                cpy_d = (
                    verticalDistance
                    / (1e-4 + (math.fabs(verticalDistance)))
                    * self._controlPointRoundness
                )
                cpy_s = -cpy_d

        path = QPainterPath(self._sourcePos)
        path.cubicTo(
            sx + cpx_s,
            sy + cpy_s,
            dx + cpx_d,
            dy + cpy_d,
            self._targetPos.x(),
            self._targetPos.y(),
        )
        return path


class GraphicsEdgeCircuit(GraphicsEdge):
    """
    Compute a path composed of vertical and horizontal lines between
    :attr:`~nodedge.graphics_edge.GraphicsEdge.sourcePos` and
    :attr:`~nodedge.graphics_edge.GraphicsEdge.targetPos`.

    :returns: The computed path
    :rtype: ``QPainterPath``
    """

    def calcPath(self) -> QPainterPath:
        """
        Compute a path composed of vertical and horizontal lines between
        :attr:`~nodedge.graphics_edge.GraphicsEdge.sourcePos` and
        :attr:`~nodedge.graphics_edge.GraphicsEdge.targetPos`.

        :returns: The computed path
        :rtype: ``QPainterPath``
        """

        sx = self._sourcePos.x()
        sy = self._sourcePos.y()
        dx = self._targetPos.x()
        dy = self._targetPos.y()

        mx = (sx + dx) * 0.5

        path = QPainterPath(self._sourcePos)
        path.lineTo(mx, sy)
        path.lineTo(mx, dy)
        path.lineTo(dx, dy)
        return path
