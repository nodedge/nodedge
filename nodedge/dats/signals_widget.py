from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QWidget

from nodedge.dats.signals_list_widget import SignalsListWidget


class SignalsWidget(QWidget):
    plotSelectedSignals = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(1)
        self.signalsListWidget = SignalsListWidget()
        self.layout.addWidget(self.signalsListWidget)
        self.lineEdit = QLineEdit()
        self.lineEdit.textChanged.connect(self.updateDisplay)  # type: ignore
        self.layout.addWidget(self.lineEdit)
        self.plotButton = QPushButton("Plot")
        self.plotButton.clicked.connect(self.onButtonClicked)  # type: ignore
        self.layout.addWidget(self.plotButton)

        self.setLayout(self.layout)

    def updateDisplay(self):
        allItems = self.signalsListWidget.findItems("", Qt.MatchContains)
        for i in allItems:
            i.setHidden(True)
        items = self.signalsListWidget.findItems(
            self.lineEdit.text(), Qt.MatchRegularExpression
        )
        for i in items:
            i.setHidden(False)

    def onButtonClicked(self):
        items = self.signalsListWidget.selectedItems()
        self.plotSelectedSignals.emit(items)  # type: ignore
