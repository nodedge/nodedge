# -*- coding: utf-8 -*-
import os

from PySide6.QtGui import QImage, QPixmap

from nodedge.graphics_node import GraphicsNode


class GraphicsBlock(GraphicsNode):
    # noinspection PyAttributeOutsideInit
    def initSizes(self):
        super().initSizes()
        self.width = 200
        self.height = 80
        self.edgeRoundness = 2.0
        self.edgePadding = 0.0
        self.titleHorizontalPadding = 8.0
        self.titleVerticalPadding = 18.0

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
        #
        # painter.drawImage(
        #     QRectF(-10.0, -10.0, 24.0, 24.0), self.icons, QRectF(offset, 0, 24.0, 24.0)
        # )

        self.statusLabel.setPixmap(QPixmap(self.icons).copy(offset, 0, 24.0, 24.0))
