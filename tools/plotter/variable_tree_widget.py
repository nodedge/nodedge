# -*- coding: utf-8 -*-
"""
VariableTreeWidget.py module containing :class:`~nodedge.VariableTreeWidget.py.<ClassName>` class.
"""
import logging
from typing import Optional

from PySide2.QtCore import QEvent, Qt, Signal, Slot
from PySide2.QtGui import QMouseEvent
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem

from tools.plotter.utils import H5Types

COLUMNS = {
    "Name": 0,
    "Type": 1,
}

H5TYPES_TO_STR = {
    H5Types.GROUP: "Group",
    H5Types.DATASET: "Dataset",
}


class VariableTreeWidget(QTreeWidget):
    variableDoubleClicked = Signal(str)
    variableCtrlClicked = Signal(str)
    variableShiftClicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.setHeaderLabels(COLUMNS.keys())
        self.setSortingEnabled(True)

        self.itemDoubleClicked.connect(self.onItemClicked)

    @Slot(str)  # type: ignore
    def onItemClicked(self, item: QTreeWidgetItem):
        # onItemClickedHdf5()
        self.__logger.debug(
            f"{item.text(COLUMNS['Name'])} "
            f"({item.text(COLUMNS['Type'])}) has been double clicked."
        )
        fullDatasetName = COLUMNS["Name"]
        if item.text(COLUMNS["Type"]) == "Dataset":
            parent: Optional[QTreeWidgetItem] = item.parent()
            fullDatasetName = item.text(COLUMNS["Name"])
            while parent is not None:
                parentName = parent.text(COLUMNS["Name"])
                fullDatasetName = parentName + "/" + fullDatasetName
                parent = parent.parent()
        self.variableDoubleClicked.emit(fullDatasetName)  # type: ignore

    def onHeaderClicked(self, index):
        self.sortItems(index, Qt.AscendingOrder)

    def updateVariablesHdf5(self, allKeys, allTypes):
        # Remove first key "/"
        allKeys = allKeys[1::]
        allTypes = allTypes[1::]

        # Create QTreeWidgetItems and store them in a dictionary
        self.variableDict = {}
        for ind, key in enumerate(allKeys):
            itemTitle = key[1::].split("/")[-1]
            item = QTreeWidgetItem()
            item.setText(COLUMNS["Name"], itemTitle)
            item.setText(COLUMNS["Type"], H5TYPES_TO_STR[allTypes[ind]])
            self.variableDict.update({key: item})

        # Populate the TreeWidget
        for key in self.variableDict.keys():
            # Keys always start with "/", so remove it
            splitKey = key[1::].split("/")
            # Case 1: Top level items
            if len(splitKey) == 1:
                self.addTopLevelItem(self.variableDict[key])
            # Case 2: Child level items
            else:
                parentItemName = "/" + "/".join(splitKey[0:-1])
                parentItem = self.variableDict[parentItemName]
                parentItem.addChild(self.variableDict[key])

    def updateVariablesCsv(self, allKeys):

        # Create QTreeWidgetItems and store them in a dictionary
        self.variableDict = {}
        for ind, key in enumerate(allKeys):
            itemTitle = key
            item = QTreeWidgetItem()
            item.setText(COLUMNS["Name"], itemTitle)
            item.setText(COLUMNS["Type"], H5TYPES_TO_STR[H5Types.DATASET])
            self.variableDict.update({key: item})

        # Populate the TreeWidget:
        # For a csv, keys are always top level
        for key in self.variableDict.keys():
            self.addTopLevelItem(self.variableDict[key])

    def mouseReleaseEvent(self, event: QMouseEvent):
        super().mouseReleaseEvent(event)
        l = [item.text(COLUMNS["Name"]) for item in self.selectedItems()]
        self.__logger.debug(l)
        mod = event.modifiers()
        self.__logger.debug(mod)

        eventButton: Qt.MouseButton = event.button()
        pos = event.pos()
        item = self.itemAt(pos)
        fullVariableName = self.getFullName(item)
        eventModifiers: Qt.KeyboardModifiers = event.modifiers()
        if eventButton == Qt.LeftButton and eventModifiers & Qt.ControlModifier:
            self.variableCtrlClicked.emit(fullVariableName)
        elif eventButton == Qt.LeftButton and eventModifiers & Qt.ShiftModifier:
            self.variableShiftClicked.emit(fullVariableName)

    def getFullName(self, item):
        fullDatasetName = COLUMNS["Name"]
        if item.text(COLUMNS["Type"]) == "Dataset":
            parent: Optional[QTreeWidgetItem] = item.parent()
            fullDatasetName = item.text(COLUMNS["Name"])
            while parent is not None:
                parentName = parent.text(COLUMNS["Name"])
                fullDatasetName = parentName + "/" + fullDatasetName
                parent = parent.parent()

        return fullDatasetName
