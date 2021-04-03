# -*- coding: utf-8 -*-
import os
import sys

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from PySide2.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from tools.main_window_template.application_styler import ApplicationStyler
from tools.plotter.utils import loadStyleSheets


class RangeSliderPlot(QWidget):
    def __init__(self, x=None, y=None, crosshair=False, *args):
        super().__init__(*args)

        self.vlayout = QVBoxLayout()
        self.setLayout(self.vlayout)
        self.mainPlot: pg.PlotWidget = pg.PlotWidget()

        self.mainPlotRange = (0, 0)
        if x is None:
            if y is None:
                x = np.arange(15)
                y = np.random.rand(15)
            else:
                x = np.arange(len(y))
        self.mainPlot.plot(x=x, y=y)
        self.linearRegion = pg.LinearRegionItem(
            [0, 0], brush=QtGui.QBrush(QtGui.QColor(0, 0, 255, 10))
        )
        self.mainPlot.addItem(self.linearRegion)
        self.linearRegion.setZValue(-10)

        self.vlayout.addWidget(self.mainPlot)

        self.sliderPlot = pg.PlotWidget()
        self.sliderPlot.setMaximumHeight(50)
        self.sliderPlot.plot(x, np.zeros(len(x)))
        self.sliderPlot.hideAxis("bottom")
        self.sliderPlot.hideAxis("left")
        self.sliderLinearRegion = pg.LinearRegionItem(
            [0, 0], brush=QtGui.QBrush(QtGui.QColor(0, 0, 255, 50))
        )
        self.sliderPlot.addItem(self.sliderLinearRegion)
        self.sliderLinearRegion.setZValue(-10)
        self.vlayout.addWidget(self.sliderPlot)

        self.linearRegion.sigRegionChanged.connect(self.updateSliderRegion)
        self.mainPlot.sigRangeChanged.connect(self.updateMainPlotRange)
        self.sliderLinearRegion.sigRegionChanged.connect(self.updateLinearRegion)
        self.sliderLinearRegion.sigRegionChangeFinished.connect(self.updateMainPlot)

        if crosshair:
            self.vLine = pg.InfiniteLine()
            self.hLine = pg.InfiniteLine(angle=0)
            self.mainPlot.addItem(self.vLine)
            self.mainPlot.addItem(self.hLine)
            proxy = pg.SignalProxy(
                self.mainPlot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved
            )
            self.mainPlot.scene().sigMouseMoved.connect(self.mouseMoved)

    def updateSliderRegion(self):
        self.linearRegion.setZValue(10)
        minX, maxX = self.linearRegion.getRegion()
        mainPlotRange = self.mainPlotRange
        self.sliderLinearRegion.setRegion((minX, maxX))
        self.mainPlot.setXRange(mainPlotRange[0], mainPlotRange[1], padding=0)

    def updateMainPlotRange(self, window, viewRange):
        self.mainPlotRange = viewRange[0]

    def updateLinearRegion(self):
        self.sliderLinearRegion.setZValue(10)
        minX, maxX = self.sliderLinearRegion.getRegion()
        self.linearRegion.setRegion((minX, maxX))

    def updateMainPlot(self):
        self.sliderLinearRegion.setZValue(10)
        minX, maxX = self.sliderLinearRegion.getRegion()
        self.mainPlot.setXRange(minX, maxX)

    def mouseMoved(self, evt):
        pos = evt
        if self.mainPlot.sceneBoundingRect().contains(pos):
            mousePoint = self.mainPlot.getPlotItem().vb.mapSceneToView(pos)
            self.vLine.setPos(mousePoint.x())
            self.hLine.setPos(mousePoint.y())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()

    appStyler = ApplicationStyler()
    pg.setConfigOption("background", app.palette().dark())  # type: ignore
    styleSheetFilename = os.path.join(
        os.path.dirname(__file__), "qss/plotter_style.qss"
    )
    loadStyleSheets(styleSheetFilename)
    mapWidget = RangeSliderPlot()
    window.setCentralWidget(mapWidget)
    window.showMaximized()
    app.exec_()
