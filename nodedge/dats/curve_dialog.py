import json

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from nodedge.dats.logs_list_widget import LogsListWidget
from nodedge.dats.signals_list_widget import SignalsListWidget


class CurveLineEdit(QLineEdit):
    def __init__(self, parent=None, signals=[]):
        super().__init__(parent)
        self.parent = parent
        self.setPlaceholderText("Enter curve name")
        self.signals = signals

        self.textChanged.connect(self.updateTextFont)

        self.valid = False

    def updateTextFont(self):
        if (
            self.text() in self.signals
            or " " in self.text()
            or not self.text().isalnum()
        ):
            self.setStyleSheet("color: red")
            self.valid = False
        else:
            self.setStyleSheet("")
            self.valid = True


class CurveDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.setWindowTitle("Curve Editor")
        self.resize(800, 600)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.leftFrame = QWidget()
        self.leftFrame.setMinimumWidth(200)
        self.layout.addWidget(self.leftFrame)
        self.leftLayout = QVBoxLayout()
        self.leftFrame.setLayout(self.leftLayout)

        self.mainFrame = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mainFrame.setLayout(self.mainLayout)
        self.layout.addWidget(self.mainFrame)
        self.mainFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        logs = self.parent.logsWidget.logsListWidget.logs
        self.logsWidget = LogsListWidget(logs=logs)
        signals = self.parent.signalsWidget.signalsListWidget.signals
        self.signalsWidget = SignalsListWidget(signals=signals)
        self.signalsWidget.itemDoubleClicked.connect(self.onSignalDoubleClicked)

        self.leftLayout.addWidget(self.logsWidget)
        self.leftLayout.addWidget(self.signalsWidget)

        self.curveNameEdit = CurveLineEdit(signals=signals)
        self.mainLayout.addWidget(self.curveNameEdit)
        self.curveDefinitionEdit = QTextEdit()
        self.curveDefinitionEdit.setPlaceholderText("Enter curve definition")
        self.mainLayout.addWidget(self.curveDefinitionEdit)

        self.unitWidget = QWidget()
        self.unitLayout = QHBoxLayout()
        self.unitWidget.setLayout(self.unitLayout)
        self.mainLayout.addWidget(self.unitWidget)

        self.unitDomainCombo = QComboBox()

        with open("nodedge/dats/unit_config.json") as f:
            self.unitsDict = json.load(f)

        self.unitDomainCombo.addItems([domain for domain in self.unitsDict.keys()])
        self.unitLayout.addWidget(self.unitDomainCombo)
        self.unitDomainCombo.currentTextChanged.connect(self.onUnitDomainChanged)
        self.unitDomainCombo.setCurrentText("Time")

        self.unitCombo = QComboBox()
        self.unitCombo.addItems(self.unitsDict["Time"])
        # self.unitCombo.addItems(["s", "ms", "us", "ns", "ps", "fs", "as"])
        self.unitLayout.addWidget(self.unitCombo)

    def onSignalDoubleClicked(self, item):
        if self.curveNameEdit.text() == "":
            self.curveNameEdit.setText(item.text())
        self.curveDefinitionEdit.setText(
            self.curveDefinitionEdit.toPlainText() + item.text()
        )

    def onUnitDomainChanged(self, text):
        self.unitCombo.clear()
        self.unitCombo.addItems(self.unitsDict[text])
