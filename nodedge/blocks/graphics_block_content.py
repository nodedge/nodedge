# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QLabel

from nodedge.graphics_node_content import GraphicsNodeContent


class GraphicsBlockContent(GraphicsNodeContent):
    # noinspection PyAttributeOutsideInit
    def initUI(self):
        # TODO: Improve robustness, node may not have operationTitle as attribute
        self.label = QLabel(self.node.contentLabel, self)
        self.label.setObjectName(self.node.contentLabelObjectName)
