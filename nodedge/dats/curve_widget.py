from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QTableWidget,
    QWidget,
)

COLUMNS = ["Name", "Formula", "Unit", "Rate", "Filter", "Rate Type"]


class CurveTableWidget(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(len(COLUMNS))
        self.setRowCount(1)
        self.setHorizontalHeaderLabels(COLUMNS)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.cellChanged.connect(self.onCellChanged)

    def onCellChanged(self, row, column):
        print("onCellChanged", row, column)


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
