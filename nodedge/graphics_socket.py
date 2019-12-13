from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class GraphicsSocket(QGraphicsItem):
    def __init__(self, socket, socketType=1):
        super(GraphicsSocket, self).__init__(socket.node.graphicsNode)

        self.radius = 6.
        self.outline_width = 1.
        self._colors = [
            QColor("#FFFF7700"),
            QColor("#FF52e220"),
            QColor("#FF0056a6"),
            QColor("#FFa86db1"),
            QColor("#FFdbe220"),
        ]

        self.socket = socket

        self._color_background = self._colors[socketType]
        self._color_outline = QColor("#FF000000")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_background)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):

        # Painting circle
        painter.setBrush(self._brush)
        painter.setPen(self._pen)

        painter.drawEllipse(-self.radius, -self.radius, 2*self.radius, 2*self.radius)

    def boundingRect(self):
        return QRectF(-self.radius - self.outline_width, -self.radius - self.outline_width,
                      2*(self.radius + self.outline_width), 2*(self.radius + self.outline_width))