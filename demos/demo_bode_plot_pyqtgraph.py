import control
import numpy as np
import pyqtgraph as pg
from PySide6 import QtGui, QtWidgets


class BodePlotDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bode Plot")
        self.setWindowIcon(QtGui.QIcon("icon.png"))

        # Create transfer function input line
        self.tf_input = QtWidgets.QLineEdit(self)
        self.tf_input.setText("(1+s)/(1+s+s**2)")
        self.tf_input.setPlaceholderText("Enter transfer function")

        # Create plot widget
        self.magnitudeWidget = pg.PlotWidget()
        self.magnitudeWidget.plotItem.setLogMode(x=True, y=True)
        self.magnitudeWidget.plotItem.showGrid(x=True, y=True, alpha=0.1)
        self.phaseWidget = pg.PlotWidget()
        self.phaseWidget.plotItem.setLogMode(x=True)
        self.phaseWidget.plotItem.showGrid(x=True, y=True, alpha=0.1)

        # Create buttons
        self.plot_button = QtWidgets.QPushButton("Plot", self)
        self.plot_button.clicked.connect(self.plot_tf)
        self.close_button = QtWidgets.QPushButton("Close", self)
        self.close_button.clicked.connect(self.close)

        # Create layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.tf_input)
        layout.addWidget(self.magnitudeWidget)
        layout.addWidget(self.phaseWidget)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.plot_button)
        button_layout.addWidget(self.close_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def plot_tf(self):
        tf_str = self.tf_input.text()
        try:
            s = control.tf("s")
            tf = eval(tf_str)
            mag, phase, omega = control.bode(tf, omega_limits=np.array([1e-3, 1e3]))
            print(max(omega))
            self.magnitudeWidget.clear()
            self.magnitudeWidget.plot(omega, mag, pen="b")
            self.magnitudeWidget.setLabel("left", "Magnitude", units="dB")
            self.magnitudeWidget.setLabel("bottom", "Frequency", units="rad/s")

            self.phaseWidget.clear()
            self.phaseWidget.plot(omega, phase * 180 / np.pi, pen="b")
            self.phaseWidget.setLabel("left", "Phase", units="degC")
            self.phaseWidget.setLabel("bottom", "Frequency", units="rad/s")
        except:
            print("Invalid transfer function")


if __name__ == "__main__":
    app = QtWidgets.QApplication()
    dialog = BodePlotDialog()
    dialog.show()
    app.exec_()
