# -*- coding: utf-8 -*-
"""
${FILE_NAME} module containing :class:`~nodedge.${FILE_NAME}.<ClassName>` class.
"""
import pyqtgraph as pg
from pyqtgraph import ViewBox
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor

MAX_NUM_SAMPLES = 10000


class CurveItem(pg.PlotCurveItem):
    def __init__(self, *args, **kwds):
        self.dataPoints = None
        self.limit = MAX_NUM_SAMPLES  # maximum number of samples to be plotted
        pg.PlotCurveItem.__init__(self, *args, **kwds)

        self.setClickable(True, 5)

        self.curveName = "Unnamed"
        self.color: QColor = self.opts["pen"].color()
        self.style: Qt.PenStyle = self.opts["pen"].style()
        self.width: float = self.opts["pen"].widthF()
        self.highlighted: bool = False

    def setDataPoints(self, y, x=None):
        self.timePoints = x
        self.dataPoints = y
        self.updatePlot()

    def viewRangeChanged(self):
        self.updatePlot()

    def updatePlot(self):
        if self.dataPoints is None:
            self.setData([])
            return
        # Remove antialias in case performance is not enough.
        self.setData(x=self.timePoints, y=self.dataPoints, antialias=True)
        self.resetTransform()
        self.scale(1, 1)
        vb: ViewBox = self.getViewBox()
        vb.update()
        # FIXME: Plotting of chuncks is disabled.
        #
        # vb = self.getViewBox()
        # if vb is None:
        #     return  # no ViewBox yet
        #
        # # Determine what data range must be read from the dataset
        # xrange = vb.viewRange()[0]
        # start = max(0, int(xrange[0]) - 1)
        # stop = min(len(self.dataPoints), int(xrange[1] + 2))
        #
        # # Decide by how much we should downsample
        # ds = int((stop - start) / self.limit) + 1
        #
        # if ds == 1:
        #     # Small enough to display with no intervention.
        #     visible = self.dataPoints[start:stop]
        #     scale = 1
        # else:
        #     # Here convert data into a down-sampled array suitable for visualizing.
        #     # Must do this piecewise to limit memory usage.
        #     samples = 1 + ((stop - start) // ds)
        #     visible = np.zeros(samples * 2, dtype=self.dataPoints.dtype)
        #     sourcePtr = start
        #     targetPtr = 0
        #
        #     # read data in chunks of ~1M samples
        #     chunkSize = (1000000 // ds) * ds
        #     while sourcePtr < stop - 1:
        #         chunk = self.dataPoints[sourcePtr : min(stop, sourcePtr + chunkSize)]
        #         sourcePtr += len(chunk)
        #
        #         # reshape chunk to be integral multiple of ds
        #         chunk = chunk[: (len(chunk) // ds) * ds].reshape(len(chunk) // ds, ds)
        #
        #         # compute max and min
        #         chunkMax = chunk.max(axis=1)
        #         chunkMin = chunk.min(axis=1)
        #
        #         # interleave min and max into plot data to preserve envelope shape
        #         visible[targetPtr : targetPtr + chunk.shape[0] * 2 : 2] = chunkMin
        #         visible[
        #             1 + targetPtr : 1 + targetPtr + chunk.shape[0] * 2 : 2
        #         ] = chunkMax
        #         targetPtr += chunk.shape[0] * 2
        #
        #     visible = visible[:targetPtr]
        #     scale = ds * 0.5
        #
        # self.setData(visible)  # update the plot
        # self.setPos(start, 0)  # shift to match starting index
        # self.resetTransform()
        # self.scale(scale, 1)  # scale to match downsampling

    def mouseClickEvent(self, ev):
        super().mouseClickEvent(ev)
        buttons = ev.button()
        modifiers = ev.modifiers()

        if buttons == Qt.LeftButton and Qt.ControlModifier & modifiers:
            self.highlighted = not self.highlighted

            if self.highlighted:
                self.setWidth(self.width * 3)
            else:
                self.setWidth(self.width / 3)

    def setStyle(self, style: Qt.PenStyle):
        self.style = style
        pen = pg.mkPen(self.color, cosmetic=True, style=self.style)
        pen.setWidthF(self.width)
        self.setPen(pen)

    def setColor(self, color: QColor):
        self.color = color
        pen = pg.mkPen(self.color, cosmetic=True, style=self.style)
        pen.setWidthF(self.width)
        self.setPen(pen)

    def setWidth(self, width: float):
        self.width = width
        pen = pg.mkPen(self.color, cosmetic=True, style=self.style)
        pen.setWidthF(self.width)
        self.setPen(pen)
