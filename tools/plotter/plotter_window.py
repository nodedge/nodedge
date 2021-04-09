# -*- coding: utf-8 -*-
"""
plotter_window.py module containing :class:`~nodedge.plotter_window.py.<ClassName>` class.
"""

import logging
import sys

import h5py
import numpy as np
import pandas as pd
from pyqtgraph.dockarea import Dock, DockArea
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QApplication, QDockWidget, QFileDialog, QInputDialog

from nodedge.utils import dumpException
from tools.main_window_template.main_window import MainWindow
from tools.plotter.curve_container import CurveContainer
from tools.plotter.utils import getAllKeysHdf5, InstanceCounterMeta
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
        d1 = CountedDock()
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
        indices = [0 for _ in range(len(shape) - 1)]
        logger.debug(f"{datasetName} {shape} is going to be plotted.")

        for dim, length in enumerate(shape[0:-1]):
            dialog = QInputDialog()
            # Resize to fit content length. See this link:
            # https://forum.qt.io/topic/113184/qinputdialog-set-the-font-for-qplaintextedit-and-qlabel-separately
            index, okPressed = dialog.getInt(
                self, "Index selection", f"Index for dim {dim}:", 0, 0, length - 1, 1
            )
            indices[dim] = index

            if okPressed is False:
                return

        plottedData = data[indices]
        for i in indices:
            plottedData = plottedData[i]

        widget = CurveContainer()
        widget.curveItem.setHDF5(plottedData)
        d1 = CountedDock()
        # Change label text
        # d1.label.setText("New label")
        d1.addWidget(widget)
        subWindow = self.mdiArea.addDock(d1)
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


# Metaclass for counting:
# https://stackoverflow.com/questions/8628123/counting-instances-of-a-class/47610553
# Solve metaclass conflicts:
# https://stackoverflow.com/questions/11276037/resolving-metaclass-conflicts/61350480#61350480
class mCountedDock(type(Dock), metaclass=InstanceCounterMeta):
    pass


class CountedDock(Dock, metaclass=mCountedDock):

    def __init__(self):
        self.id = next(self.__class__._ids)
        self.dock = Dock.__init__(self, name=f"Plot{self.id}", size=(1, 1))


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
