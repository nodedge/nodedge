import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *

from nodedge.graphics_node import GraphicsNode


class GraphicsBlock(GraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 80
        self.edgeRoundness = 10.
        self.edgePadding = 0.
        self.titleHorizontalPadding = 8.
        self.titleVerticalPadding = 10.

    def initStyle(self):
        super().initStyle()
        self.icons = QImage(f"{os.path.dirname(__file__)}/../resources/node_icons/status_icons.png")

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        offset = 24.

        if self.node.isDirty:
            offset = 0.
        if self.node.isInvalid:
            offset = 48.

        painter.drawImage(
            QRectF(-10., -10., 24., 24.),
            self.icons,
            QRectF(offset, 0, 24., 24.)
        )
