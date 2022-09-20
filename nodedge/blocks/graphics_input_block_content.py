# -*- coding: utf-8 -*-
"""
Graphics input block content module containing
:class:`~nodedge.graphics_input_block_content.GraphicsInputBlockContent` class.
"""

from typing import Optional

from PySide6.QtWidgets import QLineEdit

from nodedge.graphics_node_content import GraphicsNodeContent
from nodedge.utils import dumpException


class GraphicsInputBlockContent(GraphicsNodeContent):
    """
    :class:`~nodedge.graphics_input_block_content.GraphicsInputBlockContent` class
    """

    # noinspection PyAttributeOutsideInit
    def initUI(self):
        self.edit: QLineEdit = QLineEdit("1", self)
        self.edit.setObjectName(self.node.contentLabelObjectName)

        self.edit.editingFinished.connect(self.onEditingFinished)

    def updateIO(self):
        pass

    def serialize(self):
        res = super().serialize()
        res["value"] = self.edit.text()
        return res

    def deserialize(
        self,
        data: dict,
        hashmap: Optional[dict] = None,
        restoreId: bool = False,
        *args,
        **kwargs
    ):
        if hashmap is None:
            hashmap = {}
        res = super().deserialize(data, hashmap, restoreId)
        try:
            value = data["value"]
            self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)

        return res

    def onEditingFinished(self):
        if (
            self.node is not None
            and self.node.scene is not None
            and self.node.scene.history is not None
        ):
            self.node.scene.history.store("Change input content")
