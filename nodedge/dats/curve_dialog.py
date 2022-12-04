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
        self.curveNameEdit.setPlaceholderText("Enter curve name")

        self.textChanged.connect(self.updateTextFont)

    def updateTextFont(self):
        if self.text() in self.signals:
            self.setFont(self.parent.font)
        else:
            self.setFont(self.parent.boldFont)


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
        self.unitDomainCombo.addItems(
            [
                "Time",
                "Frequency",
                "Voltage",
                "Current",
                "Power",
                "Resistance",
                "Capacitance",
                "Inductance",
                "Temperature",
                "Angle",
                "Force",
                "Mass",
                "Length",
                "Area",
                "Volume",
                "Speed",
                "Acceleration",
                "Momentum",
                "Energy",
                "Pressure",
                "Density",
                "Concentration",
                "Charge",
                "Magnetic Flux",
                "Magnetic Field",
                "Magnetic Induction",
                "Magnetic Moment",
                "Magnetic Permeability",
                "Magnetic Susceptibility",
                "Magnetic Vector Potential",
                "Magnetic Vector Potential Flux",
                "Limunance",
                "Speed",
                "Acceleration",
                "Momentum",
                "Angular Velocity",
                "Angular Acceleration",
                "Force rate",
                "Torque",
                "Torque rate",
            ]
        )
        self.unitLayout.addWidget(self.unitDomainCombo)
        self.unitDomainCombo.currentTextChanged.connect(self.onUnitDomainChanged)

        self.unitCombo = QComboBox()
        self.unitCombo.addItems(["s", "ms", "us", "ns", "ps", "fs", "as"])
        self.unitLayout.addWidget(self.unitCombo)

    def onSignalDoubleClicked(self, item):
        if self.curveNameEdit.text() == "":
            self.curveNameEdit.setText(item.text())
        self.curveDefinitionEdit.setText(
            self.curveDefinitionEdit.toPlainText() + item.text()
        )

    def onUnitDomainChanged(self, text):
        print(text)
        if text == "Time":
            self.unitCombo.clear()
            self.unitCombo.addItems(["s", "ms", "us", "ns", "ps", "fs", "as"])
        elif text == "Frequency":
            self.unitCombo.clear()
            self.unitCombo.addItems(["Hz", "kHz", "MHz", "GHz", "THz", "PHz", "EHz"])
        elif text == "Voltage":
            self.unitCombo.clear()
            self.unitCombo.addItems(["V", "mV", "uV", "nV", "pV", "fV", "aV"])
        elif text == "Current":
            self.unitCombo.clear()
            self.unitCombo.addItems(["A", "mA", "uA", "nA", "pA", "fA", "aA"])
        elif text == "Power":
            self.unitCombo.clear()
            self.unitCombo.addItems(["W", "mW", "uW", "nW", "pW", "fW", "aW"])
        elif text == "Resistance":
            self.unitCombo.clear()
            self.unitCombo.addItems(["Ohm", "mOhm", "uOhm", "nOhm", "kOhm", "MOhm"])
        elif text == "Capacitance":
            self.unitCombo.clear()
            self.unitCombo.addItems(["F", "mF", "uF", "nF", "pF", "fF", "aF"])
        elif text == "Inductance":
            self.unitCombo.clear()
            self.unitCombo.addItems(["H", "mH", "uH", "nH", "pH", "fH", "aH"])
        elif text == "Temperature":
            self.unitCombo.clear()
            self.unitCombo.addItems(["C", "mC", "uC", "nC", "pC", "fC", "aC"])
        elif text == "Angle":
            self.unitCombo.clear()
            self.unitCombo.addItems(["deg", "rad"])
        elif text == "Length":
            self.unitCombo.clear()
            self.unitCombo.addItems(["m", "mm", "um", "nm", "pm", "fm", "am"])
        elif text == "Area":
            self.unitCombo.clear()
            self.unitCombo.addItems(["m2", "mm2", "um2", "nm2", "pm2", "fm2", "am2"])
        elif text == "Volume":
            self.unitCombo.clear()
            self.unitCombo.addItems(["m3", "mm3", "um3", "nm3", "pm3", "fm3", "am3"])
        elif text == "Mass":
            self.unitCombo.clear()
            self.unitCombo.addItems(["kg", "g", "mg", "ug", "ng", "pg", "fg", "ag"])
        elif text == "Force":
            self.unitCombo.clear()
            self.unitCombo.addItems(["N", "mN", "uN", "nN", "pN", "fN", "aN"])
        elif text == "Energy":
            self.unitCombo.clear()
            self.unitCombo.addItems(["J", "mJ", "uJ", "nJ", "pJ", "fJ", "aJ"])
        elif text == "Pressure":
            self.unitCombo.clear()
            self.unitCombo.addItems(["Pa", "mPa", "uPa", "nPa", "pPa", "fPa", "aPa"])
        elif text == "Magnetic Flux":
            self.unitCombo.clear()
            self.unitCombo.addItems(["Wb", "mWb", "uWb", "nWb", "pWb", "fWb", "aWb"])
        elif text == "Magnetic Flux Density":
            self.unitCombo.clear()
            self.unitCombo.addItems(["T", "mT", "uT", "nT", "pT", "fT", "aT"])
        elif text == "Magnetic Field":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["A/m", "mA/m", "uA/m", "nA/m", "pA/m", "fA/m", "aA/m"]
            )
        elif text == "Magnetic Field Strength":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["A/m", "mA/m", "uA/m", "nA/m", "pA/m", "fA/m", "aA/m"]
            )
        elif text == "Magnetic Induction":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["H/m", "mH/m", "uH/m", "nH/m", "pH/m", "fH/m", "aH/m"]
            )
        elif text == "Magnetic Moment":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["A*m2", "mA*m2", "uA*m2", "nA*m2", "pA*m2", "fA*m2", "aA*m2"]
            )
        elif text == "Magnetic Permeability":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["H/m", "mH/m", "uH/m", "nH/m", "pH/m", "fH/m", "aH/m"]
            )
        elif text == "Magnetic Vector Potential":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["A/m", "mA/m", "uA/m", "nA/m", "pA/m", "fA/m", "aA/m"]
            )
        elif text == "Luminous Intensity":
            self.unitCombo.clear()
            self.unitCombo.addItems(["cd", "mcd", "ucd", "ncd", "pcd", "fcd", "acd"])
        elif text == "Luminous Flux":
            self.unitCombo.clear()
            self.unitCombo.addItems(["lm", "mlm", "ulm", "nlm", "plm", "flm", "alm"])
        elif text == "Luminance":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["cd/m2", "mcd/m2", "ucd/m2", "ncd/m2", "pcd/m2", "fcd/m2", "acd/m2"]
            )
        elif text == "Speed":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["m/s", "mm/s", "um/s", "nm/s", "pm/s", "fm/s", "am/s"]
            )
        elif text == "Acceleration":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["m/s2", "mm/s2", "um/s2", "nm/s2", "pm/s2", "fm/s2", "am/s2"]
            )
        elif text == "Angular Velocity":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["rad/s", "mrad/s", "urad/s", "nrad/s", "prad/s", "frad/s", "arad/s"]
            )
        elif text == "Angular Acceleration":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                [
                    "rad/s2",
                    "mrad/s2",
                    "urad/s2",
                    "nrad/s2",
                    "prad/s2",
                    "frad/s2",
                    "arad/s2",
                ]
            )
        elif text == "Torque":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["N*m", "mN*m", "uN*m", "nN*m", "pN*m", "fN*m", "aN*m"]
            )
        elif text == "Mass Flow":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["kg/s", "g/s", "mg/s", "ug/s", "ng/s", "pg/s", "fg/s", "ag/s"]
            )
        elif text == "Volume Flow":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["m3/s", "mm3/s", "um3/s", "nm3/s", "pm3/s", "fm3/s", "am3/s"]
            )
        elif text == "Molar Flow":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["mol/s", "mmol/s", "umol/s", "nmol/s", "pmol/s", "fmol/s", "amol/s"]
            )
        elif text == "Force rate":
            self.unitCombo.clear()
            self.unitCombo.addItems(
                ["N/s", "mN/s", "uN/s", "nN/s", "pN/s", "fN/s", "aN/s"]
            )
