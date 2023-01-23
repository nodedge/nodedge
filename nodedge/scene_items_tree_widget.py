# -*- coding: utf-8 -*-
"""
Scene items tree widget module containing
:class:`~nodedge.scene_items_tree_widget.SceneItemsTreeWidget` class.
"""
import logging
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
)

from nodedge import DEBUG_ITEMS_PRESSED
from nodedge.scene import Scene
from nodedge.utils import widgetsAt

logger = logging.getLogger(__name__)


class SceneItemsTreeWidget(QTreeWidget):
    itemsPressed = Signal(list)

    def __init__(self, parent: Optional[QMainWindow] = None):
        super().__init__(parent)

        self._scene: Optional[Scene] = None

        headerNames = ("Name", "Type")
        self.setColumnCount(len(headerNames))
        for i in range(len(headerNames)):
            self.header().setSectionResizeMode(i, QHeaderView.Stretch)
        self.setHeaderLabels(headerNames)

        self.itemClicked.connect(self.onItemClicked)
        self.itemDoubleClicked.connect(self.onItemDoubleClicked)

        self.setIndentation(6)

    @property
    def scene(self) -> Optional[Scene]:
        return self._scene

    @scene.setter
    def scene(self, scene: Optional[Scene]) -> None:
        self._scene = scene
        self.update()
        if self._scene is None:
            return
        self._scene.history.addHistoryModifiedListener(self.update)

    def update(self, *__args) -> None:
        self.clear()
        logger.debug("Scene items tree widget updating.")

        if self._scene is not None:
            self.rootItem = QTreeWidgetItem()
            self.rootItem.setText(0, self._scene.shortName)
            self.addTopLevelItem(self.rootItem)
            for node in self._scene.nodes:
                nameItem = QTreeWidgetItem()
                nameItem.setText(0, node.title)
                nameItem.setText(1, f"{node.__class__.__name__}")
                # nameItem.setText(2, f"{node.pos.x()}")
                # nameItem.setText(3, f"{node.pos.y()}")
                # nameItem.setFlags(nameItem.flags() ^ Qt.ItemIsEditable)

                self.rootItem.addChild(nameItem)
        self.expandAll()

        # super().viewport().update()

    def onItemClicked(self, item: QTreeWidgetItem, column: int):
        scene = self.scene
        if scene is None:
            return
        scene.doDeselectItems(True)
        nodeTitles = {node.title: node for node in scene.nodes}
        if item.text(0) in list(nodeTitles.keys()):
            nodeTitles[item.text(0)].isSelected = True

    def onItemDoubleClicked(self, item: QTreeWidgetItem, column: int):
        scene = self.scene
        if scene is None:
            return
        scene.doDeselectItems(True)
        nodeTitles = {node.title: node for node in scene.nodes}
        if item.text(0) in list(nodeTitles.keys()):
            node = nodeTitles[item.text(0)]
            node.isSelected = True
            logger.debug(f"Double clicked on {node.title}")
            scene.graphicsView.centerOn(node.pos)

    #
    # def onCellDoubleClicked(self, row, column):
    #     self.scene.graphicsView.centerOn(
    #         float(self.item(row, 2).text()), float(self.item(row, 3).text())
    #     )
    #
    # def mousePressEvent(self, e: QMouseEvent) -> None:
    #     pos = e.globalPos()
    #     if DEBUG_ITEMS_PRESSED:
    #         itemsPressed = [w.__class__.__name__ for w in widgetsAt(pos)]
    #         self.__logger.debug(itemsPressed)
    #         # noinspection PyUnresolvedReferences
    #         self.itemsPressed.emit(itemsPressed)
    #     super().mousePressEvent(e)
