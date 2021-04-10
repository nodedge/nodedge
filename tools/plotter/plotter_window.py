# -*- coding: utf-8 -*-
"""
plotter_window.py module containing :class:`~nodedge.plotter_window.py.<ClassName>` class.
"""

import logging
import sys

import h5py
import numpy as np
import pandas as pd
from PySide2.QtCore import QSize, Qt, Slot
from PySide2.QtWidgets import QApplication, QDockWidget, QFileDialog, QInputDialog

from nodedge.utils import dumpException
from tools.main_window_template.main_window import MainWindow
from tools.plotter.countable_dock import CountableDock
from tools.plotter.curve_container import CurveContainer
from tools.plotter.plot_area import PlotArea
from tools.plotter.sized_input_dialog import SizedInputDialog
from tools.plotter.utils import getAllKeysHdf5
from tools.plotter.variable_tree_widget import DatasetTreeWidget

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PlotterWindow(MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, applicationName="Plotter")

        self.plotArea = PlotArea()
        self.setCentralWidget(self.plotArea)

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
            allKeys, allTypes = getAllKeysHdf5(self.file)
            self.variableTree.updateVariablesHdf5(allKeys, allTypes)

        elif extension == "csv":
            # Load csv file
            self.file = self.loadCsv(filename)

            # Get csv key tree
            allKeys = self.file.keys()
            self.variableTree.updateVariablesCsv(allKeys)
        else:
            return NotImplementedError

        return self.file

    @Slot(str)  # type: ignore
    def plotData(self, variableName: str):

        if isinstance(self.file, h5py.File):
            self.plotDataHdf5(variableName)
        elif isinstance(self.file, pd.core.frame.DataFrame):
            self.plotDataCsv(variableName)
        else:
            raise NotImplementedError

    def loadCsv(self, filename):
        dataFrame = pd.read_csv(filename)
        return dataFrame

    def loadHdf5(self, filename):
        f = h5py.File(filename, "r")
        return f

    def plotDataCsv(self, variableName):
        # Select data to plot
        data = np.array(self.file[variableName])

        widget = CurveContainer()
        widget.curveItem.setHDF5(data)
        d1 = CountableDock()
        # Change label text
        # d1.label.setText("New label")
        d1.addWidget(widget)
        subWindow = self.mdiArea.addDock(d1)
        subWindow.setWindowTitle(variableName)
        subWindow.showMaximized()

    def plotDataHdf5(self, datasetName):
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
        subWindow = self.plotArea.workbooks[0].addDock(countableDock, "bottom")
        subWindow.setTitle(dockTitle)
        subWindow.setWindowTitle(datasetName)
        subWindow.showMaximized()

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
