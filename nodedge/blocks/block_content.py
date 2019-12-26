from PyQt5.QtWidgets import *

from nodedge.node_content import NodeContent


class BlockContent(NodeContent):
    def initUI(self):
        self.label = QLabel(self.node.contentLabel, self)
        self.label.setObjectName(self.node.contentLabelObjectName)
