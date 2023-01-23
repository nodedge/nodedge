import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QLineEdit,
    QVBoxLayout,
)

from nodedge.scene_simulator import SolverConfiguration


class SolverDialog(QDialog):
    solverConfigChanged = Signal(SolverConfiguration)

    def __init__(self, solverConfig: SolverConfiguration):
        super(SolverDialog, self).__init__()
        self.setWindowTitle("Solver")
        self.icon = QIcon(
            os.path.join(os.path.dirname(__file__), "../resources/nodedge_logo.png")
        )
        self.setWindowIcon(self.icon)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.initUI()
        self.solverConfiguration = solverConfig
        self.updateUIFromConfig()

        self.setFixedWidth(400)

    def initUI(self):
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.configFrame = QFrame()
        self.mainLayout.addWidget(self.configFrame)
        self.configLayout = QFormLayout()
        self.configFrame.setLayout(self.configLayout)
        self.solverCombo = QComboBox()
        self.solverCombo.addItems(["Basic solver"])
        self.solverCombo.currentIndexChanged.connect(self.updateSolverConfig)

        self.solverOptions = QLineEdit()
        self.solverName = QLineEdit()
        self.timestepSpinBox = QDoubleSpinBox()
        self.maxIterationsSpinBox = QDoubleSpinBox()
        self.toleranceSpinBox = QDoubleSpinBox()
        self.finalTimeEdit = QLineEdit()

        self.configLayout.addRow("Solver name", self.solverName)
        self.configLayout.addRow("Solver", self.solverCombo)
        self.configLayout.addRow("Solver options", self.solverOptions)
        self.configLayout.addRow("Time step", self.timestepSpinBox)
        self.configLayout.addRow("Max iterations", self.maxIterationsSpinBox)
        self.configLayout.addRow("Tolerance", self.toleranceSpinBox)
        self.configLayout.addRow("Final time", self.finalTimeEdit)
        self.solverName.textChanged.connect(self.updateSolverConfig)
        self.solverOptions.textChanged.connect(self.updateSolverConfig)
        self.timestepSpinBox.valueChanged.connect(self.updateSolverConfig)
        self.maxIterationsSpinBox.valueChanged.connect(self.updateSolverConfig)
        self.toleranceSpinBox.valueChanged.connect(self.updateSolverConfig)
        self.finalTimeEdit.textChanged.connect(self.updateSolverConfig)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.onAccepted)
        self.buttonBox.rejected.connect(self.reject)
        self.mainLayout.addWidget(self.buttonBox)

    def updateUIFromConfig(self):
        self.solverCombo.currentIndexChanged.disconnect(self.updateSolverConfig)
        self.solverName.textChanged.disconnect(self.updateSolverConfig)
        self.solverOptions.textChanged.disconnect(self.updateSolverConfig)
        self.timestepSpinBox.valueChanged.disconnect(self.updateSolverConfig)
        self.maxIterationsSpinBox.valueChanged.disconnect(self.updateSolverConfig)
        self.toleranceSpinBox.valueChanged.disconnect(self.updateSolverConfig)
        self.finalTimeEdit.textChanged.disconnect(self.updateSolverConfig)

        if self.solverConfiguration.solver is not None:
            self.solverCombo.setCurrentText(self.solverConfiguration.solver)
        if self.solverConfiguration.solverOptions is not None:
            self.solverOptions.setText(self.solverConfiguration.solverOptions)
        if self.solverConfiguration.solverName is not None:
            self.solverName.setText(self.solverConfiguration.solverName)
        if self.solverConfiguration.timeStep is not None:
            self.timestepSpinBox.setValue(self.solverConfiguration.timeStep)
        if self.solverConfiguration.maxIterations is not None:
            self.maxIterationsSpinBox.setValue(self.solverConfiguration.maxIterations)
        if self.solverConfiguration.tolerance is not None:
            self.toleranceSpinBox.setValue(self.solverConfiguration.tolerance)
        if self.solverConfiguration.finalTime is not None:
            self.finalTimeEdit.setText(str(self.solverConfiguration.finalTime))

        self.solverCombo.currentIndexChanged.connect(self.updateSolverConfig)
        self.solverName.textChanged.connect(self.updateSolverConfig)
        self.solverOptions.textChanged.connect(self.updateSolverConfig)
        self.timestepSpinBox.valueChanged.connect(self.updateSolverConfig)
        self.maxIterationsSpinBox.valueChanged.connect(self.updateSolverConfig)
        self.toleranceSpinBox.valueChanged.connect(self.updateSolverConfig)
        self.finalTimeEdit.textChanged.connect(self.updateSolverConfig)

    def updateSolverConfig(self, index):
        if index == 0:
            self.solverOptions.setDisabled(True)
            self.solverName.setDisabled(True)
        else:
            self.solverOptions.setDisabled(False)
            self.solverName.setDisabled(False)

        self.solverConfiguration.solver = self.solverCombo.currentText()
        self.solverConfiguration.solverName = self.solverName.text()
        self.solverConfiguration.solverOptions = self.solverOptions.text()
        self.solverConfiguration.timeStep = self.timestepSpinBox.value()
        self.solverConfiguration.maxIterations = self.maxIterationsSpinBox.value()
        self.solverConfiguration.tolerance = self.toleranceSpinBox.value()
        self.solverConfiguration.finalTime = self.finalTimeEdit.text()

    def onAccepted(self):
        self.accept()
        self.solverConfigChanged.emit(self.solverConfiguration)
