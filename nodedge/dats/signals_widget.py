from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QWidget

from nodedge.dats.signals_table_widget import SignalsTableWidget


class SignalsWidget(QWidget):
    plotSelectedSignals = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        # self.layout.setContentsMargins(1, 1, 1, 1)
        # self.layout.setSpacing(1)
        self.signalsTableWidget = SignalsTableWidget(parent, parent.curveConfig)
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText("Search signals")
        self.lineEdit.textChanged.connect(self.updateDisplay)
        self.plotButton = QPushButton("Plot")
        self.plotButton.setFixedWidth(200)
        self.plotButton.clicked.connect(self.onButtonClicked)

        self.layout.addWidget(self.lineEdit)
        self.layout.addWidget(self.signalsTableWidget)
        self.layout.addWidget(self.plotButton, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

    def updateDisplay(self):
        allItems = self.signalsTableWidget.findItems("", Qt.MatchContains)
        for i in allItems:
            if i is not None:
                self.signalsTableWidget.setRowHidden(i.row(), True)
        items = self.signalsTableWidget.findItems(
            self.lineEdit.text(), Qt.MatchRegularExpression
        )
        for i in items:
            if i is not None:
                self.signalsTableWidget.setRowHidden(i.row(), False)

    def onButtonClicked(self):
        items = self.signalsTableWidget.selectedItems()

        for i in items:
            if i.column() != 1:
                items.remove(i)

        self.plotSelectedSignals.emit(items)
