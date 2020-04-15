import os

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QImage

from nodedge.graphics_node import GraphicsNode


class GraphicsBlock(GraphicsNode):
    # noinspection PyAttributeOutsideInit
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 80
        self.edgeRoundness = 10.0
        self.edgePadding = 0.0
        self.titleHorizontalPadding = 8.0
        self.titleVerticalPadding = 10.0

    # noinspection PyAttributeOutsideInit
    def initStyle(self):
        super().initStyle()
        self.icons = QImage(
            f"{os.path.dirname(__file__)}/../resources/node_icons/status_icons.png"
        )

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        offset = 24.0

        if self.node.isDirty:
            offset = 0.0
        if self.node.isInvalid:
            offset = 48.0

        painter.drawImage(
            QRectF(-10.0, -10.0, 24.0, 24.0), self.icons, QRectF(offset, 0, 24.0, 24.0)
        )
