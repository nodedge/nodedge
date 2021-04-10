# -*- coding: utf-8 -*-
"""
plot_area.py module containing :class:`~nodedge.plot_area.py.<ClassName>` class.
"""
import sys

from pyqtgraph.dockarea import DockArea
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from nodedge.utils import dumpException
from tools.main_window_template.mdi_area import MdiArea
from tools.plotter.range_slider_plot import RangeSliderPlot


class PlotArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(800, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.mdiArea = MdiArea(parent)
        self.workbooks = []
        self.addWorkbook()

        self.layout.addWidget(self.mdiArea)

    def addWorkbook(self):
        dockArea = DockArea()
        self.workbooks.append(dockArea)
        subwindow = self.mdiArea.addSubWindow(dockArea)
        subwindow.showMaximized()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setCentralWidget(PlotArea())
    window.showMaximized()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
