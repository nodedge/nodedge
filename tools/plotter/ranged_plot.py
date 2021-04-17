# -*- coding: utf-8 -*-
"""
${FILE_NAME} module containing :class:`~nodedge.${FILE_NAME}.<ClassName>` class.
"""
import logging
from collections import OrderedDict
from typing import Optional

import pyqtgraph as pg
from pyqtgraph import PlotItem, ViewBox
from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QBrush, QKeyEvent
from PySide2.QtWidgets import QAction, QApplication, QColorDialog, QInputDialog

from tools.plotter.curve_item import CurveItem


class RangedPlot(pg.PlotWidget):
    linearRegionChanged = Signal(list)
    restoreCurves = Signal(object)

    def __init__(self, *args):
        super().__init__(*args)

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.DEBUG)

        p = QApplication.palette()
        brushColor = p.highlight().color()
        brushColor.setAlphaF(0.1)
        brush = QBrush(brushColor)
        highlightBrushColor = p.highlight().color()
        highlightBrushColor.setAlphaF(0.4)
        highlightBrush = QBrush(p.highlight().color())
        highlightBrush.setColor(highlightBrushColor)
        pen = p.text().color()
        self.linearRegion = pg.LinearRegionItem(
            [0, 0], brush=brush, hoverBrush=highlightBrush, pen=pen
        )
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

        self.curves = OrderedDict()

        self.clickedCurve: Optional[CurveItem] = None

        menu = self.getPlotItem().getViewBox().menu
        styleAction: QAction = QAction("Style", menu)
        menu.addAction(styleAction)
        styleAction.triggered.connect(self.setStyleForClickedCurve)
        colorAction: QAction = QAction("Color", menu)
        menu.addAction(colorAction)
        colorAction.triggered.connect(self.setColorForClickedCurve)
        widthAction: QAction = QAction("Width", menu)
        menu.addAction(widthAction)
        widthAction.triggered.connect(self.setWidthForClickedCurve)

    def setStyleForClickedCurve(self):
        if self.clickedCurve is None:
            return

        items = {
            "Solid line": Qt.SolidLine,
            "Dash line": Qt.DashLine,
            "Dot line": Qt.DotLine,
            "Dash dot line": Qt.DashDotLine,
            "Dash dot dot line": Qt.DashDotDotLine,
        }
        itemNames = list(items.keys())

        dialog = QInputDialog(self)
        dialog.setComboBoxItems(items)

        itemName, ok = QInputDialog.getItem(self, "Choose style", "label", itemNames, 0)
        item = items[itemName]

        if not ok:
            return
        self.clickedCurve.setStyle(item)

    def setColorForClickedCurve(self):
        if self.clickedCurve is None:
            return

        colorDialog = QColorDialog()
        # TODO: Add custom palette as standard color
        # colorDialog.setOption(QColorDialog.DontUseNativeDialog)
        # colorDialog.setStandardColor(0, QColor("g"))
        color = colorDialog.getColor()
        if not color.isValid():
            return

        self.clickedCurve.setColor(color)

    def setWidthForClickedCurve(self):
        if self.clickedCurve is None:
            return

        width, ok = QInputDialog.getDouble(self, "Set width", "Set width", 1.0, 0.0, 10)
        if not ok:
            return

        self.clickedCurve.setWidth(width)

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

        self.__logger.debug(f"Range: {minMaxX}")
        self.setXRange(minMaxX[0], minMaxX[1])

    def updateLinearRegion(self, minMaxList):
        self.linearRegion.setRegion(minMaxList)

    def plot(self, data, name=None):
        numberOfCurves = len(self.getPlotItem().curves)

        self.updateMinMaxData(data)
        curveNames = list(self.curves.keys())
        if name not in curveNames:
            nbCurves = len(curveNames)
            pen = pg.mkPen((nbCurves, self.numberOfColors))
            pen.setWidthF(1.2)
            curveItem = CurveItem(pen=pen, clickable=True, name=name)
            self.addItem(curveItem)
            self.curves[name] = curveItem
            curveItem.setDataPoints(data)
        else:
            idx = curveNames.index(name)
            curveItem = self.curves[name]
            curveItem.setDataPoints(data)

        curveItem.sigClicked.connect(self.clicked)

        self.getViewBox().setLimits(xMin=self.dataXRange[0], xMax=self.dataXRange[1])

        self.__logger.debug(self.dataXRange)

    def clicked(self, curve):
        self.clickedCurve = curve

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

    def mouseReleaseEvent(self, ev):
        button = ev.button()
        mod = ev.modifiers()
        if button == Qt.LeftButton:
            if self.clickedCurve is not None:
                self.clickedCurve.setShadowPen(
                    pg.mkPen((70, 70, 30), width=0, cosmetic=True)
                )
                self.clickedCurve = None
            super().mouseReleaseEvent(ev)

            p = QApplication.palette()
            highlightColor = p.text().color()
            highlightColor.setAlpha(40)

            print(self.clickedCurve)

            if self.clickedCurve is not None:
                self.clickedCurve.setShadowPen(
                    pg.mkPen(highlightColor, width=6, cosmetic=True)
                )
        elif button == Qt.RightButton:
            super().mouseReleaseEvent(ev)

        self.__logger.debug(self.clickedCurve)
