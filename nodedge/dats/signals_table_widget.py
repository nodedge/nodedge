import logging
from typing import List, Optional

from asammdf import MDF
from PySide6.QtCore import QByteArray, QMimeData, Qt
from PySide6.QtGui import QDrag, QKeyEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from nodedge.utils import dumpException

COLUMNS = ["Type", "Name"]

logger = logging.getLogger(__name__)


class SignalsTableWidget(QTableWidget):
    def __init__(self, parent=None, curveConfig={}, log: MDF = None):
        super().__init__(parent)
        self._parent = parent
        self.setColumnCount(len(COLUMNS))
        self.setRowCount(1)
        self.setHorizontalHeaderLabels(COLUMNS)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.setColumnWidth(0, 40)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setDragEnabled(True)

        self.cellClicked.connect(self.onCellClicked)

        self.log = log
        self.signals: List[str] = []
        self.allSignals: List[str] = []
        self.updateItems(self.log)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        super().keyPressEvent(event)
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.multiSelectionMode = True

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        super().keyReleaseEvent(event)
        if not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.multiSelectionMode = False

    def updateItems(self, log: Optional[MDF]):
        self.clearContents()
        self.setRowCount(0)
        if log is None:
            return
        signals = list(log.channels_db.keys())

        # TODO: Fix in case of multiple signals with the same name
        # for s in signals:
        #     if len(log.channels_db[s]) > 1:
        #         for i in range(len(log.channels_db[s])):
        #             signals.append(f"{s}_{log.channels_db[s][0]}")
        signals = [c for c in signals if c[0:3] != "CAN"]
        signals = [c for c in signals if c[0:3] != "LIN"]
        signals = [c for c in signals if c != "time"]

        self.signals = sorted(signals)
        print(self.signals)

        configSignals = list(self._parent.curveConfig.keys())
        self.allSignals = sorted(list(set(self.signals + configSignals)))

        for signal in self.signals:
            typeItem = QTableWidgetItem()
            typeItem.setTextAlignment(Qt.AlignCenter)
            typeItem.setFlags(typeItem.flags() & ~Qt.ItemIsEditable)

            # The signal is computed with a formula.
            if signal in configSignals:
                typeItem.setText("ƒ")
                typeItem.setToolTip("Computed with a formula")
            else:
                typeItem.setText("~")
                typeItem.setToolTip("Raw signal")

            nameItem = QTableWidgetItem()
            nameItem.setFlags(nameItem.flags() & ~Qt.ItemIsEditable)
            nameItem.setText(signal)

            row = self.rowCount()
            self.insertRow(row)
            self.setRowHeight(row, 25)
            self.setItem(row, 0, typeItem)
            self.setItem(row, 1, nameItem)

    def onCellClicked(self, row, column):
        for item in self.selectedItems():
            if item.column() != 1:
                item.setSelected(False)
                self.item(row, 1).setSelected(True)

    def startDrag(self, supportedActions: Qt.DropAction) -> None:
        try:
            items = self.selectedItems()
            itemsNames = [item.text() for item in items if item.column() == 1]
            itemData = QByteArray()

            mimeData = QMimeData()
            mimeData.setData("text/plain", itemData)
            mimeData.setText("\n".join(itemsNames))

            drag = QDrag(self)
            drag.setMimeData(mimeData)

            drag.exec_(Qt.MoveAction)

            for item in items:
                item.setSelected(False)

        except Exception as e:
            dumpException(e)


class CurveWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(1)
        self.curveWidget = CurveWidget()
        self.layout.addWidget(self.curveWidget)

        self.setLayout(self.layout)

        self.curveTableWidget = QTableWidget()
