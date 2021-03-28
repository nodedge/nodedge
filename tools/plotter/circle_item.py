# -*- coding: utf-8 -*-
import pyqtgraph as pg
from PySide2 import QtGui
from PySide2.QtCore import QPointF, QRectF


class CircleItem(pg.GraphicsObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._center = [0, 0]
        self._radius = 0
        self.picture = QtGui.QPicture()
        self._generate_picture()

    @property
    def center(self):
        return self._center

    @center.setter
    def center(self, value):
        self._center = value
        self._generate_picture()

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        self._radius = value
        self._generate_picture()

    def _generate_picture(self):
        painter = QtGui.QPainter(self.picture)
        painter.setPen(pg.mkPen("w"))
        # painter.setBrush()
        painter.drawEllipse(QPointF(*self.center), self.radius, self.radius)
        painter.end()

    def paint(self, painter, option, widget=None):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QRectF(self.picture.boundingRect())
