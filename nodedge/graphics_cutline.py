import typing

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class GraphicsCutline(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.linePoints = []
        self._pen = QPen(Qt.gray)
        self._pen.setWidth(2.0)
        self._pen.setDashPattern([3, 3])

        self.setZValue(2)

    def boundingRect(self) -> QRectF:
        return self.shape().boundingRect()

    def shape(self):
        if len(self.linePoints) > 1:
            path = QPainterPath(self.linePoints[0])
            for point in self.linePoints[1:]:
                path.lineTo(point)
        else:
            path = QPainterPath(QPointF(0, 0))
            path.lineTo(QPointF(1, 1))

        return path

    def paint(
        self,
        painter: QPainter,
        option: "QStyleOptionGraphicsItem",
        widget: typing.Optional[QWidget] = None,
    ) -> None:
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.linePoints)
        painter.drawPolyline(poly)
