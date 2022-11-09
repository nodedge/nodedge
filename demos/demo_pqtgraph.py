import pyqtgraph as pg
from PySide6 import QtWidgets


class WdgPlot(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(WdgPlot, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        pw = pg.PlotWidget()
        pw.plot([1, 2, 3, 4])
        layout.addWidget(pw)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = WdgPlot()
    w.show()
    sys.exit(app.exec_())
