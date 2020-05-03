# -*- coding: utf-8 -*-
"""
Scene items table widget module containing
:class:`~nodedge.scene_items_table_widget.SceneItemsTableWidget` class.
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
)

from nodedge.scene import Scene


class SceneItemsTableWidget(QTableWidget):
    """:class:`~nodedge.scene_items_table_widget.SceneItemsTableWidget` class ."""

    def __init__(self, parent: Optional[QMainWindow] = None):
        super().__init__(parent)

        self.setColumnCount(4)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.scene: Optional[Scene] = None

        headerNames = ("Name", "Type", "PosX", "PosY")
        self.setHorizontalHeaderLabels(headerNames)
        # self.sceneItemsTableWidget.horizontalHeader().setSectionResizeMode(
        #     0, QHeaderView.Stretch
        # )
        self.verticalHeader().hide()
        self.setShowGrid(True)

        self.cellClicked.connect(self.onCellClicked)  # type: ignore
        self.cellDoubleClicked.connect(self.onCellDoubleClicked)  # type: ignore

    def update(self, *__args) -> None:
        if self.scene is not None:
            self.setRowCount(0)
            for node in self.scene.nodes:

                nameItem = QTableWidgetItem(node.title)
                nameItem.setFlags(nameItem.flags() ^ Qt.ItemIsEditable)  # type: ignore

                typeItem = QTableWidgetItem(f"{node.__class__.__name__}")
                typeItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                typeItem.setFlags(typeItem.flags() ^ Qt.ItemIsEditable)  # type: ignore

                posXItem = QTableWidgetItem(f"{node.pos.x()}")
                posXItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                posXItem.setFlags(posXItem.flags() ^ Qt.ItemIsEditable)  # type: ignore

                posYItem = QTableWidgetItem(f"{node.pos.y()}")
                posYItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                posYItem.setFlags(posYItem.flags() ^ Qt.ItemIsEditable)  # type: ignore

                row = self.rowCount()
                self.insertRow(row)
                self.setItem(row, 0, nameItem)
                self.setItem(row, 1, typeItem)
                self.setItem(row, 2, posXItem)
                self.setItem(row, 3, posYItem)

                if node.graphicsNode in self.scene.selectedItems:
                    nameItem.setSelected(True)
                    typeItem.setSelected(True)
                    posXItem.setSelected(True)
                    posYItem.setSelected(True)

            self.resizeColumnsToContents()

    def onCellClicked(self, row: int, column: int):
        if self.scene is not None:
            self.scene.doDeselectItems(True)
            self.scene.nodes[row].isSelected = True
        self.item(row, column).setSelected(True)

    def onCellDoubleClicked(self, row, column):
        self.scene.view.centerOn(
            float(self.item(row, 2).text()), float(self.item(row, 3).text())
        )
