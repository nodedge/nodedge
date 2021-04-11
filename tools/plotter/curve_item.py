# -*- coding: utf-8 -*-
"""
${FILE_NAME} module containing :class:`~nodedge.${FILE_NAME}.<ClassName>` class.
"""
import numpy as np
import pyqtgraph as pg
# Parameters
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QAction, QColorDialog, QInputDialog

MAX_NUM_SAMPLES = 10000


class CurveItem(pg.PlotCurveItem):
    def __init__(self, *args, **kwds):
        self.dataPoints = None
        self.limit = MAX_NUM_SAMPLES  # maximum number of samples to be plotted
        pg.PlotCurveItem.__init__(self, *args, **kwds)

        self.setClickable(True, 5)

        self.clicked = False
        self.initialized = False
        self.curveName = "Unnamed"

    def setDataPoints(self, dataPoints):
        self.dataPoints = dataPoints
        vb = self.getViewBox()
        vb.setRange(xRange=range(0, len(dataPoints)))
        self.updatePlot()

    def viewRangeChanged(self):
        self.updatePlot()

    def updatePlot(self):
        if self.dataPoints is None:
            self.setData([])
            return

        vb = self.getViewBox()
        if vb is None:
            return  # no ViewBox yet

        # Determine what data range must be read from the dataset
        xrange = vb.viewRange()[0]
        start = max(0, int(xrange[0]) - 1)
        stop = min(len(self.dataPoints), int(xrange[1] + 2))

        # Decide by how much we should downsample
        ds = int((stop - start) / self.limit) + 1

        if ds == 1:
            # Small enough to display with no intervention.
            visible = self.dataPoints[start:stop]
            scale = 1
        else:
            # Here convert data into a down-sampled array suitable for visualizing.
            # Must do this piecewise to limit memory usage.
            samples = 1 + ((stop - start) // ds)
            visible = np.zeros(samples * 2, dtype=self.dataPoints.dtype)
            sourcePtr = start
            targetPtr = 0

            # read data in chunks of ~1M samples
            chunkSize = (1000000 // ds) * ds
            while sourcePtr < stop - 1:
                chunk = self.dataPoints[sourcePtr : min(stop, sourcePtr + chunkSize)]
                sourcePtr += len(chunk)

                # reshape chunk to be integral multiple of ds
                chunk = chunk[: (len(chunk) // ds) * ds].reshape(len(chunk) // ds, ds)

                # compute max and min
                chunkMax = chunk.max(axis=1)
                chunkMin = chunk.min(axis=1)

                # interleave min and max into plot data to preserve envelope shape
                visible[targetPtr : targetPtr + chunk.shape[0] * 2 : 2] = chunkMin
                visible[
                    1 + targetPtr : 1 + targetPtr + chunk.shape[0] * 2 : 2
                ] = chunkMax
                targetPtr += chunk.shape[0] * 2

            visible = visible[:targetPtr]
            scale = ds * 0.5

        self.setData(visible)  # update the plot
        self.setPos(start, 0)  # shift to match starting index
        self.resetTransform()
        self.scale(scale, 1)  # scale to match downsampling

    def mouseClickEvent(self, event):
        super().mouseClickEvent(event)
        self.clicked = not self.clicked

        eventButton: Qt.MouseButton = event.button()
        eventModifiers: Qt.KeyboardModifiers = event.modifiers()
        if eventButton == Qt.RightButton and not self.initialized:
            menu = self.getViewBox().menu
            renameAction: QAction = QAction("Rename", menu)
            menu.addAction(renameAction)
            renameAction.triggered.connect(self.setName)
            colorAction: QAction = QAction("Color", menu)
            menu.addAction(colorAction)
            colorAction.triggered.connect(self.setColor)
            self.initialized = True

    def setName(self):
        self.curveName = QInputDialog.getText(
            None, "Set Name", "Enter the curve name below:", text=self.curveName
        )

    def setColor(self):
        colorDialog = QColorDialog()
        # TODO: Add custom palette as standard color
        # colorDialog.setOption(QColorDialog.DontUseNativeDialog)
        # colorDialog.setStandardColor(0, QColor("g"))
        color = colorDialog.getColor()
        if not color.isValid():
            return
        self.setPen(pg.mkPen(color, width=1, cosmetic=True))
