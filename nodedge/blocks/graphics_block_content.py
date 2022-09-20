# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QListWidget, QListWidgetItem, QSizePolicy

from nodedge.graphics_node_content import GraphicsNodeContent
from nodedge.socket_type import SocketType


class GraphicsBlockContent(GraphicsNodeContent):
    # noinspection PyAttributeOutsideInit
    def initUI(self):
        # TODO: Improve robustness, node may not have operationTitle as attribute
        # self.label = QLabel(self.node.contentLabel, self)
        # self.label.setObjectName(self.node.contentLabelObjectName)

        self.hLayout = QHBoxLayout(self)
        self.hLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.hLayout)
        self.listInputs = QListWidget(self)
        self.listInputs.setSizePolicy(
            QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        )
        self.listInputs.horizontalScrollBar().setDisabled(True)
        self.listInputs.verticalScrollBar().setDisabled(True)
        self.listInputs.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listInputs.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.hLayout.addWidget(self.listInputs)

        self.listOutputs = QListWidget(self)
        self.listOutputs.setItemAlignment(Qt.AlignRight)
        self.listOutputs.setSizePolicy(
            QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        )
        self.listOutputs.horizontalScrollBar().setDisabled(True)
        self.listOutputs.verticalScrollBar().setDisabled(True)
        self.listOutputs.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.listOutputs.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.hLayout.addWidget(self.listOutputs)

    def updateIO(self) -> None:
        """
        Write the types on the sockets in front of the sockets.

        Unused for now as it is not ergonomic to see as much as type on the screen.
        :return: ``None``
        """

        # self.listInputs.clear()
        # for input in self.node.inputSockets:
        #     inputItem = QListWidgetItem(SocketType(input.socketType).name)
        #     self.listInputs.addItem(inputItem)
        #     inputItem.setFlags(inputItem.flags() & ~Qt.ItemIsUserCheckable)
        #
        # self.listOutputs.clear()
        # for output in self.node.outputSockets:
        #     outputItem = QListWidgetItem(SocketType(output.socketType).name)
        #     self.listOutputs.addItem(outputItem)
        #     outputItem.setTextAlignment(Qt.AlignRight)
        #     outputItem.setFlags(outputItem.flags() & ~Qt.ItemIsUserCheckable)
        pass
