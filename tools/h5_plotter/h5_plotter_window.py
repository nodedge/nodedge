# -*- coding: utf-8 -*-
"""
h5_plotter_window.py module containing :class:`~nodedge.h5_plotter_window.py.<ClassName>` class.
"""

import logging
import sys

import h5py
import numpy as np
import pyqtgraph as pg
from PySide2.QtWidgets import QApplication, QFileDialog

from nodedge.utils import dumpException
from tools.main_window_template.main_window import MainWindow
from tools.main_window_template.mdi_area import MdiArea

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Parameters
MAX_NUM_SAMPLES = 10000


class HDF5Plot(pg.PlotCurveItem):
    def __init__(self, *args, **kwds):
        self.hdf5 = None
        self.limit = MAX_NUM_SAMPLES  # maximum number of samples to be plotted
        pg.PlotCurveItem.__init__(self, *args, **kwds)

    def setHDF5(self, data):
        self.hdf5 = data
        self.updateHDF5Plot()

    def viewRangeChanged(self):
        self.updateHDF5Plot()

    def updateHDF5Plot(self):
        if self.hdf5 is None:
            self.setData([])
            return

        vb = self.getViewBox()
        if vb is None:
            return  # no ViewBox yet

        # Determine what data range must be read from HDF5
        xrange = vb.viewRange()[0]
        start = max(0, int(xrange[0]) - 1)
        stop = min(len(self.hdf5), int(xrange[1] + 2))

        # Decide by how much we should downsample
        ds = int((stop - start) / self.limit) + 1

        if ds == 1:
            # Small enough to display with no intervention.
            visible = self.hdf5[start:stop]
            scale = 1
        else:
            # Here convert data into a down-sampled array suitable for visualizing.
            # Must do this piecewise to limit memory usage.
            samples = 1 + ((stop - start) // ds)
            visible = np.zeros(samples * 2, dtype=self.hdf5.dtype)
            sourcePtr = start
            targetPtr = 0

            # read data in chunks of ~1M samples
            chunkSize = (1000000 // ds) * ds
            while sourcePtr < stop - 1:
                chunk = self.hdf5[sourcePtr : min(stop, sourcePtr + chunkSize)]
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


class PlotterWindow(MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, applicationName="Plotter")

        self.mdiArea = MdiArea()
        self.setCentralWidget(self.mdiArea)

    def openFile(self, filename: str = ""):
        logger.debug(filename)
        if filename in ["", None, False]:
            filename, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Open graph from file",
                dir=PlotterWindow.getFileDialogDirectory(),
                filter=PlotterWindow.getFileDialogFilter(),
            )

        extension = filename.split(".")[-1]
        if extension == "hdf5":
            f = self.loadHdf5(filename)
        elif extension == "csv":
            f = self.loadCsv(filename)
        else:
            return NotImplementedError

        return f

    def loadCsv(self, filename):
        raise NotImplementedError

    def loadHdf5(self, filename):
        f = h5py.File(filename, "r")
        return f

    @staticmethod
    def getFileDialogDirectory() -> str:
        """
        Returns starting directory for ``QFileDialog`` file open/save

        :return: starting directory for ``QFileDialog`` file open/save
        :rtype: ``str``
        """
        return "../../data"

    @staticmethod
    def getFileDialogFilter() -> str:
        """
        Returns ``str`` standard file open/save filter for ``QFileDialog``

        :return: standard file open/save filter for ``QFileDialog``
        :rtype: ``str``
        """
        return "HDF5 (*.hdf5);;CSV (*.csv);;All files (*)"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PlotterWindow()
    window.showMaximized()

    # Open file
    f = window.openFile()

    # Select data to plot
    ax = 0
    agent = 0
    pos_k = np.array(f.get("sim_data/pos_k_i"))[ax, :, agent]

    # Create and plot the curve
    curve = HDF5Plot()
    curve.setHDF5(pos_k)
    plt = pg.plot()
    plt.addItem(curve)

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
