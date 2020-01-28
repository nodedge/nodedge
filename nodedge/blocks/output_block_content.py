from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

from nodedge.node_content import NodeContent


class OutputBlockContent(NodeContent):
    # noinspection PyAttributeOutsideInit
    def initUI(self):
        self.label: QLabel = QLabel("42", self)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setObjectName(self.node.contentLabelObjectName)
