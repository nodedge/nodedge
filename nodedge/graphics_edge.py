from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from nodedge.socket import *
import math


class GraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super().__init__(parent)
        self.edge = edge

        self._color = QColor("#001000")
        self._colorSelected = QColor("#00ff00")
        self._pen = QPen(self._color)
        self._pen.setWidthF(2.)
        self._penSelected = QPen(self._colorSelected)
        self._penSelected.setWidthF(2.)
        self._penDragging = QPen(self._color)
        self._penDragging.setWidthF(2.)
        self._penDragging.setStyle(Qt.DashLine)

        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.setZValue(-1)

        self.posSource = [0, 0]
        self.posDestination = [200, 100]

        self._controlPointRoundness = 100

    def setSource(self, x, y):
        self.posSource = [x, y]

    def setDestination(self, x, y):
        self.posDestination = [x, y]

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self.calcPath()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.setPath(self.calcPath())

        if self.edge.endSocket is None:
            painter.setPen(self._penDragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._penSelected)

        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    def calcPath(self):
        """ Handle drawing QPainter path from point A to B
        """
        raise NotImplemented("This method needs to be overridden in a child class")

    def intersectsWith(self, p1, p2):
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)


class GraphicsEdgeDirect(GraphicsEdge):
    def calcPath(self):
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        return path


class GraphicsEdgeBezier(GraphicsEdge):
    def calcPath(self):
        s = self.posSource
        d = self.posDestination
        dist = (d[0] - s[0]) * 0.5

        cpx_s = dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.edge.startSocket is not None:
            sspos = self.edge.startSocket.position

            if (s[0] > d[0] and sspos in [RIGHT_TOP, RIGHT_BOTTOM]) or (s[0] < d[0] and sspos in [LEFT_BOTTOM, LEFT_TOP]):
                cpx_d *= -1
                cpx_s *= -1

                verticalDistance = s[1] - d[1]
                cpy_d = verticalDistance / (1e-4 + (math.fabs(verticalDistance))) * self._controlPointRoundness
                cpy_s = -cpy_d

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.cubicTo(s[0]+cpx_s, s[1]+cpy_s,
                     d[0]+cpx_d, d[1]+cpy_d,
                     self.posDestination[0], self.posDestination[1])
        return path


