# -*- coding: utf-8 -*-
import logging
import os
import sys

import pyqtgraph as pg
from pyqtgraph.dockarea import Dock, DockArea
from pyqtgraph.Qt import QtGui
from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (
    QApplication,
    QDockWidget,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from tools.main_window_template.application_styler import ApplicationStyler
from tools.plotter.utils import loadStyleSheets


class RangedPlot(pg.PlotWidget):
    linearRegionChanged = Signal(list)

    def __init__(self, *args):
        super().__init__(*args)

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.linearRegion = pg.LinearRegionItem(
            [0, 0], brush=QtGui.QBrush(QtGui.QColor(0, 0, 255, 10))
        )
        self.addItem(self.linearRegion)
        self.linearRegion.setZValue(-10)
        self.viewRange = (0, 0)
        self.getPlotItem().getViewBox().suggestPadding = lambda *_: 0.005

        self.sigRangeChanged.connect(self.updateRange)
        self.linearRegion.sigRegionChangeFinished.connect(self.onLinearRegionChanged)

        self.numberOfColors = 10

        self.dataXRange = [1e9, -1e9]

    def onLinearRegionChanged(self):
        self.linearRegion.setZValue(10)
        minX = self.linearRegion.getRegion()
        self.linearRegionChanged.emit(minX)

    def updateRange(self, window, viewRange):
        self.viewRange = viewRange[0]

    def updateView(self, minMaxX):
        if minMaxX[0] < self.dataXRange[0]:
            return
        if minMaxX[1] > self.dataXRange[1]:
            return

        self.__logger.debug(minMaxX)
        self.setXRange(minMaxX[0], minMaxX[1])

    def updateLinearRegion(self, minMaxList):
        self.linearRegion.setRegion(minMaxList)

    def plot(self, *args, **kargs):
        numberOfCurves = len(self.getPlotItem().curves)
        self.getPlotItem().plot(
            *args, pen=(numberOfCurves + 1, self.numberOfColors), **kargs
        )

        lastCurve = self.getPlotItem().curves[-1]
        lastCurveXMax = max(lastCurve.xData)
        lastCurveXMin = min(lastCurve.xData)

        if lastCurveXMin < self.dataXRange[0]:
            self.dataXRange[0] = lastCurveXMin

        if lastCurveXMax > self.dataXRange[1]:
            self.dataXRange[1] = lastCurveXMax

        self.getViewBox().setLimits(xMin=self.dataXRange[0], xMax=self.dataXRange[1])

        self.__logger.debug(self.dataXRange)


class RangeSliderPlot(QWidget):
    sliderRangeChanged = Signal(list)
    sliderRangeChangeFinished = Signal(list)

    def __init__(self, x=None, y=None, crosshair=False, linkedPlots=[], *args):
        super().__init__(*args)

        self.vlayout = QVBoxLayout()
        self.setLayout(self.vlayout)
        self.sliderPlot = pg.PlotWidget()
        self.sliderPlot.setMaximumHeight(50)
        self.sliderPlot.hideAxis("left")
        self.sliderPlot.setMouseEnabled(False)
        self.sliderLinearRegion = pg.LinearRegionItem(
            [0, 0], brush=QtGui.QBrush(QtGui.QColor(0, 123, 255, 255))
        )
        self.sliderPlot.addItem(self.sliderLinearRegion)
        self.sliderLinearRegion.setZValue(-10)
        self.sliderLinearRegion.sigRegionChangeFinished.connect(
            self.onRegionChangeFinished
        )
        self.vlayout.addWidget(self.sliderPlot)

        self.viewRange = [0, 1]
        self.sliderPlot.setXRange(self.viewRange[0], self.viewRange[1])

        # if crosshair:
        #     self.vLine = pg.InfiniteLine()
        #     self.hLine = pg.InfiniteLine(angle=0)
        #     self.mainPlot.addItem(self.vLine)
        #     self.mainPlot.addItem(self.hLine)
        #     self.mainPlot.scene().sigMouseMoved.connect(self.mouseMoved)

    def linkPlot(self, rangedPlot: RangedPlot):
        # rangedPlot.linearRegion.sigRegionChanged.connect(self.updateSliderRegion)
        rangedPlot.linearRegionChanged.connect(self.updateSliderRegion)
        self.sliderLinearRegion.sigRegionChanged.connect(self.onSliderRegionChanged)
        self.sliderRangeChanged.connect(rangedPlot.updateLinearRegion)
        self.sliderRangeChangeFinished.connect(rangedPlot.updateView)
        self.viewRange = rangedPlot.viewRange
        self.sliderPlot.setXRange(rangedPlot.viewRange[0], rangedPlot.viewRange[1], 0)

    def onRegionChangeFinished(self):
        self.sliderLinearRegion.setZValue(10)
        minX, maxX = self.sliderLinearRegion.getRegion()
        self.sliderRangeChangeFinished.emit([minX, maxX])

    def onSliderRegionChanged(self):
        self.sliderLinearRegion.setZValue(10)
        minX, maxX = self.sliderLinearRegion.getRegion()
        if minX < self.viewRange[0]:
            minX = self.viewRange[0]
        if maxX > self.viewRange[1]:
            maxX = self.viewRange[1]
        self.sliderLinearRegion.setRegion((minX, maxX))
        self.sliderRangeChanged.emit([minX, maxX])

    def updateSliderRegion(self, minMaxX):
        self.sliderLinearRegion.setRegion(minMaxX)

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
    dockArea = DockArea()
    dock = Dock("MEOW")
    dockArea.addDock(dock)
    rangedPlot = RangedPlot()
    for i in range(10):
        rangedPlot.plot([0, 10], [i, i])
    rangedPlot.getPlotItem().removeItem(rangedPlot.getPlotItem().curves[0])
    dock.addWidget(rangedPlot)
    window.setCentralWidget(dock)
    dockWidget = QDockWidget()
    rangeSliderPlot = RangeSliderPlot()
    dockWidget.setWidget(rangeSliderPlot)
    window.addDockWidget(Qt.BottomDockWidgetArea, dockWidget)
    rangeSliderPlot.linkPlot(rangedPlot)
    window.showMaximized()
    app.exec_()
