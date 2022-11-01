# -*- coding: utf-8 -*-
"""
History list widget module containing
:class:`~nodedge.history_list_widget.HistoryListWidget` class.
"""
import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMainWindow

from nodedge import DEBUG_ITEMS_PRESSED
from nodedge.scene_history import SceneHistory
from nodedge.utils import widgetsAt


class HistoryListWidget(QListWidget):
    """:class:`~nodedge.history_list_widget.HistoryListWidget` class ."""

    itemsPressed = Signal(list)

    def __init__(self, parent: Optional[QMainWindow] = None, history=None):
        super(HistoryListWidget, self).__init__(parent)

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.history: SceneHistory = history

        self.itemClicked.connect(self.onItemClicked)  # type: ignore

    def update(self, *__args) -> None:
        """
        Qt update callback.

        :return: ``None``
        """
        if self.history is not None:
            self.clear()
            for index, stamp in enumerate(self.history.stack):
                item = QListWidgetItem(stamp["desc"], self)
                item.setData(Qt.ToolTipRole, index)

                item.setFlags(
                    Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled
                )

                if index == self.history.currentStep:
                    item.setSelected(True)

        super().viewport().update()

    def onItemClicked(self, item: QListWidgetItem):
        if self.history is not None:
            itemStep = item.data(Qt.ToolTipRole)
            self.history.restoreStep(itemStep)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if DEBUG_ITEMS_PRESSED:
            pos = e.globalPos()
            itemsPressed = [w.__class__.__name__ for w in widgetsAt(pos)]
            self.__logger.debug(itemsPressed)
            # noinspection PyUnresolvedReferences
            self.itemsPressed.emit(itemsPressed)
        super().mousePressEvent(e)
