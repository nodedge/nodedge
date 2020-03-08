# -*- coding: utf-8 -*-
"""
Graphics socket module containing :class:`~nodedge.graphics_socket.GraphicsSocket` class.
"""

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QBrush, QColor, QPen
from PyQt5.QtWidgets import QGraphicsItem


class GraphicsSocket(QGraphicsItem):
    """
    :class:`~nodedge.graphics_socket.GraphicsSocket` class.

    The graphics socket is the graphical representation of the :class:`~nodedge.socket.Socket`.
    """

    def __init__(self, socket: "Socket", socketColor: int = 1) -> None:  # type: ignore
        """
        :param socket: reference to :class:`~nodedge.socket.Socket`
        :type socket: :class:`~nodedge.socket.Socket`
        :param socketColor: Constant representing `Socket` color.
        :type socketColor: ``int``
        """

        super(GraphicsSocket, self).__init__(socket.node.graphicsNode)

        self.socket = socket
        self.socketColor = socketColor

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
        self._colors = [
            QColor("#FFFF7700"),
            QColor("#FF52e220"),
            QColor("#FF0056a6"),
            QColor("#FFa86db1"),
            QColor("#FFdbe220"),
        ]

        self._color_background = self._colors[self.socketColor]
        self._color_outline = QColor("#FF000000")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_background)

    # noinspection PyAttributeOutsideInit
    def initSizes(self) -> None:
        """
        Set up internal attributes like `width`, `height`, etc.
        """
        self.radius = 6.0
        self.outline_width = 1.0

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
            -self.radius - self.outline_width,
            -self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )
