from PySide6.QtCore import Qt
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


class SolverConfiguration:
    def __init__(self):
        self.solver = None
        self.solverName = None
        self.solverOptions = None
        self.timeStep = None
        self.maxIterations = None
        self.tolerance = None


class SolverDialog(QDialog):
    def __init__(self):
        super(SolverDialog, self).__init__()
        self.setWindowTitle("Solver")
        # self.setWindowIcon("")
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setWindowModality(Qt.ApplicationModal)
        # self.setFixedSize(400, 300)
        self.solverConfiguration = SolverConfiguration()

        self.initUI()

    def initUI(self):
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.configFrame = QFrame()
        self.mainLayout.addWidget(self.configFrame)
        self.configLayout = QFormLayout()
        self.configFrame.setLayout(self.configLayout)
        self.solverCombo = QComboBox()
        self.solverCombo.addItems(["No Solver", "Solver2", "Solver3"])
        self.solverCombo.currentIndexChanged.connect(self.solverChanged)

        self.solverOptions = QLineEdit()
        self.solverName = QLineEdit()
        self.timestepSpinBox = QDoubleSpinBox()
        self.maxIterationsSpinBox = QDoubleSpinBox()
        self.toleranceSpinBox = QDoubleSpinBox()

        self.configLayout.addRow("Solver Name", self.solverName)
        self.configLayout.addRow("Solver", self.solverCombo)
        self.configLayout.addRow("Solver Options", self.solverOptions)
        self.configLayout.addRow("Time step", self.timestepSpinBox)
        self.configLayout.addRow("Max iterations", self.maxIterationsSpinBox)
        self.configLayout.addRow("Tolerance", self.toleranceSpinBox)
        self.solverName.textChanged.connect(self.solverChanged)
        self.solverOptions.textChanged.connect(self.solverChanged)
        self.timestepSpinBox.valueChanged.connect(self.solverChanged)
        self.maxIterationsSpinBox.valueChanged.connect(self.solverChanged)
        self.toleranceSpinBox.valueChanged.connect(self.solverChanged)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.onAccepted)
        self.buttonBox.rejected.connect(self.reject)
        self.mainLayout.addWidget(self.buttonBox)

    def solverChanged(self, index):
        if index == 0:
            self.solverOptions.setDisabled(True)
            self.solverName.setDisabled(True)
        else:
            self.solverOptions.setDisabled(False)
            self.solverName.setDisabled(False)

        self.solverConfiguration.solver = index
        self.solverConfiguration.solverName = self.solverName.text()
        self.solverConfiguration.solverOptions = self.solverOptions.text()
        self.solverConfiguration.timeStep = self.timestepSpinBox.value()
        self.solverConfiguration.maxIterations = self.maxIterationsSpinBox.value()
        self.solverConfiguration.tolerance = self.toleranceSpinBox.value()

    def onAccepted(self):
        self.accept()
