from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QLineEdit


class SolverConfiguration:
    def __init__(self):
        self.solver = None
        self.solverName = None
        self.solverOptions = None


class SolverDialog(QDialog):
    def __init__(self):
        super(SolverDialog, self).__init__()
        self.setWindowTitle("Solver")
        # self.setWindowIcon("")
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setWindowModality(Qt.ApplicationModal)
        # self.setFixedSize(400, 300)
        self.layout = QFormLayout()
        self.setLayout(self.layout)
        self.solverConfiguration = SolverConfiguration()

        self.initUI()

    def initUI(self):
        self.solverCombo = QComboBox()
        self.solverCombo.addItems(["No Solver", "Solver2", "Solver3"])
        self.solverCombo.currentIndexChanged.connect(self.solverChanged)

        self.solverOptions = QLineEdit()

        self.solverName = QLineEdit()

        self.timestepSpinBox = QDoubleSpinBox()

        self.layout.addRow("Solver Name", self.solverName)
        self.layout.addRow("Solver Options", self.solverOptions)
        self.layout.addRow("Solver", self.solverCombo)
        self.layout.addRow(
            "Time step",
        )
        # self.solverOptions.setDisabled(True)
        # self.solverName.setDisabled(True)

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
