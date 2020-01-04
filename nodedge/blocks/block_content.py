from PyQt5.QtWidgets import *

from nodedge.node_content import NodeContent


class BlockContent(NodeContent):
    def initUI(self):
        # TODO: Improve robustness, node may not have operationTitle as attribute
        self.label = QLabel(self.node.contentLabel, self)
        self.label.setObjectName(self.node.contentLabelObjectName)
