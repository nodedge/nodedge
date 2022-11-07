from collections import OrderedDict
from typing import Optional

import numpy as np
import pyqtgraph as pg
from pyqtgraph import (
    ArrowItem,
    CurvePoint,
    GraphicsLayoutWidget,
    InfiniteLine,
    LegendItem,
    SignalProxy,
    TextItem,
    ViewBox,
)
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent
from PySide6 import QtCore, QtGui
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QColorDialog, QInputDialog

from nodedge.dats.n_plot_data_item import NPlotDataItem
from nodedge.logger import logger


class NPlotWidget(GraphicsLayoutWidget):
    def __init__(self, parent=None, name=""):
        super().__init__(parent)
        self.name = name

        # crosshair
        self.plotItems = []
        self.plotProxies = []
        self.plotItem = self.addPlotItem(viewBox=NViewBox(self, self))
        vb: NViewBox = self.plotItem.vb
        vb.setBackgroundColor(QApplication.palette().base().color())
        self.setBackground(QApplication.palette().base().color())

        self.textItem: TextItem = TextItem(text="")
        self.arrow: ArrowItem = ArrowItem(angle=90)

        self.plotItem.showGrid(x=True, y=True, alpha=1.0)
        self.legend: LegendItem = LegendItem((80, 60), offset=(70, 20))
        self.legend.setParentItem(self.plotItem)
        self.items = OrderedDict()

        self.xLimits = np.array([np.NaN, np.NaN])
        self.yLimits = np.array([np.NaN, np.NaN])

    def addPlotItem(self, *args, **kargs):
        plotItem = self.addPlot(*args, **kargs)
        self.plotItems.append(plotItem)

        self.plotItems[-1].addLegend()
        self.plotItems[-1].showGrid(x=True, y=True, alpha=1.0)

        proxy = SignalProxy(
            plotItem.scene().sigMouseMoved,
            rateLimit=60,
            slot=plotItem.vb.mouseMoved,
        )

        self.plotProxies.append(proxy)

        return plotItem

    def addDataItem(self, dataItem: NPlotDataItem, name):
        self.items.update({name: dataItem})
        self.plotItem.addItem(dataItem)
        dataItem.sigClicked.connect(self.modifyCurve)
        self.plotItem.vb.curves.update({name: dataItem})
        self.updateRange(dataItem, reset=False)
        # try:
        #     print(self.plotItem.legend.items[0][1].text)
        # except Exception as e:
        #     print(e)

    def updateRange(self, dataItem, reset=True):
        if reset is True:
            self.xLimits = np.array([np.NaN, np.NaN])
            self.yLimits = np.array([np.NaN, np.NaN])
        self.xLimits[0] = min(np.min(dataItem.xData), self.xLimits[0])
        self.xLimits[1] = max(np.max(dataItem.xData), self.xLimits[1])
        self.yLimits[0] = min(np.min(dataItem.yData), self.yLimits[0])
        self.yLimits[1] = max(np.max(dataItem.yData), self.yLimits[1])
        yRange = max(self.yLimits[1] - self.yLimits[0], 1)

        self.plotItem.setLimits(
            xMin=self.xLimits[0],
            xMax=self.xLimits[1],
            yMin=self.yLimits[0] - yRange * 0.1,
            yMax=self.yLimits[1] + yRange * 0.1,
        )
        self.plotItem.setRange(yRange=(self.yLimits[0], self.yLimits[1] * 0.5))

    def modifyCurve(self, curve, ev: MouseClickEvent):
        logger.info("modifyCurve")
        if (
            self.plotItem.vb.highlightedCurve
            and curve != self.plotItem.vb.highlightedCurve
        ):
            self.plotItem.vb.highlightedCurve.setSymbol(None)
            self.plotItem.vb.highlightedCurve = None
        if ev.button() == Qt.LeftButton:
            if curve.opts["symbol"] is None:
                curve.setSymbol("x")
                self.plotItem.vb.highlightedCurve = curve
                if not hasattr(self, "curvePoint") or self.curvePoint is None:
                    self.curvePoint = CurvePoint(self.plotItem.vb.highlightedCurve)
                    self.arrow = ArrowItem(angle=90)
                    self.plotItem.addItem(self.curvePoint)
                    self.textItem.setParentItem(self.curvePoint)
                    self.arrow.setParentItem(self.curvePoint)
                if self.textItem not in self.plotItem.items:
                    self.plotItem.addItem(self.textItem)
            else:
                logger.info("Supressing highlighted curve.")
                curve.setSymbol(None)
                self.plotItem.vb.highlightedCurve = None
                if self.textItem in self.plotItem.items:
                    logger.info("Removing text item")
                    self.plotItem.removeItem(self.textItem)
                    self.plotItem.removeItem(self.arrow)
                if hasattr(self, "curvePoint"):
                    logger.info("Removing curve point")
                    if self.curvePoint is not None:
                        self.plotItem.removeItem(self.curvePoint)
                        self.curvePoint = None

    def mouseMoved(self, evt: QMouseEvent):
        # using signal proxy turns original arguments into a tuple
        pos: QPointF = evt[0]  # type: ignore
        vb: ViewBox = self.plotItem.vb
        mousePoint = vb.mapSceneToView(pos)
        if self.plotItem.sceneBoundingRect().contains(pos):
            index = int(mousePoint.x())

        x = mousePoint.x()

        if not self.items:
            return

        for plotItem in self.plotItems:
            for index, (name, item) in enumerate(plotItem.vb.curves.items()):
                xData = item.xData
                yData = item.yData
                i = np.argmin(abs(xData - x))
                plotItem.legend.items[index][1].setText(f"{name}: {yData[i]:.2f}")
            # self.plotItem.update()
            # self.plotItem.legend.update()

        if self.plotItem.vb.highlightedCurve is None:
            return

        xData = self.plotItem.vb.highlightedCurve.xData
        yData = self.plotItem.vb.highlightedCurve.yData
        index = np.argmin(abs(xData - x))

        self.curvePoint.setPos(index / (len(xData) - 1))
        self.textItem.setText(f"x: {xData[index]:.2f}, y: {yData[index]:.2f}")

    # def mousePressEvent(self, evt: QMouseEvent):
    #     super().mousePressEvent(evt)

    def as_dict(self):
        rep = {}
        rep.update({self.name: [item.vb.as_dict() for item in self.plotItems]})
        return rep

    def __repr__(self):
        return str(self.as_dict())


class NViewBox(pg.ViewBox):
    """
    Subclass of ViewBox
    """

    # signalShowT0 = QtCore.Signal()
    # signalShowS0 = QtCore.Signal()

    def __init__(self, parent=None, nPlotWidget: NPlotWidget = None):
        """
        Constructor of the NViewBox
        """
        super(NViewBox, self).__init__()
        self.nPlotWidget = nPlotWidget
        # self.setRectMode() # Set mouse mode to rect for convenient zooming
        # self.menu = None # Override pyqtgraph ViewBoxMenu
        # self.menu = self.getMenu() # Create the menu
        self.customizeAct = QtGui.QAction("Customize curves", self.menu)
        self.customizeAct.triggered.connect(self.customizeCurves)  # type: ignore
        self.menu.addAction(self.customizeAct)

        self.addSubPlotAct = QtGui.QAction("Add subplot", self.menu)
        self.addSubPlotAct.triggered.connect(self.addSubPlot)  # type: ignore
        self.menu.addAction(self.addSubPlotAct)

        self.removeThisSubPlotAct = QtGui.QAction("Remove this subplot", self.menu)
        self.removeThisSubPlotAct.triggered.connect(self.removeThisSubPlot)  # type: ignore
        self.menu.addAction(self.removeThisSubPlotAct)
        self.removeThisSubPlotAct.setEnabled(False)
        self.removeThisSubPlotAct.setVisible(False)

        self.curves = {}
        self.highlightedCurve: Optional[NPlotDataItem] = None

        p = QApplication.palette()
        self.vLine: InfiniteLine = InfiniteLine(
            angle=90, movable=False, pen=pg.mkPen(p.highlight().color())
        )
        self.hLine: InfiniteLine = InfiniteLine(
            angle=0, movable=False, pen=pg.mkPen(p.highlight().color())
        )
        self.addItem(self.vLine, ignoreBounds=True)
        self.addItem(self.hLine, ignoreBounds=True)

    def mouseMoved(self, evt):
        # using signal proxy turns original arguments into a tuple
        pos: QPointF = evt[0]
        vb: ViewBox = self
        mousePoint = vb.mapSceneToView(pos)
        self.vLine.setPos(mousePoint.x())
        self.hLine.setPos(mousePoint.y())

        x = mousePoint.x()

        if not self.nPlotWidget.items:
            return

        for plotItem in self.nPlotWidget.plotItems:
            for index, (name, item) in enumerate(plotItem.vb.curves.items()):
                xData = item.xData
                yData = item.yData
                i = np.argmin(abs(xData - x))
                plotItem.legend.items[index][1].setText(f"{name}: {yData[i]:.2f}")
            # self.plotItem.update()
            # self.plotItem.legend.update()

        if self.highlightedCurve is None:
            return

        xData = self.highlightedCurve.xData
        yData = self.highlightedCurve.yData
        index = np.argmin(abs(xData - x))

        if self.nPlotWidget.curvePoint:
            self.nPlotWidget.curvePoint.setPos(index / (len(xData) - 1))
        if self.nPlotWidget.textItem:
            self.nPlotWidget.textItem.setText(
                f"x: {xData[index]:.2f}, y: {yData[index]:.2f}"
            )

    def raiseContextMenu(self, ev):
        """
        Raise the context menu
        """
        if not self.menuEnabled():
            return
        pos = ev.screenPos()
        self.menu.popup(QtCore.QPoint(pos.x(), pos.y()))

    def emitShowT0(self):
        """
        Emit signalShowT0
        """
        self.signalShowT0.emit()

    def emitShowS0(self):
        """
        Emit signalShowS0
        """
        self.signalShowS0.emit()

    def setRectMode(self):
        """
        Set mouse mode to rect
        """
        self.setMouseMode(self.RectMode)

    def setPanMode(self):
        """
        Set mouse mode to pan
        """
        self.setMouseMode(self.PanMode)

    def customizeCurves(self):

        curveName, ok = QInputDialog.getItem(
            self.nPlotWidget,
            "Select curve to modify",
            "Curves",
            list(self.curves.keys()),
            0,
        )
        curve = self.curves[curveName]

        if not ok:
            return

        color = QColorDialog.getColor()
        logger.info(f"New color for curve {curveName}: {color}")

        curve.setPen(pg.mkPen(color))
        curve.setSymbolPen(pg.mkPen(color))
        curve.setBrush(pg.mkBrush(color))
        curve.setSymbolBrush(pg.mkBrush(color))

    def addSubPlot(self):
        plotItem = self.nPlotWidget.addPlotItem(
            viewBox=NViewBox(self.nPlotWidget, self.nPlotWidget),
            row=self.nPlotWidget.nextRow(),
        )

        self.nPlotWidget.plotItems[0].setXLink(plotItem)
        for index, plotItem in enumerate(self.nPlotWidget.plotItems):
            plotItem.vb.removeThisSubPlotAct.setEnabled(True)
            plotItem.vb.removeThisSubPlotAct.setVisible(True)

    def removeThisSubPlot(self):
        for index, plotItem in enumerate(self.nPlotWidget.plotItems):
            if plotItem.vb == self:
                self.nPlotWidget.plotItems.pop(index)
                self.nPlotWidget.removeItem(plotItem)
                del plotItem

        if len(self.nPlotWidget.plotItems) == 1:
            for index, plotItem in enumerate(self.nPlotWidget.plotItems):
                plotItem.vb.removeThisSubPlotAct.setEnabled(False)
                plotItem.vb.removeThisSubPlotAct.setVisible(False)

    def mouseClickEvent(self, ev):
        super().mouseClickEvent(ev)
        if ev.button() == QtCore.Qt.MouseButton.LeftButton:
            for p in self.nPlotWidget.plotItems:
                vb = p.getViewBox()
                vb.setBorder()
                vb.update()
                if vb == self:
                    self.nPlotWidget.plotItem = p
            palette = QApplication.palette()
            self.setBorder({"color": palette.highlight().color(), "width": 4})

    def as_dict(self):
        rep = {}
        for k, v in self.curves.items():
            rep.update({k: v.opts["pen"]})

        return rep
