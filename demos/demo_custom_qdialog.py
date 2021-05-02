# -*- coding: utf-8 -*-
import sys

from PySide2.QtCore import Signal, Slot
from PySide2.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
)


class CustomDialog(QDialog):
    indicesChosen = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setWindowTitle("Custom dialog")

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.dim2Label = QLabel("Dimension 2")
        self.dim2Edit = QLineEdit()
        self.dim3Label = QLabel("Dimension 3")
        self.dim3Edit = QLineEdit()

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.onAccepted)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QGridLayout()
        self.layout.addWidget(self.dim2Label, 1, 1, 1, 1)
        self.layout.addWidget(self.dim2Edit, 1, 2, 1, 1)
        self.layout.addWidget(self.dim3Label, 2, 1, 1, 1)
        self.layout.addWidget(self.dim3Edit, 2, 2, 1, 1)
        self.layout.addWidget(self.buttonBox, 3, 1, 1, 2)
        self.setLayout(self.layout)

    @Slot()
    def onAccepted(self):
        indices = [self.dim2Edit.text(), self.dim3Edit.text()]
        self.indicesChosen.emit(indices)
        # print(indices)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Plotter custom dialog")

        button = QPushButton("Miaou miaou miaou click here")
        button.clicked.connect(self.buttonClicked)
        self.setCentralWidget(button)

    def buttonClicked(self, s):
        print("click", s)

        dlg = CustomDialog()
        dlg.indicesChosen.connect(self.onIndicesChosen)
        if dlg.exec_():
            print("Success!")
        else:
            print("Cancel!")

    def onIndicesChosen(self, indices):
        print(f"Indices: {indices}")


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
