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
from tools.plotter.range_slider_plot import RangeSliderPlot
from tools.plotter.sized_input_dialog import SizedInputDialog
from tools.plotter.utils import getAllKeysHdf5
from tools.plotter.variable_tree_widget import VariableTreeWidget

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PlotterWindow(MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, applicationName="Plotter")

        self.plotArea = PlotArea()
        self.setCentralWidget(self.plotArea)

        # Make sure left and right docks have higher priority than top and bottom docks
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)

        self.variableTree = VariableTreeWidget()
        self.variableTree.datasetDoubleClicked.connect(self.plotData)
        self.variableTreeDock = QDockWidget("Variables")
        self.variableTreeDock.setWidget(self.variableTree)
        self.variableTreeDock.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.variableTreeDock)

        self.rangeSliderPlot = RangeSliderPlot()
        self.rangeSliderDock = QDockWidget("Timeline")
        self.rangeSliderDock.setWidget(self.rangeSliderPlot)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.rangeSliderDock)

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
        widget.curveItem.setDataPoints(data)
        self.rangeSliderPlot.linkPlot(widget.graph)
        d1 = CountableDock()
        # Change label text
        # d1.label.setText("New label")
        d1.addWidget(widget)
        dock = self.plotArea.addDock(d1)
        dock.setTitle(variableName)

    def plotDataHdf5(self, datasetName):
        # Select data to plot
        data = np.array(self.file.get(datasetName))
        shape = data.shape
        logger.debug(f"{datasetName} {shape} is going to be plotted.")
        listZeros = ["0" for _ in range(len(shape) - 1)]
        defaultText = "[" + ", ".join(listZeros) + ", :]"

        if len(shape) > 1:

            dialog = SizedInputDialog(self, QSize(400, 200))
            indices, okPressed = dialog.getText(
                self,
                f"Index selection",
                f"The selected dataset has dimensions: {shape}. \nEnter below the indices to be plotted. \n\nExample: [1,:]",
                text=defaultText,
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

        widget: CurveContainer = CurveContainer()
        widget.curveItem.setDataPoints(dataToBePlotted)
        self.rangeSliderPlot.linkPlot(widget.graph)
        countableDock = CountableDock()
        countableDock.addWidget(widget)
        currentSubwindow = self.plotArea.mdiArea.currentSubWindow()
        # The first subwindow is not active, so find it manually.
        if currentSubwindow is None:
            if not self.plotArea.mdiArea.subWindowList():
                self.plotArea.addWorkbook("Untitled")
                currentSubwindow = self.plotArea.mdiArea.subWindowList()[0]
        dock = currentSubwindow.widget().addDock(countableDock, "bottom")
        dock.setTitle(dockTitle)

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

    def newFile(self):
        self.plotArea.addWorkbook()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PlotterWindow()
    window.showMaximized()

    # Open file
    # f = window.openFile()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
