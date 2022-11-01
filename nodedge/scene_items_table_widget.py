# -*- coding: utf-8 -*-
"""
Scene items table widget module containing
:class:`~nodedge.scene_items_table_widget.SceneItemsTableWidget` class.
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
)

from nodedge import DEBUG_ITEMS_PRESSED
from nodedge.scene import Scene
from nodedge.utils import widgetsAt


class SceneItemsTableWidget(QTableWidget):
    """:class:`~nodedge.scene_items_table_widget.SceneItemsTableWidget` class ."""

    itemsPressed = Signal(list)

    def __init__(self, parent: Optional[QMainWindow] = None):
        super().__init__(parent)

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.setColumnCount(4)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.scene: Optional[Scene] = None

        headerNames = ("Name", "Type", "PosX", "PosY")
        self.setHorizontalHeaderLabels(headerNames)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.verticalHeader().hide()
        self.setShowGrid(True)
        self.cellClicked.connect(self.onCellClicked)  # type: ignore
        self.cellDoubleClicked.connect(self.onCellDoubleClicked)  # type: ignore

    def update(self, *__args) -> None:
        if self.scene is not None:
            self.setRowCount(0)
            for node in self.scene.nodes:
                nameItem = QTableWidgetItem(node.title)
                nameItem.setFlags(nameItem.flags() ^ Qt.ItemIsEditable)

                typeItem = QTableWidgetItem(f"{node.__class__.__name__}")
                typeItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                typeItem.setFlags(typeItem.flags() ^ Qt.ItemIsEditable)

                posXItem = QTableWidgetItem(f"{node.pos.x()}")
                posXItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                posXItem.setFlags(posXItem.flags() ^ Qt.ItemIsEditable)

                posYItem = QTableWidgetItem(f"{node.pos.y()}")
                posYItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                posYItem.setFlags(posYItem.flags() ^ Qt.ItemIsEditable)

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

                self.setRowHeight(row, 30)

            # TODO: Activate elements in table widget.
            # for element in self.scene.elements:
            #     nameItem = QTableWidgetItem(element.content)
            #     nameItem.setFlags(nameItem.flags() ^ Qt.ItemIsEditable)
            #
            #     typeItem = QTableWidgetItem(f"{element.__class__.__name__}")
            #     typeItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            #     typeItem.setFlags(typeItem.flags() ^ Qt.ItemIsEditable)
            #
            #     posXItem = QTableWidgetItem(f"{element.pos.x()}")
            #     posXItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            #     posXItem.setFlags(posXItem.flags() ^ Qt.ItemIsEditable)
            #
            #     posYItem = QTableWidgetItem(f"{element.pos.y()}")
            #     posYItem.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            #     posYItem.setFlags(posYItem.flags() ^ Qt.ItemIsEditable)
            #
            #     row = self.rowCount()
            #     self.insertRow(row)
            #     self.setItem(row, 0, nameItem)
            #     self.setItem(row, 1, typeItem)
            #     self.setItem(row, 2, posXItem)
            #     self.setItem(row, 3, posYItem)
            #
            #     if element.graphicsElement in self.scene.selectedItems:
            #         nameItem.setSelected(True)
            #         typeItem.setSelected(True)
            #         posXItem.setSelected(True)
            #         posYItem.setSelected(True)
            #
            #     self.setRowHeight(row, 30)

        super().viewport().update()

    def onCellClicked(self, row: int, column: int):
        if self.scene is not None:
            self.scene.doDeselectItems(True)
            self.scene.nodes[row].isSelected = True
        self.item(row, column).setSelected(True)

    def onCellDoubleClicked(self, row, column):
        self.scene.graphicsView.centerOn(
            float(self.item(row, 2).text()), float(self.item(row, 3).text())
        )

    def mousePressEvent(self, e: QMouseEvent) -> None:
        pos = e.globalPos()
        if DEBUG_ITEMS_PRESSED:
            itemsPressed = [w.__class__.__name__ for w in widgetsAt(pos)]
            self.__logger.debug(itemsPressed)
            # noinspection PyUnresolvedReferences
            self.itemsPressed.emit(itemsPressed)
        super().mousePressEvent(e)
