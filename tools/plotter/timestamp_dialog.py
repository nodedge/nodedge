# -*- coding: utf-8 -*-
import sys

from PySide2.QtCore import Signal, Slot
from PySide2.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
)


class TimestampDialog(QDialog):
    optionsChosen = Signal(list)

    def __init__(self, parent=None, keys=()):
        super().__init__(parent=parent)

        self.setWindowTitle("Custom dialog")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.mainLayout = QVBoxLayout()

        hlayout = QHBoxLayout()
        self.cgb = QGroupBox("How to find timestamp?")
        self.cpbList = []
        self.cpb1 = QRadioButton("Specific dataset")
        self.cpb1.toggled.connect(self.showKeys)
        self.cpb1.toggled.connect(self.onToggled)
        self.cpbList.append(self.cpb1)
        self.cpb2 = QRadioButton("Stored as a column for each dataseet")
        self.cpb2.toggled.connect(self.showSpinbox)
        self.cpb2.toggled.connect(self.onToggled)
        self.cpbList.append(self.cpb2)
        self.cpb3 = QRadioButton("No timestamp, plot indices on the x axis")
        self.cpb3.setChecked(True)
        self.cpb3.toggled.connect(self.onToggled)
        self.cpbList.append(self.cpb3)
        hlayout.addWidget(self.cpb1)
        hlayout.addWidget(self.cpb2)
        hlayout.addWidget(self.cpb3)
        self.cgb.setLayout(hlayout)

        self.keys = keys

        self.combo = QComboBox()
        self.combo.addItems(self.keys)
        self.combo.currentTextChanged.connect(self.onComboTextChanged)
        self.combo.hide()

        self.spinbox = QSpinBox()
        self.spinbox.setRange(0, 10)
        self.spinbox.valueChanged.connect(self.onSpinboxValueChanged)
        self.spinbox.hide()

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.onAccepted)
        self.buttonBox.rejected.connect(self.reject)

        self.mainLayout.addWidget(self.cgb)
        self.mainLayout.addWidget(self.combo)
        self.mainLayout.addWidget(self.spinbox)
        self.mainLayout.addWidget(self.buttonBox)

        self.setLayout(self.mainLayout)

        self.options = [2, ""]

    @Slot()
    def onToggled(self):
        for index, cpb in enumerate(self.cpbList):
            if cpb.isChecked():
                self.options[0] = index

    @Slot()
    def showKeys(self, showKeys):
        if showKeys:
            self.combo.show()
            self.options[1] = self.combo.currentText()
        else:
            self.combo.hide()

    @Slot()
    def showSpinbox(self, showSpinbox):
        if showSpinbox:
            self.spinbox.show()
        else:
            self.spinbox.hide()

    @Slot()
    def onComboTextChanged(self, text):
        self.options[1] = text

    @Slot()
    def onSpinboxValueChanged(self, value):
        self.options[1] = value

    @Slot()
    def onAccepted(self):
        self.optionsChosen.emit(self.options)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plotter custom dialog")

        button = QPushButton("Please click here")
        button.clicked.connect(self.buttonClicked)
        self.setCentralWidget(button)

    def buttonClicked(self, s):
        print("click", s)

        dlg = TimestampDialog(keys=["Miaou de Ponguette", "Miaou de Chichinette"])
        dlg.optionsChosen.connect(self.onOptionsChosen)
        if dlg.exec_():
            print("Success!")
        else:
            print("Cancel!")

    def onOptionsChosen(self, indices):
        print(f"Indices: {indices}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
