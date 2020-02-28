# -*- coding: utf-8 -*-
"""
A module containing Graphics representation of Edge
"""

import logging
import math
from typing import Optional

from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor, QPainterPath, QPen
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
    QWidget,
)

from nodedge.socket import SocketPosition


class GraphicsEdge(QGraphicsPathItem):
    """Base class for Graphics Edge"""

    def __init__(self, edge: "Edge", parent: Optional[QWidget] = None):
        """
        :param edge: reference to :class:`~nodedge.edge.Edge`
        :type edge: :class:`~nodedge.edge.Edge`
        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance attributes:

            - **edge** - reference to :class:`~nodedge.edge.Edge`
            - **posSource** - ``[x, y]`` source position in the `Scene`
            - **posDestination** - ``[x, y]`` destination position in the `Scene`
        """

        super().__init__(parent)
        self.edge = edge

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self._posSource = [0, 0]
        self._posDestination = [200, 100]

        self._lastSelectedState = False
        self.hovered = False

        self.initUI()

    @property
    def selectedState(self):
        return self._lastSelectedState

    @selectedState.setter
    def selectedState(self, value):
        self._lastSelectedState = value

    def initUI(self):
        """Set up this ``QGraphicsPathItem``"""
        self.initStyle()
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    # noinspection PyAttributeOutsideInit
    def initStyle(self):
        """Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``"""
        self._color: QColor = QColor("#001000")
        self._colorSelected: QColor = QColor("#00ff00")
        self._colorHovered: QColor = QColor("#FF37A6FF")

        self._pen: QPen = QPen(self._color)
        self._pen.setWidthF(3.0)

        self._penSelected: QPen = QPen(self._colorSelected)
        self._penSelected.setWidthF(3.0)

        self._penDragging: QPen = QPen(self._color)
        self._penDragging.setWidthF(3.0)
        self._penDragging.setStyle(Qt.DashLine)

        self._penHovered: QPen = QPen(self._colorHovered)
        self._penHovered.setWidthF(5.0)

        self.setZValue(-1)

        self._controlPointRoundness: int = 100  #: Bezier control point distance on the line

    def setSource(self, x: float, y: float) -> None:
        """ Set source point

        :param x: x position
        :type x: ``float``
        :param y: y position
        :type y: ``float``
        :return:
        """
        self._posSource = [x, y]

    def setDestination(self, x: float, y: float) -> None:
        """ Set destination point

        :param x:
        :param y:
        :return:
        """
        self._posDestination = [x, y]

    def boundingRect(self):
        """Defining Qt' bounding rectangle"""
        return self.shape().boundingRect()

    def onSelected(self):
        """Our event handling when the node was selected"""
        self.edge.scene.graphicsScene.itemSelected.emit()

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """Overriden Qt's method to handle selecting and deselecting this `Graphics Edge`"""
        super().mouseReleaseEvent(event)
        isSelected = self.isSelected()
        if self._lastSelectedState != isSelected:
            self.edge.scene.resetLastSelectedStates()
            self._lastSelectedState = isSelected
            self.onSelected()

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """Handle hover effect"""
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """Handle hover effect"""
        self.hovered = False
        self.update()

    def shape(self) -> QPainterPath:
        """Returns ``QPainterPath`` representation of this `Edge`

        :return: path representation
        :rtype: ``QPainterPath``
        """

        return self.calcPath()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """Qt's overriden method to paint this Graphics Edge.
        Path calculated in :func:`~nodedge.graphics_edge.QDMGraphicsEdge.calcPath` method"""
        self.setPath(self.calcPath())

        painter.setBrush(Qt.NoBrush)

        if self.hovered and self.edge.endSocket is not None:
            painter.setPen(self._penHovered)
            painter.drawPath(self.path())

        if self.edge.endSocket is None:
            painter.setPen(self._penDragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._penSelected)

        painter.drawPath(self.path())

    def calcPath(self) -> QPainterPath:
        """Will handle drawing QPainterPath from Point A to B

        :returns: ``QPainterPath`` of the edge connecting `source` and `destination`
        :rtype: ``QPainterPath``
        """
        raise NotImplementedError("This method needs to be overridden in a child class")

    def intersectsWith(self, p1: QPointF, p2: QPointF) -> bool:
        """Does this Graphics Edge intersect with line between point A and point B ?

        :param p1: point A
        :type p1: ``QPointF``
        :param p2: point B
        :type p2: ``QPointF``
        :return: ``True`` if this `Graphics Edge` intersects
        :rtype: ``bool``
        """
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)


class GraphicsEdgeDirect(GraphicsEdge):
    """Direct line connection Graphics Edge"""

    def calcPath(self):
        """Calculate the Direct line connection

        :returns: ``QPainterPath`` of the direct line
        :rtype: ``QPainterPath``
        """
        path = QPainterPath(QPointF(self._posSource[0], self._posSource[1]))
        path.lineTo(self._posDestination[0], self._posDestination[1])
        return path


class GraphicsEdgeBezier(GraphicsEdge):
    """Cubic line connection Graphics Edge"""

    def calcPath(self):
        """Calculate the cubic Bezier line connection with 2 control points

        :returns: ``QPainterPath`` of the cubic Bezier line
        :rtype: ``QPainterPath``
        """
        s = self._posSource
        d = self._posDestination
        dist = (d[0] - s[0]) * 0.5

        cpx_s = dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.edge.startSocket is not None:
            sspos = self.edge.startSocket.position

            if (
                s[0] > d[0]
                and sspos in [SocketPosition.RIGHT_TOP, SocketPosition.RIGHT_BOTTOM]
            ) or (
                s[0] < d[0]
                and sspos in [SocketPosition.LEFT_BOTTOM, SocketPosition.LEFT_TOP]
            ):
                cpx_d *= -1
                cpx_s *= -1

                verticalDistance = s[1] - d[1]
                cpy_d = (
                    verticalDistance
                    / (1e-4 + (math.fabs(verticalDistance)))
                    * self._controlPointRoundness
                )
                cpy_s = -cpy_d

        path = QPainterPath(QPointF(self._posSource[0], self._posSource[1]))
        path.cubicTo(
            s[0] + cpx_s,
            s[1] + cpy_s,
            d[0] + cpx_d,
            d[1] + cpy_d,
            self._posDestination[0],
            self._posDestination[1],
        )
        return path
