import logging
from collections import OrderedDict
from typing import Dict, List, Optional

import numpy as np
import pyqtgraph as pg
from pyqtgraph import (
    AxisItem,
    GraphicsLayoutWidget,
    InfiniteLine,
    LegendItem,
    SignalProxy,
    ViewBox,
)
from pyqtgraph.graphicsItems.ViewBox.ViewBoxMenu import ViewBoxMenu
from pyqtgraph.GraphicsScene.mouseEvents import MouseClickEvent
from PySide6 import QtCore, QtGui
from PySide6.QtCore import QEvent, QPointF, Qt, Signal
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent, QMouseEvent
from PySide6.QtWidgets import QApplication, QColorDialog

from nodedge.dats.n_plot_data_item import NDataCurve

logger = logging.getLogger(__name__)

GRID_ALPHA = 0.1


class NPlotWidget(GraphicsLayoutWidget):
    xRangeUpdated = Signal(int, int)

    def __init__(self, parent=None, name=""):
        super().__init__(parent)
        self.name = name
        self.worksheetsTabWidget = parent
        app: QApplication = QApplication.instance()
        app.paletteChanged.connect(self.updateColors)
        self.setBackground(QApplication.palette().base().color())

        self.plotItems = []
        self.plotProxies = []

        self.addPlotItem(viewBox=NViewBox(self, self))
        # self.legend: LegendItem = LegendItem((80, 60), offset=(70, 20))
        # self.legend.setParentItem(self.plotItem)
        self.setAcceptDrops(True)

        self.focusedPlotItem = self.plotItems[0]

    @property
    def curveNames(self) -> List[str]:
        curveNameList = []
        for item in self.plotItems:
            for curveName in list(item.vb.curves.keys()):
                curveNameList.append(curveName)
        return curveNameList

    def updateColors(self):
        p = QApplication.palette()
        for plotItem in self.plotItems:
            plotItem.vb.setBackgroundColor(p.base().color())
            axis: AxisItem = plotItem.axes["left"]["item"]
            axis.setPen(pg.mkPen(p.text().color()))
            axis: AxisItem = plotItem.axes["bottom"]["item"]
            axis.setPen(pg.mkPen(p.text().color()))
            plotItem.vb.setBorder({"color": p.text().color(), "width": 1})
        self.setBackground(p.base().color())

    def onXRangeChanged(self, plotItem, range):
        plotItem = self.plotItems[0]
        minValue = (
            (range[0] - plotItem.vb.xLimits[0])
            / (plotItem.vb.xLimits[1] - plotItem.vb.xLimits[0])
            * 100.0
        )
        maxValue = (
            (range[1] - plotItem.vb.xLimits[0])
            / (plotItem.vb.xLimits[1] - plotItem.vb.xLimits[0])
            * 100.0
        )
        print(f"Updapte x range: [{minValue}, {maxValue}]")
        self.xRangeUpdated.emit(minValue, maxValue)

    def addPlotItem(self, *args, **kargs):
        plotItem = self.addPlot(*args, **kargs)
        axis: AxisItem = plotItem.axes["left"]["item"]
        axis.setPen(pg.mkPen(QApplication.palette().text().color()))
        axis: AxisItem = plotItem.axes["bottom"]["item"]
        axis.setPen(pg.mkPen(QApplication.palette().text().color()))

        maxWidth = 0
        plotItem.vb.sigXRangeChanged.connect(self.onXRangeChanged)

        if len(self.plotItems) > 0:
            firstPlotItem = self.plotItems[0]
            defaultViewRange = firstPlotItem.viewRange()[0]
            firstPlotItem.setXLink(plotItem)
            plotItem.setLimits(
                xMin=firstPlotItem.vb.xLimits[0],
                xMax=firstPlotItem.vb.xLimits[1],
                yMin=firstPlotItem.vb.yLimits[0],
                yMax=firstPlotItem.vb.yLimits[1],
            )
            plotItem.setRange(xRange=defaultViewRange)

        self.plotItems.append(plotItem)

        for item in self.plotItems:
            axis = item.axes["left"]["item"]
            maxWidth = max(maxWidth, axis.width())

        for item in self.plotItems:
            item.axes["left"]["item"].setWidth(maxWidth)

        self.plotItems[-1].addLegend()
        self.plotItems[-1].showGrid(x=True, y=True, alpha=GRID_ALPHA)

        proxy = SignalProxy(
            plotItem.scene().sigMouseMoved,
            rateLimit=60,
            slot=plotItem.vb.mouseMoved,
        )

        self.plotProxies.append(proxy)

        self.focusedPlotItem = plotItem

        return plotItem

    def addDataItem(self, dataItem: NDataCurve, name):
        self.focusedPlotItem.addItem(dataItem)
        dataItem.sigClicked.connect(self.modifyCurve)
        self.focusedPlotItem.vb.curves.update({name: dataItem})
        if len(self.focusedPlotItem.vb.curves.keys()) == 0:
            self.updateLimitsFromOtherItem(dataItem, reset=True)
        else:
            self.updateLimitsFromOtherItem(dataItem, reset=False)
        self.focusedPlotItem.vb.autoRange()

    def updateLimitsFromOtherItem(self, dataItem, reset=True):
        for item in self.plotItems:
            vb = item.vb
            if reset is True:
                vb.xLimits = np.array([np.NaN, np.NaN])
                vb.yLimits = np.array([np.NaN, np.NaN])
            vb.xLimits[0] = min(np.min(dataItem.xData), vb.xLimits[0])
            vb.xLimits[1] = max(np.max(dataItem.xData), vb.xLimits[1])
            vb.yLimits[0] = min(np.min(dataItem.yData), vb.yLimits[0])
            vb.yLimits[1] = max(np.max(dataItem.yData), vb.yLimits[1])
            yRange = max(vb.yLimits[1] - vb.yLimits[0], 1e-9)
            item.setLimits(
                xMin=vb.xLimits[0],
                xMax=vb.xLimits[1],
                yMin=vb.yLimits[0] - yRange * 0.1,
                yMax=vb.yLimits[1] + yRange * 0.1,
            )

        # self.plotItem.setRange(yRange=(self.yLimits[0], self.yLimits[1] * 0.5))

    def updateLimits(self, xLimits=None, yLimits=None):

        for item in self.plotItems:
            vb = item.vb
            if xLimits is not None:
                vb.xLimits = xLimits
            if yLimits is not None:
                vb.yLimits = yLimits
            yRange = max(vb.yLimits[1] - vb.yLimits[0], 1e-9)

            item.setLimits(
                xMin=vb.xLimits[0],
                xMax=vb.xLimits[1],
                yMin=vb.yLimits[0] - yRange * 0.1,
                yMax=vb.yLimits[1] + yRange * 0.1,
            )

    def modifyCurve(self, curve, ev: MouseClickEvent):
        logger.info("modifyCurve")
        highlightedCurve = self.focusedPlotItem.vb.highlightedCurve
        if highlightedCurve is not None and curve != highlightedCurve:
            self.focusedPlotItem.vb.highlightedCurve.setSymbol(None)
            self.focusedPlotItem.vb.highlightedCurve = None
        if ev.button() == Qt.LeftButton:
            if curve.opts["symbol"] is None:
                curve.setSymbol("x")
                self.focusedPlotItem.vb.highlightedCurve = curve
            else:
                logger.info("Suppressing highlighted curve.")
                curve.setSymbol(None)
                self.focusedPlotItem.vb.highlightedCurve = None

    def mouseMoved(self, evt: QMouseEvent):
        # using signal proxy turns original arguments into a tuple
        pos: QPointF = evt[0]  # type: ignore
        vb: ViewBox = self.plotItem.vb
        mousePoint = vb.mapSceneToView(pos)

        x = mousePoint.x()

        for plotItem in self.plotItems:
            for index, (name, item) in enumerate(plotItem.vb.curves.items()):
                xData = item.xData
                yData = item.yData
                i = np.argmin(abs(xData - x))
                plotItem.legend.items[index][1].setText(f"{name}: {yData[i]:.2f}")

        if self.plotItem.vb.highlightedCurve is None:
            return

    def as_dict(self):
        rep = {}
        rep.update({self.name: [item.vb.as_dict() for item in self.plotItems]})
        return rep

    def __repr__(self):
        return str(self.as_dict())

    def viewAll(self):
        for item in self.plotItems:
            item.vb.autoRange()

    def updateXAxis(self, minValue: int, maxValue: int) -> None:
        """
        Update the x-axis
        :param minValue: min x value to set
        :param maxValue:max x value to set
        :return: ``None``
        """
        vb = self.plotItems[0].vb
        minRange = ((100 - minValue) * vb.xLimits[0] + minValue * vb.xLimits[1]) / 100
        maxRange = ((100 - maxValue) * vb.xLimits[0] + maxValue * vb.xLimits[1]) / 100
        for item in self.plotItems:
            item.setRange(xRange=(minRange, maxRange))
        # self.plotItem.vb.xAxis.setRange(minRange, maxRange)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        """
        Handle drag enter event. If the MIME data contains plain text, then accept the drag event.
        :param e: `QDragEnterEvent`
        :return: None
        """
        if e.mimeData().hasFormat("text/plain"):
            e.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """
        Handle drop event. Plot curves from curves names in MIME text.
        :param event: `QDropEvent`
        :return: None
        """
        curvesNamesStr: str = event.mimeData().text()
        logger.debug("Curve names dropped: " + curvesNamesStr)
        if not curvesNamesStr:
            return
        curvesNames: List[str] = curvesNamesStr.split("\n")
        self.worksheetsTabWidget.window.plotCurves(curvesNames)
        event.accept()


class NViewBox(pg.ViewBox):
    """
    Subclass of ViewBox
    """

    # signalShowT0 = QtCore.Signal()
    # signalShowS0 = QtCore.Signal()

    def __init__(self, parent=None, nPlotWidget: Optional[NPlotWidget] = None):
        """
        Constructor of the NViewBox
        """
        super(NViewBox, self).__init__()
        self.nPlotWidget = nPlotWidget
        # self.setRectMode() # Set mouse mode to rect for convenient zooming
        # self.menu = None # Override pyqtgraph ViewBoxMenu
        # self.menu = self.getMenu() # Create the menu
        self.customizeAct = QtGui.QAction("Customize curve", self.menu)
        self.customizeAct.triggered.connect(self.customizeCurves)  # type: ignore
        self.menu.addAction(self.customizeAct)

        self.addSubPlotAct = QtGui.QAction("Add subplot", self.menu)
        self.addSubPlotAct.triggered.connect(self.addSubPlot)  # type: ignore
        self.menu.addAction(self.addSubPlotAct)

        self.removeThisSubPlotAct = QtGui.QAction("Remove this subplot", self.menu)
        self.removeThisSubPlotAct.triggered.connect(self.closeCurrentSubPlot)  # type: ignore
        self.menu.addAction(self.removeThisSubPlotAct)
        self.removeThisSubPlotAct.setEnabled(False)
        self.removeThisSubPlotAct.setVisible(False)

        menu: ViewBoxMenu = self.menu

        viewAll: QAction = menu.viewAll
        viewAll.setText("Fix to view")

        self.curves: Dict[str, NDataCurve] = {}
        self.highlightedCurve: Optional[NDataCurve] = None

        palette = QApplication.palette()
        self.vLine: InfiniteLine = InfiniteLine(
            angle=90, movable=False, pen=pg.mkPen(palette.highlight().color())
        )
        self.hLine: InfiniteLine = InfiniteLine(
            angle=0, movable=False, pen=pg.mkPen(palette.highlight().color())
        )

        self.setBorder({"color": palette.text().color(), "width": 1})
        self.setBackgroundColor(QApplication.palette().base().color())

        self.addItem(self.vLine, ignoreBounds=True)
        self.addItem(self.hLine, ignoreBounds=True)

        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)

        self.xLimits = np.array([0.0, 1.0])
        self.yLimits = np.array([0.0, 1.0])
        self.setLimits(
            xMin=self.xLimits[0],
            xMax=self.xLimits[1],
            yMin=self.yLimits[0],
            yMax=self.yLimits[1],
        )

    def hoverEnterEvent(self, ev: QEvent):
        self.vLine.show()
        self.hLine.show()

    def hoverLeaveEvent(self, ev: QEvent):
        self.vLine.hide()
        self.hLine.hide()

    def mouseMoved(self, evt):
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

        if self.highlightedCurve is None:
            return

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

        if self.highlightedCurve is None:
            logger.warning("No curve selected")
            return

        curve = self.highlightedCurve
        curveName = curve.name

        color = QColorDialog.getColor()
        logger.info(f"New color for curve {curveName}: {color}")

        curve.setPen(pg.mkPen(color, width=curve.pen.width()))
        curve.setSymbolPen(pg.mkPen(color))
        curve.setBrush(pg.mkBrush(color))
        curve.setSymbolBrush(pg.mkBrush(color))

    def addSubPlot(self):
        plotItem = self.nPlotWidget.addPlotItem(
            viewBox=NViewBox(self.nPlotWidget, self.nPlotWidget),
            row=self.nPlotWidget.nextRow(),
        )

        for item in self.nPlotWidget.plotItems:
            item.setXLink(plotItem)

        for index, plotItem in enumerate(self.nPlotWidget.plotItems):
            plotItem.vb.removeThisSubPlotAct.setEnabled(True)
            plotItem.vb.removeThisSubPlotAct.setVisible(True)

    def closeCurrentSubPlot(self):
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
            self.getFocus()

    def getFocus(self):
        palette = QApplication.palette()
        for p in self.nPlotWidget.plotItems:
            vb = p.getViewBox()
            vb.setBorder({"color": palette.text().color(), "width": 1})
            vb.update()
            if vb == self:
                self.nPlotWidget.focusedPlotItem = p
        self.setBorder({"color": palette.highlight().color(), "width": 4})

    def as_dict(self):
        rep = {}
        for k, v in self.curves.items():
            rep.update({k: v.opts["pen"]})

        return rep

    def dragEnterEvent(self, ev):
        self.getFocus()
        ev.acceptProposedAction()
