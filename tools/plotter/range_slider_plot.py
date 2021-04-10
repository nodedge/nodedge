# -*- coding: utf-8 -*-
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
        self.linearRegion = pg.LinearRegionItem(
            [0, 0], brush=QtGui.QBrush(QtGui.QColor(0, 0, 255, 10))
        )
        self.addItem(self.linearRegion)
        self.linearRegion.setZValue(-10)
        self.viewRange = (0, 0)
        self.getPlotItem().getViewBox().suggestPadding = lambda *_: 0.005

        self.sigRangeChanged.connect(self.updateRange)
        self.linearRegion.sigRegionChangeFinished.connect(self.onLinearRegionChanged)

    def onLinearRegionChanged(self):
        self.linearRegion.setZValue(10)
        minX = self.linearRegion.getRegion()
        self.linearRegionChanged.emit(minX)

    def updateRange(self, window, viewRange):
        self.viewRange = viewRange[0]

    def updateView(self, minMaxX):
        self.setXRange(minMaxX[0], minMaxX[1])

    def updateLinearRegion(self, minMaxList):
        self.linearRegion.setRegion(minMaxList)


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
    rangedPlot.plot([0, 10], [1, 2])
    dock.addWidget(rangedPlot)
    window.setCentralWidget(dock)
    dockWidget = QDockWidget()
    rangeSliderPlot = RangeSliderPlot()
    dockWidget.setWidget(rangeSliderPlot)
    window.addDockWidget(Qt.BottomDockWidgetArea, dockWidget)
    rangeSliderPlot.linkPlot(rangedPlot)
    window.showMaximized()
    app.exec_()
