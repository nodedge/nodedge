# -*- coding: utf-8 -*-
"""
plotter_window.py module containing :class:`~nodedge.plotter_window.py.<ClassName>` class.
"""

import logging
import sys
from enum import IntEnum

import h5py
import numpy as np
import pandas as pd
from pyqtgraph.dockarea import DockArea
from PySide2.QtCore import QSize, Qt, Slot
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QApplication, QDockWidget, QFileDialog

from nodedge.utils import dumpException
from tools.main_window_template.main_window import MainWindow
from tools.plotter.countable_dock import CountableDock
from tools.plotter.curve_container import CurveContainer
from tools.plotter.plot_area import PlotArea
from tools.plotter.range_slider_plot import RangeSliderPlot
from tools.plotter.ranged_plot import RangedPlot
from tools.plotter.sized_input_dialog import SizedInputDialog
from tools.plotter.utils import getAllKeysHdf5
from tools.plotter.variable_tree_widget import VariableTreeWidget

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PlottingOption(IntEnum):
    ADD_NEW_WORKSHEET = 1  #:
    APPEND_IN_CURRENT_WORKSHEET = 2  #:
    ADD_NEW_WORKBOOK = 3  #:


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
        self.variableTree.variableDoubleClicked.connect(self.plotData)
        self.variableTree.variableCtrlClicked.connect(self.onVariableCtrlClicked)
        self.variableTree.variableShiftClicked.connect(self.onVariableShiftClicked)
        self.variableTreeDock = QDockWidget("Variables")
        self.variableTreeDock.setWidget(self.variableTree)
        self.variableTreeDock.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.variableTreeDock)

        self.rangeSliderPlot = RangeSliderPlot()
        self.rangeSliderDock = QDockWidget("Timeline")
        self.rangeSliderDock.setWidget(self.rangeSliderPlot)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.rangeSliderDock)

    def openFile(self, filename: str = ""):
        self.variableTree.clear()
        # TODO: Clear all curves

        if filename in ["", None, False]:
            filename, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Open graph from file",
                dir=PlotterWindow.getFileDialogDirectory(),
                filter=PlotterWindow.getFileDialogFilter(),
            )

        extension = filename.split(".")[-1]
        if extension == "hdf5" or extension == "h5":
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

    def onVariableShiftClicked(self, variableName):
        self.plotData(variableName, option=PlottingOption.APPEND_IN_CURRENT_WORKSHEET)

    def onVariableCtrlClicked(self, variableName):
        self.plotData(variableName, option=PlottingOption.ADD_NEW_WORKBOOK)

    @Slot(str)  # type: ignore
    def plotData(
        self,
        variableName: str,
        option: PlottingOption = PlottingOption.ADD_NEW_WORKSHEET,
        indices=None,
    ):

        dataToBePlotted, fullDatasetName = self.selectDataToBePlotted(
            variableName, indices
        )

        # Select current subwindow
        currentSubwindow = self.selectSubwindow(option)

        # Select dock where to plot
        dock = self.selectDock(currentSubwindow, option)

        dock.setTitle(fullDatasetName)
        dock.widgets[0].graph.plot(dataToBePlotted, name=fullDatasetName)
        self.rangeSliderPlot.linkPlot(dock.widgets[0].graph)

    def selectDataToBePlotted(self, variableName, indices=None):
        if isinstance(self.file, h5py.File):
            dataToBePlotted, fullDatasetName = self.extractDataFromHdf5(
                variableName, indices
            )
        elif isinstance(self.file, pd.core.frame.DataFrame):
            dataToBePlotted = np.array(self.file[variableName])
            fullDatasetName = variableName
        else:
            raise NotImplementedError
        return dataToBePlotted, fullDatasetName

    def selectDock(self, currentSubwindow, option):
        keys = list(currentSubwindow.widget().docks.data.keys())
        if (
            option is PlottingOption.ADD_NEW_WORKBOOK
            or option is PlottingOption.ADD_NEW_WORKSHEET
            or (option is PlottingOption.APPEND_IN_CURRENT_WORKSHEET and not keys)
        ):
            widget: CurveContainer = CurveContainer()
            countableDock = CountableDock()
            countableDock.addWidget(widget)
            dock = currentSubwindow.widget().addDock(countableDock, "bottom")
        elif option is PlottingOption.APPEND_IN_CURRENT_WORKSHEET:
            dock = currentSubwindow.widget().docks[keys[-1]]
        else:
            raise NotImplementedError
        return dock

    def selectSubwindow(self, option):
        currentSubwindow = self.plotArea.mdiArea.currentSubWindow()
        if option is PlottingOption.ADD_NEW_WORKBOOK or (
            (
                option is PlottingOption.APPEND_IN_CURRENT_WORKSHEET
                or option is PlottingOption.ADD_NEW_WORKSHEET
            )
            and currentSubwindow is None
            and not self.plotArea.mdiArea.subWindowList()
        ):
            self.plotArea.addWorkbook("Untitled")
            currentSubwindow = self.plotArea.mdiArea.subWindowList()[-1]
        elif (
            option == PlottingOption.ADD_NEW_WORKSHEET
            or option is PlottingOption.APPEND_IN_CURRENT_WORKSHEET
        ):
            # The first subwindow is not active, so find it manually.
            if currentSubwindow is None:
                currentSubwindow = self.plotArea.mdiArea.subWindowList()[-1]
        else:
            raise NotImplementedError
        return currentSubwindow

    def loadCsv(self, filename):
        dataFrame = pd.read_csv(filename)
        return dataFrame

    def loadHdf5(self, filename):
        f = h5py.File(filename, "r")
        return f

    def extractDataFromHdf5(self, datasetName, indices=None):
        data = np.array(self.file.get(datasetName))
        shape = data.shape
        logger.debug(f"{datasetName} {shape} is going to be plotted.")
        listZeros = ["0" for _ in range(len(shape) - 1)]
        defaultText = "[" + ", ".join(listZeros) + ", :]"

        if len(shape) > 1:

            if indices is None:
                dialog = SizedInputDialog(self, QSize(400, 200))
                indices, okPressed = dialog.getText(
                    self,
                    f"Index selection",
                    f"The selected dataset has dimensions: {shape}. \n"
                    f"Enter below the indices to be plotted. \n\n"
                    f"Example: [1,:]",
                    text=defaultText,
                )

                if not okPressed:
                    return

            try:
                toBeEvaluated = "data" + indices
                dataToBePlotted = eval(toBeEvaluated)
            except SyntaxError:
                return

            fullDatasetName = datasetName + indices

        else:
            dataToBePlotted = data
            fullDatasetName = datasetName

        return dataToBePlotted, fullDatasetName

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

    def createActions(self) -> None:
        super().createActions()

        self.openWorkspaceAct = self.createAction(
            "&Open workspace",
            self.openWorkspace,
            "Open workspace",
            QKeySequence("Ctrl+Shift+o"),
        )

    def createFileMenu(self):
        super().createFileMenu()
        self.fileMenu.addAction(self.openWorkspaceAct)

    def createToolBars(self) -> None:
        super().createToolBars()
        self.fileToolBar.addAction(self.openWorkspaceAct)

    def openWorkspace(self):
        pass

    def saveFile(self):
        for workbook in self.plotArea.mdiArea.subWindowList():
            dockArea: DockArea = workbook.widget()
            print(dockArea.saveState())
            keys = list(dockArea.docks.data.keys())
            for key in keys:
                dock = dockArea.docks[key]
                graph: RangedPlot = dock.widgets[0].graph
                print(graph.saveState())
                plotItem = graph.getPlotItem()
                print(plotItem.saveState())

    def saveFileAs(self):
        raise NotImplementedError

    def newFile(self):
        self.plotArea.addWorkbook()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PlotterWindow()
    window.showMaximized()

    # Open file
    f = window.openFile("../../data/test.hdf5")
    window.plotData("sim_data/pos_k_i_dt", indices="[0,0,:]")

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
