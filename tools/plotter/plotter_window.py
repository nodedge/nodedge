# -*- coding: utf-8 -*-
"""
plotter_window.py module containing :class:`~nodedge.plotter_window.py.<ClassName>` class.
"""

import logging
import sys

import h5py
import numpy as np
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QApplication, QDockWidget, QFileDialog, QInputDialog

from nodedge.utils import dumpException
from tools.main_window_template.main_window import MainWindow
from tools.main_window_template.mdi_area import MdiArea
from tools.plotter.curve_container import CurveContainer
from tools.plotter.utils import getAllH5Keys
from tools.plotter.variable_tree_widget import DatasetTreeWidget

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PlotterWindow(MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, applicationName="Plotter")

        self.mdiArea = MdiArea()
        self.setCentralWidget(self.mdiArea)

        self.variableTree = DatasetTreeWidget()
        self.variableTree.datasetDoubleClicked.connect(self.plotData)
        self.variableTreeDock = QDockWidget("Variables")
        self.variableTreeDock.setWidget(self.variableTree)
        self.variableTreeDock.setFloating(False)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.variableTreeDock)

    def openFile(self, filename: str = ""):
        if filename in ["", None, False]:
            filename, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Open graph from file",
                dir=PlotterWindow.getFileDialogDirectory(),
                filter=PlotterWindow.getFileDialogFilter(),
            )

        extension = filename.split(".")[-1]
        if extension == "hdf5":
            self.file = self.loadHdf5(filename)
        elif extension == "csv":
            self.file = self.loadCsv(filename)
        else:
            return NotImplementedError

        # Get hdf5 key tree
        allKeys, allTypes = getAllH5Keys(self.file)

        self.variableTree.updateVariables(allKeys, allTypes)

        self.plotData("sim_data/pos_k_i")

        return self.file

    @Slot(str)
    def plotData(self, datasetName: str):
        # Select data to plot
        data = np.array(self.file.get(datasetName))
        shape = data.shape
        indices = [0 for _ in range(len(shape) - 1)]
        logger.debug(f"{datasetName} ({shape})is going to be plotted.")

        for dim, length in enumerate(shape[0:-1]):
            index, okPressed = QInputDialog.getInt(
                self, "Index", "Index:", 0, 0, length - 1, 1
            )
            indices[dim] = index

            if okPressed is False:
                return

        plottedData = data[indices]
        for i in indices:
            plottedData = plottedData[i]

        widget = CurveContainer()
        widget.curveItem.setHDF5(plottedData)
        subWindow = self.mdiArea.addSubWindow(widget)
        subWindow.setWindowTitle(datasetName)
        subWindow.showMaximized()

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

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
