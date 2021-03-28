# -*- coding: utf-8 -*-
import os
import sys

import numpy as np
import pyqtgraph as pg
from PySide2.QtCore import QTimer, Signal
from PySide2.QtWidgets import QApplication, QMainWindow

from tools.main_window_template.application_styler import ApplicationStyler
from tools.plotter.circle_item import CircleItem
from tools.plotter.utils import loadStyleSheets


class MapWidget(pg.PlotWidget):
    valuesUpdated = Signal()

    def __init__(
        self,
        simulatedData=True,
    ):
        xAxis = pg.AxisItem(orientation="bottom")
        xAxis.setTickSpacing(1, 0.1)
        xAxis.setLabel("X [m]")
        yAxis = pg.AxisItem(orientation="left")
        yAxis.setLabel("Y [m]")
        yAxis.setTickSpacing(1, 0.1)

        super().__init__(axisItems={"bottom": xAxis, "left": yAxis})
        # self.setMouseEnabled(False, False)
        self.showGrid(x=True, y=True)

        self.scatterItem = pg.PlotDataItem()
        self.setAspectLocked(True)
        self.addItem(self.scatterItem)
        self.setAutoVisible(y=True)
        self.setYRange(0, 1)
        self.setXRange(0, 1)
        self.addLegend()

        self.circle = CircleItem()
        self.addItem(self.circle)

        p = QApplication.palette()

        self.simulatedData = simulatedData
        if self.simulatedData:
            self.simulatorTimer = QTimer()
            self.simulatorTimer.timeout.connect(self.updateData)
            self.simulatorTimer.start(1000)

    def updateData(self, values=None):
        if self.simulatedData:
            self.simulatorTimer.start()

        if values is None:
            xvalues = np.random.rand(6)
            yvalues = np.random.rand(6)
            values = [xvalues, yvalues]
            symbols = ["o", "star", "s", "p", "x", "x"]
            colors = [
                (39, 125, 161),  # Blue
                (249, 199, 79),  # Yellow
                (255, 0, 0),  # Red
                (144, 190, 109),  # Green
                (87, 117, 144),  # Gray
                (87, 117, 144),  # Gray
            ]
            names = [
                "Current position",
                "Objective",
                "Command",
                "Optimal command",
                "Other drone",
                "Other drone",
            ]

        xvalues = values[0]
        yvalues = values[1]

        self.clear()
        for xv, yv, br, s, n in zip(xvalues, yvalues, colors, symbols, names):
            self.plot(
                x=[xv],
                y=[yv],
                pen=None,
                symbol=s,
                symbolPen=None,
                symbolBrush=br,
                name=n,
                symbolSize=24,
            )

        self.circle.center = [xvalues[0], yvalues[0]]
        self.circle.radius = 0.2
        self.addItem(self.circle)

        self.valuesUpdated.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()

    appStyler = ApplicationStyler()
    pg.setConfigOption("background", app.palette().dark())
    styleSheetFilename = os.path.join(
        os.path.dirname(__file__), "qss/plotter_style.qss"
    )
    loadStyleSheets(styleSheetFilename)
    mapWidget = MapWidget()
    window.setCentralWidget(mapWidget)
    window.showMaximized()
    app.exec_()
