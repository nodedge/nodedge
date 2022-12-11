import json
import re
from string import ascii_letters, digits

import numpy as np
from asammdf import MDF, Signal
from asammdf.blocks.v4_blocks import Channel
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from nodedge import utils
from nodedge.dats.logs_list_widget import LogsListWidget
from nodedge.dats.signals_list_widget import SignalsListWidget

OPERATOR_LIST = [
    "+",
    "-",
    "*",
    "/",
    "^",
    "**",
    "sin",
    "cos",
    "tan",
    "asin",
    "acos",
    "atan",
]


class CurveLineEdit(QLineEdit):
    def __init__(self, parent=None, signals=[]):
        super().__init__(parent)
        self.parent = parent
        self.setPlaceholderText("Enter curve name")
        self.signals = signals

        self.textChanged.connect(self.updateTextFont)

        self.valid = False

    def updateTextFont(self):
        diff = set(self.text()).difference(ascii_letters + digits + "_")
        if (
            self.text() in self.signals
            or " " in self.text()
            or len(diff) > 0
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
        text = self.toPlainText()
        diff = set(text).difference(ascii_letters + digits + "+-/*^()._")
        operators = re.findall(r"[^a-zA-Z0-9_]+", text)
        validOperation = True
        for op in operators:
            if op not in OPERATOR_LIST:
                validOperation = False
        if self.toPlainText() == "" or len(diff) > 0 or not validOperation:
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
        print(logs.keys())
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

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.onAccepted)
        self.buttonBox.rejected.connect(self.reject)
        self.mainLayout.addWidget(self.buttonBox)

    def onAccepted(self):
        if self.curveNameEdit.valid and self.curveFormulaEdit.valid:

            self.evaluateCurve()
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Invalid curve name or formula")
            # self.reject()

    def evaluateCurve(self):
        curveName = self.curveNameEdit.text()
        curveFormula = self.curveFormulaEdit.toPlainText()
        curveUnit = self.unitCombo.currentText()
        curveRate = self.rateSpin.value()
        curveFilter = self.filterSpin.value()
        curveTypeRate = self.typeRateCombo.currentText()

        curveFormulaNames = re.findall(r"[a-zA-Z0-9_]+", curveFormula)
        curveFormulaOperators = re.findall(r"[^a-zA-Z0-9_]+", curveFormula)

        curveFormulaNames = [i for i in curveFormulaNames if i != ""]

        for c in curveFormulaNames:
            if c.isdigit():
                curveFormulaNames.remove(c)
                continue
            if c not in self.signalsWidget.signals:
                QMessageBox.warning(self, "Error", f"Signal {c} not found")
                return

        logName = self.logsWidget.selectedItems()[0].text()

        log: MDF = self.logsWidget.logs[logName]

        timestampsUnion = np.array([], dtype=np.float64)
        for name in curveFormulaNames:
            channel: Channel = log.get(name)
            channel.samples = channel.samples.astype(np.float64)
            channel.timestamps = channel.timestamps.astype(np.float64)
            timestampsUnion = np.union1d(timestampsUnion, channel.timestamps)
        timestampsUnion.sort()

        # interpolatedSamples = np.zeros(
        #     (len(timestampsUnion), len(curveFormulaNames)), dtype=np.float64
        # )
        for i, name in enumerate(curveFormulaNames):
            channel: Channel = log.get(name)
            # interpolatedSamples[:, i] = np.interp(
            #     timestampsUnion, channel.timestamps, channel.samples
            # )
            if i == 0:
                channel.samples = channel.samples[0:-2]
                channel.timestamps = channel.timestamps[0:-2]
            exec(f"{name} = channel")

        newSignal: Signal = eval(curveFormula)
        newSignal.name = curveName

        self.signalsWidget.signals.append(curveName)
        log.append([newSignal])

        print(logName)
        self.parent.logsWidget.logsListWidget.logs[logName] = log
        print(self.parent.logsWidget.logsListWidget.logs.keys())
        self.parent.signalsWidget.signalsListWidget.updateList(log)

    def onSignalDoubleClicked(self, item):

        # Automatically set the name only if it is empty
        if self.curveNameEdit.text() == "":

            curveName = item.text()

            alreadyExistingNames = self.signalsWidget.signals
            curveName = utils.setNewTitle(curveName, alreadyExistingNames)

            self.curveNameEdit.setText(curveName)
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
