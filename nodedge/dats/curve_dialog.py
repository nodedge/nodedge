import json

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
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
            # or not (self.text().isalnum() or "_" not in self.text())
        ):
            self.setStyleSheet("color: red")
            self.valid = False
        else:
            self.setStyleSheet("")
            self.valid = True


class CurveFormulaEdit(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setPlaceholderText("Enter curve formula")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.valid = False

        self.textChanged.connect(self.updateTextFont)

    def updateTextFont(self):
        print(self.toPlainText())


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
        self.curveFormulaEdit = CurveFormulaEdit()
        self.mainLayout.addWidget(self.curveFormulaEdit)

        self.unitWidget = QWidget()
        self.unitLayout = QHBoxLayout()
        self.unitWidget.setLayout(self.unitLayout)
        self.mainLayout.addWidget(self.unitWidget)
        self.rateWidget = QWidget()
        self.rateLayout = QHBoxLayout()
        self.rateWidget.setLayout(self.rateLayout)
        self.mainLayout.addWidget(self.rateWidget)

        self.unitDomainCombo = QComboBox()

        with open("nodedge/dats/unit_config.json") as f:
            self.unitsDict = json.load(f)

        self.unitDomainCombo.addItems([domain for domain in self.unitsDict.keys()])
        self.unitLayout.addWidget(self.unitDomainCombo)
        self.unitDomainCombo.currentTextChanged.connect(self.onUnitDomainChanged)
        self.unitDomainCombo.setCurrentText("Time")

        self.unitCombo = QComboBox()
        self.unitCombo.addItems(self.unitsDict["Time"])
        self.unitLayout.addWidget(self.unitCombo)

        self.typeRateCombo = QComboBox()
        self.typeRateCombo.addItems(["Frequency", "Period"])
        self.typeRateCombo.setCurrentText("Frequency")
        self.typeRateCombo.currentTextChanged.connect(self.onTypeRateChanged)
        self.rateLayout.addWidget(self.typeRateCombo)
        self.rateSpin = QDoubleSpinBox()
        self.rateSpin.setPrefix("Interpolation: ")
        self.rateSpin.setRange(0, 100000)
        self.rateSpin.setSingleStep(0.1)
        self.rateSpin.setSuffix(" Hz")
        self.rateSpin.setValue(1)
        self.rateLayout.addWidget(self.rateSpin)

        self.filterSpin = QDoubleSpinBox()
        self.filterSpin.setPrefix("Filter: ")
        self.filterSpin.setRange(0, 100000)
        self.filterSpin.setSingleStep(0.1)
        self.filterSpin.setSuffix(" Hz")
        self.filterSpin.setValue(0)
        self.rateLayout.addWidget(self.filterSpin)

    def onSignalDoubleClicked(self, item):
        if self.curveNameEdit.text() == "":
            self.curveNameEdit.setText(item.text())
        self.curveFormulaEdit.setText(self.curveFormulaEdit.toPlainText() + item.text())

    def onUnitDomainChanged(self, text):
        self.unitCombo.clear()
        self.unitCombo.addItems(self.unitsDict[text])

    def onTypeRateChanged(self, text):
        if text == "Frequency":
            self.rateSpin.setValue(1 / (self.rateSpin.value() + 1e-9))
            self.rateSpin.setSuffix(" Hz")
            self.filterSpin.setValue(1 / (self.filterSpin.value() + 1e-9))
            self.filterSpin.setSuffix(" Hz")
        else:
            self.rateSpin.setSuffix(" s")
            self.rateSpin.setValue(1 / (self.rateSpin.value() + 1e-9))
            self.filterSpin.setSuffix(" s")
            self.filterSpin.setValue(1 / (self.filterSpin.value() + 1e-9))
