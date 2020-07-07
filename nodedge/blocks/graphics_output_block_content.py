# -*- coding: utf-8 -*-
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QLabel

from nodedge.graphics_node_content import GraphicsNodeContent


class GraphicsOutputBlockContent(GraphicsNodeContent):
    # noinspection PyAttributeOutsideInit
    def initUI(self):
        self.label: QLabel = QLabel("42", self)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setObjectName(self.node.contentLabelObjectName)
