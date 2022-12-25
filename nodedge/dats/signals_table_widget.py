from typing import List

from asammdf import MDF
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

COLUMNS = ["Type", "Name"]


class SignalsTableWidget(QTableWidget):
    def __init__(self, parent=None, curveConfig={}, log: MDF = None):
        super().__init__(parent)
        self._parent = parent
        self.setColumnCount(len(COLUMNS))
        self.setRowCount(1)
        self.setHorizontalHeaderLabels(COLUMNS)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.setColumnWidth(0, 16)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.cellClicked.connect(self.onCellClicked)

        self.log = log
        self.signals: List[str] = []
        self.updateItems(self.log)

    def updateItems(self, log: MDF):
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

        configSignals = list(self._parent.curveConfig.keys())

        self.clearContents()
        self.setRowCount(0)

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
        self.clearSelection()

        for i in range(self.columnCount()):
            item = self.item(row, i)
            if item:
                item.setSelected(True)
            else:
                widget = self.cellWidget(row, i)


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