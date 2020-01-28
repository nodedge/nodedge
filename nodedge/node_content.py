from collections import OrderedDict
from typing import cast

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFocusEvent
from PyQt5.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from nodedge.serializable import Serializable


class NodeContent(QWidget, Serializable):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node

        self.initUI()
        self.setAttribute(Qt.WA_TranslucentBackground)

    # noinspection PyAttributeOutsideInit
    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(AckTextEdit("X3"))

    def setEditingFlag(self, value):
        self.node.scene.view.editingFlag = value

    def serialize(self):
        return OrderedDict([])

    def deserialize(self, data, hashmap=None, restoreId=False):
        if hashmap is None:
            hashmap = {}
        return True


class AckTextEdit(QTextEdit):
    def focusInEvent(self, e: QFocusEvent) -> None:
        parent: NodeContent = cast(NodeContent, super().parentWidget())
        parent.setEditingFlag(True)
        super().focusInEvent(e)

    def focusOutEvent(self, e: QFocusEvent) -> None:
        parent: NodeContent = cast(NodeContent, super().parentWidget())
        parent.setEditingFlag(False)
        super().focusOutEvent(e)
