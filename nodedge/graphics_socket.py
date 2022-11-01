# -*- coding: utf-8 -*-
"""
Graphics socket module containing :class:`~nodedge.graphics_socket.GraphicsSocket`
class.
"""
import logging
from typing import Optional, Union

from PySide6.QtCore import QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsSceneHoverEvent,
    QStyleOptionGraphicsItem,
    QWidget,
)

from nodedge.socket_type import SocketType

SOCKET_COLORS = [
    QColor("#FFFF7700"),
    QColor("#FF52e220"),
    QColor("#FF0056a6"),
    QColor("#FFa86db1"),
    QColor("#FFb54747"),
    QColor("#FFdbe220"),
    QColor("#FF888888"),
]


class GraphicsSocket(QGraphicsItem):
    """
    :class:`~nodedge.graphics_socket.GraphicsSocket` class.

    The graphics socket is the graphical representation of the
    :class:`~nodedge.socket.Socket`.
    """

    def __init__(self, socket: "Socket") -> None:  # type: ignore
        """
        :param socket: reference to :class:`~nodedge.socket.Socket`
        :type socket: :class:`~nodedge.socket.Socket`
        """

        super(GraphicsSocket, self).__init__(socket.node.graphicsNode)

        self.socket = socket

        self.initUI()

        self.hovered = False

    def initUI(self) -> None:
        """
        Setup this ``QGraphicsItem``.
        """
        self.initSizes()
        self.initStyle()
        self.setAcceptHoverEvents(True)

    # noinspection PyAttributeOutsideInit
    def initStyle(self) -> None:
        """
        Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``.
        """
        self._colorBackground: QColor = getSocketColor(self.socketType.value)
        self._colorOutline: QColor = QColor("#FF000000")
        self._colorHovered: QColor = QColor("#FF37A6FF")

        self._pen: QPen = QPen(self._colorOutline)
        self._pen.setWidthF(self.outlineWidth)
        self._brush: QBrush = QBrush(self._colorBackground)
        self._penHovered: QPen = QPen(self._colorHovered)
        self._penHovered.setWidthF(2.0)

    # noinspection PyAttributeOutsideInit
    def initSizes(self) -> None:
        """
        Set up internal attributes like `width`, `height`, etc.
        """
        self.radius: int = 6
        self.outlineWidth = 1.0

    @property
    def socketType(self) -> SocketType:
        """

        :return: socket type
        :rtype: ``SocketType``
        """

        return self.socket.socketType  # type: ignore

    # noinspection PyAttributeOutsideInit
    def updateSocketType(self) -> None:
        """Change the Socket Type."""
        self._colorBackground = getSocketColor(self.socketType.value)
        self._brush = QBrush(self._colorBackground)
        self.update()

    def paint(
        self,
        painter: QPainter,
        options: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ):
        """
        Paint a circle.
        """
        painter.setBrush(self._brush)
        painter.setPen(self._pen if not self.hovered else self._penHovered)

        painter.drawEllipse(
            -self.radius, -self.radius, 2 * self.radius, 2 * self.radius
        )

        try:
            app = QApplication.palette()
            painter.setBrush(QBrush(QColor(app.dark().color())))
        except AttributeError as e:
            painter.setBrush(QBrush(QColor("white")))
            logging.warning(e)
        if not self.socket.hasAnyEdge:
            painter.drawEllipse(
                -int(self.radius * 0.5),
                -int(self.radius * 0.5),
                self.radius,
                self.radius,
            )

    def boundingRect(self) -> QRectF:
        """
        Define Qt bounding rectangle.

        :return: Graphics socket bounding rectangle.
        :rtype: ``QRectF``
        """
        return QRectF(
            -self.radius - self.outlineWidth,
            -self.radius - self.outlineWidth,
            2 * (self.radius + self.outlineWidth),
            2 * (self.radius + self.outlineWidth),
        )

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """
        Overridden Qt slot to handle mouse hovering on the edge.

        :param event: Qt mouse hover event
        :type event: ``QGraphicsSceneHoverEvent``
        """
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        """
        Overridden Qt slot to handle mouse hovering's end on the edge.

        :param event: Qt mouse hover event
        :type event: ``QGraphicsSceneHoverEvent``
        """
        self.hovered = False
        self.update()


def getSocketColor(key: Union[int, str]) -> QColor:
    """Returns the ``QColor`` for this ``key``."""
    if isinstance(key, int):
        return SOCKET_COLORS[key]
    elif isinstance(key, str):
        return QColor(key)
