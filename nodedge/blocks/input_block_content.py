from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit

from nodedge.node_content import NodeContent
from nodedge.utils import dumpException


class InputBlockContent(NodeContent):
    def initUI(self):
        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignRight)
        self.edit.setObjectName(self.node.contentLabelObjectName)

    def serialize(self):
        res = super().serialize()
        res["value"] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}, restoreId=False):
        res = super().deserialize(data, hashmap, restoreId)
        try:
            value = data["value"]
            self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)

        return res