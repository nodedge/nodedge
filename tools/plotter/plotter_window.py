# -*- coding: utf-8 -*-
"""
plotter_window.py module containing :class:`~nodedge.plotter_window.py.<ClassName>` class.
"""

import ast
import logging
import sys

import h5py
import numpy as np
import pandas as pd
from pyqtgraph.dockarea import DockArea
from PySide2.QtCore import QSize, Qt, Slot
from PySide2.QtWidgets import QApplication, QDockWidget, QFileDialog, QInputDialog

from nodedge.utils import dumpException
from tools.main_window_template.main_window import MainWindow
from tools.plotter.countable_dock import CountableDock
from tools.plotter.curve_container import CurveContainer
from tools.plotter.sized_input_dialog import SizedInputDialog
from tools.plotter.utils import getAllH5Keys
from tools.plotter.variable_tree_widget import DatasetTreeWidget

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PlotterWindow(MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, applicationName="Plotter")

        self.mdiArea = DockArea()
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
            # Load hdf5 file
            self.file = self.loadHdf5(filename)

            # Get hdf5 key tree
            allKeys, allTypes = getAllH5Keys(self.file)
            self.variableTree.updateVariables(allKeys, allTypes)

        elif extension == "csv":
            # Load csv file
            self.file = self.loadCsv(filename)

        else:
            return NotImplementedError

        return self.file

    @Slot(str)  # type: ignore
    def plotData(self, datasetName: str):
        # Select data to plot
        data = np.array(self.file.get(datasetName))
        shape = data.shape
        logger.debug(f"{datasetName} {shape} is going to be plotted.")

        if len(shape) > 1:

            dialog = SizedInputDialog(self, QSize(400, 200))
            indices, okPressed = dialog.getText(
                self,
                f"Index selection",
                f"The selected dataset has dimensions: {shape}. \nEnter below the indices to be plotted. \n\nExample: [1,:]",
            )

            if not okPressed:
                return

            try:
                toBeEvaluated = "data" + indices
                dataToBePlotted = eval(toBeEvaluated)
            except SyntaxError:
                return

            dockTitle = datasetName + indices

        else:
            dataToBePlotted = data
            dockTitle = datasetName

        widget = CurveContainer()
        widget.curveItem.setHDF5(dataToBePlotted)
        countableDock = CountableDock()
        countableDock.addWidget(widget)
        subWindow = self.mdiArea.addDock(countableDock)
        subWindow.setTitle(dockTitle)
        # subWindow.setWindowTitle(datasetName)
        # subWindow.showMaximized()

    def loadCsv(self, filename):
        dataFrame = pd.read_csv(filename)
        return dataFrame

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
