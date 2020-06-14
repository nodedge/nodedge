# -*- coding: utf-8 -*-
"""
Graphics cut line module containing :class:`~nodedge.graphics_cut_line.GraphicsCutLine` class.
"""

from typing import List, Optional, cast

from PyQt5.QtCore import QPointF, QRectF, Qt
from PyQt5.QtGui import QPainter, QPainterPath, QPen, QPolygonF
from PyQt5.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget


class GraphicsCutLine(QGraphicsItem):
    """:class:`~nodedge.graphics_cut_line.GraphicsCutLine` class

    Cutting Line used for cutting multiple `Edges` with one stroke"""

    def __init__(self, parent=None):
        """
        :param parent: parent widget
        :type parent: ``QWidget``
        """

        super().__init__(parent)

        self.linePoints: List[QPointF] = []
        self._pen: QPen = QPen(Qt.gray)
        self._pen.setWidth(2.0)
        self._pen.setDashPattern([3, 3])

        self.setZValue(2)

    def boundingRect(self) -> QRectF:
        """
        Define Qt' bounding rectangle
        """
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        """
        Calculate the ``QPainterPath`` object from list of line points.

        :return: shape function returning ``QPainterPath`` representation of cut line
        :rtype: ``QPainterPath``
        """

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
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """
        Paint the cut line
        """
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.linePoints)
        painter.drawPolyline(poly)
