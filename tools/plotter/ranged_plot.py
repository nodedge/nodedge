# -*- coding: utf-8 -*-
"""
${FILE_NAME} module containing :class:`~nodedge.${FILE_NAME}.<ClassName>` class.
"""
import logging

import pyqtgraph as pg
from PySide2 import QtGui
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QColor, QKeyEvent
from PySide2.QtWidgets import QApplication

from tools.plotter.curve_item import CurveItem


class RangedPlot(pg.PlotWidget):
    linearRegionChanged = Signal(list)
    restoreCurves = Signal(object)

    def __init__(self, *args):
        super().__init__(*args)

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        p = QApplication.palette()
        brushColor = p.highlight().color().setAlpha(250)
        pen = p.text().color()
        self.linearRegion = pg.LinearRegionItem([0, 0], brush=brushColor, pen=pen)
        self.addItem(self.linearRegion)
        self.linearRegion.setZValue(-10)
        self.viewRange = (0, 0)
        self.getPlotItem().getViewBox().suggestPadding = lambda *_: 0.007

        p = QApplication.palette()
        self.setBackground(p.base())

        self.sigRangeChanged.connect(self.updateRange)
        self.linearRegion.sigRegionChangeFinished.connect(self.onLinearRegionChanged)

        self.numberOfColors = 10

        self.dataXRange = [1e9, -1e9]
        self.dataYRange = [1e9, -1e9]
        self.getPlotItem().addLegend()
        self.getPlotItem().legend

        self.curveNames = []
        self.curves = {}

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

    def plot(self, data, name=None):
        numberOfCurves = len(self.getPlotItem().curves)

        self.updateMinMaxData(data)

        if name not in self.curves.keys():
            self.curveNames.append(name)
            idx = self.curveNames.index(name)
            curveItem = CurveItem(
                pen=(idx, self.numberOfColors), clickable=True, name=name
            )
            self.addItem(curveItem)
            self.curves[name] = curveItem
            curveItem.setDataPoints(data)
        else:
            idx = self.curveNames.index(name)
            curveItem = self.curves[name]
            curveItem.setDataPoints(data)

        curveItem.sigClicked.connect(self.clicked)

        self.getViewBox().setLimits(xMin=self.dataXRange[0], xMax=self.dataXRange[1])

        self.__logger.debug(self.dataXRange)

    def clicked(self, curve):
        self.clickedCurve: CurveItem = curve
        if curve.clicked:
            curve.setShadowPen(pg.mkPen((70, 70, 30), width=6, cosmetic=True))
        else:
            curve.setShadowPen(pg.mkPen((70, 70, 30), width=0, cosmetic=True))

    def updateMinMaxData(self, data):
        lastCurveXMax = len(data)
        lastCurveXMin = 0
        lastCurveYMax = max(data)
        lastCurveYMin = min(data)
        if lastCurveXMin < self.dataXRange[0]:
            self.dataXRange[0] = lastCurveXMin
        if lastCurveXMax > self.dataXRange[1]:
            self.dataXRange[1] = lastCurveXMax
        if lastCurveYMin < self.dataYRange[0]:
            self.dataYRange[0] = lastCurveYMin
        if lastCurveYMax > self.dataYRange[1]:
            self.dataYRange[1] = lastCurveYMax

    def keyReleaseEvent(self, ev: QKeyEvent):
        super().keyPressEvent(ev)
        key = ev.key()
        mod = ev.modifiers()

        if key == Qt.Key_Space:
            self.setXRange(self.dataXRange[0], self.dataXRange[1])
            self.setYRange(self.dataYRange[0], self.dataYRange[1])
        elif key == Qt.Key_Plus and mod & Qt.ControlModifier:
            self.getViewBox().scaleBy(s=(0.8, 0.8))
        elif key == Qt.Key_Minus and mod & Qt.ControlModifier:
            self.getViewBox().scaleBy(s=(1.2, 1.2))
        elif key == Qt.Key_D and self.clickedCurve is not None:
            self.clickedCurve.clear()
            curveNameList = list(self.curves.keys())
            curvesList = list(self.curves.values())
            index = curvesList.index(self.clickedCurve)
            self.curveNames.pop(index)
            self.curves.pop(curveNameList[index])
            self.removeItem(self.clickedCurve)

    def saveState(self):
        state = super().saveState()
        state["curveNames"] = self.curveNames
        return state

    def restoreState(self, state):
        super().restoreState(state)
        self.curveNames = state["curveNames"]
        self.restoreCurves.emit(self)
