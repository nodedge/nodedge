from PyQt5.QtWidgets import QLabel

from nodedge.node_content import NodeContent


class BlockContent(NodeContent):
    # noinspection PyAttributeOutsideInit
    def initUI(self):
        # TODO: Improve robustness, node may not have operationTitle as attribute
        self.label = QLabel(self.node.contentLabel, self)
        self.label.setObjectName(self.node.contentLabelObjectName)
