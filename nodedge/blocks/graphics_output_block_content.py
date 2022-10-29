# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from nodedge.graphics_node_content import GraphicsNodeContent


class GraphicsOutputBlockContent(GraphicsNodeContent):
    # noinspection PyAttributeOutsideInit
    def initUI(self):
        self.label: QLabel = QLabel("0", self)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setObjectName(self.node.contentLabelObjectName)

    def updateIO(self):
        pass
