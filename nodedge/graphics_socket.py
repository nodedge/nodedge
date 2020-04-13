# -*- coding: utf-8 -*-
"""
Graphics socket module containing :class:`~nodedge.graphics_socket.GraphicsSocket`
class.
"""

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPen
from PyQt5.QtWidgets import QGraphicsItem

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

    def initUI(self) -> None:
        """
        Setup this ``QGraphicsItem``
        """
        self.initSizes()
        self.initStyle()

    # noinspection PyAttributeOutsideInit
    def initStyle(self) -> None:
        """
        Initialize ``QObjects`` like ``QColor``, ``QPen`` and ``QBrush``
        """
        self._colorBackground: QColor = GraphicsSocket.getSocketColor(self.socketType)
        self._colorOutline: QColor = QColor("#FF000000")

        self._pen: QPen = QPen(self._colorOutline)
        self._pen.setWidthF(self.outlineWidth)
        self._brush: QBrush = QBrush(self._colorBackground)

    # noinspection PyAttributeOutsideInit
    def initSizes(self) -> None:
        """
        Set up internal attributes like `width`, `height`, etc.
        """
        self.radius = 6.0
        self.outlineWidth = 1.0

    @property
    def socketType(self):
        return self.socket.socketType

    @staticmethod
    def getSocketColor(key):
        """Returns the ``QColor`` for this ``key``"""
        if type(key) == int:
            return SOCKET_COLORS[key]
        elif type(key) == str:
            return QColor(key)
        return Qt.transparent

    # noinspection PyAttributeOutsideInit
    def updateSocketType(self):
        """Change the Socket Type"""
        self._colorBackground = self.getSocketColor(self.socketType)
        self._brush = QBrush(self._colorBackground)
        self.update()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        """
        Paint a circle
        """
        painter.setBrush(self._brush)
        painter.setPen(self._pen)

        painter.drawEllipse(
            -self.radius, -self.radius, 2 * self.radius, 2 * self.radius
        )

    def boundingRect(self):
        """
        Define Qt's bounding rectangle
        """
        return QRectF(
            -self.radius - self.outlineWidth,
            -self.radius - self.outlineWidth,
            2 * (self.radius + self.outlineWidth),
            2 * (self.radius + self.outlineWidth),
        )
