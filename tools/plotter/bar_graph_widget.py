# -*- coding: utf-8 -*-
import numpy as np
import pyqtgraph as pg
from PySide2.QtCore import QTimer, Signal
from PySide2.QtWidgets import QApplication

from tools.plotter.bar_graph_item import BarGraphItem


class BarGraphWidget(pg.PlotWidget):
    valuesUpdated = Signal()

    def __init__(
        self,
        x,
        height,
        width=1,
        brushes=None,
        brushesDependOnHeight=True,
        simulatedData=True,
        ignoredValueInStats=None,
    ):
        xAxis = pg.AxisItem(orientation="bottom")
        xAxis.setTickSpacing(10, 1)
        xAxis.setLabel("Cells")
        yAxis = pg.AxisItem(orientation="left")
        yAxis.setLabel("Voltage [V]")
        super().__init__(axisItems={"bottom": xAxis, "left": yAxis})
        self.setMouseEnabled(False, False)
        self.showGrid(x=True, y=True)

        self.bars = BarGraphItem(
            x=x,
            height=height,
            width=width,
            brushes=brushes,
            brushes_depend_on_height=brushesDependOnHeight,
        )
        self.addBars(self.bars)
        self.enableAutoRange(axis="y")
        self.setAutoVisible(y=True)
        self.setYRange(0, 2.5)

        p = QApplication.palette()
        # self.bars.getViewBox().setBackgroundColor(p.window().color())

        self.simulatedData = simulatedData
        if self.simulatedData:
            self.simulatorTimer = QTimer()
            self.simulatorTimer.timeout.connect(self.updateData)
            self.simulatorTimer.start(100)

        self.averageLine = pg.InfiniteLine(
            angle=0, pen=pg.mkPen(0, 255, 0, 255, width=2)
        )
        self.averageMinusStdLine = pg.InfiniteLine(
            angle=0, pen=pg.mkPen(255, 0, 0, 100, width=1)
        )
        self.averagePlusStdLine = pg.InfiniteLine(
            angle=0, pen=pg.mkPen(255, 0, 0, 100, width=1)
        )
        self.addItem(self.averageLine)
        self.addItem(self.averageMinusStdLine)
        self.addItem(self.averagePlusStdLine)
        self.minLine = pg.InfiniteLine(pen=pg.mkPen("y", width=1.2))
        self.addItem(self.minLine)
        self.maxLine = pg.InfiniteLine(pen=pg.mkPen("y", width=1.2))
        self.addItem(self.maxLine)

        self.ignoredValueInStats = ignoredValueInStats
        self.updateStatistics()

    def mousePressEvent(self, ev):
        pos = self.getPlotItem().vb.mapSceneToView(ev.pos())
        if self.bars is not None:
            for i, _ in enumerate(self.bars.x):
                if (
                    self.bars.x[i] - self.bars.width / 2
                    < pos.x()
                    < self.bars.x[i] + self.bars.width / 2
                    and 0 < pos.y() < self.bars.height[i]
                ):
                    b = self.bars.brushes
                    b[i] = pg.QtGui.QColor(255, 255, 255)
                    self.bars.setAttr(brushes=b)
                    self.__logger.debug("clicked on bar " + str(i))
                    ev.accept()
        super().mousePressEvent(ev)

    def addBars(self, bars):
        self.bars = bars
        self.clear()
        self.addItem(bars)

    def updateData(self, values=None):
        if self.simulatedData:
            self.simulatorTimer.start()

        if values is None:
            xvalues = np.random.randint(len(self.bars.x), size=10).tolist()
            yvalues = np.random.rand(10)
            yvalues *= 2.5
            yvalues[yvalues > 2.5] = 2.5
            yvalues = yvalues.tolist()
            values = [xvalues, yvalues]
        xvalues = values[0]
        yvalues = values[1]

        newValuesDict = dict(zip(xvalues, yvalues))
        valuesDict = dict(zip(self.bars.x, self.bars.height))

        valuesDict.update(newValuesDict)
        x, height = zip(*valuesDict.items())

        newInitializedDict = dict(zip(xvalues, [True for _ in range(len(xvalues))]))
        initializedDict = dict(zip(self.bars.x, self.bars.barInitialized))

        initializedDict.update(newInitializedDict)
        _, barInitialized = zip(*initializedDict.items())

        self.bars.barInitialized = barInitialized
        self.bars.setAttr(x=x, height=height)

        self.updateStatistics()

        self.valuesUpdated.emit()

    def updateStatistics(self):
        height_array = np.array(self.bars.height)

        self.average = np.mean(height_array)
        if self.ignoredValueInStats is not None:
            height_array[self.ignoredValueInStats] = self.average
        self.stdev = np.std(height_array)
        self.arg_min = np.argmin(height_array)
        self.arg_max = np.argmax(height_array)
        self.min = np.min(height_array)
        self.max = np.max(height_array)

        self.updateInfiniteLines()

    def updateInfiniteLines(self):
        self.averageLine.setPos(self.average)
        self.averageMinusStdLine.setPos(self.average - self.stdev)
        self.averagePlusStdLine.setPos(self.average + self.stdev)
        self.minLine.setPos(self.arg_min)
        self.minLine.setPos(self.arg_max)
