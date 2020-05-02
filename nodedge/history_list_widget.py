# -*- coding: utf-8 -*-
"""
History list widget module containing
:class:`~nodedge.history_list_widget.HistoryListWidget` class.
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QMainWindow

from nodedge.scene_history import SceneHistory


class HistoryListWidget(QListWidget):
    """:class:`~nodedge.history_list_widget.HistoryListWidget` class ."""

    def __init__(self, parent: Optional[QMainWindow] = None, history=None):
        super(HistoryListWidget, self).__init__(parent)

        self.history: SceneHistory = history

        self.itemClicked.connect(self.onItemClicked)  # type: ignore

    def update(self, *__args) -> None:
        if self.history is not None:
            self.clear()
            for index, stamp in enumerate(self.history.stack):
                item = QListWidgetItem(stamp["desc"], self)
                item.setData(Qt.ToolTipRole, index)

                item.setFlags(
                    Qt.ItemIsEnabled
                    | Qt.ItemIsSelectable
                    | Qt.ItemIsDragEnabled  # type: ignore
                )

                if index == self.history.currentStep:
                    item.setSelected(True)

        super().update()

    def onItemClicked(self, item: QListWidgetItem):
        if self.history is not None:
            itemStep = item.data(Qt.ToolTipRole)
            self.history.restoreStep(itemStep)
